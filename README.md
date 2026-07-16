<<<<<<< HEAD
# Bloomeroo Microclimate Loader

=======
# PS_Bloom
>>>>>>> feb3eeef4a68c40e3a328b13a93eecd3766d2f28
A small CLI that fetches readings from the City of Melbourne
[Microclimate Sensor Readings](https://data.melbourne.vic.gov.au/explore/dataset/microclimate-sensor-readings/)
API and loads them into Postgres so the analyst team can look at
temperature/humidity patterns by location and time.

<<<<<<< HEAD
## How it works

```
api_client.py   fetch_records()      -> pages through the public API
transform.py    transform_records()  -> maps raw fields to our DB row shape
db.py           insert_readings()    -> bulk insert, skips duplicates
load_data.py                          -> CLI that wires the three together
```

=======
>>>>>>> feb3eeef4a68c40e3a328b13a93eecd3766d2f28
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
<<<<<<< HEAD

This fetches at least 1000 records (paginating 100 at a time), transforms
them, and inserts new rows. Output looks like:

```
Fetching up to 1000 records from the API...
Fetched 1000 raw records. Transforming...
Connecting to Postgres...
Done. Inserted 1000 new row(s), skipped 0 duplicate(s).
```

Run it again and you'll see `skipped 1000 duplicate(s)` instead — no
duplicate rows land in the table.

## 5. Run the tests

```bash
python -m pytest
```

Tests cover `transform.py` (field mapping / bad-record handling) and
`api_client.py` (pagination, respecting `limit`) using mocked HTTP calls —
no live API or database needed to run them.

## Design decisions & assumptions

- **Duplicates**: handled at the database level via a unique constraint
  on `(site_id, reading_time)`, so the loader can simply be re-run
  (e.g. on a schedule) without ever double-counting a reading.
- **Field names**: the live API wasn't reachable from the environment
  this was written in, so `transform.py`'s `FIELD_MAP` is based on the
  published data dictionary rather than a confirmed live response. If the
  real field names differ (e.g. temperature/humidity arrive as separate
  rows via a `type`/`value` pair rather than dedicated columns), only
  `transform.py` needs to change — everything downstream stays the same.
- **Schema is flat** (one row per site per timestamp with a temperature
  and humidity column) rather than a generic key/value table, since that's
  the simplest shape for the stated use case (patterns by location/time).
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
=======
>>>>>>> feb3eeef4a68c40e3a328b13a93eecd3766d2f28
