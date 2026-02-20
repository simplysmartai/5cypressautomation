#!/usr/bin/env python3
"""
Google Maps Local Business Scraper
Scrapes Google Places API for local SMB leads within a radius of a given zip code.
Outputs a CSV file per niche, ready to feed into lead_research_orchestrator.py.

Usage:
    # Single niche
    python execution/google_maps_scraper.py \
        --config config/local_lead_gen_config.json \
        --niche med_spa

    # All niches in config
    python execution/google_maps_scraper.py \
        --config config/local_lead_gen_config.json \
        --all-niches

    # Override radius or zip
    python execution/google_maps_scraper.py \
        --config config/local_lead_gen_config.json \
        --niche dental \
        --zip 30022 \
        --radius 30

Required env vars (.env):
    GOOGLE_PLACES_API_KEY   — Google Maps Places API key
    SLACK_WEBHOOK_URL       — (optional) Slack webhook for run summary
"""

import argparse
import csv
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# Google Places API endpoints
PLACES_TEXT_SEARCH_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"
PLACES_DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"
GEOCODE_URL = "https://maps.googleapis.com/maps/api/geocode/json"

# Fields to request from Place Details (billed per field group)
# Basic: name, place_id, formatted_address, geometry  (no extra cost)
# Contact: formatted_phone_number, website, opening_hours
# Atmosphere: rating, user_ratings_total
PLACE_DETAIL_FIELDS = (
    "name,place_id,formatted_address,formatted_phone_number,"
    "website,rating,user_ratings_total,business_status,types,url"
)


# ---------------------------------------------------------------------------
# Geocoding helpers
# ---------------------------------------------------------------------------

