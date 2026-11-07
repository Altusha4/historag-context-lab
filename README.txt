HistoRAG Context Lab - AI-assisted COURSE MVP / DRAFT

Purpose
A small web/data-pipeline prototype inspired by HistoRAG hydroponic research.
It collects outdoor forecast data as contextual information, NOT grow-box
telemetry, and does NOT generate LLM advice or control actuators.

Run (Python 3.10+)
 python3 -m venv .venv
 source .venv/bin/activate
 pip install -r requirements.txt
 python core.py --collect
 flask --app 'app:create_app()' run --host 127.0.0.1 --port 8767
 Open http://127.0.0.1:8767

Test
 python -m unittest discover -s tests -v

Database setup and migrations
core.py migrate() applies migrations/001_initial.sql on startup.
The schema is idempotent. (location,time) is the unique weather key.
Collection validates the complete response before an atomic transaction.
Repeated forecasts retain the first stored value for each timestamp; this
snapshot policy makes re-runs idempotent but does not track forecast revisions.
No database, credentials, real grow-box dataset or personal data is required.

Data Collection assignment
Run python core.py --collect. It fetches Open-Meteo's HTTPS forecast endpoint,
validates arrays, and writes hourly temperature/humidity to SQLite. It records
source, fetch time and run statistics. Offline tests use explicit fake responses;
the collector itself does not silently substitute fake data on network failure.
Evidence files document the actual run; see live-collection.json.
Data source: https://open-meteo.com/en/docs ; attribution Open-Meteo, CC BY 4.0.
Reference coordinates are a fixed city location, not the learner's location.

Web Application assignment
The form posts user input to /api/echo, and renders the returned text safely
with textContent. /api/report provides persisted data and aggregate statistics.
Localhost is NOT a public submission URL. Public deployment remains required.
For a Python host use a production WSGI server, a persistent disk, HISTORAG_DB,
and a scheduled collector. Never expose Flask debug mode. No hosting claimed.

Monitoring
/health checks the database and uses HTTP 503 on failure; /metrics exports
record count, uptime and an in-process request counter. Counters reset at
restart and are per-process, not distributed production monitoring.

Architectural boundaries
Collector is a separate CLI process from the Flask API. SQL aggregates act as
the implemented analyzer. Future private telemetry ingestion, historical-episode
retrieval, document retrieval, LLM response generation, event broker and actuator
integrations are NOT implemented and are shown as future scope in the diagram.
No scalability/load-test, cloud deployment, CI execution or CD is claimed.

AI usage: see AI_ACKNOWLEDGEMENT.txt. Review before submission.

RENDER DEPLOYMENT
Runtime: Python 3
Build command: pip install -r requirements.txt
Start command: gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 60 wsgi:application
Health check: /health
Use the Free instance type for this demonstration.
The free instance filesystem is ephemeral. SQLite is recreated and forecast data
is collected on process start. This is not durable production storage. The first
request after idle sleep can take longer. No personal telemetry or credentials
are included in the public code repository. /metrics returns JSON with an average
request rate since process start, backed by prometheus_client.Counter.
