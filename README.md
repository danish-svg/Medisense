# MediSense AI – Intelligent Medical Inventory Management

## Run
1. Start PostgreSQL: `docker compose up -d` (or use your own server and set `DATABASE_URL` in `backend/.env`)
2. `cd backend && pip install -r requirements.txt`
3. `uvicorn app.main:app --reload`
4. Open http://localhost:8000  (API docs at /docs). Tables and sample data are created on first start.

## Sales
Stock goes down when a sale is recorded (Inventory > Record sale, the Sell button on a row, or Import sales CSV with lines like `Paracetamol 500mg,10`).
Each sale also adds to today's sales total, and the forecast uses the last 28 days, so reorder points and alerts update on their own.
If you upgrade from the earlier version, reset the database once: `docker compose down -v` then `docker compose up -d`.

## Structure
- `frontend/` index.html, `css/styles.css`, `js/` (utils, api, charts, app router) and one file per screen in `js/views/`
- `backend/app/models.py` tables · `schemas.py` request bodies · `seed.py` sample data
- `backend/app/routers/` HTTP endpoints (inventory, insights, planner)
- `backend/app/services/` one file per technique:

| Feature | File | Technique |
|---|---|---|
| Reorder planner | `planner.py` | Constraint satisfaction (backtracking, budget, shelf space, supplier minimums) |
| Shortage and waste risk | `bayes.py` | Bayesian network, exact inference |
| Regular vs sporadic demand | `patterns.py` | Fuzzy memberships and rules |
| Expiry action planner | `expiry.py` | AO* search on an AND/OR graph |
| Substitutes | `substitutes.py` | Semantic network (category links) |
| "Why?" explanations | `alerts.py` | Rule-based expert system |
| Criticality classes | `analytics.py` | Rules (service level and minimum cover per class) |
| Conflicting evidence | `evidence.py` | Dempster-Shafer theory |
