# -*- coding: utf-8 -*-
"""
Created on Tue Apr  9 13:17:52 2024

@author: Admin
"""

import sys
from collections import deque
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QComboBox, QPushButton, QVBoxLayout, QTextEdit, QMessageBox

def save_route_to_file(route, steps, routes_dict, filename="routes.txt"):
    # Claves para ruta directa e inversa
    key = (route[0][1], route[-1][1])  # Usar solo nombres de estaciones
    reverse_key = (route[-1][1], route[0][1])

    # Verificar si la ruta actual es más larga que la existente
    if key in routes_dict:
        if routes_dict[key][1] <= steps:  # No guardar si la ruta existente es más corta o igual
            return

    # Actualizar rutas directa e inversa
    routes_dict[key] = (route, steps)
    routes_dict[reverse_key] = (route[::-1], steps)

    # Guardar rutas en archivo
    with open(filename, "w") as file:
        for route_key, (route_val, route_steps) in routes_dict.items():
            route_str = " -> ".join(f"{line}/{station}" for line, station in route_val)
            file.write(f"{route_key[0]} to {route_key[1]} | {route_str} | Steps: {route_steps}\n")


def load_routes_from_file(filename="routes.txt"):
    routes = {}
    try:
        with open(filename, "r") as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue

                parts = line.split(' | ')
                if len(parts) != 3:
                    continue  # Ignorar líneas mal formateadas

                key_part, route_part, steps_part = parts
                origin, destination = key_part.split(' to ')
                route = [tuple(station.split('/')) for station in route_part.split(' -> ')]
                steps = int(steps_part.split(': ')[1])

                # Asumir que las rutas cargadas no son redundantes
                routes[(origin, destination)] = (route, steps)
                routes[(destination, origin)] = (route[::-1], steps)
    except FileNotFoundError:
        print("Routes file not found, creating a new one.")
    return routes










