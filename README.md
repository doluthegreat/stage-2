# INTELLIGENCE-QUERY-ENGINE
A demographic intelligence API for Insighta Labs that enables marketing teams, product teams, and growth analysts to segment users, identify patterns, and query large datasets quickly. Deployed to Railway @ [**Intelligence Query Engine 🧠 📊 🌍**](https://stage-2-production-1f46.up.railway.app)

---

## SUMMARY

This platform transforms a basic profile storage system into a fully queryable intelligence engine. It supports advanced multi-condition filtering, sorting, pagination, and a natural language search system — all rule-based, no AI or LLMs involved. The system is seeded with **2026 demographic profiles**, each storing gender, age group, and nationality alongside their respective confidence scores. The natural language query engine parses plain English queries like *"young males from nigeria"* and converts them into structured database filters automatically. All IDs are UUID v7, all timestamps are UTC ISO 8601, and all responses follow a strict structure required for automated grading.

---

## TECHNOLOGY USED

* **Python**
* **Flask**
* **PostgreSQL**
* **Gunicorn**
* **Railway**

---

## SETTING UP LOCALLY

To set up locally, follow the steps below:

* Clone the repository — `git clone https://github.com/your-username/intelligence-query-engine`
* Navigate into the cloned directory — `cd intelligence-query-engine`
* Create and activate a virtual environment:
  ```bash
  python -m venv venv
  source venv/bin/activate  # Windows: venv\Scripts\activate
  ```
* Install dependencies — `pip install -r requirements.txt`
* Create a `.env` file in the root directory and add your database URL:
  ```
  DATABASE_URL=postgresql://user:password@localhost:5432/insighta
  ```
* Initialize the database and seed profiles:
  ```bash
  python seed.py seed_profiles.json
  ```
* Start the development server:
  ```bash
  flask run
  ```

If all of the above was done correctly, the server should be running at `http://localhost:5000`.

---

## MAKING REQUESTS

### Base URL
```
https://stage-2-production-1f46.up.railway.app
```

---

### Endpoints

#### `GET /api/profiles`
Fetch all profiles with optional filters, sorting, and pagination.

**Supported Filters:**

| Parameter | Type | Description |
|---|---|---|
| `gender` | string | `male` or `female` |
| `age_group` | string | `child`, `teenager`, `adult`, `senior` |
| `country_id` | string | ISO 2-letter code e.g. `NG`, `KE` |
| `min_age` | integer | Minimum age |
| `max_age` | integer | Maximum age |
| `min_gender_probability` | float | Minimum gender confidence score |
| `min_country_probability` | float | Minimum country confidence score |
| `sort_by` | string | `age`, `created_at`, `gender_probability` |
| `order` | string | `asc` or `desc` |
| `page` | integer | Page number (default: 1) |
| `limit` | integer | Results per page (default: 10, max: 50) |

**Example:**
```
GET /api/profiles?gender=male&country_id=NG&min_age=25&sort_by=age&order=desc
```

**Response:**
```json
{
  "status": "success",
  "page": 1,
  "limit": 10,
  "total": 2026,
  "data": [ ... ]
}
```

---

#### `GET /api/profiles/search`
Query profiles using plain English natural language. Rule-based parsing only — no AI or LLMs.

**Query Parameters:**

| Parameter | Type | Description |
|---|---|---|
| `q` | string | Natural language query |
| `page` | integer | Page number (default: 1) |
| `limit` | integer | Results per page (default: 10, max: 50) |

**Example mappings:**

| Query | Interpreted As |
|---|---|
| `young males` | `gender=male` + `min_age=16` + `max_age=24` |
| `females above 30` | `gender=female` + `min_age=30` |
| `people from angola` | `country_id=AO` |
| `adult males from kenya` | `gender=male` + `age_group=adult` + `country_id=KE` |
| `male and female teenagers above 17` | `age_group=teenager` + `min_age=17` |

**Example:**
```
GET /api/profiles/search?q=young males from nigeria&page=1&limit=10
```

> Queries that cannot be interpreted return `{ "status": "error", "message": "Unable to interpret query" }`

---

#### `GET /api/profiles/:id`
Fetch a single profile by UUID v7.

**Example:**
```
GET /api/profiles/019db9df-6677-7edb-882a-8832b9270cb0
```

---

#### `POST /api/profiles`
Create a new profile by name. Gender, age, and nationality are fetched automatically from external APIs (Genderize, Agify, Nationalize).

**Request Body:**
```json
{
  "name": "John Doe"
}
```

**Response:**
```json
{
  "status": "success",
  "data": { ... }
}
```

---

## ERROR RESPONSES

All errors follow this structure:

```json
{ "status": "error", "message": "<error message>" }
```

| Code | Meaning |
|---|---|
| `400` | Missing or empty parameter |
| `422` | Invalid parameter type or value |
| `404` | Profile not found |
| `500` | Internal server error |
| `502` | Upstream API failure |
