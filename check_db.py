import pymongo, os
from dotenv import load_dotenv

load_dotenv()
client = pymongo.MongoClient(os.getenv("MONGO_DB_URL"))

print("=== Everything in your MongoDB cluster ===")
for db_name in client.list_database_names():
    db = client[db_name]
    for col_name in db.list_collection_names():
        count = db[col_name].count_documents({})
        print(f"Database: '{db_name}' → Collection: '{col_name}' → {count} documents")