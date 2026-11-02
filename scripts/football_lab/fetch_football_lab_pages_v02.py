#!/usr/bin/env python3
"""TOTO Labo Football LAB team-page and tab collector (HTML-only tabs).
Requires beautifulsoup4. Does not execute JavaScript or infer unpublished data.
"""
import argparse, csv, json, re, time
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlsplit, parse_qsl, urlencode, urlunsplit
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup

BASE='https://www.football-lab.jp'
SECTIONS=('ranking','formation','style','preview')
INITIAL=['', '/ranking', '/formation', '/style', '/style/?s=11', '/style/?s=31', '/style/?s=32', '/style/?s=33', '/preview', '/style/?s=21', '/style/?s=22', '/style/?s=23', '/style/?s=24', '/style/?s=45', '/style/?s=66', '/style/?s=67', '/style/?s=69', '/style/?s=81', '/style/?s=82', '/style/?s=83']
SLUG=re.compile(r'^[a-z0-9_-]+$')

def get(url,timeout):
    req=Request(url,headers={'User-Agent':'Mozilla/5.0 (compatible; TOTO-Labo/0.2; research)','Accept':'text/html'})
    with urlopen(req,timeout=timeout) as r:
        content=r.read(12_000_001)
        if len(content)>12_000_000 or 'html' not in r.headers.get('Content-Type','').lower():
            raise ValueError('invalid HTML response')
        return content,r.geturl(),r.status

def normalize(url,slug):
    p=urlsplit(url)
    if p.netloc!='www.football-lab.jp' or p.scheme!='https': return None
    parts=p.path.strip('/').split('/')
    if not parts or parts[0]!=slug or len(parts)>2: return None
    if len(parts)==2 and parts[1] not in SECTIONS: return None
    qs=[(k,v) for k,v in parse_qsl(p.query,keep_blank_values=True) if k in ('s','year','data','tab','type','sort','mode')]
    if len(qs)>3: return None
    return urlunsplit(('https',p.netloc,'/'+ '/'.join(parts),urlencode(sorted(qs)),''))

def tabs(soup,current,slug):
    found=set()
    for a in soup.select('a[href]'):
        href=a.get('href','')
        u=normalize(urljoin(current,href),slug)
        if u and u!=normalize(current,slug):
            # Limit discovery to page navigation and known query-driven tabs.
            target=urlsplit(u)
            if target.query or target.path.rstrip('/').split('/')[-1] in SECTIONS:
                found.add(u)
    return sorted(found)

def writecsv(path,fields,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)

