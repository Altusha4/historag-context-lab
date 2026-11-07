# AI-assisted tests: OpenAI Codex, 2026-11-07, entire file.
import unittest,tempfile,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from core import migrate,collect,report,connect
from app import create_app
class PipelineTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.db=str(Path(self.tmp.name)/'test.sqlite');migrate(self.db)
  self.payload={'hourly':{'time':['2026-11-07T00:00','2026-11-07T01:00'],'temperature_2m':[10,20],'relative_humidity_2m':[40,60]}}
 def tearDown(self):self.tmp.cleanup()
 def test_collection_idempotence_and_analysis(self):
  self.assertEqual(collect(self.db,lambda:self.payload)['inserted'],2)
  self.assertEqual(collect(self.db,lambda:self.payload)['inserted'],0)
  self.assertEqual(report(self.db)['statistics']['mean_temperature'],15)
 def test_invalid_payload_atomic(self):
  self.payload['hourly']['relative_humidity_2m'][1]=None
  with self.assertRaises(ValueError):collect(self.db,lambda:self.payload)
  self.assertEqual(report(self.db)['statistics']['rows'],0)
 def test_upstream_failure(self):
  def failing():raise TimeoutError('upstream unavailable')
  with self.assertRaises(TimeoutError):collect(self.db,failing)
  self.assertEqual(report(self.db)['statistics']['rows'],0)
 def test_migration_repeatable(self):
  collect(self.db,lambda:self.payload);migrate(self.db)
  self.assertEqual(report(self.db)['statistics']['rows'],2)
 def test_http_integration(self):
  collect(self.db,lambda:self.payload);client=create_app(self.db).test_client()
  self.assertEqual(client.get('/').status_code,200)
  self.assertEqual(client.get('/api/report').json['statistics']['rows'],2)
  self.assertEqual(client.get('/health').json['status'],'ok')
  metrics=client.get('/metrics')
  self.assertEqual(metrics.status_code,200)
  self.assertEqual(metrics.json['weather_records'],2)
  self.assertGreater(metrics.json['requests_per_second'],0)
  self.assertEqual(client.post('/api/echo',json={'question':'test'}).json['question'],'test')
  self.assertEqual(client.post('/api/echo',json={'question':''}).status_code,400)
  self.assertEqual(client.post('/api/echo',json=[]).status_code,400)
if __name__=='__main__':unittest.main(verbosity=2)
