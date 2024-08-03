import datetime
import serial
import time
import json
from time import sleep
from ComunicationPort import ComunicationPort
from bluepy.btle import Peripheral, UUID, DefaultDelegate

esp32_mac_address = 'E4:65:B8:25:04:9A'  
uart_service_uuid = UUID('6E400001-B5A3-F393-E0A9-E50E24DCCA9E')
tx_characteristic_uuid = UUID('6E400003-B5A3-F393-E0A9-E50E24DCCA9E')
rx_characteristic_uuid = UUID('6E400002-B5A3-F393-E0A9-E50E24DCCA9E')


class MyDelegate(DefaultDelegate):
    def __init__(self, bluetooth_port):
        DefaultDelegate.__init__(self)
        self.bluetooth_port = bluetooth_port

    def handleNotification(self, cHandle, data):
        decoded_data = data.decode('utf-8')
        self.bluetooth_port.lista.append(decoded_data)
        print(data)

class BluetoothPort(ComunicationPort):

    def __init__(self, type):
        super().__init__(type)
        self.connect()

    def connect(self):
        self.activo = False
        try:
            self.dev = Peripheral(esp32_mac_address)
            self.dev.setDelegate(MyDelegate(self))
                
            service = self.dev.getServiceByUUID(uart_service_uuid)
            self.tx_characteristic = service.getCharacteristics(tx_characteristic_uuid)[0]
            self.rx_characteristic = service.getCharacteristics(rx_characteristic_uuid)[0]

            # Habilitar notificaciones
            descriptor = self.tx_characteristic.getDescriptors(forUUID=UUID(0x2902))[0]
            descriptor.write(b'\x01\x00')

            # Reconfigurar notificaciones
            time.sleep(1)
            descriptor.write(b'\x00\x00')  # Deshabilitar
            time.sleep(1)
            descriptor.write(b'\x01\x00')  # Habilitar nuevamente
            self.activo = True
            self.activar = True
        except Exception as e:
            print("Error en la conexion por bluetooth:", e)


    def sendString(self, message):
        if self.activo == True:
            try:
                self.rx_characteristic.write(message.encode('utf-8'))
            except Exception as e:
                self.connect()
                print("Error en el envío de datos a bluetooth:", e)

    # LEER DATOS
    def readDevicesData(self):
        if self.activo == False:
            self.connect()

        