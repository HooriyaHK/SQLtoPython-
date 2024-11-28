from pymongo import MongoClient
from datetime import datetime


def list_top_tweets(field, n, port):
    client = MongoClient(f'mongodb://localhost:{port}/')
    db = client['291db']
    collection = db['tweets']
    
    tweets = collection.find({}, {"_id": 1, "date": 1, "content": 1, "username": 1}) \
                       .sort(field, -1).limit(n)
    
    for tweet in tweets:
        print(tweet)

def list_top_users(n, port):
    client = MongoClient(f'mongodb://localhost:{port}/')
    db = client['291db']
    collection = db['tweets']
    
    users = collection.aggregate([
        {"$group": {"_id": "$username", "displayname": {"$first": "$username"}, "followersCount": {"$max": "$followersCount"}}},
        {"$sort": {"followersCount": -1}},
        {"$limit": n}
    ])
    
    for user in users:
        print(user)


def compose_tweet(content, port):
    # Connect to MongoDB
    client = MongoClient(f'mongodb://localhost:{port}/')
    db = client['291db']
    collection = db['tweets']
    
    # Create the tweet document
    tweet = {
        "content": content,
        "username": "291user",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "retweetCount": None,
        "likeCount": None,
        "quoteCount": None,
        "followersCount": None
    }
    
    # Insert the tweet into the collection
    result = collection.insert_one(tweet)
    
    print(f"Tweet inserted with ID: {result.inserted_id}")

# Test queries
print("Top tweets by likeCount:")
list_top_tweets("likeCount", 5, 27017)

print("\nTop users by followersCount:")
list_top_users(5, 27017)

compose_tweet("This is my first tweet using Python and MongoDB!", 27017)


