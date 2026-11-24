from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
import sqlite3,json,urllib.parse,datetime,os
ROOT=Path(__file__).parent; DB=Path(os.environ.get('NUMERA_DB',ROOT/'data'/'numera.db'))
def conn():
 c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c
def init():
 DB.parent.mkdir(exist_ok=True)
 with conn() as c:
  c.execute('CREATE TABLE IF NOT EXISTS progress(user TEXT,level TEXT,score INTEGER,completed_at TEXT,PRIMARY KEY(user,level))')
  c.execute('CREATE TABLE IF NOT EXISTS stats(user TEXT PRIMARY KEY,xp INTEGER DEFAULT 0,coins INTEGER DEFAULT 0,streak INTEGER DEFAULT 0,last_active TEXT)')
  c.execute('CREATE TABLE IF NOT EXISTS answers(id INTEGER PRIMARY KEY AUTOINCREMENT,user TEXT,question TEXT,correct INTEGER,created_at TEXT DEFAULT CURRENT_TIMESTAMP)')
  c.execute('CREATE TABLE IF NOT EXISTS reviews(user TEXT,card TEXT,ease REAL DEFAULT 2.5,interval INTEGER DEFAULT 0,due TEXT,seen INTEGER DEFAULT 0,PRIMARY KEY(user,card))')
  c.execute('CREATE TABLE IF NOT EXISTS daily(user TEXT,day TEXT,score INTEGER,PRIMARY KEY(user,day))')
  c.execute('CREATE TABLE IF NOT EXISTS settings(user TEXT PRIMARY KEY,sound INTEGER DEFAULT 1,public_rank INTEGER DEFAULT 0)')
  c.execute('CREATE TABLE IF NOT EXISTS wardrobe(user TEXT,accessory TEXT,purchased_at TEXT,PRIMARY KEY(user,accessory))')
  c.execute("CREATE TABLE IF NOT EXISTS equipped(user TEXT PRIMARY KEY,accessory TEXT DEFAULT 'none')")
  # Forward-compatible migration from Build 0.1 databases.
  progress_cols={r[1] for r in c.execute('PRAGMA table_info(progress)').fetchall()}
  if 'completed_at' not in progress_cols: c.execute('ALTER TABLE progress ADD COLUMN completed_at TEXT')
  stats_cols={r[1] for r in c.execute('PRAGMA table_info(stats)').fetchall()}
  if 'last_active' not in stats_cols: c.execute('ALTER TABLE stats ADD COLUMN last_active TEXT')
  c.execute("INSERT OR IGNORE INTO stats(user) VALUES('demo')")
  c.execute("INSERT OR IGNORE INTO settings(user) VALUES('demo')")
  c.execute("INSERT OR IGNORE INTO equipped(user,accessory) VALUES('demo','none')")
def activity(c,u):
 today=datetime.date.today(); row=c.execute('SELECT streak,last_active FROM stats WHERE user=?',(u,)).fetchone()
 if not row: c.execute('INSERT OR IGNORE INTO stats(user) VALUES(?)',(u,)); row={'streak':0,'last_active':None}
 last=row['last_active']; streak=row['streak'] or 0
 if last==today.isoformat(): return
 if last==(today-datetime.timedelta(days=1)).isoformat(): streak+=1
 else: streak=1
 c.execute('UPDATE stats SET streak=?,last_active=? WHERE user=?',(streak,today.isoformat(),u))
