import json
import os
import time
import requests
from ConnectingToMongoDB import ConnectingToMongoDB
from SerialPort import SerialPort


class DataManagement:
    def __init__(self, port, baudrate):
        self.port = port
        self.baudrate = baudrate

        self.serialPortInstance = SerialPort(self.port, self.baudrate)
        self.listaJson = []

        self.loadJson()

    # Este método es el que lee lo que hay en el JSON y regresa los datos
    def readJson(self):
        with open('data.json', 'r', encoding='utf-8') as file:
            datos = json.load(file)
            return datos

    # Este método se mandará llamar para preguntar si hay datos que cargar del JSON o si el JSON se encuentra vacío
    def loadJson(self):
        if os.path.exists('data.json') and os.path.getsize('data.json') > 0:
            self.listaJson = self.readJson()
        else:
            print("No hay registros en mi JSON.")
            return []

    # Este método se va mandar llamar SIEMPRE, independientemente de si se guarda en JSON o se sube a MongoDB
    def saveJson(self):
        with open('data.json', 'w', encoding='utf-8') as file:
            json.dump(self.listaJson, file, ensure_ascii=False, indent=2)

    def verifyInternetConnection(self):
        try:
            response = requests.get('https://www.google.com', timeout=5)
            if response.status_code == 200:
                return True
            else:
                return False
        except requests.ConnectionError:
            return False

    # Este método solo se encarga de mandar los datos a MongoDB con un insertMany()
    def sendJsonToMongo(self):
        print("self.listaJson", self.listaJson)
        try:
            # print("lsitaJosn", self.listaJson)
            # print("type", type(self.listaJson))
            connection = ConnectingToMongoDB()
            connection.insertMany(self.listaJson)
            print('JSON enviado a MongoDB correctamente.')
            self.listaJson = []  # Vacíar el JSON cuando ya se subió a MongoDB
            self.saveJson()  # Guardar el JSON vacío
        except Exception as e:
            print('No se pudieron enviar los datos a MongoDB:', e)

    # Este método es el que se encarga de toda la lógica principal como cargar el JSON, agregar el objeto a la lista,
    # verificar si hay Internet y volver a guardar en el JSON
    def first(self):
        self.listaJson = self.serialPortInstance.requestData()

        # En caso de que si haya Internet y al menos se tenga un objeto mi self.listaJson
        if self.verifyInternetConnection():
            self.serialPortInstance.sendSettingsAlarms()  # CHECAR AQUÍ, PORQUE NO SE COMO SE ESTARÁ MANDANDO AL ARDUINO ----------
            if len(self.listaJson) > 0:
                self.sendJsonToMongo()
            else:
                print("No se tiene ningún dato en la lista.")
        # Si no hay Internet guardaré en mi JSON mi self.listaJson
        else:
            self.saveJson()
            print('Datos guardados en el archivo JSON porque no hay conexión a Internet.')


if __name__ == "__main__":
    port = "COM9"
    baudrate = 9600
    instancia = DataManagement(port, baudrate)
    while True:
        instancia.first()
        time.sleep(1)
