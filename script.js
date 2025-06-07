// La IP del servidor Python.
// ¡Asegúrate que este puerto y las rutas coincidan con tu server.py!
const serverIp = "http://192.168.0.14:5000"; // <--- CAMBIADO: Puerto a 5000

// Función para cargar y mostrar archivos desde el servidor
async function loadGalleryImages() {
  try {
    // CAMBIADO: La ruta para listar ahora es /Upload/list
    const response = await fetch(`${serverIp}/Upload/list`);
    if (!response.ok) {
      throw new Error(`Error HTTP: ${response.status} - ${response.statusText}`);
    }
    const files = await response.json();

    const gallery = $("#gallery");
    gallery.empty();

    if (files.length === 0) {
      gallery.append('<p class="text-center text-muted">No hay fotos o videos subidos aún.</p>');
      return;
    }

    files.forEach(fileName => {
      const ext = fileName.split('.').pop().toLowerCase();
      let tag;
      let isMedia = true;

      switch (ext) {
        case 'jpg':
        case 'jpeg':
        case 'png':
        case 'gif':
        case 'webp':
          tag = 'img';
          break;
        case 'mp4':
        case 'mov':
        case 'avi':
          tag = 'video';
          break;
        default:
          isMedia = false;
          break;
      }

      if (isMedia) {
        const content = `
          <div class="col-6 col-md-4">
            <${tag} src="${serverIp}/Upload/files/${fileName}" controls class="w-100"></${tag}> <p class="text-center text-muted small mt-1">${fileName}</p>
          </div>
        `;
        gallery.append(content);
      } else {
        console.log(`Archivo no multimedia o extensión no soportada para previsualización: ${fileName}`);
      }
    });

  } catch (error) {
    console.error("Fallo al cargar archivos desde el servidor:", error);
    $("#gallery").html('<p class="text-center text-danger">No se pudo conectar con el servidor para cargar la galería. Asegúrate que el servidor Python esté encendido y la IP sea correcta.</p>');
  }
}


$("#uploadForm").on("submit", async function (e) {
  e.preventDefault();
  const files = $("#fileInput")[0].files;

  if (!files.length) {
    alert("Seleccioná al menos un archivo");
    return;
  }

  $("#gallery").empty(); // Limpiar la galería antes de las previsualizaciones
  for (const file of files) {
    const reader = new FileReader();

    reader.onload = function (e) {
      const ext = file.type.startsWith("video") ? "video" : "img";
      const content = `
        <div class="col-6 col-md-4">
          <${ext} src="${e.target.result}" controls class="w-100"></${ext}>
          <p class="text-center text-muted small mt-1">Previsualización: ${file.name}</p>
        </div>
      `;
      $("#gallery").append(content);
    };

    reader.readAsDataURL(file);
  }

  const formData = new FormData();
  for (let i = 0; i < files.length; i++) {
    formData.append("files", files[i]);
  }

  try {
    // CAMBIADO: La ruta para subir ahora es /uploadMultiple
    const response = await fetch(`${serverIp}/uploadMultiple`, {
      method: "POST",
      body: formData,
    });

    if (response.ok) {
      const result = await response.json();
      console.log("Subida completada:", result.message);

      if (result.uploaded && result.uploaded.length > 0) {
        console.log("Archivos subidos exitosamente:", result.uploaded);
        alert(`Archivos subidos: ${result.uploaded.join(', ')}`);
      }
      if (result.failed && result.failed.length > 0) {
        console.error("Archivos que fallaron al subir:", result.failed);
        alert(`Hubo problemas al subir los siguientes archivos: ${result.failed.join(', ')}`);
      }

      await loadGalleryImages();

    } else {
      const errorText = await response.text();
      console.error(`Error al subir archivos (HTTP ${response.status}):`, errorText);
      alert(`Error al subir archivos: ${errorText}`);
    }
  } catch (error) {
    console.error("Fallo de conexión con el servidor:", error);
    alert("No se pudo conectar con el servidor. Asegúrate que el servidor Python esté encendido y la IP sea correcta.");
  }
});

$(document).ready(function() {
  loadGalleryImages();
});