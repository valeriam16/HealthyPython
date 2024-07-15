import requests


class ApiRequest:
    def requestConfigurationAlarms(self):
        try:
            endpoint = 'http://127.0.0.1:3333/'
            response = requests.get(endpoint)

            # Verificar el código de estado de la respuesta
            if response.status_code == 200:
                # Procesar la respuesta JSON
                data = response.json()
                print(data)
                return data
            else:
                print(f"Error: {response.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"Error en la conexión: {e}")
