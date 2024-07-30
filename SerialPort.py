import datetime
import serial
import time
import json
from ComunicationPort import ComunicationPort

# Nos indica si el puerto serial se encuentra abierto o cerrado
port_opened = False

class SerialPort(ComunicationPort):
    def __init__(self, port, baudrate, type):
        super().__init__(type)
        self.port = port
        self.baudrate = baudrate
        self.serialPort = None 
        self.open_port()  

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
        except Exception as e:
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
    def sendString(self, message):
        try:
            message = message + "\n"
            self.serialPort.write(message.encode())
        except Exception as e:
            print("Error en el envío de datos al puerto serial:", e)

    # LEER DATOS
    def readDevicesData(self):
        try:
            while self.serialPort.in_waiting > 0:
                line = self.serialPort.readline().decode().strip()
                if line:
                    self.lista.append(line)
            
        except Exception as e:
            print("Error en la lectura del puerto serial:", e)
            return None
