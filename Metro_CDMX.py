
# -*- coding: utf-8 -*-
"""
Equipo 3 

Aranza Ibarra Camarena 
Braulio Lozano Cuevas
Chris Montejano 
Mingyar Romero


Clase de Inteligencia Artificial
"""



import sys
from collections import deque
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QComboBox, QPushButton, QVBoxLayout, QTextEdit, QMessageBox

"""
    Guarda las rutas más cortas entre estaciones en un archivo de texto.

    Parámetros:
    - route (list of tuples): Lista de tuplas, donde cada tupla contiene la línea y la estación de la ruta.
    - steps (int): Número de pasos o estaciones totales en la ruta.
    - routes_dict (dict): Diccionario que almacena las rutas como claves y los detalles de la ruta como valores.
    - filename (str, opcional): Nombre del archivo en el que se guardará la información de las rutas.

    Descripción:
    Esta función verifica si la ruta actual es más corta que la existente guardada en el diccionario para esa pareja de estaciones.
    Si es más corta, actualiza la ruta en el diccionario y guarda todas las rutas en el archivo especificado.
    """

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



"""
    Carga las rutas desde un archivo de texto a un diccionario.

    Parámetros:
    - filename (str, opcional): Nombre del archivo de donde se cargarán las rutas.

    Retorna:
    - dict: Un diccionario con las rutas cargadas, donde las claves son tuplas de (origen, destino) y los valores son tuplas de (ruta, pasos).

    Descripción:
    Esta función intenta abrir y leer un archivo de texto que contiene rutas previamente guardadas.
    Si el archivo no existe, se maneja la excepción y se crea un diccionario vacío.
    """
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



"""
Aquí separamos para tener una mejor lectura del código
Comienza como tal la creación de la red de transporte.
Nos centramos en las subterráneas y por eso se llama Subway
"""


"""
        Inicializador para la clase Subway, que configura el sistema de rutas del metro.

        Descripción:
        Carga las rutas desde un archivo si existen, inicializa las estructuras de datos necesarias para representar
        el sistema de metro y prepara el sistema para su uso.
        """
