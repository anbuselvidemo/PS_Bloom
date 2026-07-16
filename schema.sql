-- Run once to prepare the database:
--   psql -h $PGHOST -U $PGUSER -d $PGDATABASE -f schema.sql

CREATE TABLE IF NOT EXISTS sensor_readings (
    id              BIGSERIAL PRIMARY KEY,
    site_id         TEXT NOT NULL,
    reading_time    TIMESTAMPTZ NOT NULL,
    temperature     NUMERIC,             -- degrees Celsius
    humidity        NUMERIC,             -- relative humidity, %
    latitude        DOUBLE PRECISION,
    longitude       DOUBLE PRECISION,
    inserted_at     TIMESTAMPTZ NOT NULL DEFAULT now(),

    -- One row per site/timestamp. This is what protects us from loading
    -- the same record twice if the script is re-run.
    CONSTRAINT uq_reading UNIQUE (site_id, reading_time)
);

CREATE INDEX IF NOT EXISTS idx_readings_site_time ON sensor_readings (site_id, reading_time);
