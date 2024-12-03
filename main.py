#this should be where all our code is
import load_json
from load_json import load_json_to_mongodb
import json
from pymongo import MongoClient
from datetime import datetime

#multi join should work
def search_tweets(keywords, collection):
    """Search tweets containing specific keywords."""
    # Support both single and multiple keyword search
    if isinstance(keywords, str):
        keywords = [keywords]
    # Build query to match all keywords
    query = {"$and": [{"content": {"$regex": keyword, "$options": "i"}} for keyword in keywords]}
    results = collection.find(query)
    # getting matching tweets
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


def list_top_tweets(field, n, collection):
    """List top N tweets sorted by a specific field."""
    
    tweets = collection.find({}, {"_id": 1, "date": 1, "content": 1, "username": 1}) \
                       .sort(field, -1).limit(n)
    
    for tweet in tweets:
        print(tweet)

def list_top_users(n):
    """List top N users by followersCount."""
    
    users = collection.aggregate([
        {"$group": {"_id": "$username", "displayname": {"$first": "$username"}, 
                    "followersCount": {"$max": "$followersCount"}}},
        {"$sort": {"followersCount": -1}},
        {"$limit": n}
    ])
    
    for user in users:
        print(user)

def compose_tweet(content, collection):
    """Compose a new tweet and insert into MongoDB."""
   
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

 

if __name__ == "__main__":
     port = input("Enter MongoDB port number: ")
     file = input("Enter JSON file name: ")
     db = load_json_to_mongodb(file, port)
     while True:
        print("\nMain Menu")
        print("1. Search for tweets")
        print("2. Search for users")
        print("3. List top tweets")
        print("4. List top users")
        print("5. Compose a tweet")
        print("6. Exit")
        choice = input("Enter your choice: ")
    