class Subway: 
    def __init__(self):
        
        self.subway = {}
        self.pesos = {}
        self.rutas = load_routes_from_file()  # Asegúrate de que las rutas se cargan correctamente desde el archivo
        self.clean_up_routes()  # Limpia las rutas justo después de cargarlas
        self.initialize_subway()

    """
        Configura y construye la estructura del sistema de metro con todas sus líneas y estaciones.

        Descripción:
        Este método define las líneas del metro, las estaciones en cada línea y las conexiones entre estaciones,
        incluyendo transferencias entre diferentes líneas. Cada estación puede tener estaciones consecutivas y conexiones a otras líneas.
        """ 
    def initialize_subway(self):
            
        self.subway = {
            'Linea 1': {
                'Observatorio': ['Tacubaya'],
                'Tacubaya': {
                    'connections': {
                        'Linea 7': ['Constituyentes', 'San Pedro de los Pinos'],
                        'Linea 9': ['Patriotismo'],
                    }, 
                    'next_station': ['Observatorio', 'Juanacatlan']
                }, 
                'Juanacatlan': ['Tacubaya', 'Chapultepec'],
                'Chapultepec': ['Juanacatlan', 'Sevilla'],
                'Sevilla': ['Chapultepec', 'Insurgentes'],
                'Insurgentes': ['Sevilla', 'Cuauhtemoc'],
                'Cuauhtemoc': ['Insurgentes', 'Balderas'],
                'Balderas': {
                    'connections': {
                        'Linea 3': ['Juarez', 'Ninos Heroes'],
                    }, 
                    'next_station': ['Cuauhtemoc', 'Salto del Agua']
                },
                'Salto del Agua': {
                    'connections': { 
                        'Linea 8': ['Doctores', 'San Juan de Letran'],
                    },
                    'next_station': ['Balderas', 'Isabel la Catolica']
                },
                'Isabel la Catolica': ['Salto del Agua', 'Pino Suarez'],
                'Pino Suarez': {
                    'connections': {
                        'Linea 2': ['San Antonio Abad', 'Zocalo'],
                    },
                    'next_station': ['Isabel la Catolica', 'Merced']
                },
                'Merced': ['Pino Suarez', 'Candelaria'],
                'Candelaria': {
                    'connections': {
                        'Linea 4': ['Fray Servando', 'Morelos'],
                    },
                    'next_station': ['Merced', 'San Lazaro']
                },
                'San Lazaro': {
                    'connections': {
                        'Linea B': ['Morelos', 'Flores Magon'],
                    },
                    'next_station': ['Candelaria', 'Moctezuma']
                },
                'Moctezuma': ['San Lazaro', 'Balbuena'],
                'Balbuena': ['Moctezuma', 'Boulevard Puerto Aereo'],
                'Boulevard Puerto Aereo': ['Balbuena', 'Gomez Farias'],
                'Gomez Farias': ['Boulevard Puerto Aereo', 'Zaragoza'],
                'Zaragoza': ['Gomez Farias', 'Pantitlan'],
                'Pantitlan': {
                    'connections': {
                        'Linea 5': ['Hangares'],
                        'Linea 9': ['Puebla'],
                        'Linea A': ['Agricola Oriental'],
                    },
                    'next_station': ['Zaragoza']
                },
            },
            'Linea 2': {
                'Cuatro Caminos': ['Panteones'],
                'Panteones': ['Cuatro Caminos', 'Tacuba'],
                'Tacuba': {
                    'connections': {
                        'Linea 7': ['San Joaquin', 'Refineria'],
                    },
                    'next_station': ['Panteones', 'Cuitlahuac']
                },
                'Cuitlahuac': ['Tacuba', 'Popotla'],
                'Popotla': ['Cuitlahuac', 'Colegio Militar'],
                'Colegio Militar': ['Popotla', 'Normal'],
                'Normal': ['Colegio Militar', 'San Cosme'],
                'San Cosme': ['Normal', 'Revolucion'],
                'Revolucion': ['San Cosme', 'Hidalgo'],
                'Hidalgo': {
                    'connections': {
                        'Linea 3': ['Juarez', 'Guerrero'],
                    },
                    'next_station': ['Revolucion', 'Bellas Artes']
                },
                'Bellas Artes': {
                    'connections': {
                        'Linea 8': ['San Juan de Letran', 'Garibaldi'],
                    },
                    'next_station': ['Hidalgo', 'Allende']
                },
                'Allende': ['Bellas Artes', 'Zocalo'],
                'Zocalo': ['Allende', 'Pino Suarez'],
                'Pino Suarez': {
                    'connections': {
                        'Linea 1': ['Merced', 'Isabel la Catolica'],
                    },
                    'next_station': ['Zocalo', 'San Antonio Abad']
                },
                'San Antonio Abad': ['Pino Suarez', 'Chabacano'],
                'Chabacano': {
                    'connections': {
                        'Linea 8': ['Obrera', 'La Viga'],
                        'Linea 9': ['Jamaica', 'Lazaro Cardenas'],
                    },
                    'next_station': ['San Antonio Abad', 'Viaducto']
                },
                'Viaducto': ['Chabacano', 'Xola'],
                'Xola': ['Viaducto', 'Villa de Cortes'],
                'Villa de Cortes': ['Xola', 'Nativitas'],
                'Nativitas': ['Villa de Cortes', 'Portales'],
                'Portales': ['Nativitas', 'Ermita'],
                'Ermita': {
                    'connections': {
                        'Linea 12': ['Mexicaltzingo', 'Eje Central'],
                    },
                    'next_station': ['Portales', 'General Anaya']
                },
                'General Anaya': ['Ermita', 'Tasquena'],
                'Tasquena': ['General Anaya'],
            },
            'Linea 3': {
                'Indios Verdes': ['Deportivo 18 de Marzo'],
                'Deportivo 18 de Marzo': {
                    'connections': {
                        'Linea 6': ['La Villa', 'Lindavista'],
                    },
                    'next_station': ['Indios Verdes', 'Potrero']
                },
                'Potrero': ['Deportivo 18 de Marzo', 'La Raza'],
                'La Raza': {
                    'connections': {
                        'Linea 5': ['Misterios', 'Autobuses del Norte'],
                    },
                    'next_station': ['Potrero', 'Tlatelolco']
                },
                'Tlatelolco': ['La Raza', 'Guerrero'],
                'Guerrero': {
                    'connections': {
                        'Linea B': ['Buenavista', 'Garibaldi'],
                    },
                    'next_station': ['Tlatelolco', 'Hidalgo']
                },
                'Hidalgo': {
                    'connections': {
                        'Linea 2': ['Revolucion', 'Bellas Artes'],
                    },
                    'next_station': ['Guerrero', 'Juarez']
                },
                'Juarez': ['Hidalgo', 'Balderas'],
                'Balderas': {
                    'connections': {
                        'Linea 1': ['Cuauhtemoc', 'Salto del Agua'],
                    },
                    'next_station': ['Juarez', 'Ninos Heroes']
                },
                'Ninos Heroes': ['Balderas', 'Hospital General'],
                'Hospital General': ['Ninos Heroes', 'Centro Medico'],
                'Centro Medico': {
                    'connections': {
                        'Linea 9': ['Chilpancingo', 'Lazaro Cardenas'],
                    },
                    'next_station': ['Hospital General', 'Etiopia']
                },
                'Etiopia': ['Centro Medico', 'Eugenia'],
                'Eugenia': ['Etiopia', 'Division del Norte'],
                'Division del Norte': ['Eugenia', 'Zapata'],
                'Zapata': {
                    'connections': {
                        'Linea 12': ['Hospital 20 de Noviembre', 'Parque de los Venados'],
                    },
                    'next_station': ['Division del Norte', 'Coyoacan']
                },
                'Coyoacan': ['Zapata', 'Viveros'],
                'Viveros': ['Coyoacan', 'Miguel Angel de Quevedo'],
                'Miguel Angel de Quevedo': ['Viveros', 'Copilco'],
                'Copilco': ['Miguel Angel de Quevedo', 'Universidad'],
                'Universidad': ['Copilco'],
            },
            'Linea 4': {
                'Martin Carrera': {
                    'connections': {
                        'Linea 6': ['La Villa'],
                    },
                    'next_station': ['Talisman']
                },
                'Talisman': ['Martin Carrera', 'Bondojito'],
                'Bondojito': ['Talisman', 'Consulado'],
                'Consulado': {
                    'connections': {
                        'Linea 5': ['Valle Gomez', 'Eduardo Molina'],
                    },
                    'next_station': ['Bondojito', 'Canal del Norte']
                },
                'Canal del Norte': ['Consulado', 'Morelos'],
                'Morelos': {
                    'connections': {
                        'Linea B': ['Tepito', 'San Lazaro'],
                    },
                    'next_station': ['Canal del Norte', 'Candelaria']
                },
                'Candelaria': {
                    'connections': {
                        'Linea 1': ['San Lazaro', 'Merced'],
                    },
                    'next_station': ['Morelos', 'Fray Servando']
                },
                'Fray Servando': ['Candelaria', 'Jamaica'],
                'Jamaica': {
                    'connections': {
                        'Linea 9': ['Mixiuhca', 'Chabacano'],
                    },
                    'next_station': ['Fray Servando', 'Santa Anita']
                },
                'Santa Anita': {
                    'connections': {
                        'Linea 8': ['La Viga', 'Coyuya'],
                    },
                    'next_station': ['Jamaica']
                },
            },
            'Linea 5': {
                'Pantitlan': {
                    'connections': {
                        'Linea 1': ['Zaragoza'],
                        'Linea 9': ['Puebla'],
                        'Linea A': ['Agricola Oriental'],
                    },
                    'next_station': ['Hangares']
                },
                'Hangares': ['Pantitlan', 'Terminal Aerea'],
                'Terminal Aerea': ['Hangares', 'Oceania'],
                'Oceania': {
                    'connections': {
                        'Linea B': ['Romero Rubio', 'Deportivo Oceania'],
                    },
                    'next_station': ['Terminal Aerea', 'Aragon']
                },
                'Aragon': ['Oceania', 'Eduardo Molina'],
                'Eduardo Molina': ['Aragon', 'Consulado'],
                'Consulado': {
                    'connections': {
                        'Linea 4': ['Bondojito', 'Canal del Norte'],
                    },
                    'next_station': ['Eduardo Molina', 'Valle Gomez']
                },
                'Valle Gomez': ['Consulado', 'Misterios'],
                'Misterios': ['Valle Gomez', 'La Raza'],
                'La Raza': {
                    'connections': {
                        'Linea 3': ['Potrero', 'Tlatelolco'],
                    },
                    'next_station': ['Misterios', 'Autobuses del Norte']
                },
                'Autobuses del Norte': ['La Raza', 'Instituto del Petroleo'],
                'Instituto del Petroleo': {
                    'connections': {
                        'Linea 6': ['Vallejo', 'Lindavista'],
                    },
                    'next_station': ['Autobuses del Norte', 'Politecnico']
                },
                'Politecnico': ['Instituto del Petróleo'],
            },
            'Linea 6': {
                'El Rosario': {
                    'connections': {
                        'Linea 7': ['Aquiles Serdan'],
                    },
                    'next_station': ['Tezozomoc']
                },
                'Tezozomoc': ['El Rosario', 'Azcapotzalco'],
                'Azcapotzalco': ['Tezozomoc', 'Ferreria'],
                'Ferreria': ['Azcapotzalco', 'Norte 45'],
                'Norte 45': ['Ferreria', 'Vallejo'],
                'Vallejo': ['Norte 45', 'Instituto del Petróleo'],
                'Instituto del Petroleo': {
                    'connections': {
                        'Linea 5': ['Politecnico', 'Autobuses del Norte'],
                    },
                    'next_station': ['Vallejo', 'Lindavista']
                },
                'Lindavista': ['Instituto del Petroleo', 'Deportivo 18 de Marzo'],
                'Deportivo 18 de Marzo': {
                    'connections': {
                        'Linea 3': ['Indios Verdes', 'Potrero'],
                    },
                    'next_station': ['Lindavista', 'La Villa']
                },
                'La Villa' : ['Deportivo 18 de Marzo', 'Martin Carrera'],
                'Martin Carrera': {
                    'connections': {
                        'Linea 4': ['Talisman'],
                    },
                    'next_station': ['La Villa']
                },
            },
            'Linea 7': {
                'El Rosario': {
                    'connections': {
                        'Linea 6': ['Tezozomoc'],
                    },
                    'next_station': ['Aquiles Serdan']
                },
                'Aquiles Serdan': ['El Rosario', 'Camarones'],
                'Camarones': ['Aquiles Serdan', 'Refineria'],
                'Refineria': ['Camarones', 'Tacuba'],
                'Tacuba': {
                    'connections': {
                        'Linea 2': ['Cuitlahuac', 'Panteones'],
                    },
                    'next_station': ['Refineria', 'San Joaquin']
                },
                'San Joaquin': ['Tacuba', 'Polanco'],
                'Polanco': ['San Joaquin', 'Auditorio'],
                'Auditorio': ['Polanco', 'Constituyentes'],
                'Constituyentes': ['Auditorio', 'Tacubaya'],
                'Tacubaya': {
                    'connections': {
                        'Linea 1': ['Juanacatlan', 'Observatorio'],
                        'Linea 9': ['Patriotismo'],
                    },
                    'next_station': ['Constituyentes', 'San Pedro de los Pinos']
                },
                'San Pedro de los Pinos': ['Tacubaya', 'San Antonio'],
                'San Antonio': ['San Pedro de los Pinos', 'Mixcoac'],
                'Mixcoac': {
                    'connections': {
                        'Linea 12': ['Insurgentes Sur'],
                    },
                    'next_station': ['San Antonio', 'Barranca del Muerto']
                },
                'Barranca del Muerto': ['Mixcoac'],
            },
            'Linea 8': {
                'Garibaldi': {
                    'connections': {
                        'Linea B': ['Guerrero', 'Lagunilla'],
                    },
                    'next_station': ['Bellas Artes']
                },
                'Bellas Artes': {
                    'connections': {
                        'Linea 2': ['Allende', 'Hidalgo'],
                    },
                    'next_station': ['Garibaldi', 'San Juan de Letran']
                },
                'San Juan de Letran': ['Bellas Artes', 'Salto del Agua'],
                'Salto del Agua': {
                    'connections': {
                        'Linea 1': ['Isabel la Catolica', 'Balderas'],
                    },
                    'next_station': ['San Juan de Letran', 'Doctores']
                },
                'Doctores': ['Salto del Agua', 'Obrera'],
                'Obrera': ['Doctores', 'Chabacano'],
                'Chabacano': {
                    'connections': {
                        'Linea 2': ['San Antonio Abad', 'Viaducto'],
                        'Linea 9': ['Jamaica', 'Lazaro Cardenas'],
                    },
                    'next_station': ['Obrera', 'La Viga']
                },
                'La Viga': ['Chabacano', 'Santa Anita'],
                'Santa Anita': {
                    'connections': {
                        'Linea 4': ['Jamaica'],
                    },
                    'next_station': ['La Viga', 'Coyuya']
                },
                'Coyuya': ['Santa Anita', 'Iztacalco'],
                'Iztacalco': ['Coyuya', 'Apatlaco'],
                'Apatlaco': ['Iztacalco', 'Aculco'],
                'Aculco': ['Apatlaco', 'Escuadron 201'],
                'Escuadron 201': ['Aculco', 'Atlalilco'],
                'Atlalilco': {
                    'connections': {
                        'Linea 12': ['Mexicaltzingo', 'Culhuacan'],
                    },
                    'next_station': ['Escuadron 201', 'Iztapalapa']
                },
                'Iztapalapa': ['Atlalilco', 'Cerro de la Estrella'],
                'Cerro de la Estrella': ['Iztapalapa', 'UAM'],
                'UAM': ['Cerro de la Estrella', 'Constitucion de 1917'],
                'Constitucion de 1917':['UAM'],
            },
            'Linea 9': {
                'Tacubaya': {
                    'connections': {
                        'Linea 1': ['Observatorio', 'Juanacatlan'],
                        'Linea 7': ['Constituyentes', 'San Pedro de los Pinos'],
                    },
                    'next_station': ['Patriotismo']
                },
                'Patriotismo': ['Tacubaya', 'Chilpancingo'],
                'Chilpancingo': ['Patriotismo', 'Centro Medico'],
                'Centro Medico': {
                    'connections': {
                        'Linea 3': ['Hospital General', 'Etiopia'],
                    },
                    'next_station': ['Chilpancingo', 'Lazaro Cardenas']
                },
                'Lazaro Cardenas': ['Centro Medico', 'Chabacano'],
                'Chabacano': {
                    'connections': {
                        'Linea 2': ['San Antonio Abad', 'Viaducto'],
                        'Linea 8': ['La Viga', 'Obrera'],
                    },
                    'next_station': ['Lazaro Cardenas', 'Jamaica']
                },
                'Jamaica': {
                    'connections': {
                        'Linea 4': ['Santa Anita', 'Fray Servando'],
                    },
                    'next_station': ['Chabacano', 'Mixiuhca']
                },
                'Mixiuhca': ['Jamaica', 'Velodromo'],
                'Velodromo': ['Mixiuhca', 'Ciudad Deportiva'],
                'Ciudad Deportiva': ['Velodromo', 'Puebla'],
                'Puebla': ['Ciudad Deportiva', 'Pantitlan'],
                'Pantitlan': {
                    'connections': {
                        'Linea 1': ['Zaragoza'],
                        'Linea 5': ['Hangares'],
                        'Linea A': ['Agriola Oriental'],
                    },
                    'next_station': ['Puebla']
                },
            },
            'Linea A': {
                'Pantitlan': {
                    'connections': {
                        'Linea 1': ['Zaragoza'],
                        'Linea 5': ['Hangares'],
                        'Linea 9': ['Puebla'],
                    },
                    'next_station': ['Agricola Oriental']
                },
                'Agricola Oriental': ['Pantitlan', 'Canal de San Juan'],
                'Canal de San Juan': ['Agricola Oriental', 'Tepalcates'],
                'Tepalcates': ['Canal de San Juan', 'Guelatao'],
                'Guelatao': ['Tepalcates', 'Penon Viejo'],
                'Penon Viejo': ['Guelatao', 'Acatitla'],
                'Acatitla': ['Penon Viejo', 'Santa Marta'],
                'Santa Marta': ['Acatitla', 'Los Reyes'],
                'Los Reyes': ['Santa Marta', 'La Paz'],
                'La Paz': ['Los Reyes'],
            },
            'Linea B': {
                'Ciudad Azteca': ['Plaza Aragon'],
                'Plaza Aragon': ['Ciudad Azteca', 'Olimpica'],
                'Olimpica': ['Plaza Aragon', 'Ecatepec'],
                'Ecatepec': ['Olimpica', 'Muzquiz'],
                'Muzquiz': ['Ecatepec', 'Rio de los Remedios'],
                'Rio de los Remedios': ['Muzquiz', 'Impulsora'],
                'Impulsora': ['Rio de los Remedios', 'Nezahuacoyotl'],
                'Nezahuacoyotl': ['Impulsora', 'Villa de Aragon'],
                'Villa de Aragon': ['Bosque de Aragon', 'Nezahualcoyotl'],
                'Bosque de Aragon': ['Villa de Aragon', 'Deportivo Oceania'],
                'Deportivo Oceania': ['Bosque de Aragon', 'Oceania'],
                'Oceania': {
                    'connections': {
                        'Linea 5': ['Terminal Aerea', 'Aragon'],
                    },
                    'next_station': ['Deportivo Oceanía', 'Romero Rubio']
                },
                'Romero Rubio': ['Oceania', 'Flores Magon'],
                'Flores Magon': ['Romero Rubio', 'San Lazaro'],
                'San Lazaro': {
                    'connections': {
                        'Linea 1': ['Candelaria', 'Moctezuma'],
                    },
                    'next_station': ['Flores Magon', 'Morelos']
                },
                'Morelos': {
                    'connections': {
                        'Linea 4': ['Canal del Norte', 'Candelaria'],
                    },
                    'next_station': ['San Lazaro', 'Tepito']
                },
                'Tepito': ['Morelos', 'Lagunilla'],
                'Lagunilla': ['Tepito', 'Garibaldi'],
                'Garibaldi': {
                    'connections': {
                        'Linea 8': ['Bellas Artes'],
                    },
                    'next_station': ['Lagunilla', 'Guerrero']
                },
                'Guerrero': {
                    'connections': {
                        'Linea 3': ['Tlatelolco', 'Hidalgo'],
                    },
                    'next_station': ['Garibaldi', 'Buenavista']
                },
                'Buenavista': ['Guerrero'],
            },
            'Linea 12': {
                'Mixcoac': {
                    'connections': {
                        'Linea 7': ['San Antonio', 'Barranca del Muerto'],
                    },
                    'next_station': ['Insurgentes Sur']
                },
                'Insurgentes Sur': ['Mixcoac', 'Hospital 20 de Noviembre'],
                'Hospital 20 de Noviembre': ['Insurgentes Sur', 'Zapata'],
                'Zapata': {
                    'connections': {
                        'Linea 3': ['Division del Norte', 'Coyoacan'],
                    },
                    'next_station': ['20 de Noviembre', 'Parque de los Venados']
                },
                'Parque de los Venados': ['Zapata', 'Eje Central'],
                'Eje Central': ['Parque de los Venados', 'Ermita'],
                'Ermita': {
                    'connections': {
                        'Linea 2': ['Portales', 'General Anaya'],
                    },
                    'next_station': ['Eje Central', 'Mexicaltzingo']
                },
                'Mexicaltzingo': ['Ermita', 'Atlalilco'],
                'Atlalilco': {
                    'connections': {
                        'Linea 8': ['Escuadron 201', 'Iztapalapa'],
                    },
                    'next_station': ['Mexicaltzingo', 'Culhuacan']
                },
                'Culhuacan': ['Atlalilco', 'San Andres Tomatlan'],
                'San Andres Tomatlan': ['Culhuacan', 'Lomas Estrella'],
                'Lomas Estrella': ['San Andres Tomatlan', 'Calle 11'],
                'Calle 11': ['Lomas Estrella', 'Periferico Oriente'],
                'Periferico Oriente': ['Calle 11', 'Tezonco'],
                'Tezonco': ['Periferico Oriente', 'Olivos'],
                'Olivos': ['Tezonco', 'Nopalera'],
                'Nopalera': ['Olivos', 'Zapotitlan'],
                'Zapotitlan': ['Nopalera', 'Tlaltenco'],
                'Tlaltenco': ['Zapotitlan', 'Tlahuac'],
                'Tlahuac': ['Tlaltenco'],
            }
        }


        for station in self.subway.keys():
         self.pesos[station] = 1  # Peso uniforme para la demostración
    
    """
        Realiza una búsqueda en amplitud (BFS) para encontrar la ruta más corta entre dos estaciones en el sistema de metro.

        Parámetros:
        - origin (tuple): Tupla que contiene la línea y la estación de origen.
        - destination (tuple): Tupla que contiene la línea y la estación de destino.

        Retorna:
        - tuple: Una tupla conteniendo la ruta como una lista de estaciones, el número de pasos, y un booleano indicando si se encontró una ruta.

        Descripción:
        Utiliza una cola para explorar las estaciones desde el origen y sigue las conexiones hasta encontrar el destino.
        Registra las estaciones visitadas para evitar procesarlas múltiples veces.
      """

    def bfs(self, origin, destination):
    
      origin_line, origin_station = origin
      destination_line, destination_station = destination
      queue = deque([(origin_line, origin_station, [(origin_line, origin_station)])])
      seen = set([(origin_line, origin_station)])
      
      while queue:
          current_line, current_station, path = queue.popleft()
          current_station_info = self.subway[current_line].get(current_station)
          
          if isinstance(current_station_info, dict):
              next_stations = current_station_info.get('next_station', [])
              connections = current_station_info.get('connections', {})
          else:
              next_stations = current_station_info
              connections = {}
          
          if (current_line, current_station) == (destination_line, destination_station):
              return path, len(path) - 1, True  # Ruta encontrada
          
          if next_stations is not None:  # Verificar si next_stations no es None
              for neighbor in next_stations:
                  if (current_line, neighbor) not in seen:
                      seen.add((current_line, neighbor))
                      queue.append((current_line, neighbor, path + [(current_line, neighbor)]))
          
          for line, trans_stations in connections.items():
              for trans_station in trans_stations:
                  if (line, trans_station) not in seen:
                      seen.add((line, trans_station))
                      queue.append((line, trans_station, path + [(line, trans_station)]))
      
      return [], float('inf'), False  # No se encontró ruta

      """
      Adapta o encuentra una ruta desde el origen hasta el destino, utilizando rutas caché si es posible.

        Parámetros:
        - origin (tuple): Tupla que contiene la línea y la estación de origen.
        - destination (tuple): Tupla que contiene la línea y la estación de destino.

        Retorna:
        - tuple: Una tupla conteniendo la ruta como una lista de estaciones, el número de pasos, y un booleano indicando si se encontró una ruta.

        Descripción:
        Primero intenta utilizar una ruta existente en la caché. Si no es posible, realiza una búsqueda en amplitud (BFS) para encontrar una ruta nueva.
        Si se encuentra una nueva ruta, la guarda en el archivo de rutas.
      """



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
      route, steps, found_route = self.bfs(origin, destination)
      if found_route:
          print("Ruta encontrada mediante BFS.")
          # Verificar si la ruta ya existe en las rutas guardadas en el archivo
          if (origin, destination) not in self.rutas:
              print("Guardando ruta en el archivo...")
              self.rutas[(origin, destination)] = (route, steps)
              self.rutas[(destination, origin)] = (route[::-1], steps)
              save_route_to_file(route, steps, self.rutas)
      return route, steps, found_route


    

    """
        Busca una ruta entre el origen y el destino en el caché de rutas.

        Parámetros:
        - origin (tuple): Tupla que contiene la línea y la estación de origen.
        - destination (tuple): Tupla que contiene la línea y la estación de destino.

        Retorna:
        - tuple: Una tupla conteniendo la ruta como una lista de estaciones, el número de pasos y un booleano indicando si se encontró una ruta.

        Descripción:
        Verifica si existe una ruta directa entre el origen y el destino en el caché.
        Si no se encuentra una ruta directa, intenta adaptar una subruta de las rutas guardadas en el caché que pueda satisfacer la solicitud.
        """
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
    
        return None
     # No se encontró una ruta útil en caché


    """
        Limpia y elimina rutas redundantes del caché de rutas.

        Parámetros:
        - filename (str, opcional): Nombre del archivo donde se guardan las rutas, para actualizarlo tras la limpieza.

        Descripción:
        Revisa todas las rutas guardadas y elimina aquellas que son subrutas de otras rutas más completas.
        Actualiza el archivo de rutas para reflejar solo las rutas no redundantes.
        """

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

       

    """
        Determina si una ruta es subruta de otra.

        Parámetros:
        - subroute (list): La posible subruta a verificar.
        - route (list): La ruta principal contra la cual se verifica la subruta.

        Retorna:
        - bool: True si subroute es una subruta de route, de lo contrario False.

        Descripción:
        Verifica si todos los elementos de la subruta están en la ruta principal en el mismo orden, lo cual indicaría que subroute es una parte de route.
        """
             
    def is_subroute(self, subroute, route):
      
        try:
            # Encontrar índices de inicio y fin de la subruta en la ruta principal
            start_index = route.index(subroute[0])
            end_index = route.index(subroute[-1], start_index)  # Buscar fin desde el inicio encontrado
            # Comprobar si los segmentos coinciden
            return route[start_index:end_index + 1] == subroute
        except ValueError:
            return False  # Retorna Falso si no se encuentra algún elemento

