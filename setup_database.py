import pymongo

myclient = pymongo.MongoClient("mongodb://localhost:27017/") # Crearea unui obiect MongoClient și conectarea la serverul MongoDB
mydb = myclient["mydatabase"] # Crearea sau accesarea bazei de date
mycol = mydb["user_details"] # Crearea sau accesarea colecției user_details în cadrul bazei de date