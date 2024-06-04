import csv
import requests
import math
from abc import ABC, abstractmethod

class Coordenada:
    def __init__(self, latitud, longitud):
        self.latitud = latitud
        self.longitud = longitud

class Ciudad:
    def __init__(self, nombre_ciudad, nombre_pais):
        self.nombre_ciudad = nombre_ciudad
        self.nombre_pais = nombre_pais

class ICoordinateService(ABC):
    @abstractmethod
    def obtener_coordenadas(self, ciudad: Ciudad) -> Coordenada:
        pass

class CSVCoordinateService(ICoordinateService):
    def __init__(self, csv_file):
        self.csv_file = csv_file

    def obtener_coordenadas(self, ciudad: Ciudad) -> Coordenada:
        with open(self.csv_file, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['city'].strip().lower() == ciudad.nombre_ciudad.strip().lower() and row['country'].strip().lower() == ciudad.nombre_pais.strip().lower():
                    return Coordenada(float(row['lat']), float(row['lng']))
        return None

class APICoordinateService(ICoordinateService):
    def obtener_coordenadas(self, ciudad: Ciudad) -> Coordenada:
        url = f"https://nominatim.openstreetmap.org/search?q={ciudad.nombre_ciudad},{ciudad.nombre_pais}&format=json"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data:
                return Coordenada(float(data[0]['lat']), float(data[0]['lon']))
        return None

class MockCoordinateService(ICoordinateService):
    def obtener_coordenadas(self, ciudad: Ciudad) -> Coordenada:
        return Coordenada(0.0, 0.0)

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  # Radio de la Tierra en kilómetros
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance

class DistanceCalculator:
    def __init__(self, service: ICoordinateService):
        self.service = service

    def calculate_distance(self, ciudad1: Ciudad, ciudad2: Ciudad):
        coords1 = self.service.obtener_coordenadas(ciudad1)
        coords2 = self.service.obtener_coordenadas(ciudad2)
        if not coords1 or not coords2:
            return None
        return haversine(coords1.latitud, coords1.longitud, coords2.latitud, coords2.longitud)

if __name__ == "__main__":
    # Ruta del archivo CSV
    csv_file_path = 'worldcities.csv'  # Ajusta esta ruta según la ubicación de tu archivo CSV

    csv_service = CSVCoordinateService(csv_file_path)
    api_service = APICoordinateService()
    mock_service = MockCoordinateService()

    print("Elija una opcion: ")
    print("1. Calcular distancia entre ciudades usando el servicio CSV")
    print("2. Calcular distancia entre ciudades usando el servicio API")
    opcion = int(input("Ingrese el numero de opcion: "))
    if opcion == 1:
        calculator = DistanceCalculator(csv_service)
    elif opcion == 2:
        calculator = DistanceCalculator(api_service)
    else:
        print("Opcion invalida")
        exit()
    
    nombre_ciudad1 = input("Ingrese la primera ciudad: ")
    nombre_pais1 = input("Ingrese el primer país: ")
    nombre_ciudad2 = input("Ingrese la segunda ciudad: ")
    nombre_pais2 = input("Ingrese el segundo país: ")

    ciudad1 = Ciudad(nombre_ciudad1, nombre_pais1)
    ciudad2 = Ciudad(nombre_ciudad2, nombre_pais2)

    distancia = calculator.calculate_distance(ciudad1, ciudad2)
    if distancia is not None:
        print(f"La distancia entre {ciudad1.nombre_ciudad}, {ciudad1.nombre_pais} y {ciudad2.nombre_ciudad}, {ciudad2.nombre_pais} es {distancia:.2f} km.")
    else:
        print("No se pudieron obtener las coordenadas para una o ambas ciudades.")
