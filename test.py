import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from google.cloud.firestore_v1.base_query import FieldFilter


cred = credentials.Certificate("./au.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

data = {
    'city': input('enter city : ')
}

query_ad = db.collection(u'test_coll').where(filter=FieldFilter(u"name", u"==", data["city"])).get()

if query_ad:
    print('Exist')
    print(query_ad.get().to_dict())
else:
    print("Doesn't Exist")
