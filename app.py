import os, re, uuid6
import requests as req
import psycopg2
from flask import Flask, request, jsonify
from flask_cors import CORS
from utils import *

app = Flask(__name__)
CORS(app)

DATABASE_URL = os.environ.get("DATABASE_URL", "").replace("postgres://", "postgresql://")

def get_conn():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            id UUID PRIMARY KEY,
            name VARCHAR UNIQUE NOT NULL,
            gender VARCHAR,
            gender_probability FLOAT,
            age INT,
            age_group VARCHAR,
            country_id VARCHAR(2),
            country_name VARCHAR,
            country_probability FLOAT,
            created_at TIMESTAMPTZ DEFAULT NOW()
        )
    """)
    c.execute("CREATE INDEX IF NOT EXISTS idx_filters ON profiles(gender, age_group, country_id)")
    conn.commit()
    conn.close()

@app.before_first_request
def setup():
    init_db()

def run_query(filters, page, limit):
    where, params = [], []

    for key, col in [("gender","gender"),("age_group","age_group"),("country_id","country_id")]:
        if key in filters:
            where.append(f"{col} = %s")
            params.append(filters[key])

    if "min_age" in filters:
        where.append("age >= %s"); params.append(filters["min_age"])
    if "max_age" in filters:
        where.append("age <= %s"); params.append(filters["max_age"])
    if "min_gender_probability" in filters:
        where.append("gender_probability >= %s"); params.append(filters["min_gender_probability"])
    if "min_country_probability" in filters:
        where.append("country_probability >= %s"); params.append(filters["min_country_probability"])

    where_sql = "WHERE " + " AND ".join(where) if where else ""

    sort_col = filters.get("sort_by", "created_at")
    order = filters.get("order", "asc").upper()
    offset = (page - 1) * limit

    conn = get_conn()
    c = conn.cursor()

    c.execute(f"SELECT COUNT(*) FROM profiles {where_sql}", params)
    total = c.fetchone()[0]

    c.execute(f"""
        SELECT id, name, gender, gender_probability, age, age_group,
               country_id, country_name, country_probability, created_at
        FROM profiles
        {where_sql}
        ORDER BY {sort_col} {order}
        LIMIT %s OFFSET %s
    """, params + [limit, offset])

    rows = c.fetchall()
    conn.close()

    return jsonify({
        "status": "success",
        "page": page,
        "limit": limit,
        "total": total,
        "data": [{
            "id": str(r[0]),
            "name": r[1],
            "gender": r[2],
            "gender_probability": r[3],
            "age": r[4],
            "age_group": r[5],
            "country_id": r[6],
            "country_name": r[7],
            "country_probability": r[8],
            "created_at": r[9].strftime("%Y-%m-%dT%H:%M:%SZ")
        } for r in rows]
    }), 200

def parse_nl(q):
    s = q.lower().strip()
    f = {}

    has_male = "male" in s
    has_female = "female" in s
    if has_male and not has_female:
        f["gender"] = "male"
    elif has_female and not has_male:
        f["gender"] = "female"

    if "child" in s: f["age_group"] = "child"
    elif "teen" in s: f["age_group"] = "teenager"
    elif "adult" in s: f["age_group"] = "adult"
    elif "senior" in s: f["age_group"] = "senior"

    if "young" in s:
        f["min_age"], f["max_age"] = 16, 24

    m = re.search(r"(above|over|older than)\s+(\d+)", s)
    if m: f["min_age"] = int(m.group(2))

    m = re.search(r"(below|under|younger than)\s+(\d+)", s)
    if m: f["max_age"] = int(m.group(2))

    m = re.search(r"(from|in)\s+([a-z\s]+)", s)
    if m:
        name = m.group(2).strip()
        cid = COUNTRY_NAME_TO_ID.get(name)
        if cid:
            f["country_id"] = cid

    return f if f else None

@app.route("/api/profiles", methods=["GET"])
def get_profiles():
    try:
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 10))
        if page < 1 or limit < 1 or limit > 50:
            raise ValueError
    except:
        return jsonify({"status":"error","message":"Invalid query parameters"}), 422

    filters = {}

    if g := request.args.get("gender"):
        if g not in VALID_GENDERS:
            return jsonify({"status":"error","message":"Invalid query parameters"}), 422
        filters["gender"] = g

    if ag := request.args.get("age_group"):
        if ag not in VALID_AGE_GROUPS:
            return jsonify({"status":"error","message":"Invalid query parameters"}), 422
        filters["age_group"] = ag

    if cid := request.args.get("country_id"):
        if not re.match(r"^[A-Za-z]{2}$", cid):
            return jsonify({"status":"error","message":"Invalid query parameters"}), 422
        filters["country_id"] = cid.upper()

    # safe parsing
    try:
        if v := request.args.get("min_age"): filters["min_age"] = int(v)
        if v := request.args.get("max_age"): filters["max_age"] = int(v)
        if v := request.args.get("min_gender_probability"): filters["min_gender_probability"] = float(v)
        if v := request.args.get("min_country_probability"): filters["min_country_probability"] = float(v)
    except:
        return jsonify({"status":"error","message":"Invalid query parameters"}), 422

    if s := request.args.get("sort_by"):
        if s not in VALID_SORT_COLS:
            return jsonify({"status":"error","message":"Invalid query parameters"}), 422
        filters["sort_by"] = s

    if o := request.args.get("order","asc"):
        if o not in ("asc","desc"):
            return jsonify({"status":"error","message":"Invalid query parameters"}), 422
        filters["order"] = o

    return run_query(filters, page, limit)

@app.route("/api/profiles/search", methods=["GET"])
def search():
    q = request.args.get("q","").strip()
    if not q:
        return jsonify({"status":"error","message":"Invalid query parameters"}), 400

    filters = parse_nl(q)
    if not filters:
        return jsonify({"status":"error","message":"Unable to interpret query"}), 400

    page = int(request.args.get("page",1))
    limit = int(request.args.get("limit",10))

    return run_query(filters, page, limit)

@app.route("/api/profiles", methods=["POST"])
def create():
    data = request.get_json()
    if not data or not data.get("name"):
        return jsonify({"status":"error","message":"Missing or empty name"}), 400

    name = data["name"].strip().lower()

    conn = get_conn()
    c = conn.cursor()

    c.execute("SELECT * FROM profiles WHERE name=%s", (name,))
    if c.fetchone():
        conn.close()
        return jsonify({"status":"success","message":"Profile already exists"}), 200

    try:
        g = req.get(f"https://api.genderize.io/?name={name}", timeout=10)
        a = req.get(f"https://api.agify.io/?name={name}", timeout=10)
        n = req.get(f"https://api.nationalize.io/?name={name}", timeout=10)

        if g.status_code != 200 or a.status_code != 200 or n.status_code != 200:
            conn.close()
            return jsonify({"status":"error","message":"Upstream server failure"}), 502

        g, a, n = g.json(), a.json(), n.json()
    except:
        conn.close()
        return jsonify({"status":"error","message":"Upstream server failure"}), 502

    if not g.get("gender") or a.get("age") is None or not n.get("country"):
        conn.close()
        return jsonify({"status":"error","message":"Upstream server failure"}), 502

    age = a["age"]
    country = max(n["country"], key=lambda x: x["probability"])
    cid = country["country_id"]

    c.execute("""
        INSERT INTO profiles VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW())
    """, (
        str(uuid6.uuid7()), name, g["gender"], g["probability"],
        age, age_to_group(age),
        cid, COUNTRY_ID_TO_NAME.get(cid, cid),
        country["probability"]
    ))

    conn.commit()
    conn.close()

    return jsonify({"status":"success"}), 201
@app.route("/api/profiles/<profile_id>", methods=["GET"])
def get_profile(profile_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        SELECT id, name, gender, gender_probability, age, age_group,
               country_id, country_name, country_probability, created_at
        FROM profiles WHERE id = %s
    """, (profile_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        return jsonify({"status":"error","message":"Profile not found"}), 404
    return jsonify({"status":"success","data":{
        "id": str(row[0]), "name": row[1], "gender": row[2],
        "gender_probability": row[3], "age": row[4], "age_group": row[5],
        "country_id": row[6], "country_name": row[7],
        "country_probability": row[8],
        "created_at": row[9].strftime("%Y-%m-%dT%H:%M:%SZ")
    }}), 200
@app.errorhandler(404)
def nf(_): return jsonify({"status":"error","message":"Profile not found"}), 404

@app.errorhandler(500)
def se(_): return jsonify({"status":"error","message":"Internal server error"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)