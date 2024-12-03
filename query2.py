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
                "full_info": user  # Store full information for later retrieval
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
