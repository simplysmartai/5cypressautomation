"""
conftest.py
Shared pytest fixtures for 5 Cypress Automation test suite.

All fixtures that need to be shared across unit and integration tests live here.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent


# ---------------------------------------------------------------------------
# Environment fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_env(monkeypatch):
    """
    Set all required env vars to safe test values.
    Apply to any test that imports from execution/shared/config.py.
    """
    env_vars = {
        "QBO_CLIENT_ID":         "test_qbo_client_id",
        "QBO_CLIENT_SECRET":     "test_qbo_client_secret",
        "QBO_REFRESH_TOKEN":     "test_qbo_refresh_token",
        "QBO_REALM_ID":          "123456789",
        "QBO_ENVIRONMENT":       "sandbox",
        "STRIPE_SECRET_KEY":     "sk_test_placeholder_key",
        "RESEND_API_KEY":        "re_test_placeholder_key",
        "TELEGRAM_BOT_TOKEN":    "test:telegram_token",
        "TELEGRAM_CHAT_ID":      "12345",
        "ANTHROPIC_API_KEY":     "sk-ant-test-placeholder",
        "OPENAI_API_KEY":        "sk-test-placeholder",
        "DATAFORSEO_LOGIN":      "test@example.com",
        "DATAFORSEO_PASSWORD":   "test_password",
        "ZOHO_CLIENT_ID":        "test_zoho_client_id",
        "ZOHO_CLIENT_SECRET":    "test_zoho_client_secret",
        "ZOHO_REFRESH_TOKEN":    "test_zoho_refresh_token",
        "DRY_RUN":               "true",
    }
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)
    return env_vars


@pytest.fixture
def no_qbo_env(monkeypatch):
    """Env with QBO credentials removed — tests should raise ConfigError."""
    monkeypatch.delenv("QBO_CLIENT_ID", raising=False)
    monkeypatch.delenv("QBO_CLIENT_SECRET", raising=False)


# ---------------------------------------------------------------------------
# Client data fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_info_json() -> dict:
    """Nexairi-style flat info.json structure."""
    return {
        "client_name":   "Test Corp",
        "client_slug":   "test-corp",
        "contact_name":  "Jane Smith",
        "contact_email": "jane@testcorp.com",
        "phone":         "+1-555-0100",
        "website":       "https://testcorp.com",
        "status":        "active",
        "start_date":    "2025-01-01",
        "industry":      "Technology",
        "tags":          ["b2b", "tech"],
        "workflows":     [],
        "deliverables":  [],
        "notes":         "Test client fixture",
    }


@pytest.fixture
def sample_client_config() -> dict:
    """Remy-lasers-style hierarchical client-config.json structure."""
    return {
        "client_name":    "Laser Corp",
        "status":         "prospecting",
        "engagement_type":"trial_program",
        "trial_program": {
            "type":       "form_to_fulfillment",
            "investment": 2500,
            "start_date": None,
            "end_date":   None,
            "status":     "pending",
        },
        "contact": {
            "company":         "Laser Corp",
            "primary_contact": "Bob Laser",
            "title":           "CEO",
            "email":           "bob@lasercorp.com",
            "phone":           "+1-555-0200",
        },
        "business_info": {
            "industry": "Manufacturing",
            "monthly_order_volume": 200,
            "current_systems": {
                "form":       "Microsoft Forms",
                "accounting": "QuickBooks Online",
                "shipping":   "ShipStation",
                "inventory":  "TBD",
            },
            "pain_points": ["Manual order entry", "No shipping automation"],
        },
        "roi_estimate": {
            "monthly_orders":           200,
            "manual_time_per_order":    15,
            "automated_time_per_order": 0.5,
            "hourly_cost":              30,
            "monthly_savings":          735,
            "annual_savings":           8820,
            "break_even_months":        4,
        },
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-15T00:00:00Z",
    }


@pytest.fixture
def sample_canonical_client() -> dict:
    """Fully normalised canonical client dict (post-migration)."""
    return {
        "slug":            "test-corp",
        "name":            "Test Corp",
        "website":         "https://testcorp.com",
        "status":          "active",
        "engagement_type": "retainer",
        "contact": {
            "name":    "Jane Smith",
            "title":   "",
            "email":   "jane@testcorp.com",
            "phone":   "+1-555-0100",
            "company": "Test Corp",
        },
        "business": {
            "industry":            "Technology",
            "pain_points":         [],
            "monthly_order_volume":None,
            "current_systems":     {},
        },
        "trial_program":   None,
        "roi_estimate":    None,
        "api_access": {
            "qbo_company_id":   None,
            "shipstation_key":  None,
            "stripe_customer":  None,
        },
        "created_at":  "2025-01-01T00:00:00+00:00",
        "updated_at":  "2026-01-01T00:00:00+00:00",
        "notes":       "Test client fixture",
        "tags":        ["b2b", "tech"],
        "_migrated_from": "info.json",
    }


# ---------------------------------------------------------------------------
# API mock fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_qbo_response() -> dict:
    """Minimal valid QBO invoice response."""
    return {
        "Invoice": {
            "Id":          "INV-001",
            "DocNumber":   "5C-0001",
            "TotalAmt":    500.00,
            "Balance":     500.00,
            "CustomerRef": {"value": "1", "name": "Test Corp"},
        }
    }


@pytest.fixture
def mock_stripe_customer() -> dict:
    """Minimal valid Stripe customer object."""
    return {
        "id":    "cus_test123",
        "email": "jane@testcorp.com",
        "name":  "Jane Smith",
    }
