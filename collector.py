#!/usr/bin/env python3
"""Permitted public RSS/Atom metadata ingestion. No full-text scraping."""
import argparse, datetime as dt, email.utils, hashlib, json, pathlib, re, time, urllib.parse, urllib.request, xml.etree.ElementTree as ET
ROOT=pathlib.Path(__file__).parent
DATA=ROOT/'data/articles.json'
USER_AGENT='GlobalIntelligenceHub/1.0 (+personal metadata reader; respects publisher feeds)'
MAX_RECORDS=12000

def text(el, path):
    n=el.find(path)
    return ''.join(n.itertext()).strip() if n is not None else ''

def date_iso(raw):
    if not raw:return None
    try:
        v=email.utils.parsedate_to_datetime(raw)
        return v.astimezone(dt.timezone.utc).isoformat() if v.tzinfo else v.replace(tzinfo=dt.timezone.utc).isoformat()
    except Exception:pass
    try:return dt.datetime.fromisoformat(raw.replace('Z','+00:00')).astimezone(dt.timezone.utc).isoformat()
    except Exception:return None

def valid_url(url):
    p=urllib.parse.urlparse(url)
    return p.scheme=='https' and bool(p.netloc) and not p.username and not p.password

def canonical(url):
    p=urllib.parse.urlsplit(url)
    q=[(k,v) for k,v in urllib.parse.parse_qsl(p.query,keep_blank_values=True) if not k.lower().startswith('utm_') and k.lower() not in ('fbclid','gclid')]
    return urllib.parse.urlunsplit((p.scheme,p.netloc.lower(),p.path.rstrip('/') or '/',urllib.parse.urlencode(q),'')).strip()

def parse(xml, source):
    root=ET.fromstring(xml)
    items=root.findall('.//item')
    if not items:
        ns={'a':'http://www.w3.org/2005/Atom'}
        items=root.findall('.//a:entry',ns)
    out=[]
    for el in items[:70]:
        title=text(el,'title') or text(el,'{http://www.w3.org/2005/Atom}title')
        url=text(el,'link')
        if not url:
            for link in el.findall('{http://www.w3.org/2005/Atom}link'):
                if link.attrib.get('rel','alternate')=='alternate':url=link.attrib.get('href','');break
        date=date_iso(text(el,'pubDate') or text(el,'{http://purl.org/dc/elements/1.1/}date') or text(el,'{http://www.w3.org/2005/Atom}published') or text(el,'{http://www.w3.org/2005/Atom}updated'))
        title=re.sub(r'\s+',' ',title).strip()
        if not title or not valid_url(url):continue
        url=canonical(url)
        ident=hashlib.sha256(url.encode()).hexdigest()[:16]
        out.append({'id':ident,'title':title,'url':url,'source':source['name'],'category':source['category'],'published_at':date,'discovered_at':dt.datetime.now(dt.timezone.utc).isoformat(),'access':'Unknown','tags':[]})
    return out

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--edition',choices=['morning','evening','manual'],default='manual');args=parser.parse_args()
    now=dt.datetime.now(dt.timezone.utc);ist=dt.timezone(dt.timedelta(hours=5,minutes=30));local=now.astimezone(ist)
    sources=json.loads((ROOT/'sources.json').read_text());old=json.loads(DATA.read_text()) if DATA.exists() else {'articles':[]}
    indexed={x['id']:x for x in old.get('articles',[])};status=[];new=0
    for src in sources:
        try:
            req=urllib.request.Request(src['url'],headers={'User-Agent':USER_AGENT,'Accept':'application/rss+xml,application/atom+xml,application/xml,text/xml;q=0.9,*/*;q=0.5'})
            with urllib.request.urlopen(req,timeout=13) as response:
                raw=response.read(1_500_000)
            records=parse(raw,src)
            for item in records:
                if item['id'] not in indexed:
                    item['edition_date']=local.date().isoformat();item['edition']=args.edition;indexed[item['id']]=item;new+=1
            status.append({'source':src['name'],'ok':True,'items':len(records)})
        except Exception as e:
            status.append({'source':src['name'],'ok':False,'error':str(e)[:140]})
        time.sleep(.15)
    ordered=sorted(indexed.values(),key=lambda x:x.get('published_at') or x.get('discovered_at') or '',reverse=True)[:MAX_RECORDS]
    old_dates=old.get('edition_dates',[])
    if args.edition!='manual' and new:
        record={'date':local.date().isoformat(),'edition':args.edition,'collected_at':now.isoformat(),'new_articles':new}
        old_dates=[x for x in old_dates if (x['date'],x['edition'])!=(record['date'],record['edition'])]+[record]
    DATA.write_text(json.dumps({'updated_at':now.isoformat(),'articles':ordered,'feed_status':status,'edition_dates':old_dates[-800:]},ensure_ascii=False,separators=(',',':'))+'\n')
    print(f'Collected {new} new articles, total {len(ordered)}; {sum(s["ok"] for s in status)}/{len(status)} feeds succeeded')
    for s in status:
        if not s['ok']:print('WARN:',s['source'],s['error'])
if __name__=='__main__':main()
