from pymongo import MongoClient


class ConnectingToMongoDB:
    def __init__(self):
        self.uri = "mongodb+srv://myAtlasDBUser:rEqYo5tJvuYzFlI3@myatlasclusteredu.ipyk1vz.mongodb.net/?retryWrites=true&w=majority&appName=myAtlasClusterEDU"
        self.databaseName = 'TestIntegradora01'
        self.collectionName = "Dispositives"
        # Aquí comienza la conexión
        self.client = MongoClient(self.uri)
        self.db = self.client[self.databaseName]
        self.collection = self.db[self.collectionName]

    def insertMany(self, documents):
        self.collection.insert_many(documents)
