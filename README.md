# Smart Marketplace Search and Real-Time Analytics System

A beginner-friendly local prototype for the 26CS5206E Algorithm Engineering for Data Systems project. It provides a Streamlit dashboard, SQLite persistence, product search, inventory/version history, duplicate candidates, event-window analytics, and algorithm experiments.

## Features
- Dashboard KPIs and charts for a seeded 1,000-product catalogue and anonymous demo events.
- Product search with price, category-root, and stock filters.
- Keyword search, deterministic feature-hash vector similarity, hybrid ranking, and a simple reranking boost.
- Catalogue manager: add products and update stock.
- Version history: previous inventory state is stored before an update.
- Near-duplicate candidate review using token-set Jaccard similarity and exact verification.
- Windowed event analytics, exact and approximate visitor counts, and event charts.
- Algorithm lab: linear scan timing, p50/p95 calculations, and local shard/replica simulation.
- SQLite database; no paid APIs, payment processing, real customer data, or production deployment.

## Requirements
- Python 3.10 or newer
- Internet connection only for installing Python packages

## Run on Windows PowerShell
```powershell
cd smart_marketplace_analytics
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app.py
```
Open the local URL printed by Streamlit (usually http://localhost:8501).

## Run on macOS/Linux
```bash
cd smart_marketplace_analytics
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

The SQLite database `marketplace.db` and seeded demo data are created automatically on first launch. To reset all demo data, stop the app and delete `marketplace.db`; it will be recreated on the next launch.

## Tests
```bash
python -m unittest discover -s tests -v
```

## GitHub upload
Create an empty repository on GitHub, then run these commands from this folder:
```bash
git init
git add .
git commit -m "Initial smart marketplace analytics project"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
git push -u origin main
```
Replace the remote URL with your own repository URL. Do not commit `marketplace.db`, `.venv`, credentials, or private data.

## Project structure
```text
smart_marketplace_analytics/
├── app.py
├── algorithms.py
├── database.py
├── seed_data.py
├── requirements.txt
├── README.md
├── .gitignore
└── tests/
    └── test_algorithms.py
```

## Architecture
Streamlit provides the local user interface and invokes Python application logic. `algorithms.py` contains search, similarity, approximate counting, percentile, scan, and shard simulation methods. `database.py` provides SQLite persistence. `seed_data.py` inserts reproducible sample products and anonymous events.

## Algorithm notes and limitations
- The vector representation is a deterministic feature-hashing baseline, not a trained language model. It is included to demonstrate vector retrieval without external APIs.
- Hybrid ranking combines normalized keyword overlap and cosine similarity; it is a teaching prototype, not a production relevance model.
- Duplicate candidates use Jaccard similarity on token sets. Similarity is a review signal, not proof of duplication.
- Approximate unique counting is a compact HyperLogLog-style sketch; its estimate is less reliable for small cardinalities.
- Event windows are calculated from locally stored timestamped events. Seeded events are synthetic.
- The shard/replica page simulates partition assignment and local copies in one process; it is not a distributed deployment.
- Benchmark timings are local observations and vary by machine, Python version, and system load. Run repeated trials before making performance claims.

## Course evidence
The supplied project brief explicitly details Sessions 1–6. The project includes:
- L1: linear scan, correctness oracle, operation count and block-read discussion.
- L2: contiguous catalogue records and profiling discussion; memory-layout comparison is a documented extension.
- L3: dynamic event storage and amortized-analysis exercise (see `docs/ALGORITHM_TRACES.md`).
- L4: fingerprint collision and exact verification discussion (see `docs/ALGORITHM_TRACES.md`).
- L5: before/after profiling workflow and reproducibility notes.
- L6: scan benchmark and model-selection evidence.

The brief also states broader required capabilities and 36-session integration areas. Those are represented in the prototype where feasible. The uploaded material contained detailed session plans only for Sessions 1–6; consult the remaining course session plans for exact algorithm-by-algorithm coverage and CO/COI/BTL mapping.

## Screenshots
Run the app and capture the Dashboard, Smart Product Search, Catalogue Manager, Streaming Analytics, and Algorithm Lab pages for your report.
