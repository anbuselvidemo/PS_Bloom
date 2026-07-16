#!/usr/bin/env python
"""CLI: fetch microclimate readings from the City of Melbourne API and load
them into Postgres.

Usage:
    python load_data.py --limit 1000
"""
import argparse
import sys

from dotenv import load_dotenv

from api_client import fetch_records
from transform import transform_records
from db import get_connection, insert_readings


def parse_args():
    parser = argparse.ArgumentParser(description="Load microclimate sensor data into Postgres")
    parser.add_argument(
        "--limit",
        type=int,
        default=1000,
        help="Minimum number of records to fetch from the API (default: 1000)",
    )
    return parser.parse_args()


def main():
    load_dotenv()
    args = parse_args()

    print(f"Fetching up to {args.limit} records from the API...")
    try:
        raw_records = fetch_records(limit=args.limit)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"Fetched {len(raw_records)} raw records. Transforming...")
    rows = transform_records(raw_records)
    dropped = len(raw_records) - len(rows)
    if dropped:
        print(f"Dropped {dropped} record(s) missing required fields.")

    print("Connecting to Postgres...")
    try:
        conn = get_connection()
    except Exception as exc:  # noqa: BLE001 - want to report any connection failure clearly
        print(f"ERROR: could not connect to database: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        inserted = insert_readings(conn, rows)
    finally:
        conn.close()

    skipped = len(rows) - inserted
    print(f"Done. Inserted {inserted} new row(s), skipped {skipped} duplicate(s).")


if __name__ == "__main__":
    main()
