"""Render startup. AI-assisted implementation, OpenAI Codex, 2026-11-07."""
import json, logging, os
from pathlib import Path
from app import create_app
from core import collect
application = create_app()
path = os.environ.get('HISTORAG_DB', 'data/weather.sqlite')
try:
    collect(path)
except Exception:
    logging.exception('Live refresh unavailable; loading an explicitly labeled saved API snapshot')
    snapshot = json.loads(Path(__file__).with_name('forecast_snapshot.json').read_text())
    collect(path, lambda: snapshot)
    application.config['DATA_NOTE'] = 'Live weather refresh unavailable. Showing a saved Open-Meteo API snapshot collected at ' + snapshot['snapshot_fetched_at'] + '. This is not a current forecast.'
