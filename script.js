const serverIp = "http://192.168.1.5:5134"; // Asegurate que este puerto sea el correcto del servidor

$("#uploadForm").on("submit", async function (e) {
  e.preventDefault();
  const files = $("#fileInput")[0].files;

  if (!files.length) {
    alert("Seleccioná al menos un archivo");
    return;
  }

  for (const file of files) {
    // Crear la vista previa
    const reader = new FileReader();

    reader.onload = function (e) {
      const ext = file.type.startsWith("video") ? "video" : "img";
      const content = `
        <div class="col-6 col-md-4">
          <${ext} src="${e.target.result}" controls class="w-100"></${ext}>
        </div>
      `;
      $("#gallery").append(content);
    };

    reader.readAsDataURL(file);

    // Subida al servidor ASP.NET
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(`${serverIp}/Upload/upload`, {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        console.log(`${file.name} subido correctamente`);
      } else {
        console.error(`Error al subir ${file.name}:`, await response.text());
        alert(`Error al subir ${file.name}`);
      }
    } catch (error) {
      console.error("Fallo de conexión con el servidor:", error);
      alert("No se pudo conectar con el servidor. Asegurate que esté encendido.");
    }
  }
});
