#!/usr/bin/env python3
"""Best-effort, publisher-permitted RSS/Atom metadata collection; preserves archive."""
import argparse,datetime as dt,email.utils,hashlib,json,pathlib,re,time,urllib.parse,urllib.request,urllib.error
import feedparser
ROOT=pathlib.Path(__file__).resolve().parent
DATA=ROOT/'data/articles.json'
IST=dt.timezone(dt.timedelta(hours=5,minutes=30))
UA='GlobalIntelligenceHub/2.0 (personal public-feed metadata aggregator)'
# Alternatives are publisher-owned feeds only. Unverified URLs are not silently treated as working.
ALTERNATES={
 'PIB India':['https://pib.gov.in/RssMain.aspx?ModId=6&Lang=1&Regid=1','https://www.pib.gov.in/RssMain.aspx?ModId=6&Lang=1&Regid=1'],
 'BIS':['https://data.bis.org/feed.xml'],
 'CFR':['https://www.cfr.org/rss','https://www.cfr.org/feed'],
 'ORF':['https://www.orfonline.org/rss.xml'],
 'PRS India':['https://prsindia.org/feed'],
 'World Bank Blogs':['https://blogs.worldbank.org/rss.xml'],
 'EconTalk':['https://www.econtalk.org/feed/'],
 'Carnegie Endowment':['https://carnegieendowment.org/rss'],
 'Harvard Business Review':['https://hbr.org/rss'],
}
SUBJECT={'News':'Geopolitics & World','Markets':'Finance & Capital Markets','Science & Technology':'Science & Technology','Research':'Research & Ideas','Geopolitics':'Geopolitics & World','India & Policy':'Indian Policy & Governance','Podcasts':'Podcasts & Forums','Economy & Policy':'Economics & Development','Defence & Security':'Defence & Security','Global intellectual forums':'Podcasts & Forums','Business & Strategy':'Business & Management','Technology & Products':'Technology & AI'}
def stamp(raw):
 if not raw:return None
 try:
  v=email.utils.parsedate_to_datetime(raw)
  return v.replace(tzinfo=v.tzinfo or dt.timezone.utc).astimezone(dt.timezone.utc).isoformat()
 except Exception:pass
 try:return dt.datetime.fromisoformat(raw.replace('Z','+00:00')).replace(tzinfo=dt.timezone.utc) .isoformat() if dt.datetime.fromisoformat(raw.replace('Z','+00:00')).tzinfo is None else dt.datetime.fromisoformat(raw.replace('Z','+00:00')).astimezone(dt.timezone.utc).isoformat()
 except Exception:return None
def url_ok(u):
 try:
  p=urllib.parse.urlsplit(u);return p.scheme=='https' and bool(p.netloc) and not p.username and not p.password
 except Exception:return False
def clean_url(u):
 p=urllib.parse.urlsplit(u);q=urllib.parse.parse_qsl(p.query,keep_blank_values=True)
 q=[(k,v) for k,v in q if not k.lower().startswith('utm_') and k.lower() not in ('fbclid','gclid')]
 return urllib.parse.urlunsplit((p.scheme,p.netloc.lower(),p.path.rstrip('/') or '/',urllib.parse.urlencode(q),''))
def getfeed(url):
 req=urllib.request.Request(url,headers={'User-Agent':UA,'Accept':'application/rss+xml,application/atom+xml,application/xml,text/xml;q=0.9,*/*;q=0.5'})
 with urllib.request.urlopen(req,timeout=12) as resp:
  final=resp.geturl();raw=resp.read(2_500_000);typ=resp.headers.get('Content-Type','')
 if not raw:raise ValueError('Empty response')
 parsed=feedparser.parse(raw)
 if not parsed.entries:
  raise ValueError('No usable RSS/Atom entries; '+('HTML page' if b'<html' in raw[:1000].lower() else str(getattr(parsed,'bozo_exception','unknown format'))[:110]))
 return parsed,final,typ
