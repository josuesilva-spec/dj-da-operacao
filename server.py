import json, os, re, threading, time, urllib.parse, urllib.request
import qrcode.image.svg
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
ROOT=Path(__file__).parent
STATE={'queue':[],'current':None,'revision':0,'playing':False,'history':[]}
LOCK=threading.RLock()
ADMIN_PIN=os.environ.get('DJ_ADMIN_PIN','1234')
API_KEY=os.environ.get('YOUTUBE_API_KEY','')
PORT=int(os.environ.get('PORT','8765'))
VIDEO=re.compile(r'^[A-Za-z0-9_-]{11}$')
def video_id(value):
    value=value.strip()
    if VIDEO.fullmatch(value): return value
    try:
        u=urllib.parse.urlparse(value)
        if u.hostname in ('youtu.be','www.youtu.be'): candidate=u.path.strip('/').split('/')[0]
        elif u.hostname in ('youtube.com','www.youtube.com','m.youtube.com','music.youtube.com','www.youtube-nocookie.com'):
            candidate=urllib.parse.parse_qs(u.query).get('v',[''])[0] if u.path=='/watch' else (u.path.split('/')[2] if u.path.startswith(('/shorts/','/embed/','/live/')) and len(u.path.split('/'))>2 else '')
        else: return None
        return candidate if VIDEO.fullmatch(candidate) else None
    except Exception:return None
class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*a,**kw):super().__init__(*a,directory=str(ROOT/'static'),**kw)
    def reply(self,status,obj):
        data=json.dumps(obj,ensure_ascii=False).encode()
        self.send_response(status);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
    def body(self):
        try:return json.loads(self.rfile.read(min(int(self.headers.get('Content-Length','0')),10000)))
        except:return {}
    def admin(self,data):return str(data.get('pin',''))==ADMIN_PIN
    def do_GET(self):
        u=urllib.parse.urlparse(self.path)
        if u.path=='/qr.svg':
            target=urllib.parse.parse_qs(u.query).get('url',[''])[0]
            if not target.startswith(('http://','https://')) or len(target)>300:return self.reply(400,{'error':'URL inválida'})
            import qrcode
            img=qrcode.make(target,image_factory=qrcode.image.svg.SvgPathImage)
            import io
            b=io.BytesIO();img.save(b);data=b.getvalue()
            self.send_response(200);self.send_header('Content-Type','image/svg+xml');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
        elif u.path=='/api/state':
            with LOCK:self.reply(200,{**STATE,'search_enabled':bool(API_KEY)})
        elif u.path=='/api/search':
            if not API_KEY:return self.reply(400,{'error':'Pesquisa desativada. Configure YOUTUBE_API_KEY ou cole um link do YouTube.'})
            q=urllib.parse.parse_qs(u.query).get('q',[''])[0][:100]
            if not q:return self.reply(400,{'error':'Digite sua pesquisa.'})
            try:
                url='https://www.googleapis.com/youtube/v3/search?'+urllib.parse.urlencode({'part':'snippet','type':'video','videoEmbeddable':'true','maxResults':8,'q':q,'key':API_KEY})
                with urllib.request.urlopen(url,timeout=8) as r: obj=json.load(r)
                self.reply(200,{'results':[{'id':i['id']['videoId'],'title':i['snippet']['title'],'channel':i['snippet']['channelTitle']} for i in obj.get('items',[])]})
            except Exception as e:self.reply(502,{'error':'Falha na pesquisa do YouTube. Confira a chave e a cota da API.'})
        elif u.path=='/api/config':self.reply(200,{'search_enabled':bool(API_KEY)})
        else:super().do_GET()
    def do_POST(self):
        path=urllib.parse.urlparse(self.path).path; d=self.body()
        with LOCK:
            if path=='/api/add':
                name=str(d.get('name','')).strip()[:40];vid=video_id(str(d.get('video','')));title=str(d.get('title','')).strip()[:120]
                if not name or not vid:return self.reply(400,{'error':'Informe seu nome e um link válido do YouTube.'})
                if len(STATE['queue'])>=100:return self.reply(400,{'error':'Fila cheia.'})
                if vid in [x['id'] for x in STATE['queue']] or (STATE['current'] and STATE['current']['id']==vid):return self.reply(400,{'error':'Essa música já está na fila ou tocando.'})
                item={'id':vid,'title':title or 'Vídeo '+vid,'name':name,'added':int(time.time())}
                STATE['queue'].append(item);STATE['revision']+=1;return self.reply(200,{'ok':True})
            if path in ('/api/next','/api/remove','/api/clear','/api/stop','/api/play'):
                if not self.admin(d):return self.reply(403,{'error':'PIN de administrador incorreto.'})
                if path=='/api/next':
                    if STATE['current']:STATE['history'].insert(0,STATE['current']);STATE['history']=STATE['history'][:20]
                    STATE['current']=STATE['queue'].pop(0) if STATE['queue'] else None;STATE['playing']=bool(STATE['current'])
                elif path=='/api/remove':STATE['queue']=[x for x in STATE['queue'] if x['id']!=d.get('id')]
                elif path=='/api/clear':STATE['queue']=[]
                elif path=='/api/stop':STATE['playing']=False
                elif path=='/api/play':STATE['playing']=bool(STATE['current'])
                STATE['revision']+=1;return self.reply(200,{'ok':True})
        self.reply(404,{'error':'Não encontrado'})
if __name__=='__main__':
    print(f'DJ da Operação: http://localhost:{PORT}/admin.html | PIN inicial: {ADMIN_PIN}')
    print('Acesse pelo IP do computador na rede local para abrir nos celulares.')
    ThreadingHTTPServer(('0.0.0.0',PORT),Handler).serve_forever()
