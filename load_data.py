import requests
import pymongo
import pandas as pd 

def load_machhines(db, session):
    db.drop_collection('machines')
    colection = db['machines']
    page_num=0
    response = session.get("https://api.eversys-telemetry.com/v3/machines?offset={}".format(page_num))
    collection_machines.insert_many(response.json)
    while(len(response.json > 0)):
        page_num += 1
        response = session.get("https://api.eversys-telemetry.com/v3/machines?offset={}".format(page_num))
        collection_machines.insert_many(response.json)


machine_ids = ['14658', '14651', '11027', '9048', '8863']

df = pd.DataFrame()
dates = pd.date_range('02.01.2021', '03.01.2021', freq='2880min')
df['dates'] = dates.strftime('%Y-%m-%d').to_list()
df['times'] = dates
df['hour']= df['times'].dt.hour.apply(str)
df['minute']= df['times'].dt.minute.apply(str)
df['second'] = df['times'].dt.second.apply(str)
df['date'] = df['dates'] + 'T' + df['times'].dt.strftime('%H') + '%3A' + df['times'].dt.strftime('%M') + '%3A' +df['times'].dt.strftime('%S') + 'Z'
print(df['date'])

session = requests.Session()
session.headers.update({"Accept": "application/json"})


client = pymongo.MongoClient('localhost', 27017)  
db = client['eversys']
collection_machines = db['product-history-dodo']

for first, second in zip(df['date'], df['date'][1:]):
    response = session.get('https://api.eversys-telemetry.com/v3/machines/328/products?st1={}&st2={}'.format(first, second))
    result = response.json()
    collection_machines.insert_many(result)
    print(len(result))

client.close()
