import serial
from ComunicationPort import ComunicationPort

# Nos indica si el puerto serial se encuentra abierto o cerrado

class SerialPort(ComunicationPort):
    def __init__(self, port, baudrate, type):
        super().__init__(type)
        self.port = port
        self.baudrate = baudrate
        self.serialPort = None 
        self.open_port()  

    # MANEJO DE PUERTO
    def open_port(self):
        self.activo = False
        # Pregunta si el puerto serial se encuentra abierto y en caso de que si, ya solo imprime un msj
        for port in self.port:
            try:
                print("Conectando puerto ", port)
                self.serialPort = serial.Serial(port, self.baudrate)
                print("Conectado, puerto: ", port)
                self.activo = True
                self.activar = True
            except Exception as e:
                print(f"Error al conectar al puerto {port}: {e}")
                self.activo = False
            print("¿Está abierto?: ", self.activo)
            if self.activo == True: 
                return

    def closePort(self):
        if self.serialPort:
            self.serialPort.close()
        print(f"Puerto {self.port} cerrado.")
        self.activo = False

    # ENVÍAR DATOS
    def sendString(self, message):
        if self.activo == True:
            try:
                message = message + "\n"
                self.serialPort.write(message.encode())
            except Exception as e:
                print("Error en el envío de datos al puerto serial:", e)
                self.open_port()
                return

    # LEER DATOS
    def readDevicesData(self):
        if self.activo != False:
            try:
                while self.serialPort.in_waiting > 0:
                    line = self.serialPort.readline().decode().strip()
                    if line:
                        self.lista.append(line)
                
            except Exception as e:
                print("Error en la lectura del puerto serial:", e)
                self.open_port()
                return None
        else:
            self.open_port()
