"""Official course dealership sample, with clearly labelled 5-row offline fallback.
The verified IBM original JSON is downloaded by refresh_official_data.sh.
"""
import json
from pathlib import Path
OFFICIAL_SOURCE = Path(__file__).with_name('official_dealerships.json')
DEALERS = [
 {"id":1,"full_name":"Prairie Star Auto — Kansas City","short_name":"Prairie Star Auto","city":"Kansas City","state":"Kansas","address":"101 Market Street","zip":"66101","lat":39.1155,"long":-94.6268},
 {"id":2,"full_name":"Wichita Motor Works","short_name":"Wichita Motor Works","city":"Wichita","state":"Kansas","address":"245 Commerce Drive","zip":"67202","lat":37.6872,"long":-97.3301},
 {"id":3,"full_name":"Best Cars — New York","short_name":"Best Cars NYC","city":"New York","state":"New York","address":"100 Example Avenue","zip":"10001","lat":40.7505,"long":-73.9934},
 {"id":4,"full_name":"Windy City Auto","short_name":"Windy City Auto","city":"Chicago","state":"Illinois","address":"200 Demo Street","zip":"60601","lat":41.8864,"long":-87.6186},
 {"id":5,"full_name":"Golden Gate Motors","short_name":"Golden Gate Motors","city":"San Francisco","state":"California","address":"300 Sample Road","zip":"94103","lat":37.7764,"long":-122.4172},
 ]
if OFFICIAL_SOURCE.is_file():
    raw=json.loads(OFFICIAL_SOURCE.read_text(encoding='utf-8'))
    official=raw.get('dealerships', [])
    if len(official)!=50:
        raise RuntimeError(f'Expected 50 official dealerships, got {len(official)}')
    DEALERS=official
STATE_ALIASES={'KS':'Kansas','NY':'New York','IL':'Illinois','CA':'California'}
CAR_DATA = [
 {'id':1,'name':'Toyota','description':'Japanese automaker','models':[{'id':1,'name':'Camry','type':'Sedan','year':2023},{'id':2,'name':'RAV4','type':'SUV','year':2022}]},
 {'id':2,'name':'Honda','description':'Japanese automaker','models':[{'id':3,'name':'Civic','type':'Sedan','year':2023},{'id':4,'name':'CR-V','type':'SUV','year':2022}]},
 {'id':3,'name':'Ford','description':'American automaker','models':[{'id':5,'name':'Mustang','type':'Coupe','year':2023},{'id':6,'name':'Escape','type':'SUV','year':2021}]},
]
SEED_REVIEWS = [
 {'dealership':1,'name':'Alex Morgan','purchase':True,'review':'Friendly staff and clear pricing. Fantastic service.','purchase_date':'2026-06-10','car_make':'Toyota','car_model':'Camry','car_year':2023},
 {'dealership':1,'name':'Jordan Lee','purchase':True,'review':'Helpful team and a straightforward purchase.','purchase_date':'2026-06-12','car_make':'Honda','car_model':'Civic','car_year':2023},
 {'dealership':2,'name':'Taylor Chen','purchase':False,'review':'Great selection and quick answers.','purchase_date':'2026-07-05','car_make':'Ford','car_model':'Escape','car_year':2021},
]

def filter_dealers(state=None):
 if not state or state.lower() == 'all': return DEALERS
 key=STATE_ALIASES.get(state.upper(),state)
 return [d for d in DEALERS if d['state'].lower()==key.lower() or d.get('st','').lower()==state.lower()]

def analyze_text(text):
 """Simple deterministic offline sentiment demo, not a production NLP model."""
 words=text.lower()
 pos=('fantastic','excellent','great','good','amazing','friendly','helpful','love','smooth','easy','best')
 neg=('terrible','awful','bad','poor','rude','worst','unhappy','broken','horrible')
 p=sum(word in words for word in pos); n=sum(word in words for word in neg)
 return 'positive' if p>n else 'negative' if n>p else 'neutral'
