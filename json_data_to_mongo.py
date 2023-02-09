from curses import raw
import json
from pprint import pprint
from pymongo import MongoClient

with open("./flux/index.json", "r") as read_file:
    data = json.load(read_file)

pprint(len(data))

def update_otherColls(raw_json_obj):
    # to update POI_Types, Themes, Features, Theme_Type, Feature_Type

    if "themes" in raw_json_obj:
        if len(raw_json_obj.themes) > 0:
            update_themes(raw_json_obj.themes)

    if "features" in raw_json_obj:
        if len(raw_json_obj.features) > 0:
            update_features(raw_json_obj.features)

    if len(raw_json_obj.categories) > 0:
        update_categories(raw_json_obj.categories)

    return

categories = set()

themes = set()
theme_type = set()

features = set()
feature_type = set()

def update_themes(listThemes):
    for theme_type in listThemes:
        themeTypes = theme_type.split("|")
        theme.add(themeTypes[0])
        theme_type.add(themeTypes[1])

def update_features(listFeatures):
    for feature_type in listFeatures:
        featureTypes = feature_type.split("|")
        feature.add(featureTypes[0])
        feature_type.add(featureTypes[1])

def update_categories(listTypes):
    for category in listTypes:
        categories.add(category)

def get_features_POI(POI):
    features_POI=[]
    list_feature=[]
    noInfo = 0
    try:
        list_feature=POI["hasFeature"]
    except:
        noInfo += 1
    if list_feature!= []:
        for feat in list_feature:
            if "features" in feat:
                for feature in feat["features"]:
                    features_POI.append((feature["@id"] if "@id" in feature else "")+"|"+((feature["@type"][0] if len(feature["@type"]) > 0 else "") if "@type" in feature else ""))
                    if "@id" in feature:
                        features.add(feature["@id"])
                        if "@type" in feature:
                            if len(feature["@type"]) > 0:
                                feature_type.add(feature["@type"][0])
            #if "features" in list(feature.keys()):
                #features_POI.append((feature["@id"] if "@id" in theme else "")+":"+((theme["@type"][0] if len(theme["@type"]) > 0 else "") if "@type" in theme else ""))
                #features_POI = feature["features"][0]["rdfs:label"]["fr"][0] + "#"
    #print("les features de POI pour ", noInfo," POI n'a pas d'informations sur ses caractéristiques")
    return features_POI

def get_themes_POI(POI):
    themes_POI=[]
    list_theme=[]
    noInfo = 0
    try:
        list_theme=POI["hasTheme"]
    except:
        noInfo += 1
    if list_theme!= []:
        for theme in list_theme:
            themes_POI.append((theme["@id"] if "@id" in theme else "")+"|"+((theme["@type"][0] if len(theme["@type"]) > 0 else "") if "@type" in theme else ""))
            if "@id" in theme:
                themes.add(theme["@id"])
                if "@type" in theme:
                    if len(theme["@type"]) > 0:
                        theme_type.add(theme["@type"][0])
            #if "features" in list(theme.keys()):
                #themes_POI+= theme["features"][0]["rdfs:label"]["fr"][0] + "#"
    #print("les features de POI pour ", noInfo," POI n'a pas d'informations sur ses caractéristiques")
    return themes_POI

def get_categories(raw_json):
    if "@type" in raw_json:
        if len(raw_json["@type"]) > 0:
            cats = raw_json["@type"]
            update_categories(cats)
            return cats
    return []

