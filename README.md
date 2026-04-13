# Investigación Histórica

Herramienta en Python para cargar, explorar y analizar colecciones de datos históricos almacenados en archivos **JSON**, **Markdown** y **PDF**.

## Estructura del proyecto

```
investigacion-historica/
├── datos/                        # Archivos de datos históricos
│   ├── eventos_historicos.json
│   ├── personajes_historicos.json
│   ├── fuentes_bibliograficas.json
│   └── *.md / *.pdf              # Documentos narrativos y fuentes
├── reportes/                     # Reportes generados (excluidos del repositorio)
├── tests/
│   └── test_analizador.py        # Pruebas unitarias e integración
├── analizador.py                 # Script principal de análisis
├── utilidades.py                 # Funciones auxiliares reutilizables
├── requirements.txt              # Dependencias del proyecto
└── README.md
```

## Formatos de datos soportados

### JSON

Cada archivo JSON debe seguir esta estructura general:

```json
{
  "coleccion": "Nombre de la colección",
  "descripcion": "Descripción breve",
  "version": "1.0",
  "<tipo>": [
    {
      "id": 1,
      "titulo": "...",
      "fecha": "YYYY-MM-DD",
      "categoria": "...",
      "importancia": "alta | media | baja",
      ...
    }
  ]
}
```

El campo raíz que contiene la lista puede llamarse `eventos`, `personajes`, `fuentes`, `documentos`, `lugares`, `periodos`, `hechos` o `registros`. También se detecta automáticamente cualquier campo que contenga una lista.

### Markdown

Los archivos `.md` se analizan extrayendo sus encabezados y el contenido de cada sección. Se admiten en la carpeta `datos/` o como argumento directo.

### PDF

Los archivos `.pdf` se analizan extrayendo el texto de cada página. Requieren la dependencia `pypdf`.

## Instalación de dependencias

```bash
pip install -r requirements.txt
```

## Uso

### Analizar todos los archivos en `datos/` (JSON, MD y PDF)

```bash
python analizador.py
```

### Analizar un archivo específico

```bash
python analizador.py datos/eventos_historicos.json
python analizador.py datos/av_estrategia_impacto.md
python analizador.py 05-de-la-nostalgia.pdf
```

### Buscar un término en todos los datos

```bash
python analizador.py --buscar "Zapata"
```

### Generar un reporte completo (texto + JSON) en `reportes/`

```bash
python analizador.py --reporte
```

### Filtrar registros por campo y valor

```bash
python analizador.py --filtrar importancia alta
```

### Ordenar registros cronológicamente

```bash
python analizador.py --ordenar-fecha fecha
```

### Combinar opciones

```bash
python analizador.py --filtrar categoria Revolución --ordenar-fecha fecha --reporte
```

## Agregar tus propios datos

1. Crea un archivo `.json`, `.md` o `.pdf` dentro de la carpeta `datos/`.
2. Ejecuta `python analizador.py` y el archivo será detectado y analizado automáticamente.

## Ejecutar las pruebas

```bash
python -m unittest tests/test_analizador.py -v
```