class Subway: 
    def __init__(self):
        self.subway = {}
        self.pesos = {}
        self.rutas = load_routes_from_file()  # Asegúrate de que las rutas se cargan correctamente desde el archivo
        self.clean_up_routes()  # Limpia las rutas justo después de cargarlas
        self.initialize_subway()

    def initialize_subway(self):

        self.subway = {
        'Línea 1': {
            'Talleres': ['San Bernabé'],
            'San Bernabé': ['Talleres', 'Unidad Modelo'],
            'Unidad Modelo': ['San Bernabé', 'Aztlán'],
            'Aztlán': ['Unidad Modelo', 'Penitenciaría'],
            'Penitenciaría': ['Aztlán', 'Alfonso Reyes'],
            'Alfonso Reyes': ['Penitenciaría', 'Mitras'],
            'Mitras': ['Alfonso Reyes', 'Simón Bolívar'],
            'Simón Bolívar': ['Mitras', 'Hospital'],
            'Hospital': ['Simón Bolívar', 'Edison'],
            'Edison': ['Hospital', 'Central'],
            'Central': ['Edison', 'Cuauhtémoc'],
            'Cuauhtémoc': {
                'connections': {
                    'Línea 2': 'Cuauhtémoc'
                },
                'next_stations': ['Central', 'Del Golfo']
            },
            'Del Golfo': ['Cuauhtémoc', 'Félix Uresti Gómez'],
            'Félix Uresti Gómez': {
                'connections': {
                    'Línea 3': 'Félix Uresti Gómez'
                },
                'next_stations': ['Del Golfo', 'Parque Fundidora']
            },
            'Parque Fundidora': ['Félix Uresti Gómez', 'Y Griega'],
            'Y Griega': ['Parque Fundidora', 'Eloy Cavazos'],
            'Eloy Cavazos': ['Y Griega', 'Lerdo de Tejada'],
            'Lerdo de Tejada': ['Eloy Cavazos', 'Exposición'],
            'Exposición': ['Lerdo de Tejada']
        },
        'Línea 2': {
            'Sendero': ['Santiago Tapia'],
            'Santiago Tapia': ['Sendero', 'San Nicolás'],
            'San Nicolás': ['Santiago Tapia', 'Anáhuac'],
            'Anáhuac': ['San Nicolás', 'Universidad'],
            'Universidad': ['Anáhuac', 'Niños Héroes'],
            'Niños Héroes': ['Universidad', 'Regina'],
            'Regina': ['Niños Héroes', 'General Anaya'],
            'General Anaya': ['Regina', 'Cuauhtémoc'],
            'Cuauhtémoc': {
                'connections': {
                    'Línea 1': 'Cuauhtémoc'
                },
                'next_stations': ['General Anaya', 'Alameda']
            },
            'Alameda': ['Cuauhtémoc', 'Fundadores'],
            'Fundadores': ['Alameda', 'Padre Mier'],
            'Padre Mier': ['Fundadores', 'General I. Zaragoza'],
            'General I. Zaragoza': {
                'connections': {
                    'Línea 3': 'General I. Zaragoza'
                },
                'next_stations': ['Padre Mier']
            }
        },
        'Línea 3': {
            'General I. Zaragoza': {
                'connections': {
                    'Línea 2': 'General I. Zaragoza'
                },
                'next_stations': ['Santa Lucía']
            },
            'Santa Lucía': ['General I. Zaragoza', 'Colonia Obrera'],
            'Colonia Obrera': ['Santa Lucía', 'Félix Uresti Gómez'],
            'Félix Uresti Gómez': {
                'connections': {
                    'Línea 1': 'Félix Uresti Gómez'
                },
                'next_stations': ['Colonia Obrera', 'Metalúrgicos']
            },
            'Metalúrgicos': ['Félix Uresti Gómez', 'Moderna'],
            'Moderna': ['Metalúrgicos', 'Ruiz Cortines'],
            'Ruiz Cortines': ['Moderna', 'Los Ángeles'],
            'Los Ángeles': ['Ruiz Cortines', 'Hospital Metropolitano'],
            'Hospital Metropolitano': ['Los Ángeles']
        }
    }







        for station in self.subway.keys():
         self.pesos[station] = 1  # Peso uniforme para la demostración
    

    def bfs(self, origin, destination, subway_graph):
        origin_line, origin_station = origin
        destination_line, destination_station = destination
        queue = deque([(origin_line, origin_station, [(origin_line, origin_station)])])
        seen = set([(origin_line, origin_station)])
        
        while queue:
            current_line, current_station, path = queue.popleft()
            current_station_info = subway_graph[current_line].get(current_station)
            
            # Comprueba si la información actual de la estación es un diccionario (tiene conexiones/transbordos)
            if isinstance(current_station_info, dict):
                next_stations = current_station_info.get('next_stations', [])
                connections = current_station_info.get('connections', {})
            else:
                next_stations = current_station_info
                connections = {}
            
            if (current_line, current_station) == (destination_line, destination_station):
                return path, len(path) - 1, True  # Ruta encontrada
            
            # Revisar vecinos directos
            for neighbor in next_stations:
                if (current_line, neighbor) not in seen:
                    seen.add((current_line, neighbor))
                    queue.append((current_line, neighbor, path + [(current_line, neighbor)]))
            
            # Revisar posibles transbordos
            for line, trans_station in connections.items():
                if (line, trans_station) not in seen:
                    seen.add((line, trans_station))
                    queue.append((line, trans_station, path + [(line, trans_station)]))
        
        return [], float('inf'), False  # No se encontró ruta








    def adapt_route(self, origin, destination):
        print(f"Buscando ruta de {origin} a {destination}")
        if origin == destination:
            print("Origen y destino son la misma estación.")
            return [(origin[0], origin[1])], 0, True
    
        # Intentar reutilizar cualquier ruta caché existente
        cached_route = self.find_cached_route(origin, destination)
        if cached_route:
            print(f"Ruta desde caché utilizada: {origin} a {destination}")
            return cached_route
    
        # Si no hay rutas caché útiles, realizar BFS
        print("No se encontró una ruta útil en caché, realizando BFS completo.")
        route, steps, found_route = self.bfs(origin, destination, self.subway)
        if found_route:
            print("Ruta encontrada mediante BFS, guardando en caché...")
            self.rutas[(origin, destination)] = (route, steps)
            self.rutas[(destination, origin)] = (route[::-1], steps)
            save_route_to_file(route, steps, self.rutas)  # Asegúrate de guardar la ruta en el archivo
        return route, steps, found_route



    def find_cached_route(self, origin, destination):
        # Verificar ruta directa en caché
        if (origin, destination) in self.rutas:
            route, steps = self.rutas[(origin, destination)]
            print(f"Reutilizando ruta exacta de: {origin} a {destination} con {steps} pasos.")
            return route, steps, True
    
        # Intentar adaptar una subruta de las rutas guardadas
        for (start, end), (route, steps) in self.rutas.items():
            try:
                start_index = route.index(origin)
                end_index = route.index(destination, start_index)
                if start_index <= end_index:  # Asegurarse de que la subruta sea válida
                    subroute = route[start_index:end_index + 1]
                    substeps = end_index - start_index
                    print(f"Adaptando subruta existente de: {origin} a {destination} con {substeps} pasos.")
                    return subroute, substeps, True
            except ValueError:
                continue  # El origen o destino no está en esta ruta
    
        return None  # No se encontró una ruta útil en caché


       





    def clean_up_routes(self, filename="routes.txt"):
        to_remove = set()  # Usar un conjunto para evitar duplicados desde el inicio
    
        keys = list(self.rutas.keys())  # Lista de claves para iterar de forma segura
    
        for i in range(len(keys)):
            key1 = keys[i]
            if key1 not in self.rutas:
                continue
            route1, steps1 = self.rutas[key1]
    
            for j in range(i + 1, len(keys)):
                key2 = keys[j]
                if key2 not in self.rutas:
                    continue
                route2, steps2 = self.rutas[key2]
    
                # Comprobar subrutas en ambos sentidos
                if self.is_subroute(route1, route2):
                    to_remove.add(key1)
                elif self.is_subroute(route2, route1):
                    to_remove.add(key2)
    
        # Eliminar rutas identificadas como redundantes
        for key in to_remove:
            if key in self.rutas:
                del self.rutas[key]
                reverse_key = (key[1], key[0])  # Clave inversa para rutas bidireccionales
                self.rutas.pop(reverse_key, None)  # Eliminar también la ruta inversa, si existe
    
        # Actualizar archivo de rutas
        with open(filename, "w") as file:
            for (route_origin, route_dest), (route, steps) in self.rutas.items():
                route_str = " -> ".join(f"{line}/{station}" for line, station in route)
                file.write(f"{route_origin} to {route_dest} | {route_str} | Steps: {steps}\n")

                    
    def is_subroute(self, subroute, route):
        try:
            # Encontrar índices de inicio y fin de la subruta en la ruta principal
            start_index = route.index(subroute[0])
            end_index = route.index(subroute[-1], start_index)  # Buscar fin desde el inicio encontrado
            # Comprobar si los segmentos coinciden
            return route[start_index:end_index + 1] == subroute
        except ValueError:
            return False  # Retorna Falso si no se encuentra algún elemento


