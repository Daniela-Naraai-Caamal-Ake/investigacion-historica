"""
Módulo de utilidades para el análisis de datos históricos.
Proporciona funciones auxiliares para cargar, validar y procesar datos
en formato JSON, Markdown y PDF.
"""

import json
import os
import re
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


def _listar_archivos_por_extension(directorio, extension):
    """
    Lista recursivamente los archivos de un directorio (y sus subdirectorios)
    que tienen la extensión indicada.

    Args:
        directorio (str): Ruta al directorio raíz a explorar.
        extension (str): Extensión a buscar, incluyendo el punto (ej. '.json').

    Returns:
        list[str]: Lista de rutas encontradas, ordenadas alfabéticamente.
    """
    if not os.path.isdir(directorio):
        return []

    ext_lower = extension.lower()
    rutas = []
    for raiz, _dirs, archivos in os.walk(directorio):
        for nombre in archivos:
            if nombre.lower().endswith(ext_lower):
                rutas.append(os.path.join(raiz, nombre))
    return sorted(rutas)


def listar_archivos_json(directorio):
    """
    Lista todos los archivos JSON en un directorio.

    Args:
        directorio (str): Ruta al directorio a explorar.

    Returns:
        list[str]: Lista de rutas a archivos JSON encontrados.
    """
    return _listar_archivos_por_extension(directorio, ".json")


def listar_archivos_md(directorio):
    """
    Lista todos los archivos Markdown (.md) en un directorio.

    Args:
        directorio (str): Ruta al directorio a explorar.

    Returns:
        list[str]: Lista de rutas a archivos .md encontrados.
    """
    return _listar_archivos_por_extension(directorio, ".md")


def listar_archivos_pdf(directorio):
    """
    Lista todos los archivos PDF (.pdf) en un directorio.

    Args:
        directorio (str): Ruta al directorio a explorar.

    Returns:
        list[str]: Lista de rutas a archivos .pdf encontrados.
    """
    return _listar_archivos_por_extension(directorio, ".pdf")


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
                if not isinstance(v, (str, int, float, bool)):
                    continue
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


def cargar_markdown(ruta_archivo):
    """
    Carga y parsea el contenido de un archivo Markdown.

    Extrae el título (primer encabezado H1), las secciones con su nivel
    y contenido, y el texto completo del documento.

    Args:
        ruta_archivo (str): Ruta al archivo Markdown.

    Returns:
        dict: Diccionario con 'titulo', 'secciones', 'contenido_completo',
              'total_secciones' y 'total_palabras'.

    Raises:
        FileNotFoundError: Si el archivo no existe.
    """
    if not os.path.exists(ruta_archivo):
        raise FileNotFoundError(f"Archivo no encontrado: {ruta_archivo}")

    with open(ruta_archivo, "r", encoding="utf-8") as f:
        contenido = f.read()

    lineas = contenido.splitlines()
    titulo = None
    secciones = []
    seccion_actual = None
    lineas_seccion = []

    for linea in lineas:
        match = re.match(r'^(#{1,6})\s+(.*)', linea)
        if match:
            if seccion_actual is not None:
                seccion_actual["contenido"] = "\n".join(lineas_seccion).strip()
                secciones.append(seccion_actual)

            nivel = len(match.group(1))
            titulo_seccion = match.group(2).strip()

            if titulo is None and nivel == 1:
                titulo = titulo_seccion

            seccion_actual = {"nivel": nivel, "titulo": titulo_seccion, "contenido": ""}
            lineas_seccion = []
        elif seccion_actual is not None:
            lineas_seccion.append(linea)

    if seccion_actual is not None:
        seccion_actual["contenido"] = "\n".join(lineas_seccion).strip()
        secciones.append(seccion_actual)

    if titulo is None:
        titulo = os.path.splitext(os.path.basename(ruta_archivo))[0]

    return {
        "titulo": titulo,
        "secciones": secciones,
        "contenido_completo": contenido,
        "total_secciones": len(secciones),
        "total_palabras": len(contenido.split()),
    }


