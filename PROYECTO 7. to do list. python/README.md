# Mini servidor Flask (Windows)

Instrucciones mínimas para levantar el servidor y ver cambios en caliente.

1) Crear entorno virtual (PowerShell):

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2) Ejecutar el servidor:

```powershell
python app.py
```

Abrir http://localhost:5000

3) Debug / recarga automática:

El `app.py` inicia Flask con `debug=True`, así que al modificar archivos y guardar, el servidor se recargará automáticamente y verás los cambios sin reiniciar manualmente.
