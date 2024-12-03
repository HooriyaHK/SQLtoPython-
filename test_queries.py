import json
from pymongo import MongoClient
from datetime import datetime

def load_json_data(filename, port):
    """Load tweets from a JSON file into MongoDB."""
    client = MongoClient(f'mongodb://localhost:{port}/')
    db = client['291db']
    collection = db['tweets']
    
    with open(filename, 'r', encoding='utf-8') as file:
        json_data = [json.loads(line) for line in file]
        
    collection.insert_many(json_data)
    print(f"Data from {filename} loaded successfully!")

#multi join should work
def search_tweets(keywords, port):
    """Search tweets containing specific keywords."""
    client = MongoClient(f'mongodb://localhost:{port}/')
    db = client['291db']
    collection = db['tweets']

    # Support both single and multiple keyword search
    if isinstance(keywords, str):
        keywords = [keywords]

    # Build query to match all keywords
    query = {"$and": [{"content": {"$regex": keyword, "$options": "i"}} for keyword in keywords]}
    results = collection.find(query)

    for tweet in results:
        print(f"ID: {tweet.get('_id')}")
        print(f"Date: {tweet.get('date')}")
        print(f"Content: {tweet.get('content')}")
        print(f"Username: {tweet.get('username', {}).get('username', 'Unknown')}")
        print("-" * 40)

def search_users(db, keyword):
    collection = db['tweets']  # collection name // not sure if we 
                               # hardcode this so .. 

    query = {
        "$or": [
            {"user.displayname": {"$regex": keyword, "$options": "i"}},
            {"user.location": {"$regex": keyword, "$options": "i"}}
        ]
    }
    
    results = collection.find(query)
    user_list = []
    seen_users = set()  # using a set to avoid duplicates

    # getting matching users
    for result in results:
        user = result['user']
        if user['username'] not in seen_users:
            seen_users.add(user['username'])
            user_list.append({
                "username": user['username'],
                "displayname": user.get('displayname', 'N/A'),
                "location": user.get('location', 'N/A'),
                "full_info": user  #store full information for later retrieval
            })
    # print matching users
    print("\nUsers matching the keyword:")
    if user_list:
        for i, user in enumerate(user_list):
            print(f"{i + 1}. Username: {user['username']}, Displayname: {user['displayname']}, Location: {user['location']}")
        
        # viewing full information
        while True:
            try:
                choice = int(input("\nEnter the number of the user to view full information (or 0 to go back): "))
                if choice == 0:
                    print("Returning to main menu.")
                    break
                elif 1 <= choice <= len(user_list):
                    selected_user = user_list[choice - 1]
                    print("\nFull information about the selected user:")
                    for key, value in selected_user['full_info'].items():
                        print(f"{key}: {value}")
                else:
                    print("Invalid choice. Please choose a valid user number.")
            except ValueError:
                print("Invalid input. Please enter a number.")
    else:
        print("No users found.")


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
#list_top_tweets("likeCount", 5, 27017)

print("\nTop users by followersCount:")
#list_top_users(5, 27017)

# Compose a sample tweet
#compose_tweet("This is my first tweet using Python and MongoDB!", 27017)

# Search for tweets with the keyword "Farmer"
print("\nSearch keyword:")
print("\nSearch keyword (tweets):")
#search_tweets("Farmer", 27017)

# Connect to the database for user search
client = MongoClient('mongodb://localhost:27017/')
db = client['291db']

# Search for users with the keyword "John"
print("\nSearch keyword (users):")
search_users(db, "diamondhorse19")
