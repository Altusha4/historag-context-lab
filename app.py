# AI-assisted implementation: OpenAI Codex, 2026-11-07, entire file.
# See AI_ACKNOWLEDGEMENT.txt. No real user telemetry is included.
import os, time, sqlite3
from flask import Flask, request, jsonify, render_template
from core import migrate, connect, report
from prometheus_client import CollectorRegistry, Counter

def create_app(db=None):
    app=Flask(__name__)
    app.config['MAX_CONTENT_LENGTH']=8192
    path=db or os.environ.get('HISTORAG_DB','data/weather.sqlite')
    migrate(path)
    started=time.monotonic()
    registry=CollectorRegistry()
    request_counter=Counter('historag_requests','HTTP requests',registry=registry)
    @app.before_request
    def count(): request_counter.inc()
    @app.after_request
    def headers(response):
        response.headers['X-Content-Type-Options']='nosniff'
        response.headers['Content-Security-Policy']="default-src 'self'; script-src 'self'; style-src 'self'; frame-ancestors 'none'"
        return response
    @app.get('/')
    def index(): return render_template('index.html', data_note=app.config.get('DATA_NOTE', ''))
    @app.post('/api/echo')
    def echo():
        data=request.get_json(silent=True)
        if not isinstance(data,dict) or not isinstance(data.get('question'),str) or not 1<=len(data['question'].strip())<=500:
            return jsonify(error='Enter a question between 1 and 500 characters.'),400
        return jsonify(question=data['question'].strip(),message='Question received. This MVP echoes input; it does not generate agronomic advice.')
    @app.get('/api/report')
    def analysis(): return jsonify(report(path))
    @app.get('/health')
    def health():
        try:
            with connect(path) as con: con.execute('SELECT count(*) FROM weather').fetchone()
            return jsonify(status='ok',database='reachable')
        except sqlite3.Error:
            return jsonify(status='unavailable',database='unreachable'),503
    @app.get('/metrics')
    def metrics():
        with connect(path) as con: n=con.execute('SELECT count(*) FROM weather').fetchone()[0]
        total=next(sample.value for family in request_counter.collect() for sample in family.samples if sample.name=='historag_requests_total')
        elapsed=max(time.monotonic()-started,0.001)
        return jsonify(requests_total=total, requests_per_second=total/elapsed,
                       rate_window='since process start', uptime_seconds=elapsed,
                       weather_records=n)
    return app
