"""
seed.py — Populate the profiles table from the seed data file.

Usage:
    python seed.py path/to/seed_file.json
    python seed.py path/to/seed_file.csv

Re-running is safe: existing names are skipped (ON CONFLICT DO NOTHING).
"""

import os
import sys
import json
import csv
import uuid6
import psycopg2
from datetime import datetime, timezone

# ── DB connection ──────────────────────────────────────────────────────────────
DATABASE_URL = os.environ.get("DATABASE_URL", "")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# ── Country lookup (same as app.py) ───────────────────────────────────────────
COUNTRY_ID_TO_NAME = {
    "NG": "Nigeria",        "AO": "Angola",          "KE": "Kenya",
    "BJ": "Benin",          "GH": "Ghana",           "ZA": "South Africa",
    "EG": "Egypt",          "ET": "Ethiopia",        "TZ": "Tanzania",
    "UG": "Uganda",         "SN": "Senegal",         "CM": "Cameroon",
    "CI": "Côte d'Ivoire",  "ML": "Mali",            "BF": "Burkina Faso",
    "NE": "Niger",          "TD": "Chad",            "SD": "Sudan",
    "SO": "Somalia",        "MZ": "Mozambique",      "MG": "Madagascar",
    "ZM": "Zambia",         "ZW": "Zimbabwe",        "MW": "Malawi",
    "RW": "Rwanda",         "BI": "Burundi",         "TG": "Togo",
    "SL": "Sierra Leone",   "LR": "Liberia",         "GN": "Guinea",
    "GW": "Guinea-Bissau",  "GM": "Gambia",          "MR": "Mauritania",
    "MA": "Morocco",        "DZ": "Algeria",         "TN": "Tunisia",
    "LY": "Libya",          "CG": "Congo",           "CD": "DR Congo",
    "GA": "Gabon",          "GQ": "Equatorial Guinea","CF": "Central African Republic",
    "SS": "South Sudan",    "ER": "Eritrea",         "DJ": "Djibouti",
    "KM": "Comoros",        "CV": "Cabo Verde",      "ST": "São Tomé and Príncipe",
    "SC": "Seychelles",     "MU": "Mauritius",       "BW": "Botswana",
    "NA": "Namibia",        "LS": "Lesotho",         "SZ": "Eswatini",
    "US": "United States",  "GB": "United Kingdom",  "FR": "France",
    "DE": "Germany",        "IT": "Italy",           "ES": "Spain",
    "PT": "Portugal",       "BR": "Brazil",          "IN": "India",
    "CN": "China",          "JP": "Japan",           "RU": "Russia",
    "CA": "Canada",         "AU": "Australia",       "MX": "Mexico",
    "AR": "Argentina",      "CO": "Colombia",        "VE": "Venezuela",
    "PE": "Peru",           "CL": "Chile",           "ID": "Indonesia",
    "PK": "Pakistan",       "BD": "Bangladesh",      "PH": "Philippines",
    "VN": "Vietnam",        "TH": "Thailand",        "MY": "Malaysia",
    "SG": "Singapore",      "TR": "Turkey",          "IR": "Iran",
    "IQ": "Iraq",           "SA": "Saudi Arabia",    "AE": "United Arab Emirates",
    "IL": "Israel",         "KR": "South Korea",     "SE": "Sweden",
    "NO": "Norway",         "DK": "Denmark",         "FI": "Finland",
    "NL": "Netherlands",    "BE": "Belgium",         "CH": "Switzerland",
    "AT": "Austria",        "PL": "Poland",          "UA": "Ukraine",
    "RO": "Romania",        "GR": "Greece",          "NZ": "New Zealand",
}


def age_to_group(age: int) -> str:
    if age <= 12:  return "child"
    if age <= 19:  return "teenager"
    if age <= 59:  return "adult"
    return "senior"


def load_profiles(filepath: str) -> list:
    """Read a JSON or CSV file and return a list of dicts."""
    if filepath.endswith(".json"):
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Handle both a top-level list and {"data": [...]} shape
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            for key in ("data", "profiles", "results"):
                if key in data and isinstance(data[key], list):
                    return data[key]
        raise ValueError("Unexpected JSON structure — expected an array of profiles.")

    if filepath.endswith(".csv"):
        with open(filepath, "r", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    raise ValueError("Unsupported file format. Use .json or .csv")


def seed(filepath: str):
    profiles = load_profiles(filepath)
    print(f"Loaded {len(profiles)} profiles from {filepath}")

    conn = psycopg2.connect(DATABASE_URL)
    c    = conn.cursor()
    inserted = skipped = errors = 0

    for p in profiles:
        try:
            name = str(p.get("name", "")).strip().lower()
            if not name:
                errors += 1
                continue

            # Age / age_group
            age       = int(p.get("age") or 0)
            age_group = (p.get("age_group") or "").strip().lower() or age_to_group(age)

            # Country
            c_id   = str(p.get("country_id") or "").strip().upper()
            c_name = (p.get("country_name") or COUNTRY_ID_TO_NAME.get(c_id, c_id)).strip()

            # ID and timestamp
            profile_id = str(p.get("id") or uuid6.uuid7())
            created_at = (
                p.get("created_at")
                or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            )

            c.execute(
                """INSERT INTO profiles
                   (id, name, gender, gender_probability, age, age_group,
                    country_id, country_name, country_probability, created_at)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                   ON CONFLICT (name) DO NOTHING""",
                (
                    profile_id,
                    name,
                    str(p.get("gender") or "").strip().lower(),
                    float(p.get("gender_probability") or 0),
                    age,
                    age_group,
                    c_id,
                    c_name,
                    float(p.get("country_probability") or 0),
                    created_at,
                ),
            )
            if c.rowcount > 0:
                inserted += 1
            else:
                skipped += 1

        except Exception as e:
            errors += 1
            print(f"  ✗ Error on '{p.get('name', '?')}': {e}")

    conn.commit()
    conn.close()
    print(f"\n✓ Done — {inserted} inserted, {skipped} skipped (duplicates), {errors} errors.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python seed.py <path_to_seed_file.json|.csv>")
        sys.exit(1)
    seed(sys.argv[1])
