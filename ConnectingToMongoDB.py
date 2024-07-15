from pymongo import MongoClient


class ConnectingToMongoDB:
    def __init__(self):
        self.uri = "mongodb+srv://admin:valeria1611@myatlasclusteredu.njl6yr2.mongodb.net/?retryWrites=true&w=majority"
        self.databaseName = 'integradora'
        self.collectionName = "historial"
        # Aquí comienza la conexión
        self.client = MongoClient(self.uri)
        self.db = self.client[self.databaseName]
        self.collection = self.db[self.collectionName]

    def insertMany(self, documents):
        self.collection.insert_many(documents)