class SubwayApp(QWidget):
    def __init__(self, subway_system):
        super().__init__()
        self.subway = subway_system  # Supongo que esta es una instancia de alguna clase que gestiona el sistema de metro.
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 400, 300)
        self.setWindowTitle('Sistema de Metro')

        layout = QVBoxLayout()

        # Línea de origen
        self.origin_line_label = QLabel('Línea de origen:')
        self.origin_line_combo = QComboBox()
        self.origin_line_combo.addItems(sorted(self.subway.subway.keys()))
        self.origin_line_combo.currentIndexChanged.connect(self.updateOriginStations)

        # Estación de origen
        self.origin_station_label = QLabel('Estación de origen:')
        self.origin_station_combo = QComboBox()

        # Línea de destino
        self.destination_line_label = QLabel('Línea de destino:')
        self.destination_line_combo = QComboBox()
        self.destination_line_combo.addItems(sorted(self.subway.subway.keys()))
        self.destination_line_combo.currentIndexChanged.connect(self.updateDestinationStations)

        # Estación de destino
        self.destination_station_label = QLabel('Estación de destino:')
        self.destination_station_combo = QComboBox()

        self.search_button = QPushButton('Buscar Ruta')
        self.search_button.clicked.connect(self.find_route)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)

        layout.addWidget(self.origin_line_label)
        layout.addWidget(self.origin_line_combo)
        layout.addWidget(self.origin_station_label)
        layout.addWidget(self.origin_station_combo)
        layout.addWidget(self.destination_line_label)
        layout.addWidget(self.destination_line_combo)
        layout.addWidget(self.destination_station_label)
        layout.addWidget(self.destination_station_combo)
        layout.addWidget(self.search_button)
        layout.addWidget(self.result_text)

        self.setLayout(layout)
        self.updateOriginStations()  # Inicializar las estaciones de origen
        self.updateDestinationStations()  # Inicializar las estaciones de destino

    def updateOriginStations(self):
        current_line = self.origin_line_combo.currentText()
        stations = sorted(self.subway.subway[current_line].keys())
        self.origin_station_combo.clear()
        self.origin_station_combo.addItems(stations)
    
    def updateDestinationStations(self):
        current_line = self.destination_line_combo.currentText()
        stations = sorted(self.subway.subway[current_line].keys())
        self.destination_station_combo.clear()
        self.destination_station_combo.addItems(stations)

    def find_route(self):
        origin_line = self.origin_line_combo.currentText()
        origin_station = self.origin_station_combo.currentText()
        destination_line = self.destination_line_combo.currentText()
        destination_station = self.destination_station_combo.currentText()
    
        route, steps, found = self.subway.adapt_route((origin_line, origin_station), (destination_line, destination_station))
        
        if found:
            route_str = ' -> '.join([f"{line}/{station}" for line, station in route])
            self.result_text.setText(f'Ruta encontrada: {route_str}\nNúmero de estaciones: {steps}')
        else:
            self.result_text.setText("No se encontró ruta.")
            QMessageBox.information(self, 'No se encontró ruta', 'No se pudo encontrar una ruta entre las estaciones seleccionadas.')
        
        self.subway.clean_up_routes()  # Llamar a clean_up_routes después de encontrar la ruta o mostrar un mensaje

if __name__ == '__main__':
    app = QApplication(sys.argv)
    subway_system = Subway()  # Asegúrate de que Subway está correctamente definido e inicializado
    ex = SubwayApp(subway_system)
    ex.show()
    sys.exit(app.exec_())
