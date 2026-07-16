# PS_Bloom
A small CLI that fetches readings from the City of Melbourne
[Microclimate Sensor Readings](https://data.melbourne.vic.gov.au/explore/dataset/microclimate-sensor-readings/)
API and loads them into Postgres so the analyst team can look at
temperature/humidity patterns by location and time.

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
