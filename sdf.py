from google.cloud import storage
from google.oauth2 import service_account

cred = service_account.Credentials.from_service_account_file(
    "/home/ddddewang/Desktop/jams-f92b1-firebase-adminsdk-fbsvc-8651bbf671.json"
)
client = storage.Client(credentials=cred)
for bucket in client.list_buckets():
    print(bucket.name)