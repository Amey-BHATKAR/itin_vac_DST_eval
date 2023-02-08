'''from pymongo import MongoClient

def get_db_obj():
    client = MongoClient(
        host="127.0.0.1",
        port = 27017
    )

    #print(client.list_database_names())

    sa = client.test_eval

    print(len(sa.list_collection_names()))

    if len(sa.list_collection_names()) == 0:
        import subprocess
        subprocess.run(["mongorestore", "-d", "test_eval", os.path.join(os.getcwd(), "dump/test_eval/")])

    return sa

db = get_db_obj()

unique_cities = db.poi.distinct("address.city", {"address.city": 1, "_id": 0})
print(unique_cities)'''

import json, os
cities = []
with open(os.path.join(os.getcwd(), "dump/city_names.json"), "r") as f_in:
    cities = f_in.read()#json.load(f_in)
'''city_datalist = html.Datalist(
    id='list-suggested-cities', 
    children=[html.Option(value=city) for city in cities]
)'''

print(len(cities))