import os, json, uuid6, psycopg2, sys
from utils import *

DATABASE_URL = os.environ.get("DATABASE_URL", "").replace("postgres://", "postgresql://")

def seed(path):
    print("🔵 Loading file...")

    with open(path) as f:
        data = json.load(f)

    print("🔵 Raw data type:", type(data))

    if isinstance(data, dict):
        print("🔵 Keys:", data.keys())

    if isinstance(data, dict):
        data = data.get("profiles") or data.get("data") or []

    print("🔵 Final records:", len(data))

    conn = psycopg2.connect(DATABASE_URL)
    print("🟢 DB connected")

    c = conn.cursor()

    values = []

    for p in data:
        if not isinstance(p, dict):
            continue

        values.append((
            str(uuid6.uuid7()),
            p["name"].lower(),
            p["gender"],
            p["gender_probability"],
            p["age"],
            age_to_group(p["age"]),
            p["country_id"],
            COUNTRY_ID_TO_NAME.get(p["country_id"], p["country_id"]),
            p["country_probability"]
        ))

    c.executemany("""
        INSERT INTO profiles VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW())
        ON CONFLICT (name) DO NOTHING
    """, values)

    conn.commit()
    conn.close()

    print(f"Done! {len(values)} profiles processed.")

if __name__ == "__main__":
    seed(sys.argv[1])