def zip_to_latlng(zip_code: str, api_key: str) -> Optional[tuple[float, float]]:
    """Convert a US zip code to (lat, lng) using Geocoding API."""
    params = {"address": zip_code, "key": api_key}
    resp = requests.get(GEOCODE_URL, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    if data.get("status") != "OK" or not data.get("results"):
        logger.error("Geocoding failed for zip %s: %s", zip_code, data.get("status"))
        return None
    loc = data["results"][0]["geometry"]["location"]
    return loc["lat"], loc["lng"]


# ---------------------------------------------------------------------------
# Places search + detail enrichment
# ---------------------------------------------------------------------------

def search_places(keyword: str, lat: float, lng: float, radius_meters: int,
                  api_key: str) -> List[Dict]:
    """
    Text search for businesses matching `keyword` within radius.
    Handles pagination (up to 3 pages = ~60 results per keyword).
    """
    results = []
    params = {
        "query": keyword,
        "location": f"{lat},{lng}",
        "radius": radius_meters,
        "type": "establishment",
        "key": api_key,
    }

    page = 0
    next_page_token = None

    while page < 3:  # cap at 3 pages (60 results)
        if next_page_token:
            params = {"pagetoken": next_page_token, "key": api_key}
            time.sleep(2)  # Google requires a short delay before using page token

        resp = requests.get(PLACES_TEXT_SEARCH_URL, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        status = data.get("status")
        if status not in ("OK", "ZERO_RESULTS"):
            logger.warning("Places search status: %s — stopping pagination", status)
            break

        results.extend(data.get("results", []))
        next_page_token = data.get("next_page_token")
        page += 1

        if not next_page_token:
            break

    logger.info("  Found %d raw results for keyword: %s", len(results), keyword)
    return results


def get_place_details(place_id: str, api_key: str) -> Dict:
    """Fetch enriched details for a single place."""
    params = {
        "place_id": place_id,
        "fields": PLACE_DETAIL_FIELDS,
        "key": api_key,
    }
    try:
        resp = requests.get(PLACES_DETAILS_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data.get("status") == "OK":
            return data.get("result", {})
    except Exception as e:
        logger.warning("  Failed to get details for %s: %s", place_id, e)
    return {}


# ---------------------------------------------------------------------------
# Lead scoring
# ---------------------------------------------------------------------------

def score_lead(detail: Dict, config: Dict) -> int:
    """
    Score a lead 0-100 based on ICP fit, buying signals, and reachability.
    Weights match config/local_lead_gen_config.json scoring_model.
    """
    score = 0
    model = config.get("scoring_model", {})

    # --- ICP Fit (40 pts) ---
    icp_score = 0
    icp = config.get("icp", {})

    # Has website
    if detail.get("website"):
        icp_score += 15

    # Has phone
    if detail.get("formatted_phone_number"):
        icp_score += 10

    # Business is operational
    if detail.get("business_status") == "OPERATIONAL":
        icp_score += 15

    score += min(icp_score, 40)

    # --- Buying Signals (40 pts) ---
    signal_score = 0
    review_count = detail.get("user_ratings_total", 0)
    rating = detail.get("rating", 0)

    # Low review count = likely no automated review system
    if review_count < 20:
        signal_score += 25
    elif review_count < 50:
        signal_score += 15
    elif review_count < 100:
        signal_score += 5

    # No website = no automation, but also harder to contact (slight penalty)
    if not detail.get("website"):
        signal_score += 5

    # Low rating = pain is happening (service problems, likely poor follow-up)
    if 0 < rating < 4.0:
        signal_score += 10

    score += min(signal_score, 40)

    # --- Reachability (20 pts) ---
    reach_score = 0
    if detail.get("formatted_phone_number"):
        reach_score += 10
    if detail.get("website"):
        reach_score += 10

    score += min(reach_score, 20)

    return min(score, 100)


# ---------------------------------------------------------------------------
# CSV output
# ---------------------------------------------------------------------------

def build_lead_row(detail: Dict, niche_id: str, keyword: str, score: int,
                   scraped_at: str) -> Dict:
    """Flatten a Place Details response into a flat CSV row."""
    address = detail.get("formatted_address", "")
    parts = address.split(",")
    city = parts[1].strip() if len(parts) >= 2 else ""
    state_zip = parts[2].strip() if len(parts) >= 3 else ""

    return {
        "niche": niche_id,
        "search_keyword": keyword,
        "business_name": detail.get("name", ""),
        "place_id": detail.get("place_id", ""),
        "address": address,
        "city": city,
        "state_zip": state_zip,
        "phone": detail.get("formatted_phone_number", ""),
        "website": detail.get("website", ""),
        "google_maps_url": detail.get("url", ""),
        "rating": detail.get("rating", ""),
        "review_count": detail.get("user_ratings_total", 0),
        "business_status": detail.get("business_status", ""),
        "fit_score": score,
        "status": "new",
        "email": "",           # to be enriched downstream
        "owner_name": "",      # to be enriched downstream
        "notes": "",
        "scraped_at": scraped_at,
    }


CSV_COLUMNS = [
    "niche", "search_keyword", "business_name", "place_id",
    "address", "city", "state_zip", "phone", "website",
    "google_maps_url", "rating", "review_count", "business_status",
    "fit_score", "status", "email", "owner_name", "notes", "scraped_at",
]


def write_csv(rows: List[Dict], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    logger.info("Wrote %d leads to %s", len(rows), output_path)


# ---------------------------------------------------------------------------
# Slack notification
# ---------------------------------------------------------------------------

def notify_slack(message: str) -> None:
    webhook = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook:
        return
    try:
        requests.post(webhook, json={"text": message}, timeout=5)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Core scraper logic
# ---------------------------------------------------------------------------

def scrape_niche(niche: Dict, config: Dict, lat: float, lng: float,
                 radius_meters: int, api_key: str, output_dir: Path,
                 min_score: int = 0) -> List[Dict]:
    """
    Scrape all keywords for a single niche, deduplicate by place_id,
    score each lead, and write a CSV.
    """
    niche_id = niche["id"]
    keywords = niche["google_maps_keywords"]
    logger.info("=== Niche: %s (%d keywords) ===", niche["label"], len(keywords))

    seen_place_ids: set = set()
    all_rows: List[Dict] = []
    scraped_at = datetime.now().strftime("%Y-%m-%d %H:%M")

    for keyword in keywords:
        full_keyword = f"{keyword} near {config['geography']['anchor_zip']}"
        raw = search_places(full_keyword, lat, lng, radius_meters, api_key)

        for place in raw:
            pid = place.get("place_id", "")
            if pid in seen_place_ids:
                continue
            seen_place_ids.add(pid)

            # Enrich with details
            detail = get_place_details(pid, api_key)
            if not detail:
                continue

            # Skip permanently closed
            if detail.get("business_status") == "CLOSED_PERMANENTLY":
                continue

            score = score_lead(detail, config)

            # Apply minimum score filter
            if score < min_score:
                continue

            row = build_lead_row(detail, niche_id, keyword, score, scraped_at)
            all_rows.append(row)
            time.sleep(0.1)  # gentle rate limiting

    # Sort by fit_score descending
    all_rows.sort(key=lambda r: int(r.get("fit_score", 0)), reverse=True)

    date_str = datetime.now().strftime("%Y-%m-%d")
    output_path = output_dir / f"leads_{niche_id}_{date_str}.csv"
    write_csv(all_rows, output_path)

    hot_leads = [r for r in all_rows if int(r.get("fit_score", 0)) >= config["thresholds"]["hot_immediate_contact"]]
    logger.info(
        "  %s: %d total leads, %d hot (score >= %d)",
        niche["label"], len(all_rows), len(hot_leads),
        config["thresholds"]["hot_immediate_contact"]
    )

    return all_rows


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Scrape Google Maps for local SMB leads")
    parser.add_argument("--config", required=True, help="Path to local_lead_gen_config.json")
    parser.add_argument("--niche", help="Niche id to scrape (e.g. med_spa)")
    parser.add_argument("--all-niches", action="store_true", help="Scrape all niches in config")
    parser.add_argument("--zip", dest="zip_code", help="Override anchor zip from config")
    parser.add_argument("--radius", type=int, help="Override radius (miles) from config")
    parser.add_argument("--min-score", type=int, default=0,
                        help="Minimum fit score to include in output (default: 0 = all)")
    parser.add_argument("--output-dir", default=".tmp",
                        help="Directory for CSV output (default: .tmp)")
    args = parser.parse_args()

    if not args.niche and not args.all_niches:
        parser.error("Provide --niche <id> or --all-niches")

    api_key = os.getenv("GOOGLE_PLACES_API_KEY")
    if not api_key:
        logger.error("GOOGLE_PLACES_API_KEY not set in .env")
        sys.exit(1)

    with open(args.config, "r") as f:
        config = json.load(f)

    zip_code = args.zip_code or config["geography"]["anchor_zip"]
    radius_miles = args.radius or config["geography"]["radius_miles"]
    radius_meters = int(radius_miles * 1609.34)

    logger.info("Geocoding zip code %s ...", zip_code)
    coords = zip_to_latlng(zip_code, api_key)
    if not coords:
        logger.error("Could not geocode zip %s — check API key and billing", zip_code)
        sys.exit(1)
    lat, lng = coords
    logger.info("Anchor: %.5f, %.5f | Radius: %d miles (%d m)", lat, lng, radius_miles, radius_meters)

    output_dir = Path(args.output_dir)
    niches = config["target_niches"]

    if args.niche:
        niches = [n for n in niches if n["id"] == args.niche]
        if not niches:
            valid = [n["id"] for n in config["target_niches"]]
            logger.error("Unknown niche '%s'. Valid options: %s", args.niche, ", ".join(valid))
            sys.exit(1)

    # Sort by priority
    niches_sorted = sorted(niches, key=lambda n: n.get("priority", 99))

    total_leads = 0
    total_hot = 0
    summary_lines = []

    for niche in niches_sorted:
        rows = scrape_niche(
            niche, config, lat, lng, radius_meters, api_key,
            output_dir, min_score=args.min_score
        )
        hot = len([r for r in rows if int(r.get("fit_score", 0)) >= config["thresholds"]["hot_immediate_contact"]])
        total_leads += len(rows)
        total_hot += hot
        summary_lines.append(f"  • {niche['label']}: {len(rows)} leads, {hot} hot")

    summary = (
        f"*Google Maps Scraper — Run Complete*\n"
        f"Zip: {zip_code} | Radius: {radius_miles}mi | {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        f"Total leads: {total_leads} | Hot (score ≥ {config['thresholds']['hot_immediate_contact']}): {total_hot}\n"
        + "\n".join(summary_lines)
        + f"\n\nCSVs saved to: `{output_dir}/`"
    )

    print("\n" + summary)
    notify_slack(summary)


if __name__ == "__main__":
    main()
