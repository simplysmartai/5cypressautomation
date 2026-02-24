#!/usr/bin/env python3
"""
Compatibility wrapper so the skill id `seo-audit` (hyphen) can be executed
by the skills runner which expects `execution/seo-audit.py`.

This forwards all CLI args to the real runner `seo_audit_runner.py`.
"""
import os
import sys
import subprocess

HERE = os.path.dirname(__file__)
REAL = os.path.join(HERE, 'seo_audit_runner.py')

if not os.path.exists(REAL):
    print(f"Error: expected runner at {REAL} not found.")
    sys.exit(2)

cmd = [sys.executable, REAL] + sys.argv[1:]
try:
    rc = subprocess.call(cmd)
    sys.exit(rc)
except KeyboardInterrupt:
    sys.exit(130)
except Exception as e:
    print(f"Wrapper execution failed: {e}")
    sys.exit(1)