"""
    Aplicación GUI para la interacción con el sistema de metro.

    Descripción:
    Provee una interfaz gráfica de usuario para seleccionar la línea y estación de origen y destino,
    y para buscar rutas entre estas estaciones usando la instancia de la clase Subway.
    """

class SubwayApp(QWidget):
  
    """
        Inicializa la aplicación de metro con una instancia del sistema de metro.

        Parámetros:
        - subway_system (Subway): La instancia del sistema de metro utilizada para operaciones de ruta.
        """
    
    def __init__(self, subway_system):
        
        super().__init__()
        self.subway = subway_system  # Supongo que esta es una instancia de alguna clase que gestiona el sistema de metro.
        self.initUI()

    """
        Configura la interfaz de usuario, incluyendo widgets para la selección de líneas y estaciones y para mostrar resultados.
        """

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

    """
        Actualiza la lista de estaciones disponibles en el combo de estación de origen basado en la línea seleccionada.
        """
    def updateOriginStations(self):
       
        current_line = self.origin_line_combo.currentText()
        stations = sorted(self.subway.subway[current_line].keys())
        self.origin_station_combo.clear()
        self.origin_station_combo.addItems(stations)
    
    """
        Actualiza la lista de estaciones disponibles en el combo de estación de destino basado en la línea seleccionada.
        """

    def updateDestinationStations(self):
       
        current_line = self.destination_line_combo.currentText()
        stations = sorted(self.subway.subway[current_line].keys())
        self.destination_station_combo.clear()
        self.destination_station_combo.addItems(stations)

    """
        Encuentra una ruta entre la estación de origen y destino seleccionadas y muestra los resultados en la interfaz.
        """

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


