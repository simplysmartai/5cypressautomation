"""
tests/unit/test_normalize_clients.py
Unit tests for scripts/normalize_clients.py

Tests:
- dry-run flag does not write files
- Backup creation on migration
- Report summary counts
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


class TestMigrateClient:
    def test_dry_run_does_not_write(self, tmp_path, sample_info_json):
        """--dry-run should not create client.json."""
        client_dir = tmp_path / "test-corp"
        client_dir.mkdir()
        (client_dir / "info.json").write_text(json.dumps(sample_info_json), encoding="utf-8")

        import scripts.normalize_clients as nc
        original = nc.CLIENTS_DIR
        nc.CLIENTS_DIR = tmp_path
        try:
            from scripts.normalize_clients import migrate_client
            result = migrate_client("test-corp", dry_run=True)
        finally:
            nc.CLIENTS_DIR = original

        assert not (client_dir / "client.json").exists()
        assert result["status"] == "would_migrate"

    def test_migration_creates_canonical(self, tmp_path, sample_info_json):
        """Successful migration writes client.json."""
        client_dir = tmp_path / "test-corp"
        client_dir.mkdir()
        (client_dir / "info.json").write_text(json.dumps(sample_info_json), encoding="utf-8")

        import scripts.normalize_clients as nc
        original = nc.CLIENTS_DIR
        nc.CLIENTS_DIR = tmp_path
        try:
            from scripts.normalize_clients import migrate_client
            result = migrate_client("test-corp", dry_run=False)
        finally:
            nc.CLIENTS_DIR = original

        assert (client_dir / "client.json").exists()
        assert result["status"] == "ok"
        data = json.loads((client_dir / "client.json").read_text())
        assert data["slug"] == "test-corp"

    def test_migration_creates_backup(self, tmp_path, sample_info_json):
        """Original info.json is backed up to backups/."""
        client_dir = tmp_path / "test-corp"
        client_dir.mkdir()
        (client_dir / "info.json").write_text(json.dumps(sample_info_json), encoding="utf-8")

        import scripts.normalize_clients as nc
        original = nc.CLIENTS_DIR
        nc.CLIENTS_DIR = tmp_path
        try:
            from scripts.normalize_clients import migrate_client
            migrate_client("test-corp", dry_run=False)
        finally:
            nc.CLIENTS_DIR = original

        assert (client_dir / "backups" / "info.json").exists()

    def test_already_migrated_skipped(self, tmp_path, sample_canonical_client):
        """If client.json already exists, return skipped status."""
        client_dir = tmp_path / "test-corp"
        client_dir.mkdir()
        (client_dir / "client.json").write_text(
            json.dumps(sample_canonical_client), encoding="utf-8"
        )

        import scripts.normalize_clients as nc
        original = nc.CLIENTS_DIR
        nc.CLIENTS_DIR = tmp_path
        try:
            from scripts.normalize_clients import migrate_client
            result = migrate_client("test-corp", dry_run=False)
        finally:
            nc.CLIENTS_DIR = original

        assert result["status"] == "skipped"

    def test_no_source_returns_no_source(self, tmp_path):
        """If no info.json or client-config.json, return no_source."""
        client_dir = tmp_path / "empty-client"
        client_dir.mkdir()

        import scripts.normalize_clients as nc
        original = nc.CLIENTS_DIR
        nc.CLIENTS_DIR = tmp_path
        try:
            from scripts.normalize_clients import migrate_client
            result = migrate_client("empty-client", dry_run=False)
        finally:
            nc.CLIENTS_DIR = original

        assert result["status"] == "no_source"