def row_to_add(raw_json):
    #new_json = {}
    #try:
    new_json = {
        "id": raw_json["dc:identifier"],
        "categories": get_categories(raw_json),
        "availableLanguages": raw_json["availableLanguage"] if "availableLanguage" in raw_json else "noLanguages",
        "description_en": (raw_json["rdfs:comment"]["en"][0] if ("en" in raw_json["rdfs:comment"]) and len(raw_json["rdfs:comment"]["en"]) > 0 else "noCommentEN") if "rdfs:comment" in raw_json else "noComment",
        "description_fr": (raw_json["rdfs:comment"]["fr"][0] if ("fr" in raw_json["rdfs:comment"]) and len(raw_json["rdfs:comment"]["fr"]) > 0 else "noCommentFR") if "rdfs:comment" in raw_json else "noComment",
        "description_es": (raw_json["rdfs:comment"]["es"][0] if ("es" in raw_json["rdfs:comment"]) and len(raw_json["rdfs:comment"]["es"]) > 0 else "noCommentES") if "rdfs:comment" in raw_json else "noComment",
        "name": raw_json["rdfs:label"]["fr"][0],
        "contact_tel": ((raw_json["hasContact"][0]["schema:telephone"][0] if "schema:telephone" in raw_json["hasContact"][0] else "noEmail") if len(raw_json["hasContact"]) > 0 else "noContact") if "hasContact" in raw_json else "noHasContact",
        "contact_email": ((raw_json["hasContact"][0]["schema:email"][0] if "schema:email" in raw_json["hasContact"][0] else "noEmail") if len(raw_json["hasContact"]) > 0 else "noContact")  if "hasContact" in raw_json else "noHasContact",
        "contact_webpage": ((raw_json["hasContact"][0]["foaf:homepage"][0] if "foaf:homepage" in raw_json["hasContact"][0] else "noHomepage") if len(raw_json["hasContact"]) > 0 else "noContact")  if "hasContact" in raw_json else "noHasContact",
        #"location": raw_json["isLocatedAt"],
        "streetName": ((raw_json["isLocatedAt"][0]["schema:address"][0]["schema:streetAddress"][0] if "schema:streetAddress" in raw_json["isLocatedAt"][0]["schema:address"][0] else "noStreetAdd") if "schema:address" in raw_json["isLocatedAt"][0] else "noAddress") if len(raw_json["isLocatedAt"]) > 0 else "noLocation",
        "postalCode": raw_json["isLocatedAt"][0]["schema:address"][0]["schema:postalCode"],
        "city": raw_json["isLocatedAt"][0]["schema:address"][0]["schema:addressLocality"],
        "lat": raw_json["isLocatedAt"][0]["schema:geo"]["schema:latitude"],
        "long": raw_json["isLocatedAt"][0]["schema:geo"]["schema:longitude"],
        "reducedMobilityAccess": raw_json["reducedMobilityAccess"] if "reducedMobilityAccess" in raw_json else False,
        "petsAllowed": raw_json["petsAllowed"] if "petsAllowed" in raw_json else False,
        "lastUpdated": raw_json["lastUpdateDatatourisme"] if "lastUpdateDatatourisme" in raw_json else False,
        "features": get_features_POI(raw_json),
        "themes": get_themes_POI(raw_json)
    }
    #except Exception:
        #print("Error reading ", raw_json["@id"], " from input raw json")
    return new_json

file_obj_data = []

for file_obj in data:
    with open("./flux/objects/"+file_obj["file"], "r") as read_file:
       json_obj = json.load(read_file)

       #pprint(json_obj["@type"])
       new_json = row_to_add(json_obj)
       file_obj_data.append(new_json)
       #update_otherColls(new_json)
       #pois.insert_one(new_json)
       #pprint(file_obj)
       #break

pprint(len(file_obj_data))
#pprint(file_obj_data[0])

print("Categories len:", len(categories))
print("Themes len:", len(themes))
print("Themes Type len:", len(theme_type))
print("Features len:", len(features))
print("Features Type len:", len(feature_type))

# So far the data is set up to be inserted in their respective collections

'''
    Collection representation: 
    (- representing columns to be removed AFTER + representing columns are added)
    Theme_Type (_id, name)
    Feature_Type (_id, name)
    Theme (_id, name, -type_name, +id_theme_type)
    Feature (_id, name, -feature_name, +id_feature_type)
    POI (_id, -categories, desc_en, desc_fr, desc_es, name, contact_tel, contact_email,
        contact_webpage, street_name, postal_code, city, lat, long, 
        reduced_mobility_access, pets_allowed, last_updated, -features, -themes,
        +id_categories, +id_features, +id_themes)

'''

'''
    At the same time, we will update the IDs for so that whenever CSV is needed, its easy to build :
        id_feature_type for each feature
        id_theme_type for each theme
        id_features, id_themes and id_categories for each POI
'''

client = MongoClient(
    host="127.0.0.1",
    port = 27017
)

db = client.test_eval

print(db.list_collection_names())

# making feature types
coll_feature_type = db.feature_type
dict_feature_types = {}
for x in feature_type:
    f_t = coll_feature_type.insert_one({"name": x})
    #if "inserted_id" in f_t:
    dict_feature_types[x] = f_t.inserted_id

# making theme types
coll_theme_type = db.theme_type
dict_theme_types = {}
for x in theme_type:
    f_t = coll_theme_type.insert_one({"name": x})
    #if "inserted_id" in f_t:
    dict_theme_types[x] = f_t.inserted_id

