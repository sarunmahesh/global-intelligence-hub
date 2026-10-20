#!/usr/bin/env python3
"""Publisher-aware recovery of public article metadata; no paywall bypass or full-text scraping."""
import argparse, datetime as dt, email.utils, hashlib, json, pathlib, re, urllib.parse
import requests, feedparser
from bs4 import BeautifulSoup
ROOT=pathlib.Path(__file__).resolve().parent
DATA=ROOT/'data/articles.json'
UA='GlobalIntelligenceHub/2.0 (public metadata index; respects publisher access)'
# Official publication homepages; use for source discovery and human fallback.
HOMES={
 'Nature':'https://www.nature.com/','Brookings':'https://www.brookings.edu/','CFR':'https://www.cfr.org/latest',
 'ORF':'https://www.orfonline.org/','PIB India':'https://pib.gov.in/','PRS India':'https://prsindia.org/',
 'EconTalk':'https://www.econtalk.org/','Macro Musings':'https://www.mercatus.org/macro-musings',
 'Odd Lots':'https://www.bloomberg.com/oddlots','The Ezra Klein Show':'https://www.nytimes.com/column/ezra-klein-podcast',
 'Dwarkesh Podcast':'https://www.dwarkesh.com/','IMF News':'https://www.imf.org/en/News',
 'World Bank Blogs':'https://blogs.worldbank.org/','OECD':'https://www.oecd.org/','BIS':'https://www.bis.org/',
 'Chatham House':'https://www.chathamhouse.org/','Carnegie Endowment':'https://carnegieendowment.org/',
 'Harvard Business Review':'https://hbr.org/','VoxEU':'https://cepr.org/voxeu',
}
# Candidate URLs are attempted, not represented as verified functioning feeds.
CANDIDATES={
 'CFR':['https://www.cfr.org/rss.xml','https://www.cfr.org/feed'],
 'PIB India':['https://pib.gov.in/RssMain.aspx','https://pib.gov.in/rss.aspx'],
 'BIS':['https://www.bis.org/doclist/all_pressrels.rss','https://www.bis.org/doclist/all_speeches.rss'],
 'World Bank Blogs':['https://blogs.worldbank.org/en/rss.xml'],
 'Brookings':['https://www.brookings.edu/feed/'],
 'Nature':['https://www.nature.com/nature.rss'],
}
TIMEOUT=12
session=requests.Session();session.headers.update({'User-Agent':UA,'Accept':'application/rss+xml, application/atom+xml, text/xml, text/html;q=0.8'})
def https(u):
 try:
  p=urllib.parse.urlsplit(u);return p.scheme=='https' and bool(p.hostname) and not p.username and not p.password
 except Exception:return False
def publisher_host(url):return (urllib.parse.urlsplit(url).hostname or '').lower().removeprefix('www.')
def same_publisher(url,home):
 a=publisher_host(url);b=publisher_host(home)
 return bool(a and b and (a==b or a.endswith('.'+b) or b.endswith('.'+a)))
def fetch(url):
 if not https(url):raise ValueError('Non-HTTPS URL')
 r=session.get(url,timeout=TIMEOUT,allow_redirects=True);r.raise_for_status()
 if not https(r.url):raise ValueError('Redirected outside HTTPS')
 return r

def date(raw):
 if not raw:return None
 try:
  d=email.utils.parsedate_to_datetime(raw)
 except Exception:
  try:d=dt.datetime.fromisoformat(str(raw).replace('Z','+00:00'))
  except Exception:return None
 if d.tzinfo is None:d=d.replace(tzinfo=dt.timezone.utc)
 return d.astimezone(dt.timezone.utc).isoformat()
def clean(s):return re.sub(r'\s+',' ',BeautifulSoup(str(s or ''),'html.parser').get_text(' ',strip=True)).strip()[:350]
def parse_feed(content,source,home):
 feed=feedparser.parse(content)
 if not feed.entries:return []
 out=[]
 for e in feed.entries[:100]:
  url=e.get('link','');title=clean(e.get('title',''))
  if not https(url) or not title:continue
  if not same_publisher(url,home):continue
  authors=clean(e.get('author','')) or None
  pub=date(e.get('published') or e.get('updated'))
  thumbnail=None
  for m in (e.get('media_thumbnail') or [])+(e.get('media_content') or []):
   candidate=m.get('url','')
   if https(candidate):thumbnail=candidate;break
  if not thumbnail:
   for link in e.get('links',[]):
    if str(link.get('type','')).startswith('image/') and https(link.get('href','')):thumbnail=link['href'];break
  out.append(make(url,title,source,pub,authors,thumbnail,clean(e.get('summary',''))[:300]))
 return out

def make(url,title,source,published=None,author=None,thumbnail=None,summary=None):
 ident=hashlib.sha256(url.encode()).hexdigest()[:16]
 return {'id':ident,'title':title,'url':url,'source':source['name'],'category':source.get('category','Research'),
  'published_at':published,'discovered_at':dt.datetime.now(dt.timezone.utc).isoformat(),
  'author':author,'thumbnail':thumbnail,'summary':summary,'access':'Unknown','tags':[],
  'verification':'Publisher metadata; content not independently verified','item_type':'Publisher item'}

