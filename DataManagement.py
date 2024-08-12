import json
import os
import time
import requests
from ConnectingToMongoDB import ConnectingToMongoDB
from SerialPort import SerialPort
from BluetoothPort import BluetoothPort
import threading
import serial
from time import sleep


class DataManagement:
    def __init__(self, port, baudrate):
        self.port = port
        self.baudrate = baudrate
        self.serialPortInstance = SerialPort(self.port, self.baudrate, "PSA")
        self.bluetoothPortInstance = BluetoothPort("BRZ")
        self.connectionBrz = ConnectingToMongoDB(self.bluetoothPortInstance)
        self.connectionPsa = ConnectingToMongoDB(self.serialPortInstance)

        self.listaJson = []
        self.time = ""
        self.deviceID = self.leer_configuracion()

        self.loadJson()
        self.verifyConfig(self.connectionBrz)
        self.verifyConfig(self.connectionPsa)

    def verifyConfig(self,connection):
        if self.verifyInternetConnection() == True:
            if connection.findAndUpdateChanges(self.deviceID, self.saveJson, self.updateConfig) == False:
                print("No se encontró un registro de este dispositivo.")
                connection.sender.sendString("DES:"+str(self.deviceID[0])+":"+str(self.deviceID[1]))
                sleep(10)
                self.verifyConfig()
                return
            else:
                print("Configuración actualizada correctamente.")
                connection.startWatching(self.saveJson, self.updateConfig, self.setTime, self.deviceID)
                return
        else:
            print("No hay conexión a Internet.")
            if self.updateConfig(connection.sender) == False:
                print("El dispositivo no ha sido registrado. Conectate a internet para obtener la configuración.")
                connection.sender.sendString("DES:0:0")
                sleep(10)
                self.verifyConfig()
                return
                
    def leer_configuracion(self):
        archivo_config = 'config.json'
        try:
            with open(archivo_config, 'r') as archivo:
                configuracion = json.load(archivo)
                return configuracion.get('dispositives', [])
        except IOError as e:
            print(f"Error al abrir el archivo JSON: {e}")
            return []
    # Este método es el que lee lo que hay en el JSON y regresa los datos
    def readJson(self):
        with open('data.json', 'r', encoding='utf-8') as file:
            datos = json.load(file)
            return datos

    # Este método se mandará llamar para preguntar si hay datos que cargar del JSON o si el JSON se encuentra vacío
    def loadJson(self):
        if os.path.exists('data.json') and os.path.getsize('data.json') > 0:
            self.listaJson = self.readJson()
            self.sendJsonToMongo()
        else:
            print("No hay registros en mi JSON.")
            return []



    # Este método se va mandar llamar SIEMPRE, independientemente de si se guarda en JSON o se sube a MongoDB
    def saveJson(self,jsonObject,jsonFile):
        with open(jsonFile+'.json', 'w', encoding='utf-8') as file:
            json.dump(jsonObject, file, ensure_ascii=False, indent=2)

    def verifyInternetConnection(self):
        try:
            response = requests.get('https://www.google.com', timeout=5)
            if response.status_code == 200:
                return True
            else:
                return False
        except Exception as e:
            return False

    # Este método solo se encarga de mandar los datos a MongoDB con un insertMany()
    def sendJsonToMongo(self):
        if len(self.listaJson) <= 0:
            return
        try:
            # print("lsitaJosn", self.listaJson)
            # print("type", type(self.listaJson))
            self.connectionBrz.insertMany(self.listaJson)
            print('JSON enviado a MongoDB correctamente.')
            self.listaJson = []  # Vacíar el JSON cuando ya se subió a MongoDB
            self.saveJson(self.listaJson,"data")  # Guardar el JSON vacío
        except Exception as e:
            print('No se pudieron enviar los datos a MongoDB:', e)

    # Este método es el que se encarga de toda la lógica principal como cargar el JSON, agregar el objeto a la lista,
    # verificar si hay Internet y volver a guardar en el JSON
    def first(self):

        
        if self.serialPortInstance.activar == True:
            self.verifyConfig(self.connectionPsa)
            self.serialPortInstance.activar = False
        elif self.bluetoothPortInstance.activar==True:
            self.verifyConfig(self.connectionBrz)
            self.bluetoothPortInstance.activar = False

        self.listaJson = []
        self.listaJson.extend(self.serialPortInstance.requestData())  
        self.enviarHora(self.listaJson)
        self.listaJson.extend(self.bluetoothPortInstance.requestData())  

        with open("data.json", 'r') as file:
            data = json.load(file)
            self.listaJson.extend(data)

        if self.verifyInternetConnection():
            
            self.sendJsonToMongo()
        else:
            self.saveJson(self.listaJson,"data")
            print('Datos guardados en el archivo JSON porque no hay conexión a Internet.')
                    
    def updateConfig(self,sender):
        try:
            with open('device.json', 'r') as archivo:
                configuraciones = json.load(archivo)
                if len(configuraciones) == 0:
                    print("No hay dispositivos en el archivo JSON.")
                    return False
        except IOError as e:
            print(f"Error al abrir el archivo JSON: {e}")
            return False

        for dispositivo in configuraciones:
            if dispositivo['type'] == sender.type:
                for sensor in dispositivo['sensors']:
                    mensaje_sensor = f"NEW:{sensor['type']}:{sensor['id']}"
                    sender.sendString(mensaje_sensor) 

                for configuracion in dispositivo['configurations']:
                    mensaje_config = f"UPA:{configuracion['type']}:{configuracion['value']}"
                    sender.sendString(mensaje_config)
                    
        return True
    
    def enviarHora(self, array):
        for item in array:
            if item["identifier"] == "RLJ":
                self.setTime(self.bluetoothPortInstance,item["value"])
                return

    def setTime(self, sender, time):
        print("Enviando hora al dispositivo..."+time)
        sender.sendString("RLJ:"+time)

if __name__ == "__main__":
    sleep(40)
    port = ["/dev/ttyUSB0","/dev/ttyUSB1"]
    baudrate = 9600
    instancia = DataManagement(port, baudrate)
    while True:
        instancia.first()