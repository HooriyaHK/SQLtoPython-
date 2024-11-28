from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['291db']
tweets = db['tweets']

tweets.insert_many([
    {
        "_id": 1,
        "content": "Learning MongoDB is fun!",
        "username": "user1",
        "date": "2024-11-28",
        "retweetCount": 10,
        "likeCount": 25,
        "quoteCount": 5,
        "followersCount": 100  
    },
    {
        "_id": 2,
        "content": "Working on the CMPUT 291 project.",
        "username": "user2",
        "date": "2024-11-27",
        "retweetCount": 15,
        "likeCount": 30,
        "quoteCount": 8,
        "followersCount": 200  
    }
])
