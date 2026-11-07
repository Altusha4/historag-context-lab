"""Render entry point. AI-assisted deployment setup, OpenAI Codex, 2026-11-07."""
import logging
import os
from app import create_app
from core import collect

application = create_app()
try:
    collect(os.environ.get('HISTORAG_DB', 'data/weather.sqlite'))
except Exception:
    logging.exception('Forecast refresh failed; app remains available with existing data')
