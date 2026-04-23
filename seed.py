import os, json, uuid6, psycopg2
from utils import age_to_group, COUNTRY_ID_TO_NAME

DATABASE_URL = os.environ.get("DATABASE_URL", "").replace("postgres://", "postgresql://")

def seed(path):
    with open(path) as f:
        data = json.load(f)

    conn = psycopg2.connect(DATABASE_URL)
    c = conn.cursor()

    for p in data:
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

if __name__ == "__main__":
    import sys
    seed(sys.argv[1])