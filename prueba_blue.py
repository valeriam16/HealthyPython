from bluepy.btle import Peripheral, UUID, DefaultDelegate

class MyDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleNotification(self, cHandle, data):
        print("Received:", data.decode('utf-8'))

def connect_to_device(mac_address):
    print("Connecting to", mac_address)
    dev = Peripheral(mac_address)
    dev.setDelegate(MyDelegate())
    return dev

def send_data(dev, characteristic, data):
    characteristic.write(data.encode('utf-8'))
    print("Sent:", data)

def receive_data(dev):
    if dev.waitForNotifications(1.0):
        return True
    return False

def main():
    esp32_mac_address = 'E4:65:B8:25:04:9A' # Reemplaza con la dirección MAC de tu ESP32
    uart_service_uuid = UUID('6E400001-B5A3-F393-E0A9-E50E24DCCA9E')
    tx_characteristic_uuid = UUID('6E400003-B5A3-F393-E0A9-E50E24DCCA9E')
    rx_characteristic_uuid = UUID('6E400002-B5A3-F393-E0A9-E50E24DCCA9E')

    try:
        dev = connect_to_device(esp32_mac_address)
        service = dev.getServiceByUUID(uart_service_uuid)
        tx_characteristic = service.getCharacteristics(tx_characteristic_uuid)[0]
        rx_characteristic = service.getCharacteristics(rx_characteristic_uuid)[0]

        print("Connected. Ready to receive and send data.")
        while True:
            # Leer notificaciones
            if receive_data(dev):
                continue
            
            # Enviar datos
            data_to_send = input("Enter data to send: ")
            send_data(dev, rx_characteristic, data_to_send)
    except Exception as e:
        print(e)
    finally:
        dev.disconnect()
        print("Disconnected.")

if __name__ == "__main__":
    main()
