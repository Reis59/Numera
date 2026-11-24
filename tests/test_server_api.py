import json, os, socket, subprocess, sys, tempfile, time, unittest, urllib.request, urllib.error
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class TestLocalAPI(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  sock=socket.socket(); sock.bind(('127.0.0.1',0)); cls.port=sock.getsockname()[1]; sock.close()
  fd,cls.db=tempfile.mkstemp(suffix='.db'); os.close(fd)
  env=os.environ.copy(); env['NUMERA_DB']=cls.db; env['NUMERA_PORT']=str(cls.port)
  cls.proc=subprocess.Popen([sys.executable,str(ROOT/'server.py')],cwd=ROOT,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
  cls.base=f'http://127.0.0.1:{cls.port}'
  for _ in range(40):
   try: urllib.request.urlopen(cls.base+'/api/state?user=tester',timeout=.2); break
   except Exception: time.sleep(.1)
  else: raise RuntimeError('NUMERA test server did not start')
 @classmethod
 def tearDownClass(cls):
  cls.proc.terminate(); cls.proc.wait(timeout=3)
  try: os.remove(cls.db)
  except OSError: pass
 def call(self,path,data=None):
  raw=None if data is None else json.dumps(data).encode()
  req=urllib.request.Request(self.base+path,data=raw,headers={'Content-Type':'application/json'} if raw else {})
  with urllib.request.urlopen(req,timeout=2) as r:return json.loads(r.read())
 def test_persistent_learning_rewards_and_review(self):
  r=self.call('/api/complete',{'user':'tester','level':'bilangan-1','score':100,'xp':20})
  self.assertEqual(r['xp_awarded'],20); self.assertTrue(r['passed'])
  r=self.call('/api/complete',{'user':'tester','level':'bilangan-1','score':100,'xp':20})
  self.assertEqual(r['xp_awarded'],0)
  threshold=self.call('/api/complete',{'user':'thresholdtester','level':'bilangan-1','score':67,'min_score':60,'xp':20})
  self.assertTrue(threshold['passed'])
  self.call('/api/answer',{'user':'tester','question':'q-test','correct':True})
  review=self.call('/api/review',{'user':'tester','card':'fc-test','quality':5})
  self.assertTrue(review['ok']); self.assertGreaterEqual(review['interval'],1)
  state=self.call('/api/state?user=tester')
  self.assertEqual(state['xp'],20); self.assertEqual(state['coins'],5)
  self.assertEqual(state['answered'],1); self.assertIn('bilangan-1',state['completed'])
 def test_xp_shop_purchase_and_equipping(self):
  self.call('/api/state?user=shoptester')
  reward=self.call('/api/complete',{'user':'shoptester','level':'shop-level','score':100,'xp':50})
  self.assertEqual(reward['xp_awarded'],50)
  bought=self.call('/api/shop/buy',{'user':'shoptester','accessory':'cap'})
  self.assertTrue(bought['ok']); self.assertEqual(bought['spent'],35)
  equipped=self.call('/api/shop/equip',{'user':'shoptester','accessory':'cap'})
  self.assertEqual(equipped['equipped'],'cap')
  state=self.call('/api/state?user=shoptester')
  self.assertEqual(state['xp'],15); self.assertIn('cap',state['owned']); self.assertEqual(state['equipped'],'cap')
  with self.assertRaises(urllib.error.HTTPError):
   self.call('/api/shop/buy',{'user':'shoptester','accessory':'cap'})
  with self.assertRaises(urllib.error.HTTPError):
   self.call('/api/shop/equip',{'user':'shoptester','accessory':'crown'})
 def test_daily_bonus_only_once(self):
  first=self.call('/api/daily-complete',{'user':'dailytester','score':100})
  second=self.call('/api/daily-complete',{'user':'dailytester','score':100})
  self.assertEqual(first['awarded'],15); self.assertEqual(second['awarded'],0)
  self.assertTrue(self.call('/api/state?user=dailytester')['daily_done'])

class TestLegacyMigration(unittest.TestCase):
 def test_build_01_database_migrates(self):
  fd,db=tempfile.mkstemp(suffix='.db'); os.close(fd)
  old=__import__('sqlite3').connect(db)
  old.execute('CREATE TABLE progress(user TEXT,level TEXT,score INTEGER,PRIMARY KEY(user,level))')
  old.execute('CREATE TABLE stats(user TEXT PRIMARY KEY,xp INTEGER DEFAULT 0,coins INTEGER DEFAULT 0,streak INTEGER DEFAULT 0)')
  old.execute("INSERT INTO stats(user,xp,coins,streak) VALUES('demo',12,4,2)"); old.commit(); old.close()
  sock=socket.socket();sock.bind(('127.0.0.1',0));port=sock.getsockname()[1];sock.close()
  env=os.environ.copy();env['NUMERA_DB']=db;env['NUMERA_PORT']=str(port)
  proc=subprocess.Popen([sys.executable,str(ROOT/'server.py')],cwd=ROOT,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
  try:
   base=f'http://127.0.0.1:{port}'; result=None
   for _ in range(40):
    try:
     with urllib.request.urlopen(base+'/api/state',timeout=.2) as r: result=json.loads(r.read())
     break
    except Exception: time.sleep(.1)
   self.assertIsNotNone(result); self.assertEqual(result['xp'],12)
   raw=json.dumps({'user':'demo','level':'bilangan-1','score':100,'xp':20}).encode()
   req=urllib.request.Request(base+'/api/complete',data=raw,headers={'Content-Type':'application/json'})
   with urllib.request.urlopen(req,timeout=2) as r: self.assertTrue(json.loads(r.read())['passed'])
  finally:
   proc.terminate();proc.wait(timeout=3); proc.stderr.close()
   try:os.remove(db)
   except OSError:pass

if __name__=='__main__': unittest.main()
