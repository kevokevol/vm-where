import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import asyncio

# Use a service account CHANGE THIS TO THE PATH OF YOUR OWN CERTIFICATE
cred = credentials.Certificate('./roketto-dan-firebase-adminsdk-1tvwb-a77cbc7880.json')
firebase_admin.initialize_app(cred)

db = firestore.client()

def readFromDB(collection):
    """
    Prints all the entries in a specified collection in the database
    """
    users_ref = db.collection(collection)
    docs = users_ref.stream()

    for doc in docs:
        print(u'{} => {}'.format(doc.id, doc.to_dict()))


async def insertIntoDB(collection, numCars):
    """
    Inserts current time and number of cars into the database with the respective
    collection and document categories
    """
    
    gen_id = db.collection('prom').where(u'count', u'>=', 0)
    g_id = gen_id.stream()

    for gid in g_id:
        index = gid.to_dict()['count']
    
    doc = 'test-' + str(index)
    index = index + 1
    
    # increment count
    gen_id = db.collection('prom').document('numEntries')
    gen_id.set({
        'count': index
    })

    doc_ref = db.collection(collection).document(doc)
    doc_ref.set({
        'time': datetime.datetime.now(),
        'index': index,
        'cars': numCars
    })






