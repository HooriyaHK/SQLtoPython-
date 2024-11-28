import json
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['291db']
tweets = db['tweets']

# Load the JSON file
with open('10.json', 'r', encoding='utf-8') as file:
    json_data = [json.loads(line) for line in file]

# Insert data into MongoDB
tweets.insert_many(json_data)

print("Data loaded successfully!")
