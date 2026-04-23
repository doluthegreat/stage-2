import os, json, uuid6, psycopg2, sys
from utils import *
import sys
import json

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

    for p in data:
        if not isinstance(p, dict):
            continue  

        name = p["name"].lower()
        age = p["age"]
        cid = p["country_id"]

        c.execute("""
            INSERT INTO profiles VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW())
            ON CONFLICT (name) DO NOTHING
        """, (
            str(uuid6.uuid7()), name, p["gender"], p["gender_probability"],
            age, age_to_group(age),
            cid, COUNTRY_ID_TO_NAME.get(cid, cid),
            p["country_probability"]
        ))

    conn.commit()
    conn.close()
    print(f"Done! {len(data)} profiles processed.")  
if __name__ == "__main__":
    seed(sys.argv[1])