def parse_entries(parsed,src,now):
 out=[]
 for entry in parsed.entries[:90]:
  title=re.sub(r'\s+',' ',re.sub('<[^>]*>','',entry.get('title',''))).strip()
  link=entry.get('link','')
  if not title or not url_ok(link):continue
  link=clean_url(link)
  author=entry.get('author') or ', '.join(x.get('name','') for x in entry.get('authors',[]) if x.get('name')) or None
  author=re.sub(r'\s+',' ',re.sub('<[^>]*>','',author)).strip() if author else None
  thumb=None
  for media in entry.get('media_thumbnail',[])+entry.get('media_content',[]):
   candidate=media.get('url','')
   if url_ok(candidate) and (media.get('medium') in ('image',None) or media.get('type','').startswith('image/')):thumb=candidate;break
  if not thumb:
   for enclosure in entry.get('enclosures',[]):
    if enclosure.get('type','').startswith('image/') and url_ok(enclosure.get('href','')):thumb=enclosure['href'];break
  date=stamp(entry.get('published') or entry.get('updated') or entry.get('created'))
  id=hashlib.sha256(link.encode()).hexdigest()[:16]
  out.append({'id':id,'title':title,'url':link,'source':src['name'],'category':src.get('category','Other'),'subject':SUBJECT.get(src.get('category'),src.get('category','Other')),'published_at':date,'discovered_at':now,'author':author,'thumbnail':thumb,'access':'Unknown','tags':[],'verification':'Publisher feed metadata; article not independently fact-checked','item_type':'Feed item'})
 return out
def main():
 p=argparse.ArgumentParser();p.add_argument('--edition',choices=['morning','evening','manual'],default='manual');p.add_argument('--backfill-days',type=int,default=0);args=p.parse_args()
 now=dt.datetime.now(dt.timezone.utc);nowstr=now.isoformat();today=now.astimezone(IST).date().isoformat()
 sources=json.loads((ROOT/'sources.json').read_text(encoding='utf-8'))
 DATA.parent.mkdir(exist_ok=True)
 old=json.loads(DATA.read_text(encoding='utf-8')) if DATA.exists() else {'articles':[]}
 indexed={a['id']:a for a in old.get('articles',[]) if a.get('id')};statuses=[];added=[]
 for src in sources:
  candidates=list(dict.fromkeys([src['url']]+ALTERNATES.get(src['name'],[])))
  errors=[];records=None;chosen=None
  for candidate in candidates:
   try:
    parsed,chosen,_=getfeed(candidate);records=parse_entries(parsed,src,nowstr)
    if not records:raise ValueError('No entries with valid HTTPS links')
    break
   except Exception as e:errors.append(candidate+': '+str(e)[:110])
  if records is None:
   statuses.append({'source':src['name'],'ok':False,'items':0,'error':' | '.join(errors)[-600:]});continue
  for a in records:
   if args.backfill_days and a['published_at']:
    published=dt.datetime.fromisoformat(a['published_at'])
    if not(now-dt.timedelta(days=args.backfill_days)<=published<=now+dt.timedelta(hours=2)):continue
   if a['id'] not in indexed:
    a['edition_date']=today;a['edition']=args.edition;indexed[a['id']]=a;added.append(a['id'])
   else:
    existing=indexed[a['id']]
    for field in ('author','thumbnail','subject','published_at'):
     if not existing.get(field) and a.get(field):existing[field]=a[field]
  statuses.append({'source':src['name'],'ok':True,'items':len(records),'feed_url':chosen})
  time.sleep(.1)
 ordered=sorted(indexed.values(),key=lambda a:a.get('published_at') or a.get('discovered_at') or '',reverse=True)[:12000]
 editions=old.get('edition_dates',[])
 if args.edition!='manual':
  editions=[e for e in editions if (e.get('date'),e.get('edition'))!=(today,args.edition)]
  editions.append({'date':today,'edition':args.edition,'collected_at':nowstr,'new_articles':len(added)})
 snapshots=old.get('edition_snapshots',[])
 if args.edition!='manual':
  snapshots=[s for s in snapshots if (s.get('date'),s.get('edition'))!=(today,args.edition)]
  snapshots.append({'date':today,'edition':args.edition,'collected_at':nowstr,'article_ids':[a['id'] for a in ordered if a.get('edition_date')==today and a.get('edition')==args.edition][:500]})
 out={'updated_at':nowstr,'articles':ordered,'feed_status':statuses,'edition_dates':editions[-1000:],'edition_snapshots':snapshots[-1000:]}
 DATA.write_text(json.dumps(out,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
 ok=sum(s['ok'] for s in statuses);print(f'Added {len(added)}; total {len(ordered)}; feeds {ok}/{len(statuses)}')
 for s in statuses:
  if not s['ok']:print('WARN',s['source'],s['error'][:180])
 if ok==0:raise SystemExit('All feeds failed; existing archive preserved in data/articles.json')
if __name__=='__main__':main()
