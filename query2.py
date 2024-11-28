import pymongo
from pymongo import MongoClient

def search_users(db, keyword):
    """Search for users based on a keyword."""
    collection = db['tweets']  # Change to your collection name
    
    query = {"$or": [
        {"user.displayname": {"$regex": keyword, "$options": "i"}},
        {"user.location": {"$regex": keyword, "$options": "i"}}
    ]}
    
    results = collection.find(query)
    user_list = []
    seen_users = []

    for result in results:
        user = result['user']
        if user['username'] not in seen_users:
            seen_users.append(user['username'])
            user_list.append({
                "username": user['username'],
                "displayname": user['displayname'],
                "location": user.get('location', 'N/A')
            })

    print("\nUsers matching the keyword:")
    if user_list:
        for user in user_list:
            print(f"Username: {user['username']}, Displayname: {user['displayname']}, Location: {user['location']}")
    else:
        print("No users found.")