"""
def heuristic(self, current, goal):
    # Extrae la línea y estación actual de la tupla 'current'.
    current_line, current_station = current
    # Extrae la línea y estación objetivo de la tupla 'goal'.
    goal_line, goal_station = goal

    # Verifica si la estación actual y la estación objetivo están en la misma línea.
    if current_line == goal_line:
        # Si están en la misma línea, obtiene una lista de todas las estaciones en esa línea.
        stations = list(self.subway[current_line].keys())
        # Calcula y devuelve la diferencia absoluta de índices entre la estación actual y la estación objetivo.
        # Esto representa la cantidad mínima de estaciones que deben cruzarse para llegar al objetivo directamente en la misma línea.
        return abs(stations.index(current_station) - stations.index(goal_station))
    # Si las estaciones están en líneas diferentes, devuelve un valor heurístico arbitrario, en este caso 20.
    return 20


def a_star(self, origin, destination):
    # Extraemos las líneas y estaciones de origen y destino.
    origin_line, origin_station = origin
    destination_line, destination_station = destination

    # Inicializamos la cola de prioridad para controlar los nodos a explorar, con el primer nodo siendo el origen.
    # Utilizamos una función heurística para estimar el costo total desde el origen hasta el destino inicialmente.
    queue = []
    heapq.heappush(queue, (0 + self.heuristic(origin, destination), 0, origin, [origin]))
    
    # Conjunto para mantener un registro de las estaciones ya vistas y evitar reevaluarlas.
    seen = set([origin])
    
    while queue:
        # Extraemos el nodo con el menor costo estimado de la cola de prioridad.
        estimated_total_cost, accrued_cost, (current_line, current_station), path = heapq.heappop(queue)
        
        # Obtenemos información sobre la estación actual; puede ser un diccionario si tiene conexiones o una lista si solo tiene estaciones siguientes.
        current_station_info = self.subway[current_line].get(current_station)
        
        # Verificamos si la información de la estación es un diccionario (tiene conexiones) o solo una lista de estaciones adyacentes.
        if isinstance(current_station_info, dict):
            next_stations = current_station_info.get('next_station', [])
            connections = current_station_info.get('connections', {})
        else:
            next_stations = current_station_info
            connections = {}
        
        # Verificamos si hemos llegado al destino.
        if (current_line, current_station) == destination:
            return path, len(path) - 1, True
        
        # Exploramos todas las estaciones adyacentes.
        for next_station in next_stations:
            if (current_line, next_station) not in seen:
                seen.add((current_line, next_station))
                # Calculamos el nuevo costo acumulado y lo agregamos a la cola con la nueva estimación heurística.
                new_cost = accrued_cost + 1  # Suponemos un costo uniforme por estación.
                heapq.heappush(queue, (new_cost + self.heuristic((current_line, next_station), destination), new_cost, (current_line, next_station), path + [(current_line, next_station)]))
        
        # Exploramos todas las conexiones a otras líneas.
        for line, trans_stations in connections.items():
            for trans_station in trans_stations:
                if (line, trans_station) not in seen:
                    seen.add((line, trans_station))
                    # Igual que para las estaciones adyacentes, calculamos el nuevo costo y actualizamos la cola.
                    new_cost = accrued_cost + 1  # Suponemos un costo uniforme por cada transferencia.
                    heapq.heappush(queue, (new_cost + self.heuristic((line, trans_station), destination), new_cost, (line, trans_station), path + [(line, trans_station)]))
    
    # Si agotamos la cola y no encontramos una ruta, devolvemos un resultado negativo.
    return [], float('inf'), False  # Indica que no se encontró ruta.
"""