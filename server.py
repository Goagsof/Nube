import os
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import uuid
from flask_cors import CORS # Necesario para permitir solicitudes desde GitHub Pages

app = Flask(__name__) # Inicializa la aplicación Flask
CORS(app) # Habilita CORS para todas las rutas. ¡Esto es crucial para GitHub Pages!

# Define la carpeta donde se guardarán los archivos subidos.
# Crea la carpeta 'uploads' si no existe.
UPLOAD_FOLDER = 'uploads'
# Obtén la ruta absoluta de la carpeta 'Nube' donde está server.py
base_dir = os.path.dirname(os.path.abspath(__file__))
full_upload_path = os.path.join(base_dir, UPLOAD_FOLDER)

if not os.path.exists(full_upload_path):
    os.makedirs(full_upload_path)
app.config['UPLOAD_FOLDER'] = full_upload_path # Configura la ruta de subida en Flask

# Tipos de archivo permitidos para la validación (opcional)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'mp4', 'mov', 'avi'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- RUTAS DE LA API ---

# RUTA: Para subir MÚLTIPLES archivos (ENDPOINT: /upload-files)
@app.route('/upload-files', methods=['POST'])
def upload_files():
    print(f"[{os.path.basename(__file__)} {os.getenv('FLASK_ENV', 'development')}] Received POST /upload-files request.")

    if 'files' not in request.files:
        print(f"[{os.path.basename(__file__)}] No 'files' key in request.files.")
        return jsonify({"message": "No se encontraron archivos en la solicitud."}), 400

    files = request.files.getlist('files')
    if not files:
        print(f"[{os.path.basename(__file__)}] No files selected for upload (empty list).")
        return jsonify({"message": "No se seleccionaron archivos para subir."}), 400

    uploaded_file_names = []
    failed_file_names = []

    for file in files:
        if file.filename == '':
            failed_file_names.append("Archivo desconocido (vacío)")
            print(f"[{os.path.basename(__file__)}] Empty filename detected.")
            continue

        if file and allowed_file(file.filename):
            original_filename = secure_filename(file.filename) # Limpia el nombre del archivo para seguridad

            # Generar un nombre de archivo único para evitar colisiones
            name, ext = os.path.splitext(original_filename)
            unique_filename = f"{name}_{uuid.uuid4().hex[:8]}{ext}" # Ejemplo: "mi_foto_abcdefgh.jpg"

            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)

            try:
                file.save(filepath)
                uploaded_file_names.append(original_filename)
                print(f"[{os.path.basename(__file__)}] Saved: {unique_filename}")
            except Exception as e:
                failed_file_names.append(f"{original_filename} (Error: {str(e)})")
                print(f"[{os.path.basename(__file__)}] Error saving {original_filename}: {str(e)}")
        else:
            failed_file_names.append(f"{file.filename} (Error: Tipo de archivo no permitido o nombre inválido.)")
            print(f"[{os.path.basename(__file__)}] File not allowed: {file.filename}")

    if uploaded_file_names and not failed_file_names:
        print(f"[{os.path.basename(__file__)}] All files uploaded successfully. Count: {len(uploaded_file_names)}")
        return jsonify({"message": "Todos los archivos se subieron correctamente.", "uploaded": uploaded_file_names}), 200
    elif uploaded_file_names and failed_file_names:
        print(f"[{os.path.basename(__file__)}] Some files uploaded, some failed. Uploaded: {len(uploaded_file_names)}, Failed: {len(failed_file_names)}")
        return jsonify({
            "message": "Algunos archivos subidos correctamente, otros fallaron.",
            "uploaded": uploaded_file_names,
            "failed": failed_file_names
        }), 206 # Partial Content
    else:
        print(f"[{os.path.basename(__file__)}] No files could be uploaded.")
        return jsonify({"message": "Ningún archivo pudo ser subido.", "failed": failed_file_names}), 500

# RUTA: Para listar todos los archivos subidos (ENDPOINT: /list-files)
@app.route('/list-files', methods=['GET'])
def list_files():
    print(f"[{os.path.basename(__file__)}] Received GET /list-files request.")
    files = []
    try:
        # os.listdir(app.config['UPLOAD_FOLDER']) lista los nombres de archivos dentro de la carpeta 'uploads'
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            if allowed_file(filename): # Filtra por extensiones permitidas si deseas
                files.append(filename)
        print(f"[{os.path.basename(__file__)}] Found {len(files)} files in uploads folder.")
    except FileNotFoundError:
        print(f"[{os.path.basename(__file__)}] Uploads folder not found: {app.config['UPLOAD_FOLDER']}")
        return jsonify({"message": "Carpeta de subidas no encontrada."}), 404
    except Exception as e:
        print(f"[{os.path.basename(__file__)}] Error listing files: {str(e)}")
        return jsonify({"message": f"Error al listar archivos: {str(e)}"}), 500

    return jsonify(files), 200

# RUTA: Para servir archivos estáticos desde la carpeta 'uploads' (ENDPOINT: /uploads/<nombre_archivo>)
@app.route('/uploads/<path:filename>')
def serve_uploaded_file(filename):
    print(f"[{os.path.basename(__file__)}] Serving uploaded file: {filename}")
    # send_from_directory maneja la seguridad y los tipos MIME automáticamente
    # Sirve el archivo desde la carpeta 'uploads'
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# --- RUTAS DE SERVICIO WEB (para probar localmente si quieres) ---
# RUTA: Para servir index.html por defecto cuando acceden a la raíz (ENDPOINT: /)
@app.route('/')
def index():
    print(f"[{os.path.basename(__file__)}] Root path accessed (serving index.html).")
    # Asume que index.html está en el mismo directorio que server.py
    return send_from_directory(base_dir, 'index.html')


if __name__ == '__main__':
    print("==================================================")
    print("Servidor Python Flask iniciado.")
    print("Accede a tu galería desde tu navegador/celular en:")
    print(f"  http://192.168.0.14:5000/") # Usando tu IP local
    print(f"  (o http://127.0.0.1:5000/ si estás en la misma máquina)")
    print(f"Los archivos se guardarán en la carpeta: {full_upload_path}")
    print("Presiona Ctrl+C para detener el servidor.")
    print("==================================================")
    # La IP 0.0.0.0 permite que el servidor sea accesible desde otras máquinas en la misma red.
    # El puerto 5000 es el que ahora estamos usando (coincidiendo con tu última salida de Flask).
    # debug=True es útil para desarrollo, muestra errores detallados y recarga el servidor al guardar cambios.
    app.run(host='0.0.0.0', port=5000, debug=True)