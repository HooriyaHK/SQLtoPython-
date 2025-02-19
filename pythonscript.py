import json
from datetime import datetime

# Load JSON data
def load_data(filename):
    with open(filename, 'r') as file:
        return json.load(file)

# Query 1: Search tweets
def search_tweets(data, query):
    query_terms = query.get("terms", [])
    results = []
    for tweet in data['tweets']:
        content = tweet['content'].lower()
        if all(term.lower() in content for term in query_terms):
            results.append({
                "id": tweet['id'],
                "date": tweet['date'],
                "content": tweet['content'],
                "username": tweet['user']['username']
            })
    return sorted(results, key=lambda x: x['date'])

# Query 2: Search users
def search_users(data, query):
    search_term = query.get("term", "").lower()
    results = []
    for user in data['users']:
        if search_term in user['displayname'].lower() or search_term in user['location'].lower():
            results.append({
                "username": user['username'],
                "displayname": user['displayname'],
                "location": user['location']
            })
    # Remove duplicates
    unique_results = {f"{user['username']}": user for user in results}
    return sorted(unique_results.values(), key=lambda x: len(x['displayname']))

# Query 3: List top tweets
def list_top_tweets(data, query):
    criteria = query['criteria']
    count = query['count']
    sorted_tweets = sorted(
        data['tweets'],
        key=lambda x: x.get(criteria, 0),
        reverse=True
    )
    results = [{
        "id": tweet['id'],
        "date": tweet['date'],
        "content": tweet['content'],
        "username": tweet['user']['username']
    } for tweet in sorted_tweets[:count]]
    return results

# Query 4: List top users
def list_top_users(data, query):
    count = query['count']
    sorted_users = sorted(
        data['users'],
        key=lambda x: x['followersCount'],
        reverse=True
    )
    results = [{
        "username": user['username'],
        "displayname": user['displayname'],
        "followersCount": user['followersCount']
    } for user in sorted_users[:count]]
    return results

# Query 5: Compose tweet
def compose_tweet(data, query):
    new_tweet = {
        "id": max(tweet['id'] for tweet in data['tweets']) + 1,
        "date": datetime.utcnow().isoformat() + "Z",
        "content": query['content'],
        "user": {
            "username": "291user",
        },
        "retweetCount": 0,
        "likeCount": 0,
        "quoteCount": 0
    }
    data['tweets'].append(new_tweet)
    return new_tweet

# Run test cases
def run_tests():
    # Load data
    data = load_data('data.json')
    tests = load_data('queries_test.json')
    
    results = []

    for test in tests:
        query_type = test['type']
        query_input = test['query']
        expected_output = test['expected_output']

        if query_type == "search_tweets":
            output = search_tweets(data, query_input)
        elif query_type == "search_users":
            output = search_users(data, query_input)
        elif query_type == "list_top_tweets":
            output = list_top_tweets(data, query_input)
        elif query_type == "list_top_users":
            output = list_top_users(data, query_input)
        elif query_type == "compose_tweet":
            output = compose_tweet(data, query_input)
        else:
            output = None

        results.append({
            "test_name": test['name'],
            "passed": output == expected_output,
            "output": output,
            "expected": expected_output
        })

    # Print results
    for result in results:
        print(f"Test: {result['test_name']}")
        print(f"Passed: {result['passed']}")
        if not result['passed']:
            print(f"Output: {result['output']}")
            print(f"Expected: {result['expected']}")
        print('-' * 50)

# Entry point
if __name__ == "__main__":
    run_tests()
