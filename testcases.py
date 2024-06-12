import unittest
from unittest.mock import patch, mock_open
import requests
import csv
from io import StringIO
from main import CSVCoordinateService, APICoordinateService, Ciudad, DistanceCalculator

class TestCoordinateServices(unittest.TestCase):

    def setUp(self):
        self.csv_data = """city,country,lat,lng
        New York,USA,40.7128,-74.0060
        Los Angeles,USA,34.0522,-118.2437
        Madrid,Spain,40.4165,-3.70256
        Berlin,Germany,52.5200,13.4050
        Mexico City,Mexico,19.4326,-99.1332
        """
        
        self.mock_csv_file = mock_open(read_data=self.csv_data)

    def test_csv_coordinate_service_city_exists(self):
        with patch('builtins.open', self.mock_csv_file):
            service = CSVCoordinateService('mock_file.csv')
            ciudad = Ciudad('Madrid', 'Spain')
            coords = service.obtener_coordenadas(ciudad)
            self.assertIsNotNone(coords)
            self.assertAlmostEqual(coords.latitud, 40.4165)
            self.assertAlmostEqual(coords.longitud, -3.70256)

    def test_csv_coordinate_service_city_does_not_exist(self):
        with patch('builtins.open', self.mock_csv_file):
            service = CSVCoordinateService('mock_file.csv')
            ciudad = Ciudad('Atlantis', 'None')
            coords = service.obtener_coordenadas(ciudad)
            self.assertIsNone(coords)

    @patch('requests.get')
    def test_api_coordinate_service_city_exists(self, mock_get):
        mock_response = {
            "lat": "52.5200",
            "lon": "13.4050"
        }
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [mock_response]

        service = APICoordinateService()
        ciudad = Ciudad('Berlin', 'Germany')
        coords = service.obtener_coordenadas(ciudad)
        self.assertIsNotNone(coords)
        self.assertAlmostEqual(coords.latitud, 52.5200)
        self.assertAlmostEqual(coords.longitud, 13.4050)

    def test_calculate_distance_csv_both_cities_exist(self):
        with patch('builtins.open', self.mock_csv_file):
            service = CSVCoordinateService('mock_file.csv')
            calculator = DistanceCalculator(service)
            ciudad1 = Ciudad('New York', 'USA')
            ciudad2 = Ciudad('Los Angeles', 'USA')
            distancia = calculator.calculate_distance(ciudad1, ciudad2)
            self.assertIsNotNone(distancia)
            self.assertAlmostEqual(distancia, 3936.5, delta=1.0)  # Aproximadamente 3936.5 km

    @patch('requests.get')
    def test_calculate_distance_api_one_city_does_not_exist(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = []

        service = APICoordinateService()
        calculator = DistanceCalculator(service)
        ciudad1 = Ciudad('Gotham', 'USA')
        ciudad2 = Ciudad('Metropolis', 'USA')
        distancia = calculator.calculate_distance(ciudad1, ciudad2)
        self.assertIsNone(distancia)

    def test_csv_coordinate_service_city_case_and_spaces(self):
        with patch('builtins.open', self.mock_csv_file):
            service = CSVCoordinateService('mock_file.csv')
            ciudad = Ciudad(' mexico city ', ' MEXICO ')
            coords = service.obtener_coordenadas(ciudad)
            self.assertIsNotNone(coords)
            self.assertAlmostEqual(coords.latitud, 19.4326)
            self.assertAlmostEqual(coords.longitud, -99.1332)

if __name__ == '__main__':
    unittest.main()
