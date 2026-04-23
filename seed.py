def seed(path):
    with open(path) as f:
        data = json.load(f)

    if isinstance(data, dict) and "data" in data:
        data = data["data"]

    conn = psycopg2.connect(DATABASE_URL)
    c = conn.cursor()

    for p in data:
        if not isinstance(p, dict):
            continue  # safety guard

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