from pymongo import MongoClient, UpdateOne
import json
import threading
from time import sleep


class ConnectingToMongoDB:
    def __init__(self):
        self.uri = "mongodb+srv://myAtlasDBUser:rEqYo5tJvuYzFlI3@myatlasclusteredu.ipyk1vz.mongodb.net/?retryWrites=true&w=majority&appName=myAtlasClusterEDU"
        self.databaseName = 'TestIntegradora01'
        self.db = None
        self.client = None
        self.collection = None
        self.collectionConfig = None
        # Aquí comienza la conexión
        self.startConnection()


    def startConnection(self):
        if self.db is None:
            try:
                self.client = MongoClient(self.uri)
                self.db = self.client[self.databaseName]
                self.collection = self.db["Dispositives"]
                self.collectionConfig = self.db["Configurations"]
                return True
            except Exception as e:
                print(f"Error al conectar a la base de datos")
                return False
        return True

    def insertMany(self, documents):
        if self.startConnection() == False:
            return
        operations = []
        for doc in documents:
            sensor_id = doc.pop('id', None)
            if sensor_id is not None:
                operation = UpdateOne(
                    {"Sensors.sensorID": sensor_id},
                    {"$push": {"Sensors.$.data": doc}}
                )
                operations.append(operation)
        
        if operations:
            result = self.collection.bulk_write(operations)
            print(f"Insertados: {result.modified_count} documentos.")
        else:
            print("No se encontraron ids de sensores válidos en los documentos.")

    def findAndUpdateChanges(self, deviceIDs, saveChanges, updateConfig, serialPortInstance):
        if self.startConnection() == False:
            return False
        matching_documents = list(self.collectionConfig.find({"id": {"$in": deviceIDs}},{"_id": 0}))
        print("Documentos coincidentes:", matching_documents)
        if len(matching_documents) < 2 or (matching_documents[1]["id"] != deviceIDs[1] and matching_documents[1]["id"] != deviceIDs[0]):
            return False
        saveChanges(matching_documents, "device")
        sleep(1)
        updateConfig(serialPortInstance)
        return True

    def watchCollection(self, saveChanges, updateConfig, serialPortInstance, deviceIDs):
        pipeline = [
            { '$match': { 'fullDocument.id': { '$in': deviceIDs } } }
        ]
        with self.collectionConfig.watch(pipeline, full_document='updateLookup') as stream:
            for change in stream:
                self.findAndUpdateChanges(deviceIDs, saveChanges, updateConfig, serialPortInstance)


    def getTimeId(self, deviceID):
        with open("device.json", 'r') as file:
            data = json.load(file)
            for devices in data:
                if devices['id'] == deviceID:
                    for sensor in devices['sensors']:
                        if sensor['type'] == "RLJ":
                            return sensor['id']

    def watchTime(self, setTime, serialPortInstance, deviceID):
        with self.collection.watch([
            {'$match': {'fullDocument.DispositiveID': int(deviceID[1])}},
            {'$match': {'operationType': 'update'}}
        ], full_document='updateLookup') as stream:
            for change in stream:
                for data in change['fullDocument']['Sensors']:
                    if data['sensorID'] == self.getTimeId(int(deviceID[1])):
                        time = data['data'][data['data'].__len__()-1]['value']
                        setTime(serialPortInstance, time)
                        break

    def startWatching(self, saveChanges, updateConfig, serialPortInstance, setTime, deviceID):
        if self.startConnection() == False:
            return
        threading.Thread(target=self.watchCollection, args=(saveChanges, updateConfig, serialPortInstance,deviceID)).start()
        threading.Thread(target=self.watchTime, args=(setTime, serialPortInstance, deviceID)).start()
