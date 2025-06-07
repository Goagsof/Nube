from flask import Flask, request, send_from_directory, render_template_string
import os
import uuid
import datetime

# Inicializa la aplicación Flask
app = Flask(__name__, static_folder='.', static_url_path='') # Servir archivos estáticos desde la carpeta actual

# Directorio donde se guardarán los archivos subidos
# Esto se resolverá dentro de la misma carpeta donde está server.py
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER) # Crea la carpeta 'uploads' si no existe

# -----------------------------------------------------------
# Ruta principal para servir tu index.html
# Cuando alguien acceda a http://<tu_ip>:5000/
# -----------------------------------------------------------
@app.route('/')
def serve_index():
    # Asume que index.html está en la misma carpeta que server.py
    # Flask buscará index.html en su 'static_folder'
    return send_from_directory(app.static_folder, 'index.html')

# -----------------------------------------------------------
# Endpoint para subir múltiples archivos
# El frontend POSTeará a http://<tu_ip>:5000/uploadMultiple
# -----------------------------------------------------------
@app.route('/uploadMultiple', methods=['POST'])
def upload_multiple_files():
    if 'files' not in request.files:
        return {'message': 'No se encontró la parte de archivos en la solicitud.'}, 400

    files = request.files.getlist('files') # 'files' debe coincidir con formData.append("files", ...) en JS

    if not files:
        return {'message': 'No se seleccionaron archivos para subir.'}, 400

    uploaded_file_names = []
    failed_file_names = []

    for file in files:
        if file.filename == '':
            failed_file_names.append("Archivo desconocido (nombre vacío)")
            continue

        # Generar un nombre de archivo único para evitar colisiones
        original_filename, file_extension = os.path.splitext(file.filename)
        unique_filename = f"{original_filename}_{uuid.uuid4().hex[:8]}{file_extension}"
        
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)

        try:
            file.save(file_path)
            uploaded_file_names.append(file.filename) # Reporta el nombre original
            print(f"Archivo '{file.filename}' subido exitosamente como '{unique_filename}'")
        except Exception as e:
            failed_file_names.append(f"{file.filename} (Error: {str(e)})")
            print(f"Error al subir el archivo '{file.filename}': {str(e)}")

    if uploaded_file_names and not failed_file_names:
        return {'message': 'Todos los archivos se subieron correctamente.', 'uploaded': uploaded_file_names}, 200
    elif uploaded_file_names and failed_file_names:
        return {'message': 'Algunos archivos subidos correctamente, otros fallaron.', 'uploaded': uploaded_file_names, 'failed': failed_file_names}, 206
    else:
        return {'message': 'Ningún archivo pudo ser subido.', 'failed': failed_file_names}, 500

# -----------------------------------------------------------
# Endpoint para listar todos los archivos subidos
# El frontend GETeará a http://<tu_ip>:5000/Upload/list
# -----------------------------------------------------------
@app.route('/Upload/list')
def list_files():
    try:
        files_in_upload_folder = [f for f in os.listdir(UPLOAD_FOLDER) if os.path.isfile(os.path.join(UPLOAD_FOLDER, f))]
        return files_in_upload_folder, 200
    except Exception as e:
        print(f"Error al listar archivos: {str(e)}")
        return {'message': f"Error al listar archivos: {str(e)}"}, 500

# -----------------------------------------------------------
# Endpoint para servir un archivo específico
# El frontend GETeará a http://<tu_ip>:5000/Upload/files/<nombre_archivo>
# -----------------------------------------------------------
@app.route('/Upload/files/<filename>')
def serve_uploaded_file(filename):
    # send_from_directory es seguro y busca el archivo dentro de la carpeta especificada
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    # Obtener la IP local de la máquina
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80)) # Conectar a una IP externa (Google DNS) para obtener la IP de la interfaz activa
    local_ip = s.getsockname()[0]
    s.close()

    port = 5000 # Puedes cambiar el puerto si lo necesitas, pero asegúrate de actualizar el JS

    print(f"==================================================")
    print(f"Servidor Python Flask iniciado.")
    print(f"Accede a tu galería desde tu navegador/celular en:")
    print(f"  http://{local_ip}:{port}/")
    print(f"  (o http://127.0.0.1:{port}/ si estás en la misma máquina)")
    print(f"Los archivos se guardarán en la carpeta: {os.path.abspath(UPLOAD_FOLDER)}")
    print(f"Presiona Ctrl+C para detener el servidor.")
    print(f"==================================================")

    # Ejecuta la aplicación Flask
    # host='0.0.0.0' hace que sea accesible desde cualquier IP en tu red local.
    app.run(host='0.0.0.0', port=port, debug=True) # debug=True para ver errores en la consola