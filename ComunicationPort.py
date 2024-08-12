import datetime
import serial
import time
import json

class ComunicationPort():
    def __init__(self,type):
        self.lista = []
        self.activo = False
        self.type=type
        self.activar = False

    # ENVÍAR DATOS
    def sendString(self, message):
        return

    # LEER DATOS
    def readDevicesData(self):
        return

    def parseData(self):
        
        parsed_data = []
        
        print("enviado a parsear: ")
        print(self.lista)
        for line in self.lista:
            try:
                sensorData = line.split(":")

                identifier = sensorData[0].strip()
                value = sensorData[2].strip()
                id = int(sensorData[1].strip())
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                if(identifier == "RLJ"):
                    value =  sensorData[2].strip()+":"+sensorData[3].strip()
                parsed_data.append({
                    'identifier': identifier,
                    'value': value,
                    'id': id,
                    'timestamp': timestamp
                })
                
                self.lista = []
            except Exception as e:
                print(f"Error al parsear los datos del puerto serial: {e}")
        
        self.lista = []
        return parsed_data

    def requestData(self):
        with open('device.json', 'r') as archivo:
            configuraciones = json.load(archivo)
            for dispositivo in configuraciones:
                if dispositivo['type'] == self.type:
                    for sensor in dispositivo['sensors']:
                        self.sendString("REA:"+str(sensor['id']))
        time.sleep(1) 
        self.readDevicesData()
        return self.parseData()
