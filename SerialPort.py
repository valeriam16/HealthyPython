import datetime
import serial
import time
from ApiRequest import ApiRequest

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
    def sendRequest(self, char):
        try:
            self.serialPort.write(char.encode())
        except serial.SerialException as e:
            print("Error en el envío de datos al puerto serial:", e)

    # LEER DATOS
    def readSerialPort(self):
        try:
            self.lista = []
            while self.serialPort.in_waiting > 0:
                line = self.serialPort.readline().decode().strip()
                if line:
                    self.lista.append(line)
        except serial.SerialException as e:
            print("Error en la lectura del puerto serial:", e)
            return None

    def parseData(self):
        parsed_data = []
        for line in self.lista:
            try:
                sensorData = line.split(":")
                if len(sensorData) < 3:
                    print(f"Dato en formato incorrecto: {line}")
                    continue

                identifier = sensorData[0].strip()
                number = "1"
                value = sensorData[1].strip()
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                parsed_data.append({
                    'Identifier': identifier,
                    'Number': number,
                    'Value': value,
                    'Timestamp': timestamp
                })
            except Exception as e:
                print(f"Error al parsear los datos del puerto serial: {e}")

        return parsed_data

    def request(self, char):
        self.sendRequest(char)
        time.sleep(0.1)  # Esperar un poco para recibir respuesta
        self.readSerialPort()
        print("Esto es lo que me retorna el método parseData()", self.parseData())
        return self.parseData()

    def impresion(self):
        print("Seleccione un número según los datos que necesita obtener: ")
        print("1. Temperatura")
        print("2. Ritmo cardiaco")
        print("3. Alcohol")
        print("4. Peso")
        print("5. Tiempo")
        print("6. Distancia")  # Flotante
        print("7. Pasos")  # Entero
        print("8. Requiero todo")
        print("9. Salir")
        try:
            opcion = int(input("Opción: "))
        except ValueError:
            print("Entrada no válida. Por favor, ingrese un número.")
            return None
        return opcion

    # Método general para solicitar datos y procesarlos
    def requestData(self):
        opcion = self.impresion()
        if opcion == 1:
            return self.request('TMP')
        elif opcion == 2:
            return self.request('RTC')
        elif opcion == 3:
            return self.request('ALC')
        elif opcion == 4:
            return self.request('P')
        elif opcion == 5:
            return self.request('M')
        elif opcion == 6:
            return self.request('DST')
        elif opcion == 7:
            return self.request('PSS')
        elif opcion == 8:
            return self.request('TDO')
        elif opcion == 9:
            print("Cerrando puerto COM.")
            self.closePort()
            print("Saliendo del programa... ¡Nos vemos!")
            exit()
        else:
            print("Tipo de dato no válido.")
            return None

    # Recibir configuración de alarmas de la API y mandar al Arduino --------- CHECAR CON LA API, PORQUE NO SE CUAL ES EL RESPONSE
    # def sendSettingsAlarms(self):
    #     try:
    #         instance = ApiRequest()
    #         response = instance.requestConfigurationAlarms()
    #         self.serialPort.write(response.encode())
    #     except serial.SerialException as e:
    #         print("Error en el envío de datos al puerto serial:", e)

