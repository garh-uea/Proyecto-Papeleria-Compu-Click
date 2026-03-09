import os
import json
import csv

# Carpeta donde se guardarán los archivos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CARPETA_DATA = os.path.join(BASE_DIR, "data")

RUTA_TXT = os.path.join(CARPETA_DATA, "datos.txt")
RUTA_JSON = os.path.join(CARPETA_DATA, "datos.json")
RUTA_CSV = os.path.join(CARPETA_DATA, "datos.csv")


class PersistenciaArchivos:

    # ================= TXT =================
    def guardar_txt(self, id, nombre, cantidad, precio):

        with open(RUTA_TXT, "a", encoding="utf-8") as archivo:
            linea = f"{id},{nombre},{cantidad},{precio}\n"
            archivo.write(linea)

    def leer_txt(self):

        datos = []

        if os.path.exists(RUTA_TXT):
            with open(RUTA_TXT, "r", encoding="utf-8") as archivo:

                for linea in archivo:
                    datos.append(linea.strip().split(","))

        return datos

    # ================= JSON =================
    def guardar_json(self, id, nombre, cantidad, precio):

        producto = {
            "id": id,
            "nombre": nombre,
            "cantidad": cantidad,
            "precio": precio
        }

        datos = []

        if os.path.exists(RUTA_JSON):
            with open(RUTA_JSON, "r", encoding="utf-8") as archivo:
                try:
                    datos = json.load(archivo)
                except:
                    datos = []

        datos.append(producto)

        with open(RUTA_JSON, "w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, indent=4)

    def leer_json(self):

        if os.path.exists(RUTA_JSON):

            with open(RUTA_JSON, "r", encoding="utf-8") as archivo:
                try:
                    return json.load(archivo)
                except:
                    return []

        return []

    # ================= CSV =================
    def guardar_csv(self, id, nombre, cantidad, precio):

        existe = os.path.exists(RUTA_CSV)

        with open(RUTA_CSV, "a", newline="", encoding="utf-8") as archivo:

            writer = csv.writer(archivo)

            if not existe:
                writer.writerow(["id", "nombre", "cantidad", "precio"])

            writer.writerow([id, nombre, cantidad, precio])

    def leer_csv(self):

        datos = []

        if os.path.exists(RUTA_CSV):

            with open(RUTA_CSV, "r", encoding="utf-8") as archivo:

                reader = csv.reader(archivo)

                next(reader, None)

                for fila in reader:
                    datos.append(fila)

        return datos