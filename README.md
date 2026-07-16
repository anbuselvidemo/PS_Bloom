# Bloomeroo Microclimate Loader

A small CLI that fetches readings from the City of Melbourne
[Microclimate sensors data](https://data.melbourne.vic.gov.au/explore/dataset/microclimate-sensors-data/)
API and loads them into Postgres so the analyst team can look at
temperature/humidity patterns by location and time.

## How it works
## 1. Prepare the database

You need a running Postgres instance (any local install or Docker works).

```bash
createdb bloomeroo
psql -d bloomeroo -f schema.sql
```

`schema.sql` creates one table, `sensor_readings`, with a unique
constraint on `(site_id, reading_time)`. Re-running the loader is safe —
matching rows are skipped (`ON CONFLICT DO NOTHING`) rather than duplicated.

## 2. Configure connection

```bash
cp .env.example .env
# edit .env with your Postgres host/user/password
```

## 3. Install dependencies

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

## 4. Run it

```bash
python load_data.py --limit 1000
```

This fetches at least 1000 records (paginating 100 at a time), transforms
them, and inserts new rows. Output looks like:
Run it again and you'll see `skipped 1000 duplicate(s)` instead — no
duplicate rows land in the table. Verified end-to-end against the live
API on 2026-07-16, with 1000 rows loaded and dedup confirmed on re-run.

## 5. Run the tests

```bash
python -m pytest -v
```

6 tests cover `transform.py` (field mapping, missing-field handling, a
record with no `latlong`) and `api_client.py` (pagination, respecting
`limit`) using mocked HTTP calls — no live API or database needed.

## Design decisions & assumptions

- **Duplicates**: handled at the database level via a unique constraint
  on `(site_id, reading_time)`, so the loader can simply be re-run
  (e.g. on a schedule) without ever double-counting a reading.
- **Dataset**: uses `microclimate-sensors-data`, the current, live dataset
  (~950k total records, updated every 15 minutes). An earlier, deprecated
  dataset (`microclimate-sensor-readings`) was capped at ~56 historical
  rows and ruled out during testing.
- **Field mapping** (confirmed against a live API response):
  `device_id` → `site_id`, `received_at` → `reading_time`,
  `airtemperature` → `temperature`, `relativehumidity` → `humidity`,
  `latlong.lat`/`latlong.lon` → `latitude`/`longitude`.
- **Other fields ignored**: the API also returns wind speed/direction,
  atmospheric pressure, PM2.5, PM10, and noise. These aren't needed for
  the stated use case (temperature/humidity by location and time) and
  are left out of the schema to keep things simple.
- **Schema is flat** (one row per site per timestamp with a temperature
  and humidity column) rather than a generic key/value table, since that's
  the simplest shape for the stated use case.
- **Retries**: `api_client.py` retries transient network errors 3x with a
  short backoff, since this is a public API over the internet.
- **No ORM**: plain `psycopg2` felt like enough for one table and one
  bulk insert; happy to discuss SQLAlchemy/Alembic if the schema were
  expected to grow.

## What I'd improve with more time

- Store the raw API response (e.g. in a `raw JSONB` column) alongside the
  parsed fields, so a bug in `transform.py` doesn't mean re-fetching data.
- Add an integration test that spins up Postgres (e.g. via `testcontainers`)
  and exercises `db.py` against a real database.
- Make `--limit` incremental (only fetch readings newer than the latest
  `reading_time` already stored) instead of always re-fetching from the top.
- Structured logging instead of `print`, and a `--dry-run` flag.
- A small Dockerfile / docker-compose for a one-command local setup
  (Postgres + loader).
