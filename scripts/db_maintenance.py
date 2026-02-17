#!/usr/bin/env python3
"""
Database Backup & Disaster Recovery Utility
Aligns with CTO Advisor Framework: Crisis Management (Data Loss)
"""

import os
import sqlite3
import shutil
from datetime import datetime
from pathlib import Path

# Paths
DB_PATH = Path('platform.db')
BACKUP_DIR = Path('backups')
MAX_BACKUPS = 7  # Keep one week of dailies

def create_backup():
    """Create a point-in-time snapshot of the database."""
    if not DB_PATH.exists():
        print(f"❌ Error: {DB_PATH} not found.")
        return False
        
    BACKUP_DIR.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = BACKUP_DIR / f"platform_backup_{timestamp}.db"
    
    try:
        # Use SQLite backup API for a hot backup while the app is running
        src = sqlite3.connect(DB_PATH)
        dst = sqlite3.connect(backup_path)
        with dst:
            src.backup(dst)
        dst.close()
        src.close()
        
        print(f"✅ Backup created: {backup_path}")
        _rotate_backups()
        return True
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return False

def _rotate_backups():
    """Remove old backups to save space."""
    backups = sorted(list(BACKUP_DIR.glob('platform_backup_*.db')))
    if len(backups) > MAX_BACKUPS:
        to_delete = backups[:-MAX_BACKUPS]
        for b in to_delete:
            os.remove(b)
            print(f"🧹 Rotated old backup: {b.name}")

def restore_latest():
    """Restore the most recent backup (destructive to current state)."""
    backups = sorted(list(BACKUP_DIR.glob('platform_backup_*.db')))
    if not backups:
        print("❌ No backups found to restore.")
        return False
        
    latest = backups[-1]
    print(f"⚠️ Restoring from: {latest.name}")
    
    # Safety: backup the current failing state before overwriting
    if DB_PATH.exists():
        shutil.move(DB_PATH, DB_PATH.with_suffix('.db.corrupt'))
        
    shutil.copy2(latest, DB_PATH)
    print("✅ Restoration complete. System state recovered.")
    return True

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "restore":
        restore_latest()
    else:
        create_backup()
