import pymongo
from pymongo import MongoClient

def connect_to_db(port):
    """Connect to MongoDB and return the database instance."""
    try:
        client = pymongo.MongoClient(f"mongodb://localhost:{port}")
        db = client["291db"]  # Replace with the correct database name
        print(f"Connected to MongoDB on port {port}.")
        return db
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return None

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

def main():
    port = input("Enter the port number where MongoDB is running: ").strip()
    
    # Connect to database
    db = connect_to_db(port)
    if db is None:  # Corrected check
        print("Failed to connect to the database. Exiting.")
        return
    
    # Main menu
    while True:
        print("\nSelect an operation:")
        print("1. Search for users")
        print("2. Exit")
        
        choice = input("Enter your choice: ").strip()
        
        if choice == "1":
            keyword = input("Enter keyword: ").strip()
            search_users(db, keyword)
        elif choice == "2":
            print("Exiting program.")
            break
        else:
            print("Invalid choice. Please select again.")

if __name__ == "__main__":
    main()