def extraer_texto_pdf(ruta_archivo):
    """
    Extrae el texto y metadatos de un archivo PDF.

    Requiere la librería 'pypdf'. Instálala con: pip install pypdf

    Args:
        ruta_archivo (str): Ruta al archivo PDF.

    Returns:
        dict: Diccionario con 'paginas', 'total_paginas', 'metadatos'
              y 'contenido_completo'.

    Raises:
        FileNotFoundError: Si el archivo no existe.
        ImportError: Si 'pypdf' no está instalado.
    """
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise ImportError(
            "La librería 'pypdf' es necesaria para procesar PDFs. "
            "Instálala con: pip install pypdf"
        ) from exc

    if not os.path.exists(ruta_archivo):
        raise FileNotFoundError(f"Archivo no encontrado: {ruta_archivo}")

    reader = PdfReader(ruta_archivo)
    paginas = []
    for i, pagina in enumerate(reader.pages, start=1):
        texto = pagina.extract_text() or ""
        paginas.append({"numero": i, "texto": texto.strip()})

    metadatos = {}
    if reader.metadata:
        for clave, valor in reader.metadata.items():
            clave_limpia = clave.lstrip("/")
            if isinstance(valor, str) and valor:
                metadatos[clave_limpia] = valor

    contenido_completo = "\n\n".join(p["texto"] for p in paginas if p["texto"])

    return {
        "paginas": paginas,
        "total_paginas": len(paginas),
        "metadatos": metadatos,
        "contenido_completo": contenido_completo,
    }


def extraer_citas_textos_contextos(datos, categoria_default="Sin categoría", longitud_minima=50):
    """
    Extrae citas largas, textos y contextos de un objeto JSON con sus fuentes.

    Reconoce tres tipos de contenido:
      - ``cita``: campos cuyo nombre contiene "cita" (p. ej. ``cita_directa``,
        ``cita_clave``, ``cita_relevante``).
      - ``texto``: campos con nombre ``texto_completo_transcript``,
        ``texto_decreto`` u otros que empiecen por ``texto_``, así como
        ``descripcion`` cuando su contenido supera ``longitud_minima * 2``.
      - ``contexto``: campos con nombre exacto ``contexto``.

    Args:
        datos (dict): Diccionario con los datos JSON cargados.
        categoria_default (str): Categoría a asignar cuando no se encuentra
            ningún descriptor en el objeto raíz.
        longitud_minima (int): Longitud mínima (en caracteres) para considerar
            un texto como cita larga o contexto relevante.

    Returns:
        list[dict]: Lista de entradas, cada una con las claves:
            ``categoria``, ``tipo``, ``subtipo``, ``texto``, ``fuente``,
            ``origen``.
    """
    # Detectar la categoría principal del documento
    categoria_raiz = (
        datos.get("titulo")
        or datos.get("coleccion")
        or datos.get("nodo_id")
        or categoria_default
    )

    resultados = []

    # Nombres de campo que se tratan como "cita"
    _CITA_PREFIJOS = ("cita",)
    # Nombres de campo que se tratan como "texto"
    _TEXTO_EXACTOS = {"texto_completo_transcript", "texto_decreto"}
    _TEXTO_PREFIJOS = ("texto_",)

    def _es_cita(nombre):
        nl = nombre.lower()
        return any(nl.startswith(p) for p in _CITA_PREFIJOS)

    def _es_texto(nombre):
        nl = nombre.lower()
        return nl in _TEXTO_EXACTOS or any(nl.startswith(p) for p in _TEXTO_PREFIJOS)

    def _es_contexto(nombre):
        return nombre.lower() == "contexto"

    def _resolver_fuente(obj):
        """Busca el campo de fuente más cercano dentro del mismo objeto."""
        if not isinstance(obj, dict):
            return None
        for clave in ("fuente", "fuente_academica", "fuente_primaria",
                      "fuente_secundaria", "referencia", "autor", "fuentes"):
            val = obj.get(clave)
            if val is None:
                continue
            if isinstance(val, str) and val:
                return val
            if isinstance(val, list):
                partes = [str(v) for v in val if isinstance(v, (str, int, float)) and str(v)]
                if partes:
                    return "; ".join(partes[:3])
        return None

    def _recorrer(obj, path, categoria_local):
        if isinstance(obj, dict):
            fuente_local = _resolver_fuente(obj)
            for nombre, valor in obj.items():
                ruta_campo = f"{path}.{nombre}"

                if isinstance(valor, str) and len(valor) >= longitud_minima:
                    tipo = None
                    if _es_cita(nombre):
                        tipo = "cita"
                    elif _es_texto(nombre):
                        tipo = "texto"
                    elif _es_contexto(nombre):
                        tipo = "contexto"
                    elif nombre.lower() == "descripcion" and len(valor) >= longitud_minima * 2:
                        tipo = "texto"

                    if tipo:
                        resultados.append({
                            "categoria": categoria_local,
                            "tipo": tipo,
                            "subtipo": nombre,
                            "texto": valor,
                            "fuente": fuente_local,
                            "origen": ruta_campo,
                        })
                elif isinstance(valor, (dict, list)):
                    # Refinar la categoría usando el subtítulo del registro
                    cat_hijo = categoria_local
                    if isinstance(valor, dict):
                        cat_hijo = (
                            valor.get("subtitulo")
                            or valor.get("titulo")
                            or categoria_local
                        )
                    _recorrer(valor, ruta_campo, cat_hijo)

        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                _recorrer(item, f"{path}[{i}]", categoria_local)

    _recorrer(datos, "", categoria_raiz)
    return resultados


