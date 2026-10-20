#!/usr/bin/env python3
"""Run once from repository root: python upgrade_collector.py. Idempotent RSS metadata enhancement."""
from pathlib import Path
p=Path('collector.py')
s=p.read_text()
needle="        out.append({'id':ident,'title':title,'url':url,'source':source['name']"
if 'def extract_extra_metadata(' not in s:
    fn='''def extract_extra_metadata(el):
    """Extract only metadata explicitly provided in RSS/Atom; no scraping."""
    author=(text(el,'{http://purl.org/dc/elements/1.1/}creator') or text(el,'author') or text(el,'{http://www.w3.org/2005/Atom}author/{http://www.w3.org/2005/Atom}name') or text(el,'{http://www.w3.org/2005/Atom}author'))
    thumbnail=''
    for tag in ('{http://search.yahoo.com/mrss/}thumbnail','{http://search.yahoo.com/mrss/}content','enclosure','{http://www.w3.org/2005/Atom}link'):
        for node in el.findall(tag):
            candidate=node.attrib.get('url') or (node.attrib.get('href') if node.attrib.get('type','').startswith('image/') else '')
            if candidate and valid_url(candidate) and (tag!='enclosure' or node.attrib.get('type','').startswith('image/')):
                thumbnail=candidate;break
        if thumbnail:break
    summary=(text(el,'description') or text(el,'{http://www.w3.org/2005/Atom}summary'))
    summary=re.sub(r'<[^>]+>',' ',summary)
    summary=re.sub(r'\\s+',' ',summary).strip()[:400]
    return {'author':re.sub(r'\\s+',' ',author).strip()[:180] or None,'thumbnail':thumbnail or None,'summary':summary or None}

'''
    pos=s.index('def parse(xml, source):')
    s=s[:pos]+fn+s[pos:]
    s=s.replace(needle,"        extra=extract_extra_metadata(el)\n"+needle)
    s=s.replace("'access':'Unknown','tags':[]})","'access':'Unknown','tags':[],**extra})")
    s=s.replace("                if item['id'] not in indexed:","                if item['id'] in indexed:\n                    for field in ('author','thumbnail','summary'):\n                        if item.get(field) and not indexed[item['id']].get(field):indexed[item['id']][field]=item[field]\n                if item['id'] not in indexed:")
    p.write_text(s)
    print('collector.py upgraded with RSS author, thumbnail, summary metadata')
else:print('collector.py already upgraded')
