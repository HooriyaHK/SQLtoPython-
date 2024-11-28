from pymongo import MongoClient

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

