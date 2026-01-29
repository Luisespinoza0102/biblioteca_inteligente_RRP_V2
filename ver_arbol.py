import os

def generar_arbol(ruta, prefijo='', ignore_dirs=None, include_ext=None):
    if ignore_dirs is None:
        ignore_dirs = ['__pycache__', '.idea', '.git', 'migrations', 'venv', 'env']
    if include_ext is None:
        # Aquí pones las extensiones que sí quieres ver
        include_ext = ['.py', '.html', '.css', '.js']

    archivos = os.listdir(ruta)
    # Filtramos para que solo aparezcan carpetas que no queremos ignorar
    archivos = [a for a in archivos if a not in ignore_dirs]
    
    for i, archivo in enumerate(sorted(archivos)):
        ruta_completa = os.path.join(ruta, archivo)
        es_ultimo = (i == len(archivos) - 1)
        conector = '└── ' if es_ultimo else '├── '
        
        # Si es carpeta, entramos recursivamente
        if os.path.isdir(ruta_completa):
            print(f"{prefijo}{conector}{archivo}/")
            nuevo_prefijo = prefijo + ('    ' if es_ultimo else '│   ')
            generar_arbol(ruta_completa, nuevo_prefijo, ignore_dirs, include_ext)
        else:
            # Si es archivo, solo lo mostramos si tiene la extensión permitida
            if any(archivo.endswith(ext) for ext in include_ext) or archivo == 'manage.py':
                print(f"{prefijo}{conector}{archivo}")

print("Estructura de mi Proyecto Django:")
generar_arbol('.') # El punto significa la carpeta actual