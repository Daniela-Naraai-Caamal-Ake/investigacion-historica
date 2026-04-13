"""
Módulo de utilidades para el análisis de datos históricos en formato JSON.
Proporciona funciones auxiliares para cargar, validar y procesar datos.
"""

import json
import os
from datetime import datetime


def cargar_json(ruta_archivo):
    """
    Carga y retorna el contenido de un archivo JSON.

    Args:
        ruta_archivo (str): Ruta al archivo JSON.

    Returns:
        dict | list: Contenido del archivo JSON.

    Raises:
        FileNotFoundError: Si el archivo no existe.
        json.JSONDecodeError: Si el archivo no es un JSON válido.
    """
    if not os.path.exists(ruta_archivo):
        raise FileNotFoundError(f"Archivo no encontrado: {ruta_archivo}")

    with open(ruta_archivo, "r", encoding="utf-8") as archivo:
        return json.load(archivo)


def guardar_json(datos, ruta_archivo):
    """
    Guarda datos en un archivo JSON con formato legible.

    Args:
        datos (dict | list): Datos a guardar.
        ruta_archivo (str): Ruta destino del archivo JSON.
    """
    directorio = os.path.dirname(ruta_archivo)
    if directorio and not os.path.exists(directorio):
        os.makedirs(directorio)

    with open(ruta_archivo, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=2)


def listar_archivos_json(directorio):
    """
    Lista todos los archivos JSON en un directorio.

    Args:
        directorio (str): Ruta al directorio a explorar.

    Returns:
        list[str]: Lista de rutas a archivos JSON encontrados.
    """
    if not os.path.isdir(directorio):
        return []

    archivos = []
    for nombre in os.listdir(directorio):
        if nombre.endswith(".json"):
            archivos.append(os.path.join(directorio, nombre))
    return sorted(archivos)


def parsear_fecha(cadena_fecha):
    """
    Intenta parsear una cadena de fecha en varios formatos.

    Args:
        cadena_fecha (str): Cadena con la fecha a parsear.

    Returns:
        datetime | None: Objeto datetime si se pudo parsear, None en caso contrario.
    """
    formatos = ["%Y-%m-%d", "%Y/%m/%d", "%d/%m/%Y", "%d-%m-%Y", "%Y"]
    for fmt in formatos:
        try:
            return datetime.strptime(str(cadena_fecha), fmt)
        except ValueError:
            continue
    return None


def obtener_campo_principal(datos):
    """
    Detecta el campo principal de una colección JSON histórica.

    Busca claves comunes como 'eventos', 'personajes', 'fuentes', etc.

    Args:
        datos (dict): Diccionario con los datos JSON cargados.

    Returns:
        tuple[str, list]: Nombre del campo y su lista de elementos,
                          o (None, []) si no se encuentra.
    """
    claves_conocidas = [
        "eventos", "personajes", "fuentes", "documentos",
        "lugares", "periodos", "hechos", "registros"
    ]
    for clave in claves_conocidas:
        if clave in datos and isinstance(datos[clave], list):
            elementos = [e for e in datos[clave] if isinstance(e, dict)]
            if elementos:
                return clave, elementos

    # Si no coincide ninguna clave conocida, buscar la primera lista de dicts
    for clave, valor in datos.items():
        if isinstance(valor, list) and len(valor) > 0:
            elementos = [e for e in valor if isinstance(e, dict)]
            if elementos:
                return clave, elementos

    return None, []


def contar_por_campo(elementos, campo):
    """
    Cuenta la frecuencia de valores en un campo específico.

    Args:
        elementos (list[dict]): Lista de registros.
        campo (str): Nombre del campo a analizar.

    Returns:
        dict: Diccionario {valor: frecuencia} ordenado por frecuencia descendente.
    """
    conteo = {}
    for elem in elementos:
        valor = elem.get(campo)
        if valor is None:
            continue
        if isinstance(valor, list):
            for v in valor:
                conteo[v] = conteo.get(v, 0) + 1
        else:
            valor_str = str(valor)
            conteo[valor_str] = conteo.get(valor_str, 0) + 1

    return dict(sorted(conteo.items(), key=lambda x: x[1], reverse=True))


def buscar_en_elementos(elementos, termino):
    """
    Busca un término en todos los campos de texto de los elementos.

    Args:
        elementos (list[dict]): Lista de registros a buscar.
        termino (str): Término de búsqueda (no distingue mayúsculas).

    Returns:
        list[dict]: Lista de elementos que contienen el término.
    """
    termino_lower = termino.lower()
    resultados = []

    for elem in elementos:
        encontrado = False
        for valor in elem.values():
            if isinstance(valor, str) and termino_lower in valor.lower():
                encontrado = True
                break
            if isinstance(valor, list):
                for v in valor:
                    if isinstance(v, str) and termino_lower in v.lower():
                        encontrado = True
                        break
        if encontrado:
            resultados.append(elem)

    return resultados


def filtrar_por_campo(elementos, campo, valor):
    """
    Filtra elementos donde un campo específico coincide con un valor.

    Args:
        elementos (list[dict]): Lista de registros.
        campo (str): Nombre del campo a filtrar.
        valor (str): Valor a buscar (no distingue mayúsculas).

    Returns:
        list[dict]: Elementos que coinciden con el filtro.
    """
    valor_lower = str(valor).lower()
    resultados = []
    for elem in elementos:
        campo_valor = elem.get(campo)
        if campo_valor is None:
            continue
        if isinstance(campo_valor, list):
            if any(str(v).lower() == valor_lower for v in campo_valor):
                resultados.append(elem)
        elif str(campo_valor).lower() == valor_lower:
            resultados.append(elem)
    return resultados


def ordenar_por_fecha(elementos, campo_fecha="fecha"):
    """
    Ordena elementos por un campo de fecha de forma cronológica.

    Args:
        elementos (list[dict]): Lista de registros.
        campo_fecha (str): Nombre del campo que contiene la fecha.

    Returns:
        list[dict]: Lista ordenada cronológicamente. Los elementos sin fecha
                    válida se colocan al final.
    """
    def clave_orden(elem):
        fecha_str = elem.get(campo_fecha, "")
        fecha = parsear_fecha(str(fecha_str)) if fecha_str else None
        return fecha if fecha else datetime.max

    return sorted(elementos, key=clave_orden)


def formatear_tabla(elementos, campos=None, ancho_col=25):
    """
    Formatea una lista de elementos como una tabla de texto.

    Args:
        elementos (list[dict]): Lista de registros.
        campos (list[str] | None): Campos a mostrar. Si es None, usa todos.
        ancho_col (int): Ancho máximo por columna.

    Returns:
        str: Tabla formateada como cadena de texto.
    """
    if not elementos:
        return "  (sin resultados)"

    if campos is None:
        campos = list(elementos[0].keys())

    def truncar(texto, max_ancho):
        texto_str = str(texto)
        if isinstance(texto, list):
            texto_str = ", ".join(str(v) for v in texto)
        return texto_str[:max_ancho - 3] + "..." if len(texto_str) > max_ancho else texto_str

    lineas = []
    encabezado = " | ".join(c[:ancho_col].ljust(ancho_col) for c in campos)
    separador = "-+-".join("-" * ancho_col for _ in campos)
    lineas.append(encabezado)
    lineas.append(separador)

    for elem in elementos:
        fila = " | ".join(
            truncar(elem.get(c, ""), ancho_col).ljust(ancho_col) for c in campos
        )
        lineas.append(fila)

    return "\n".join(lineas)