def discover_feeds(page,home):
 soup=BeautifulSoup(page,'html.parser');found=[]
 for el in soup.find_all('link',href=True):
  if el.get('rel') and 'alternate' in el.get('rel',[]) and any(x in str(el.get('type','')).lower() for x in ('rss','atom','xml')):
   url=urllib.parse.urljoin(home,el['href'])
   if https(url) and same_publisher(url,home):found.append(url)
 return list(dict.fromkeys(found))[:6]

def jsonld_articles(page,source,home):
 soup=BeautifulSoup(page,'html.parser');out=[]
 def walk(node):
  if isinstance(node,list):
   for x in node:yield from walk(x)
  elif isinstance(node,dict):
   yield node
   for key in ('@graph','itemListElement','item','mainEntity'):
    if key in node:yield from walk(node[key])
 for script in soup.select('script[type="application/ld+json"]'):
  try:obj=json.loads(script.string or script.get_text())
  except Exception:continue
  for a in walk(obj):
   types=a.get('@type',[]);types=[types] if isinstance(types,str) else types
   if not any(t in ('NewsArticle','Article','BlogPosting','ScholarlyArticle','Report') for t in types):continue
   url=a.get('url') or a.get('mainEntityOfPage');url=url.get('@id') if isinstance(url,dict) else url
   url=urllib.parse.urljoin(home,url) if isinstance(url,str) else ''
   title=clean(a.get('headline') or a.get('name'))
   if not https(url) or not same_publisher(url,home) or not title:continue
   author=a.get('author');author=', '.join(x.get('name','') for x in author if isinstance(x,dict)) if isinstance(author,list) else (author.get('name') if isinstance(author,dict) else author)
   image=a.get('image');image=image[0] if isinstance(image,list) and image else image
   image=image.get('url') if isinstance(image,dict) else image
   out.append(make(url,title,source,date(a.get('datePublished')),clean(author) or None,image if isinstance(image,str) and https(image) else None,clean(a.get('description'))[:300]))
 return out

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--edition',choices=['morning','evening','manual'],default='manual');args=ap.parse_args()
 sources=json.loads((ROOT/'sources.json').read_text());old=json.loads(DATA.read_text()) if DATA.exists() else {'articles':[]}
 indexed={a['id']:a for a in old.get('articles',[]) if a.get('id')};status=[];added=0
 now=dt.datetime.now(dt.timezone.utc);ist=now.astimezone(dt.timezone(dt.timedelta(hours=5,minutes=30)))
 for src in sources:
  name=src['name'];home=HOMES.get(name)
  if not home:
   p=urllib.parse.urlsplit(src['url']);home=f'{p.scheme}://{p.netloc}/'
  found=[];attempts=[];urls=list(dict.fromkeys([src['url']]+CANDIDATES.get(name,[])))
  try:
   landing=fetch(home)
   if 'html' in landing.headers.get('Content-Type','').lower():
    urls+=discover_feeds(landing.text,landing.url)
    found+=jsonld_articles(landing.text,src,home)
  except Exception as e:attempts.append('homepage: '+str(e)[:90])
  for url in list(dict.fromkeys(urls))[:9]:
   try:
    response=fetch(url)
    records=parse_feed(response.content,src,home)
    if records:found.extend(records);break
    attempts.append('empty or unsupported feed: '+url[:80])
   except Exception as e:attempts.append(str(e)[:100])
  unique={a['id']:a for a in found}
  for ident,a in unique.items():
   if ident not in indexed:
    a['edition']=args.edition;a['edition_date']=ist.date().isoformat();indexed[ident]=a;added+=1
   else:
    for key in ('author','thumbnail','summary','published_at'):
     if not indexed[ident].get(key) and a.get(key):indexed[ident][key]=a[key]
  status.append({'source':name,'ok':bool(unique),'items':len(unique),'homepage':home,'error':'; '.join(attempts[-2:])[:240] if not unique else None})
  print(f'{name}: {len(unique)} records',flush=True)
 old['articles']=sorted(indexed.values(),key=lambda x:x.get('published_at') or x.get('discovered_at') or '',reverse=True)[:12000]
 old['updated_at']=now.isoformat();old['feed_status']=status
 if args.edition!='manual':
  old.setdefault('edition_dates',[]).append({'date':ist.date().isoformat(),'edition':args.edition,'collected_at':now.isoformat(),'new_articles':added})
  old['edition_dates']=old['edition_dates'][-800:]
 DATA.parent.mkdir(parents=True,exist_ok=True);DATA.write_text(json.dumps(old,ensure_ascii=False,separators=(',',':'))+'\n')
 print(f'New: {added}; total: {len(old["articles"])}; responding: {sum(x["ok"] for x in status)}/{len(status)}')
if __name__=='__main__':main()
