#this should be where all our code is
import load_json
from load_json import load_json_to_mongodb
import json
from pymongo import MongoClient
from datetime import datetime

#multi join should work
def search_tweets(db, keywords):
    collection = db['tweets']
    
    query = {"$and": [{"content": {"$regex": rf"\b{keyword}\b", "$options": "i"}} for keyword in keywords]} 
    
    results = collection.find(query)

    tweets = []
    seen_ids = set()  # tracking seen tweet IDs avoid duplicates

    print("\nTweets matching the keywords:")
    for i, tweet in enumerate(results):
        if tweet['id'] not in seen_ids: 
            seen_ids.add(tweet['id'])
            tweets.append(tweet)
            print(f"({len(tweets)}). ID: {tweet['id']}, Date: {tweet['date']}, Content: {tweet['content']}, Username: {tweet['user']['username']}")
    if not tweets:
        print("No tweets found.")
        return

    while True:
        try:
            selection = int(input("\nEnter the number of the tweet to view full information (or 0 to go back): "))
            if selection == 0:
                print("Returning to main menu.")
                break
            elif 1 <= selection <= len(tweets):
                selected_tweet = tweets[selection - 1]
                print("\nFull information about the selected tweet:")
                for key, value in selected_tweet.items(): #printing everything
                    print(f"{key}: {value}")
            else:
                print("Invalid selection. Please choose a valid tweet number.")
        except ValueError:
            print("Invalid input. Please enter a number.")


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

def list_top_users(n, collection):
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
     collection = load_json_to_mongodb(file, port)
     while True:
        print("\nMain Menu")
        print("1. Search for tweets")
        print("2. Search for users")
        print("3. List top tweets")
        print("4. List top users")
        print("5. Compose a tweet")
        print("6. Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            keywords = input("Enter keywords to search tweets: ").split()
            search_tweets(keywords, collection)
        elif choice == "2":
            keyword = input("Enter user name to search users: ")
            search_users(collection, keyword)
        elif choice == "3":
            n = input("How many tweets do you want to rank? ")
            print("1. Rank by Retweet Count")
            print("2. Rank by Like Count")
            print("3. Rank by Quote Count")
            field = input("How do you want the tweets to be ranked? ")
            list_top_tweets(field, n, collection)
        elif choice == "4":
            n = input("How many users would you like to list?: ")
            list_top_users(n, collection)
        elif choice == "5":
            content = input("Enter the tweet you would like to compose: ")
            compose_tweet(content, collection)
        elif choice == "6":
            print("Goodbye! :)")
            break


        else:
            print("invalid choice")

        

    