def preview_extract(soup,slug,opponent,analysis):
    comparison=' '.join(t.get_text(' ',strip=True) for t in soup.select('.tblCompare'))
    status=('not_published' if not comparison or 'HOME' not in comparison or 'AWAY' not in comparison
            else 'match_mismatch' if opponent and opponent not in comparison else 'published')
    rows=[]
    for i,t in enumerate(soup.select('table'),1):
        if 'hotzone' in (t.get('class') or []):continue
        for j,tr in enumerate(t.select('tr'),1):
            cells=tr.find_all(['td','th'],recursive=False)
            if cells:rows.append({'table_no':i,'table_class':' '.join(t.get('class') or []),'row_no':j,'cells_json':json.dumps([c.get_text(' ',strip=True) for c in cells],ensure_ascii=False)})
    zones=soup.select('table.hotzone'); heat=[]
    for zi,t in enumerate(zones,1):
        for ri,tr in enumerate(t.select('tr'),1):
            for ci,td in enumerate(tr.select('td'),1):
                style=td.get('style',''); m=re.search(r'rgba?\([^)]*\)',style,re.I)
                heat.append({'team_side':'home' if zi==1 else 'away' if zi==2 else f'unknown_{zi}','zone_no':zi,'row':ri,'col':ci,'color':m.group(0) if m else '', 'style':style,'text':td.get_text(' ',strip=True)})
    writecsv(analysis/f'{slug}_preview_tables.csv',['table_no','table_class','row_no','cells_json'],rows)
    writecsv(analysis/f'{slug}_preview_hotzone.csv',['team_side','zone_no','row','col','color','style','text'],heat)
    counts=[len(t.select('td')) for t in zones]
    valid=(counts==[54,54] and all(h['color'] for h in heat) and
           all(len({(h['row'],h['col']) for h in heat if h['zone_no']==z})==54 for z in (1,2)))
    if status=='published' and not valid:status='partial_hotzone'
    return {'status':status,'table_rows':len(rows),'hotzone_tables':len(zones),'hotzone_cells':len(heat),'hotzone_cells_per_table':counts,'hotzone_structure_valid':valid,'comparison_header':comparison[:180]}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--round',type=int,required=True)
    ap.add_argument('--team',help='Football LAB slug for single-team test')
    ap.add_argument('--team-map',type=Path,help='CSV team_name,football_lab_slug')
    ap.add_argument('--official-csv',type=Path)
    ap.add_argument('--opponent',help='Expected opponent, for single-team preview verification')
    ap.add_argument('--delay',type=float,default=3)
    ap.add_argument('--timeout',type=int,default=25)
    ap.add_argument('--max-pages-per-team',type=int,default=20)
    ap.add_argument('--dry-run',action='store_true')
    args=ap.parse_args()
    if args.delay<2:ap.error('--delay must be >= 2')
    if args.max_pages_per_team<9:ap.error('--max-pages-per-team must be >= 9')
    slugs=set(); opponents={}
    if args.team:slugs.add(args.team);opponents[args.team]=args.opponent
    if args.team_map:
        card=args.official_csv or Path(f'data/analysis/toto{args.round}_official_matches_v01.csv')
        if not card.exists():ap.error(f'Official fixtures missing: {card}')
        with card.open(encoding='utf-8-sig',newline='') as f:matches=list(csv.DictReader(f))
        if len(matches)!=13 or len({r['match_no'] for r in matches})!=13:ap.error('Expected 13 distinct fixtures')
        with args.team_map.open(encoding='utf-8-sig',newline='') as f: mapping={(r.get('team_name') or r.get('team_short') or '').strip():(r.get('football_lab_slug') or r.get('slug') or '').strip() for r in csv.DictReader(f)}
        teams={r[k].strip() for r in matches for k in ('home_team','away_team')}
        if teams-set(mapping):ap.error('Unmapped teams: '+', '.join(sorted(teams-set(mapping))))
        slugs.update(mapping[t] for t in teams)
        for r in matches:
            opponents[mapping[r['home_team'].strip()]]=r['away_team'].strip()
            opponents[mapping[r['away_team'].strip()]]=r['home_team'].strip()
    if not slugs:ap.error('Specify --team or --team-map')
    if any(not SLUG.fullmatch(s) for s in slugs):ap.error('Invalid slug')
    raw=Path(f'data/raw/football_lab/toto{args.round}');raw.mkdir(parents=True,exist_ok=True)
    analysis=Path(f'data/analysis/football_lab/toto{args.round}');analysis.mkdir(parents=True,exist_ok=True)
    records=[]
    for slug in sorted(slugs):
        queue=deque(normalize(BASE+'/'+slug+path,slug) for path in INITIAL)
        seen=set(); index=0
        while queue and index<args.max_pages_per_team:
            url=queue.popleft()
            if not url or url in seen:continue
            seen.add(url);index+=1
            path=urlsplit(url);section=path.path.strip('/').split('/')[-1]
            kind='stats' if section==slug else section
            if path.query:kind+='_'+re.sub(r'[^a-zA-Z0-9_-]+','_',path.query)
            filename=f'{slug}_{kind}.html'
            rec={'round':args.round,'team_slug':slug,'page_type':kind,'url':url,'retrieved_at_utc':datetime.now(timezone.utc).isoformat(),'status':'planned' if args.dry_run else 'failed'}
            if not args.dry_run:
                try:
                    dest=raw/filename
                    cached=dest.exists() and dest.stat().st_size > 0
                    if cached:
                        content=dest.read_bytes()
                        final=url
                        code=200
                    else:
                        content,final,code=get(url,args.timeout)
                    if not cached:
                        dest.write_bytes(content)
                    soup=BeautifulSoup(content,'html.parser')
                    discovered=tabs(soup,final,slug)
                    for next_url in []:
                        if next_url not in seen and next_url not in queue:queue.append(next_url)
                    rec.update(status='saved_raw_unvalidated',path=str(dest),http_status=(None if cached else code),bytes=len(content),tabs_discovered=len(discovered),source=('cache' if cached else 'network'),file_modified_at_utc=datetime.fromtimestamp(dest.stat().st_mtime,timezone.utc).isoformat())
                    if section=='preview' and not path.query:
                        rec['preview_validation']=preview_extract(soup,slug,opponents.get(slug),analysis)
                        rec['status']=rec['preview_validation']['status']
                except Exception as e:rec['error']=f'{type(e).__name__}: {e}'
            records.append(rec)
            print(f'[{slug} {index}/{args.max_pages_per_team}] {kind}: {rec["status"]}',flush=True)
            if not args.dry_run and queue and not cached:time.sleep(args.delay)
        if queue:records.append({'team_slug':slug,'status':'page_limit_reached','remaining_queue':len(queue)})
    report=raw/'collection_report_v02.json'
    report.write_text(json.dumps({'round':args.round,'phase':'raw_html_and_preview_structural_validation','javascript_tabs_executed':False,'league_rankings_included':False,'records':records},ensure_ascii=False,indent=2),encoding='utf-8')
    print('Report:',report)
    if any(r['status'] in ('failed','match_mismatch','partial_hotzone','page_limit_reached') for r in records):raise SystemExit(1)

if __name__=='__main__':main()
