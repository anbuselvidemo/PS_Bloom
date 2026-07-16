"""Small helper around psycopg2 for connecting and upserting readings."""
import os
import psycopg2
import psycopg2.extras


def get_connection():
    return psycopg2.connect(
        host=os.environ.get("PGHOST", "localhost"),
        port=os.environ.get("PGPORT", 5432),
        dbname=os.environ.get("PGDATABASE", "bloomeroo"),
        user=os.environ.get("PGUSER", "postgres"),
        password=os.environ.get("PGPASSWORD", ""),
    )


UPSERT_SQL = """
INSERT INTO sensor_readings (site_id, reading_time, temperature, humidity, latitude, longitude)
VALUES %s
ON CONFLICT ON CONSTRAINT uq_reading DO NOTHING
"""


def insert_readings(conn, readings):
    """Bulk insert a list of reading dicts, skipping ones already stored.

    Returns the number of rows actually inserted (duplicates are skipped,
    not counted).
    """
    if not readings:
        return 0

    rows = [
        (
            r["site_id"],
            r["reading_time"],
            r.get("temperature"),
            r.get("humidity"),
            r.get("latitude"),
            r.get("longitude"),
        )
        for r in readings
    ]

    with conn.cursor() as cur:
        psycopg2.extras.execute_values(cur, UPSERT_SQL, rows)
        inserted = cur.rowcount
    conn.commit()
    return inserted
