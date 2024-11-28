import pymongo
from pymongo import MongoClient

def search_tweets(keywords, port):
    client = MongoClient(f'mongodb://localhost:{port}/')
    db = client['291db']
    collection = db['tweets']

    query = {"$and": [{"content": {"$regex": keyword, "$options": "i"}} for keyword in keywords]}
    results = collection.find(query)

    # results
    for tweet in results:
        print(f"ID: {tweet['id']}")
        print(f"Date: {tweet['date']}")
        print(f"Content: {tweet['content']}")
        print(f"Username: {tweet['user']['username']}")
        print("-" * 40)
