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

# query_ad = db.collection(u'test_coll').where(filter=FieldFilter(u"name", u"==", data["city"])).get()
query_all = db.collection(u'test_coll').stream()
# Add a new doc in collection 'cities' with ID 'LA'
db.collection("test_coll").document(data['city']).set(data)

for doc in query_all:
    print(f"{doc.id}\t {doc.to_dict()}")