# setting feature_type_ids to features AND theme_type_ids to themes
dict_feature_with_types = {}
dict_theme_with_types = {}
for poi in file_obj_data:
    if "features" in poi:
        if len(poi["features"]) > 0:
            for feat in poi["features"]:
                f_t = feat.split("|")
                if f_t[1] in dict_feature_types:
                    dict_feature_with_types[f_t[0]] = dict_feature_types[f_t[1]]
    if "themes" in poi:
        if len(poi["themes"]) > 0:
            for tem in poi["themes"]:
                f_t = tem.split("|")
                if f_t[1] in dict_theme_types:
                    dict_theme_with_types[f_t[0]] = dict_theme_types[f_t[1]]



print("Features len after update:", len(features))
print("Themes len after update:", len(themes))

#pprint(dict_theme_with_types)

# TODO: create categories
coll_category = db.category
dict_poi_types = {}
for x in categories:
    f_t = coll_category.insert_one({"name": x})
    #if "inserted_id" in f_t:
    dict_poi_types[x] = f_t.inserted_id

# TODO: create features
coll_feature = db.feature
dict_poi_feats = {}
for x in features:
    f_t = coll_feature.insert_one({"name": x, "id_feature_type": dict_feature_with_types[x]})
    #if "inserted_id" in f_t:
    dict_poi_feats[x] = f_t.inserted_id

# TODO: create themes
coll_theme = db.theme
dict_poi_themes = {}
for x in themes:
    f_t = coll_feature.insert_one({"name": x, "id_theme_type": dict_theme_with_types[x]})
    #if "inserted_id" in f_t:
    dict_poi_themes[x] = f_t.inserted_id

# setting category_id, feature_id, theme_id to POI
# TODO: create POIs
coll_poi = db.poi
dict_poi_with_types = {}
csv_rows = [["alt_id", "name", "lat", "long", "types", "features_with_types", "themes_with_types"]]
for poi in file_obj_data:
    if "categories" in poi:
        if len(poi["categories"]) > 0:
            id_categories = []
            for cat in poi["categories"]:
                #f_t = feat.split("|")
                if cat in dict_poi_types:
                    id_categories.append(dict_poi_types[cat])
            if len(id_categories) > 0:
                poi["id_categories"] = id_categories
                #del poi["categories"]
    if "features" in poi:
        if len(poi["features"]) > 0:
            id_features = []
            for feat in poi["features"]:
                f_t = feat.split("|")
                if f_t[0] in dict_poi_feats:
                    id_features.append(dict_poi_feats[f_t[0]])
            if len(id_features) > 0:
                poi["id_features"] = id_features
                #del poi["features"]
    if "themes" in poi:
        if len(poi["themes"]) > 0:
            id_themes = []
            for tem in poi["themes"]:
                f_t = tem.split("|")
                if f_t[0] in dict_poi_themes:
                    id_themes.append(dict_poi_themes[f_t[0]])
            if len(id_themes) > 0:
                poi["id_themes"] = id_themes
                #del poi["themes"]
    coll_poi.insert_one({
        "alt_id": poi["id"],
        "spoken_langs": poi["availableLanguages"],
        "desc_en": poi["description_en"],
        "desc_fr": poi["description_fr"],
        "desc_es": poi["description_es"],
        "name": poi["name"],
        "contact": {"tel": poi["contact_tel"], "email": poi["contact_email"], "homepage": poi["contact_webpage"]},
        "address": {"street": poi["streetName"], "zip": poi["postalCode"], "city": poi["city"]},
        "lat": poi["lat"],
        "long": poi["long"],
        "mobility_access": poi["reducedMobilityAccess"],
        "pets_allowed": poi["petsAllowed"],
        "last_updated": poi["lastUpdated"],
        "id_categories": poi["id_categories"] if "id_categories" in poi else [],
        "id_features": poi["id_features"] if "id_features" in poi else [],
        "id_themes": poi["id_themes"] if "id_themes" in poi else []
    })
    csv_rows.append(list([
        poi["id"],
        poi["name"], 
        poi["lat"], 
        poi["long"],
        poi["categories"] if "categories" in poi else [],
        poi["features"] if "features" in poi else [],
        poi["themes"] if "themes" in poi else []]))

import csv
import calendar
import time
ts = calendar.timegm(time.gmtime())
print(ts)

with open('./csvs/POIs_'+str(ts)+'.csv', 'w', newline='') as file:
     writer = csv.writer(file)
     writer.writerows(csv_rows)

#pprint(file_obj_data[0])
