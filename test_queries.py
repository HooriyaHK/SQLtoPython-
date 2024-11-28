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


#QUERY FOR SEARCHING TWEETS:
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

##search_tweets(["farmers", "protest"], 61448)

def select_tweet_by_id(tweet_id):
    query = {"id": tweet_id}
    return collection.find_one(query)


#QUERY FOR SEARCHING USERS
def search_users(keyword, port):
    client = MongoClient(f'mongodb://localhost:{port}/')
    db = client['291db']
    collection = db['tweets']

    query = {"$or": [
        {"user.location": {"$regex": keyword, "$options": "i"}}
    ]}
    results = collection.find(query)

    # avoding duplicates
    seen_users = set()
    user_list = []
    for tweet in results:
        user = tweet['user']
        if user['username'] not in seen_users:
            seen_users.add(user['username'])
            user_list.append(user)
            print(f"Username: {user['username']}")
            print(f"Displayname: {user['displayname']}")
            print(f"Location: {user['location']}")
            print("-" * 40)

    # let the user to select a specific user for full details
    if user_list:
        selected_username = input("Enter the username to view full details: ").strip()
        for user in user_list:
            if user['username'] == selected_username:
                print("Full User Details:")
                for key, value in user.items():
                    print(f"{key}: {value}")
                break
        else:
            print("Username not found in the search results.")
    else:
        print("No matching users found.")

##search_users("Punjab", 61448)