class H(SimpleHTTPRequestHandler):
 def __init__(self,*a,**k): super().__init__(*a,directory=str(ROOT/'static'),**k)
 def sendjson(self,obj,status=200):
  b=json.dumps(obj,ensure_ascii=False).encode(); self.send_response(status); self.send_header('Content-Type','application/json; charset=utf-8'); self.send_header('Content-Length',str(len(b))); self.end_headers(); self.wfile.write(b)
 def do_GET(self):
  p=urllib.parse.urlparse(self.path); q=urllib.parse.parse_qs(p.query); u=q.get('user',['demo'])[0]
  if p.path=='/api/state':
   with conn() as c:
    c.execute('INSERT OR IGNORE INTO stats(user) VALUES(?)',(u,)); c.execute('INSERT OR IGNORE INTO settings(user) VALUES(?)',(u,)); c.execute("INSERT OR IGNORE INTO equipped(user,accessory) VALUES(?,'none')",(u,))
    s=c.execute('SELECT * FROM stats WHERE user=?',(u,)).fetchone(); rows=c.execute('SELECT level,score FROM progress WHERE user=?',(u,)).fetchall(); n=c.execute('SELECT COUNT(*),COALESCE(SUM(correct),0) FROM answers WHERE user=?',(u,)).fetchone(); setting=c.execute('SELECT sound,public_rank FROM settings WHERE user=?',(u,)).fetchone(); worn=c.execute('SELECT accessory FROM equipped WHERE user=?',(u,)).fetchone(); owned=[r['accessory'] for r in c.execute('SELECT accessory FROM wardrobe WHERE user=?',(u,)).fetchall()]; due=c.execute('SELECT COUNT(*) FROM reviews WHERE user=? AND due<=?',(u,datetime.date.today().isoformat())).fetchone()[0]; daily_done=bool(c.execute('SELECT 1 FROM daily WHERE user=? AND day=?',(u,datetime.date.today().isoformat())).fetchone()); qstats=c.execute('SELECT question,COUNT(*) AS total,COALESCE(SUM(correct),0) AS correct FROM answers WHERE user=? GROUP BY question',(u,)).fetchall()
   return self.sendjson({'xp':s['xp'],'coins':s['coins'],'streak':s['streak'],'last_active':s['last_active'],'completed':{r['level']:r['score'] for r in rows},'answered':n[0],'correct':n[1],'sound':bool(setting['sound']),'public_rank':bool(setting['public_rank']),'reviews_due':due,'daily_done':daily_done,'question_stats':{r['question']:{'total':r['total'],'correct':r['correct']} for r in qstats},'equipped':worn['accessory'] if worn else 'none','owned':owned})
  if p.path=='/api/reviews':
   with conn() as c: rows=c.execute('SELECT card,ease,interval,due,seen FROM reviews WHERE user=? AND due<=? ORDER BY due LIMIT 30',(u,datetime.date.today().isoformat())).fetchall()
   return self.sendjson([dict(x) for x in rows])
  return super().do_GET()
 def do_POST(self):
  p=urllib.parse.urlparse(self.path); d=json.loads(self.rfile.read(int(self.headers.get('Content-Length',0)) or 0) or b'{}'); u=d.get('user','demo')
  with conn() as c:
   c.execute('INSERT OR IGNORE INTO stats(user) VALUES(?)',(u,))
   c.execute("INSERT OR IGNORE INTO equipped(user,accessory) VALUES(?,'none')",(u,))
   if p.path=='/api/complete':
    level=d['level']; score=max(0,min(100,int(d['score']))); minimum=max(0,min(100,int(d.get('min_score',70)))); xp=int(d.get('xp',20)) if score>=minimum else 0; old=c.execute('SELECT 1 FROM progress WHERE user=? AND level=?',(u,level)).fetchone(); awarded=0
    if score>=minimum:
     c.execute('INSERT OR REPLACE INTO progress(user,level,score,completed_at) VALUES(?,?,?,?)',(u,level,score,datetime.datetime.now().isoformat(timespec='seconds')))
     if not old and xp: c.execute('UPDATE stats SET xp=xp+?,coins=coins+5 WHERE user=?',(xp,u)); awarded=xp
     activity(c,u)
    return self.sendjson({'ok':True,'xp_awarded':awarded,'passed':score>=minimum})
   if p.path=='/api/answer':
    c.execute('INSERT INTO answers(user,question,correct) VALUES(?,?,?)',(u,d['question'],int(bool(d['correct'])))); activity(c,u); return self.sendjson({'ok':True})
   if p.path=='/api/review':
    card=d['card']; quality=max(0,min(5,int(d.get('quality',3)))); old=c.execute('SELECT ease,interval,seen FROM reviews WHERE user=? AND card=?',(u,card)).fetchone(); ease=old['ease'] if old else 2.5; interval=old['interval'] if old else 0; seen=old['seen'] if old else 0
    if quality<3: interval=1
    else: interval=1 if interval==0 else 6 if interval==1 else round(interval*ease)
    ease=max(1.3,ease+0.1-(5-quality)*(0.08+(5-quality)*0.02)); due=(datetime.date.today()+datetime.timedelta(days=interval)).isoformat()
    c.execute('INSERT OR REPLACE INTO reviews(user,card,ease,interval,due,seen) VALUES(?,?,?,?,?,?)',(u,card,ease,interval,due,seen+1)); activity(c,u); return self.sendjson({'ok':True,'due':due,'interval':interval})
   if p.path=='/api/daily-complete':
    day=datetime.date.today().isoformat(); old=c.execute('SELECT 1 FROM daily WHERE user=? AND day=?',(u,day)).fetchone()
    if old: return self.sendjson({'ok':True,'awarded':0,'already_done':True})
    score=max(0,min(100,int(d.get('score',0)))); c.execute('INSERT INTO daily(user,day,score) VALUES(?,?,?)',(u,day,score)); award=15 if score>=0 else 0; c.execute('UPDATE stats SET xp=xp+?,coins=coins+3 WHERE user=?',(award,u)); activity(c,u); return self.sendjson({'ok':True,'awarded':award,'already_done':False})
   if p.path=='/api/shop/buy':
    catalog={'cap':('Topi Petualang',35),'crown':('Mahkota Juara',90),'glasses':('Kacamata Pintar',45),'halo':('Halo Bintang',120),'bow':('Pita Ceria',30),'scarf':('Syal Hangat',55),'antenna':('Antena Alien',70),'flower':('Bunga Keberuntungan',65)}
    item=d.get('accessory');
    if item not in catalog: return self.sendjson({'ok':False,'error':'Aksesori tidak dikenal'},400)
    if c.execute('SELECT 1 FROM wardrobe WHERE user=? AND accessory=?',(u,item)).fetchone(): return self.sendjson({'ok':False,'error':'Aksesori sudah dimiliki'},409)
    cost=catalog[item][1]; row=c.execute('SELECT xp FROM stats WHERE user=?',(u,)).fetchone()
    if not row or row['xp']<cost: return self.sendjson({'ok':False,'error':'XP belum cukup','cost':cost},400)
    c.execute('UPDATE stats SET xp=xp-? WHERE user=?',(cost,u)); c.execute('INSERT INTO wardrobe(user,accessory,purchased_at) VALUES(?,?,?)',(u,item,datetime.datetime.now().isoformat(timespec='seconds')))
    return self.sendjson({'ok':True,'spent':cost,'accessory':item})
   if p.path=='/api/shop/equip':
    item=d.get('accessory','none')
    if item!='none' and not c.execute('SELECT 1 FROM wardrobe WHERE user=? AND accessory=?',(u,item)).fetchone(): return self.sendjson({'ok':False,'error':'Aksesori belum dimiliki'},403)
    c.execute('INSERT OR REPLACE INTO equipped(user,accessory) VALUES(?,?)',(u,item)); return self.sendjson({'ok':True,'equipped':item})
   if p.path=='/api/settings':
    c.execute('INSERT OR IGNORE INTO settings(user) VALUES(?)',(u,)); c.execute('UPDATE settings SET sound=?,public_rank=? WHERE user=?',(int(bool(d.get('sound',True))),int(bool(d.get('public_rank',False))),u)); return self.sendjson({'ok':True})
  self.sendjson({'error':'not found'},404)
init(); PORT=int(os.environ.get('NUMERA_PORT','8000')); print(f'NUMERA: http://127.0.0.1:{PORT}',flush=True); ThreadingHTTPServer(('127.0.0.1',PORT),H).serve_forever()
