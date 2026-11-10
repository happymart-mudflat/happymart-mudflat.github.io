"""국립해양조사원 조석예보(고·저조) API로 앞으로 N일치 물때를 받아 index.html의 TIDES 블록을 갱신한다.
인증키는 환경변수 KHOA_KEY 로 받는다 (GitHub 저장소 Secrets에 저장).
사용: KHOA_KEY=... python3 tools/update_tides.py [일수]"""
import json, math, os, re, sys, time, urllib.parse, urllib.request, datetime as dt
from pathlib import Path
KEY=os.environ['KHOA_KEY'].strip()
PAGE=Path(__file__).resolve().parent.parent/'index.html'
OBS='DT_0067'          # 안흥 관측소
LAT,LON=36.60,126.30   # 체험장(남면 진산리) 부근 — 해뜸·해짐 계산용
DAYS=int(sys.argv[1]) if len(sys.argv)>1 else 45
def sun(d,rise):
    N=d.timetuple().tm_yday; lh=LON/15; t=N+((6 if rise else 18)-lh)/24
    M=0.9856*t-3.289; L=(M+1.916*math.sin(math.radians(M))+0.020*math.sin(math.radians(2*M))+282.634)%360
    RA=math.degrees(math.atan(0.91764*math.tan(math.radians(L))))%360; RA=(RA+(math.floor(L/90)*90-math.floor(RA/90)*90))/15
    sd=0.39782*math.sin(math.radians(L)); cd=math.cos(math.asin(sd))
    cH=(math.cos(math.radians(90.833))-sd*math.sin(math.radians(LAT)))/(cd*math.cos(math.radians(LAT)))
    H=((360-math.degrees(math.acos(cH))) if rise else math.degrees(math.acos(cH)))/15
    k=((H+RA-0.06571*t-6.622-lh)%24+9)%24; return f"{int(k):02d}:{int(round((k%1)*60))%60:02d}"
def get(url):
    for k in range(4):
        try:
            with urllib.request.urlopen(url,timeout=20) as r: return json.load(r)
        except Exception as e: err=e; time.sleep(1+k)
    raise SystemExit(f'API 호출 실패: {err}')
today=(dt.datetime.now(dt.timezone.utc)+dt.timedelta(hours=9)).date(); out={}
for i in range(DAYS):
    d=today+dt.timedelta(days=i)
    q=urllib.parse.urlencode({'serviceKey':KEY,'type':'json','obsCode':OBS,'reqDate':d.strftime('%Y%m%d'),'numOfRows':10,'pageNo':1})
    j=get('https://apis.data.go.kr/1192136/tideFcstHghLw/GetTideFcstHghLwApiService?'+q)
    items=j['body']['items']['item']; items=items if isinstance(items,list) else [items]
    out[d.isoformat()]={"sunrise":sun(d,True),"sunset":sun(d,False),
      "tides":[[x['predcDt'][11:16],round(float(x['predcTdlvVl'])),"H" if int(x['extrSe'])%2 else "L"] for x in items]}
    time.sleep(.15)
body='{\n'+',\n'.join(f'  "{k}": '+json.dumps(v,ensure_ascii=False) for k,v in out.items())+'\n}'
s=PAGE.read_text(encoding='utf-8')
s,n=re.subn(r'/\*TIDES_START\*/.*?/\*TIDES_END\*/','/*TIDES_START*/'+body+'/*TIDES_END*/',s,flags=re.S)
assert n==1, 'TIDES 블록을 찾지 못했습니다'
PAGE.write_text(s,encoding='utf-8'); print(f'{len(out)}일치 갱신: {min(out)} ~ {max(out)}')
