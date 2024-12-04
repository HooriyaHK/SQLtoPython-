#this should be where all our code is
import load_json
from load_json import load_json_to_mongodb
import json
from pymongo import MongoClient
from datetime import datetime

#multi join should work
def search_tweets(keywords, collection):
    # Normalize keywords to remove apostrophes and extra spaces
    normalized_keywords = [keyword.replace("'", "").strip() for keyword in keywords]

    # Build a flexible query to match hashtags and plain text, considering word boundaries
    query = {
        "$and": [
            {
                "$or": [
                    {"content": {"$regex": rf"\b{keyword}\b", "$options": "i"}},  # Exact word match with boundary
                    {"content": {"$regex": rf"\b{keyword.replace('#', '')}\b", "$options": "i"}},  # Match without hashtag
                    {"content": {"$regex": rf"{keyword}", "$options": "i"}}  # General match without boundaries
                ]
            }
            for keyword in normalized_keywords
        ]
    }

    # Execute the query
    results = collection.find(query)

    tweets = []
    seen_ids = set()  # Track seen tweet IDs to avoid duplicates

    print("\nTweets matching the keywords:")
    for i, tweet in enumerate(results):
        if tweet['id'] not in seen_ids:
            seen_ids.add(tweet['id'])
            tweets.append(tweet)
            print(f"({len(tweets)}). ID: {tweet['id']}, Date: {tweet['date']}, Content: {tweet['content']}, Username: {tweet['user']['username']}")

    if not tweets:
        print("No tweets found.")
        return

    # Display detailed tweet information
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
                    if key == "user":  # Format user details neatly
                        user_info = value
                        print("\nUser Information:")
                        print(f"  Username: {user_info.get('username', 'N/A')}")
                        print(f"  Display Name: {user_info.get('displayname', 'N/A')}")
                        print(f"  User ID: {user_info.get('id', 'N/A')}")
                        print(f"  Description: {user_info.get('description', 'N/A')}")
                        print(f"  Location: {user_info.get('location', 'N/A')}")
                        print(f"  Followers: {user_info.get('followersCount', 'N/A')}")
                        print(f"  Friends: {user_info.get('friendsCount', 'N/A')}")
                        print(f"  Verified: {'Yes' if user_info.get('verified') else 'No'}")
                        print(f"  Profile URL: {user_info.get('url', 'N/A')}")
                        print(f"  Profile Image: {user_info.get('profileImageUrl', 'N/A')}")
                        print(f"  Account Created: {user_info.get('created', 'N/A')}")
                    else:
                        print(f"{key}: {value}")
            else:
                print("Invalid selection. Please choose a valid tweet number.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def search_users(keyword, collection):
    # Define the query to match display names or locations, case-insensitively
    query = {
        "$or": [
            {"user.displayname": {"$regex": keyword, "$options": "i"}},
            {"user.location": {"$regex": keyword, "$options": "i"}}
        ]
    }
    
    results = collection.find(query)

    user_list = []
    seen_usernames = set()  # Track seen usernames to avoid duplicates

    # Gather unique users from the results
    for result in results:
        user = result['user']
        username = user['username'].lower()  # Make username case-insensitive
        if username not in seen_usernames:
            seen_usernames.add(username)
            user_list.append({
                "username": user['username'],
                "displayname": user.get('displayname', 'N/A'),
                "location": user.get('location', 'N/A'),
                "full_info": user  # Store full user information for detailed view
            })

    # Sort user list by the length of the display name
    user_list.sort(key=lambda x: len(x['displayname'].strip()))

    # Display matching users
    print("\nUsers matching the keyword (sorted by display name length):")
    if user_list:
        for i, user in enumerate(user_list):
            print(f"{i + 1}. Username: {user['username']}, Displayname: {user['displayname']}, Location: {user['location']}")

        # Allow user to view full details of a selected user
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

def list_top_tweets(field_choice, n, collection):
    """List top N tweets sorted by a specified field (retweetCount, likeCount, quoteCount)."""

    # Map field choices to MongoDB fields
    field_mapping = {
        "1": "retweetCount",
        "2": "likeCount",
        "3": "quoteCount"
    }

    # Validate field choice
    field = field_mapping.get(field_choice)
    if not field:
        print("Invalid field choice. Please choose 1 for Retweet Count, 2 for Like Count, or 3 for Quote Count.")
        return

    # Validate `n` is an integer
    try:
        n = int(n)
        if n <= 0:
            print("Please enter a positive number for the number of tweets.")
            return
    except ValueError:
        print("The number of tweets must be an integer.")
        return

    # Query and sort in descending order by the chosen field
    tweets = collection.find(
        {},  # Query all tweets
        {"_id": 0, "id": 1, "date": 1, "content": 1, "user.username": 1, field: {"$ifNull": [f"${field}", 0]}}  # Include field even if missing
    ).sort(field, -1).limit(n)

    tweet_list = list(tweets)  # Convert cursor to list

    print(f"\nTop {n} tweets sorted by {field}:")
    if not tweet_list:
        print("No tweets found.")
        return

    # Display the top tweets
    for i, tweet in enumerate(tweet_list, start=1):
        # Safely access fields using .get() to avoid KeyErrors
        tweet_id = tweet.get("id", "N/A")
        date = tweet.get("date", "N/A")
        content = tweet.get("content", "N/A")
        username = tweet.get("user", {}).get("username", "N/A")

        print(f"{i}. ID: {tweet_id}, Date: {date}, Content: {content}, Username: {username}")

    # Allow user to view full details of a selected tweet
    while True:
        try:
            selection = int(input("\nEnter the number of the tweet to view full information (or 0 to go back): "))
            if selection == 0:
                print("Returning to main menu.")
                break
            elif 1 <= selection <= len(tweet_list):
                selected_tweet = tweet_list[selection - 1]
                print("\nFull information about the selected tweet:")
                for key, value in selected_tweet.items():
                    print(f"{key}: {value}")
            else:
                print("Invalid selection. Please choose a valid tweet number.")
        except ValueError:
            print("Invalid input. Please enter a number.")


def list_top_users(n, collection):
    """List top N users by followersCount."""
    try:
        # Ensure `n` is a valid positive integer
        n = int(n)
        if n <= 0:
            print("Please enter a positive number for the number of users.")
            return
    except ValueError:
        print("The number of users must be an integer.")
        return

    # Aggregate to group by username, take the max followersCount, and get displayname
    users = collection.aggregate([
        {
            "$group": {
                "_id": "$user.username",
                "username": {"$first": "$user.username"},
                "displayname": {"$first": "$user.displayname"},
                "followersCount": {"$max": "$user.followersCount"},
                "full_info": {"$first": "$user"},  # Save full user info for later
            }
        },
        {"$sort": {"followersCount": -1}},  # Sort by followersCount descending
        {"$limit": n}  # Limit to top N users
    ])

    user_list = list(users)  # Convert aggregation cursor to list
    print(f"\nTop {n} users sorted by followersCount:")
    if not user_list:
        print("No users found.")
        return

    # Display users in a list
    for i, user in enumerate(user_list, start=1):
        username = user.get("username", "N/A")
        displayname = user.get("displayname", "N/A")
        followers_count = user.get("followersCount", "N/A")
        print(f"{i}. Username: {username}, Displayname: {displayname}, FollowersCount: {followers_count}")

    # Allow selection to view full details of a user
    while True:
        try:
            selection = int(input("\nEnter the number of the user to view full information (or 0 to go back): "))
            if selection == 0:
                print("Returning to main menu.")
                break
            elif 1 <= selection <= len(user_list):
                selected_user = user_list[selection - 1]["full_info"]
                print("\nFull information about the selected user:")
                for key, value in selected_user.items():
                    print(f"{key}: {value}")
            else:
                print("Invalid choice. Please choose a valid user number.")
        except ValueError:
            print("Invalid input. Please enter a number.")


from datetime import datetime

def compose_tweet(content, collection):
    """
    Compose a new tweet and insert it into MongoDB.
    Args:
        content (str): The content of the tweet.
        collection: MongoDB collection instance.
    """
    # Validate content
    if not content or not isinstance(content, str):
        print("Tweet content cannot be empty and must be a string.")
        return

    # Create the tweet document
    tweet = {
        "content": content.strip(),  # Remove leading/trailing spaces
        "username": "291user",
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # Include time for better granularity
        "retweetCount": None,
        "likeCount": None,
        "quoteCount": None,
        "followersCount": None
    }

    try:
        # Insert tweet into the database
        result = collection.insert_one(tweet)
        print(f"Tweet successfully inserted with ID: {result.inserted_id}")
    except Exception as e:
        print(f"An error occurred while inserting the tweet: {e}")


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
            search_users(keyword, collection)
        elif choice == "3":
            n = input("How many tweets do you want to rank? ")
            print("1. Rank by Retweet Count")
            print("2. Rank by Like Count")
            print("3. Rank by Quote Count")
            field_choice = input("How do you want the tweets to be ranked? ")
            list_top_tweets(field_choice, n, collection)
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

        

    