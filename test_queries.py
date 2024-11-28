import json
from pymongo import MongoClient
from datetime import datetime

def load_json_data(filename, port):
    """Load tweets from a JSON file into MongoDB."""
    client = MongoClient(f'mongodb://localhost:{port}/')
    db = client['291db']
    collection = db['tweets']
    
    # Read and parse JSON
    with open(filename, 'r', encoding='utf-8') as file:
        json_data = [json.loads(line) for line in file]
        
    # Insert data into MongoDB
    collection.insert_many(json_data)
    print(f"Data from {filename} loaded successfully!")

def list_top_tweets(field, n, port):
    """List top N tweets sorted by a specific field."""
    client = MongoClient(f'mongodb://localhost:{port}/')
    db = client['291db']
    collection = db['tweets']
    
    tweets = collection.find({}, {"_id": 1, "date": 1, "content": 1, "username": 1}) \
                       .sort(field, -1).limit(n)
    
    for tweet in tweets:
        print(tweet)

def list_top_users(n, port):
    """List top N users by followersCount."""
    client = MongoClient(f'mongodb://localhost:{port}/')
    db = client['291db']
    collection = db['tweets']
    
    users = collection.aggregate([
        {"$group": {"_id": "$username", "displayname": {"$first": "$username"}, 
                    "followersCount": {"$max": "$followersCount"}}},
        {"$sort": {"followersCount": -1}},
        {"$limit": n}
    ])
    
    for user in users:
        print(user)

def compose_tweet(content, port):
    """Compose a new tweet and insert into MongoDB."""
    client = MongoClient(f'mongodb://localhost:{port}/')
    db = client['291db']
    collection = db['tweets']
    
    tweet = {
        "content": content,
        "username": "291user",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "retweetCount": None,
        "likeCount": None,
        "quoteCount": None,
        "followersCount": None
    }
    
    result = collection.insert_one(tweet)
    print(f"Tweet inserted with ID: {result.inserted_id}")

# Load data from 10.json
load_json_data('10.json', 27017)

# Run test queries
print("\nTop tweets by likeCount:")
list_top_tweets("likeCount", 5, 27017)

print("\nTop users by followersCount:")
list_top_users(5, 27017)

# Compose a sample tweet
compose_tweet("This is my first tweet using Python and MongoDB!", 27017)
