import pymongo
from pymongo import MongoClient

def connect_to_db(port):
    """Connect to MongoDB and return the database instance."""
    try:
        client = MongoClient(f"mongodb://localhost:{port}")
        db = client["291db"]
        print(f"Connected to MongoDB on port {port}.")
        return db
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return None

def search_tweets(db, keywords):
    """Search for tweets based on keywords (AND semantics)."""
    collection = db['tweets']
    
    # Build the query for AND semantics
    query = {"$and": [{"content": {"$regex": keyword, "$options": "i"}} for keyword in keywords]}
    print(f"Constructed Query: {query}")  # Debug: Print the query being executed
    
    results = collection.find(query)

    tweets = []
    seen_ids = set()  # To keep track of seen tweet IDs and avoid duplicates
    print("\nTweets matching the keywords:")
    for tweet in results:
        if tweet['id'] not in seen_ids:
            seen_ids.add(tweet['id'])  # Mark this ID as seen
            print(f"ID: {tweet['id']}, Date: {tweet['date']}, Content: {tweet['content']}, Username: {tweet['user']['username']}")
            tweets.append(tweet)

    if not tweets:
        print("No tweets found.")
        return

    # Allow user to select a tweet to view full details
    while True:
        try:
            selection = int(input("\nEnter the number of the tweet to view full information (or 0 to go back): "))
            if selection == 0:
                print("Returning to main menu.")
                break
            elif 1 <= selection <= len(tweets):
                selected_tweet = tweets[selection - 1]
                print("\nFull information about the selected tweet:")
                for key, value in selected_tweet.items():
                    print(f"{key}: {value}")
            else:
                print("Invalid selection. Please choose a valid tweet number.")
        except ValueError:
            print("Invalid input. Please enter a number.")




def main():
    port = input("Enter the port number where MongoDB is running: ").strip()
    
    # Connect to database
    db = connect_to_db(port)
    if db is None:
        print("Failed to connect to the database. Exiting.")
        return

    # Main menu
    while True:
        print("\nSelect an operation:")
        print("1. Search for tweets by keywords")
        print("2. Exit")
        
        choice = input("Enter your choice: ").strip()
        
        if choice == "1":
            keywords = input("Enter keywords (comma-separated): ").strip().split(',')
            search_tweets(db, [kw.strip() for kw in keywords])
        elif choice == "2":
            print("Exiting program.")
            break
        else:
            print("Invalid choice. Please select again.")

main()