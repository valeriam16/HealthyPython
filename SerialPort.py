import datetime
import serial
import time
import json

# Nos indica si el puerto serial se encuentra abierto o cerrado
port_opened = False


class SerialPort:
    def __init__(self, port, baudrate):
        self.port = port
        self.baudrate = baudrate
        self.serialPort = None  # Instancia para abrir y cerrar el puerto seial
        self.open_port()  # Abrir el puerto
        self.lista = []

    # MANEJO DE PUERTO
    def open_port(self):
        global port_opened
        # Pregunta si el puerto serial se encuentra abierto y en caso de que si, ya solo imprime un msj
        if port_opened:
            print(f"El puerto {self.port} ya está abierto.")
            return
        try:
            print("Conectando puerto ", self.port)
            self.serialPort = serial.Serial(self.port, self.baudrate)
            print("Conectado, puerto: ", self.port)
            port_opened = True
        except serial.SerialException as e:
            print(f"Error al conectar al puerto {self.port}: {e}")
            port_opened = False
        print("¿Está abierto?: ", port_opened)

    def closePort(self):
        global port_opened
        if self.serialPort:
            self.serialPort.close()
        print(f"Puerto {self.port} cerrado.")
        port_opened = False

    # ENVÍAR DATOS
    def sendSerialString(self, message):
        try:
            message = message + "\n"
            self.serialPort.write(message.encode())
        except serial.SerialException as e:
            print("Error en el envío de datos al puerto serial:", e)

    # LEER DATOS
    def readDevicesData(self):
        try:
            self.lista = []
            while self.serialPort.in_waiting > 0:
                line = self.serialPort.readline().decode().strip()
                if line:
                    self.lista.append(line)
            
            self.lista.append("RLJ:44"+":"+datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
        except UnicodeDecodeError as e:
            print("Error en la lectura del puerto serial:", e)
            return None

    def parseData(self):
        parsed_data = []
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
            except Exception as e:
                print(f"Error al parsear los datos del puerto serial: {e}")

        return parsed_data

    def requestData(self):
        with open('device.json', 'r') as archivo:
            configuraciones = json.load(archivo)
            for dispositivo in configuraciones:
                if dispositivo['type'] == "BRZ":
                    for sensor in dispositivo['sensors']:
                        self.sendSerialString("REA:"+str(sensor['id']))
                # elif dispositivo['type'] == "PSA":
                #     for sensor in dispositivo['sensors']:
                #         self.sendSerialString("REA:"+str(sensor['id']))
        time.sleep(6) 
        self.readDevicesData()
        # print("Esto es lo que me retorna el método parseData()", self.parseData())
        return self.parseData()

    # def impresion(self):
    #     print("Ingresa 'salir' para cerrar el puerto COM.")
    #     try:
    #         opcion = input("Ingresa id de sensor: ")
    #         if opcion == 'salir':
    #             print("Cerrando puerto COM.")
    #             self.closePort()
    #             print("Saliendo del programa... ¡Nos vemos!")
    #             exit()
    #     except ValueError:
    #         print("Entrada no válida. Por favor, ingrese un número.")
    #         return None
    #     return opcion

