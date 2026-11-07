# AI-assisted implementation: OpenAI Codex, 2026-11-07, entire file.
# See AI_ACKNOWLEDGEMENT.txt for prompts, scope and verification.
import json, math, sqlite3
from contextlib import contextmanager
from pathlib import Path
from datetime import datetime, timezone
from urllib.request import urlopen
from urllib.parse import urlencode

SOURCE = 'https://api.open-meteo.com/v1/forecast'
LOCATION = 'Astana reference location (51.17, 71.43)'
PARAMS = {'latitude':51.17, 'longitude':71.43, 'hourly':'temperature_2m,relative_humidity_2m', 'forecast_days':2, 'timezone':'UTC'}

@contextmanager
def connect(path):
    con = sqlite3.connect(path, timeout=10)
    con.row_factory = sqlite3.Row
    try:
        with con:
            yield con
    finally:
        con.close()

def migrate(path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with connect(path) as con:
        for script in sorted((Path(__file__).parent/'migrations').glob('*.sql')):
            con.executescript(script.read_text())

def fetch():
    with urlopen(SOURCE+'?'+urlencode(PARAMS), timeout=20) as response:
        return json.load(response)

def validate(payload):
    hourly = payload['hourly']
    times, temps, humidities = [hourly[k] for k in ('time','temperature_2m','relative_humidity_2m')]
    if not times or len(times)!=len(temps) or len(times)!=len(humidities):
        raise ValueError('Missing or misaligned hourly arrays')
    rows=[]
    for timestamp,temp,humidity in zip(times,temps,humidities):
        datetime.fromisoformat(timestamp)
        if any(isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) for v in (temp,humidity)):
            raise ValueError('Non-finite or missing measurement')
        if not -100<=temp<=70 or not 0<=humidity<=100:
            raise ValueError('Measurement outside validation bounds')
        rows.append((timestamp,float(temp),float(humidity)))
    return rows

def collect(path, fetcher=fetch):
    # Validate entire response before beginning an atomic insert transaction.
    rows=validate(fetcher())
    now=datetime.now(timezone.utc).isoformat()
    with connect(path) as con:
        before=con.total_changes
        con.executemany('INSERT OR IGNORE INTO weather VALUES (?,?,?,?,?,?)',
          [(LOCATION,t,temp,rh,now,SOURCE) for t,temp,rh in rows])
        inserted=con.total_changes-before
        con.execute('INSERT INTO collection_runs(fetched_at,received,inserted,source) VALUES (?,?,?,?)',
                    (now,len(rows),inserted,SOURCE))
    return {'received':len(rows),'inserted':inserted,'fetched_at':now,'source':SOURCE}

def report(path):
    with connect(path) as con:
        stats=dict(con.execute('SELECT count(*) AS rows, min(temperature) AS min_temperature, max(temperature) AS max_temperature, avg(temperature) AS mean_temperature, avg(humidity) AS mean_humidity FROM weather').fetchone())
        recent=[dict(r) for r in con.execute('SELECT time,temperature,humidity FROM weather ORDER BY time DESC LIMIT 48')]
    return {'location':LOCATION,'data_type':'outdoor model forecast; NOT grow-box sensor telemetry', 'units':{'temperature':'C','humidity':'%'}, 'statistics':stats,'records':recent}

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(); parser.add_argument('--db',default='data/weather.sqlite'); parser.add_argument('--collect',action='store_true'); args=parser.parse_args()
    migrate(args.db)
    if args.collect: print(json.dumps(collect(args.db),indent=2))
    print(json.dumps(report(args.db)['statistics'],indent=2))
