# CS411-Project
CAS CS411 Final Project

PyMongo - official Python driver for MongoDB
  - Documentation: https://api.mongodb.com/python/current/
  
Create client: 
  - client = MongoClient()
  
Access Database 'db': 
  - database = client.db

Get collection 'cl':
  - collection = database.cl
  
Documents = python dictionaries

Insert Document:
  - collection.insert_one()
  
Get single document:
  - collection.find_one()
    - get first document in collection
  - collection.find_one(key:value)
    - find document with matching key:value pair
    
Insert multiple documents:
  - insert_many(list)
  
Find many:
  - collection.find()
    - returns iterable of matching documents
