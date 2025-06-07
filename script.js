// The IP address of your Python server on your local network.
// This is critical when your frontend is hosted on a different domain (like GitHub Pages)
// and your backend is running locally on your PC.
// Replace "192.168.0.14" with your actual PC's local IPv4 address if it has changed.
// The port "5500" should match the port your Python server is running on.
const serverIp = "http://192.168.0.14:5500"; 

// Function to load and display files from the server
async function loadGalleryImages() {
  try {
    // The endpoint to list files on the Python server is /list-files
    const response = await fetch(`${serverIp}/list-files`);
    if (!response.ok) {
      throw new Error(`HTTP Error: ${response.status} - ${response.statusText}`);
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
            <${tag} src="${serverIp}/uploads/${fileName}" controls class="w-100"></${tag}>
            <p class="text-center text-muted small mt-1">${fileName}</p>
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

  $("#gallery").empty(); // Clear the gallery before previews
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
    // The field name "files" must match how the Python server expects the files
    formData.append("files", files[i]);
  }

  try {
    // The endpoint to upload files on the Python server is /upload-files
    const response = await fetch(`${serverIp}/upload-files`, {
      method: "POST",
      body: formData,
    });

    if (response.ok) {
      const result = await response.json();
      console.log("Upload completed:", result.message);

      if (result.uploaded && result.uploaded.length > 0) {
        console.log("Files uploaded successfully:", result.uploaded);
        alert(`Archivos subidos: ${result.uploaded.join(', ')}`);
      }
      if (result.failed && result.failed.length > 0) {
        console.error("Files that failed to upload:", result.failed);
        alert(`Hubo problemas al subir los siguientes archivos: ${result.failed.join(', ')}`);
      }

      await loadGalleryImages();

    } else {
      const errorText = await response.text();
      console.error(`Error uploading files (HTTP ${response.status}):`, errorText);
      alert(`Error al subir archivos: ${errorText}`);
    }
  } catch (error) {
    console.error("Connection to server failed:", error);
    alert("No se pudo conectar con el servidor. Asegúrate que el servidor Python esté encendido y la IP sea correcta.");
  }
});

$(document).ready(function() {
  loadGalleryImages();
});