def agrupar_citas_por_categoria(citas):
    """
    Agrupa una lista de entradas de citas por su campo ``categoria``.

    Args:
        citas (list[dict]): Lista producida por :func:`extraer_citas_textos_contextos`.

    Returns:
        dict[str, list[dict]]: Diccionario ``{categoria: [entradas]}``,
            ordenado por nombre de categoría.
    """
    agrupado = {}
    for entrada in citas:
        cat = entrada["categoria"]
        agrupado.setdefault(cat, []).append(entrada)
    return dict(sorted(agrupado.items()))


def normalizar_id_fuente(texto):
    """
    Extrae y normaliza todos los IDs de fuente del tipo ``F###`` o ``FX###``
    presentes en un texto.

    Args:
        texto (str): Cadena de texto donde buscar identificadores de fuente.

    Returns:
        list[str]: Lista de IDs encontrados en mayúsculas, sin duplicados y
                   ordenados alfabéticamente.  Por ejemplo: ['F001', 'FX003'].
    """
    if not isinstance(texto, str):
        return []
    patron = re.compile(r'\bF(?:X)?[0-9]{1,4}\b', re.IGNORECASE)
    ids = {m.upper() for m in patron.findall(texto)}
    return sorted(ids)


def detectar_duplicados(elementos, campo):
    """
    Detecta registros duplicados en una colección JSON según un campo clave.

    Args:
        elementos (list[dict]): Lista de registros a analizar.
        campo (str): Nombre del campo cuyo valor se usa para detectar duplicados.

    Returns:
        dict[str, list[dict]]: Diccionario ``{valor: [registros]}``.
            Solo incluye entradas donde el valor aparece más de una vez.
    """
    conteo = {}
    for elem in elementos:
        valor = elem.get(campo)
        if valor is None:
            continue
        clave = str(valor)
        conteo.setdefault(clave, []).append(elem)
    return {k: v for k, v in conteo.items() if len(v) > 1}


def exportar_csv(elementos, ruta):
    """
    Exporta una lista de registros a un archivo CSV.

    Los valores que sean listas se convierten a cadenas separadas por punto y
    coma.  Si todos los registros comparten las mismas claves, se usan como
    cabecera; de lo contrario, se usa la unión de todas las claves.

    Args:
        elementos (list[dict]): Lista de registros a exportar.
        ruta (str): Ruta destino del archivo CSV (se crea si no existe).

    Returns:
        str: Ruta al archivo creado.

    Raises:
        ValueError: Si la lista de elementos está vacía.
    """
    import csv

    if not elementos:
        raise ValueError("La lista de elementos está vacía; no hay nada que exportar.")

    # Unión ordenada de todas las claves
    campos = list(dict.fromkeys(k for elem in elementos for k in elem.keys()))

    directorio = os.path.dirname(ruta)
    if directorio and not os.path.exists(directorio):
        os.makedirs(directorio)

    with open(ruta, "w", encoding="utf-8", newline="") as archivo:
        escritor = csv.DictWriter(
            archivo,
            fieldnames=campos,
            extrasaction="ignore",
            restval="",
        )
        escritor.writeheader()
        for elem in elementos:
            fila = {}
            for campo in campos:
                valor = elem.get(campo, "")
                if isinstance(valor, list):
                    valor = "; ".join(str(v) for v in valor)
                elif isinstance(valor, dict):
                    valor = json.dumps(valor, ensure_ascii=False)
                fila[campo] = valor
            escritor.writerow(fila)

    return ruta


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



