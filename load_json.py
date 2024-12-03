import json
import sys
from pymongo import MongoClient

def load_json_to_mongodb(json_file, port):
    # Connect to MongoDB server
        client = MongoClient(f"mongodb://localhost:{port}")
        print(f"Connected to MongoDB on port {port}.")

        # Create database and collection
        db = client["291db"]
        collection = db["tweets"]

         # Drop the collection if it exists
        if "tweets" in db.list_collection_names():
            collection.drop()
            print("Existing 'tweets' collection dropped.")


        # Insert data in batches
        with open(json_file, "r", encoding="utf-8") as file:
            batch = []
            batch_size = 1000  # Set batch size

            for line_number, line in enumerate(file, start=1):
                tweet = json.loads(line.strip())
                batch.append(tweet)

                if len(batch) >= batch_size:
                    collection.insert_many(batch)
                    print(f"Inserted {len(batch)} tweets into the collection.")
                    batch.clear()

            # Insert any remaining tweets in the last batch
            if batch:
                collection.insert_many(batch)
                print(f"Inserted {len(batch)} tweets into the collection.")

        #print("All tweets have been successfully loaded into the 'tweets' collection.")
       # client.close()
       # print("MongoDB connection closed.")