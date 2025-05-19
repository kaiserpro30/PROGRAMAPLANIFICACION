
import streamlit as st
import dropbox
from dropbox.files import WriteMode, SearchOptions, FileMetadata

import io
from datetime import datetime

st.set_page_config(page_title="Revisión de OT", layout="wide")

st.title("📁 Revisión de OT")
st.write("Busca, visualiza y descarga archivos desde una OT")

# Autenticación con Dropbox
DROPBOX_TOKEN = st.secrets["DROPBOX_TOKEN"] if "DROPBOX_TOKEN" in st.secrets else "YOUR_DROPBOX_ACCESS_TOKEN"
dbx = dropbox.Dropbox(DROPBOX_TOKEN)

# Función para obtener carpetas dentro de una ruta raíz
@st.cache_data
def listar_carpetas(dropbox_path="/"):
    try:
        carpetas = []
        lista = dbx.files_list_folder(dropbox_path)
        for entrada in lista.entries:
            if isinstance(entrada, dropbox.files.FolderMetadata):
                carpetas.append(entrada.path_display)
        return carpetas
    except Exception as e:
        st.error(f"Error al listar carpetas: {e}")
        return []

# Pestañas
tab1, tab2 = st.tabs(["🔍 Revisión de Archivos", "📷 Cargar Foto a OT"])

with tab1:
    st.subheader("🔍 Buscar archivos en Dropbox")
    archivo = st.text_input("🔍 Nombre del archivo a buscar:", "")
    carpeta = st.text_input("📁 Carpeta dentro de Dropbox (ej: /Proyectos)", "/")

    if st.button("Buscar archivo"):
        try:
            results = dbx.files_search_v2(
                query=archivo,
                options=SearchOptions(
                    path=carpeta,
                    max_results=100,
                    filename_only=True
                )
            )
            matches = results.matches if hasattr(results, 'matches') else []

            archivos_validos = [m for m in matches if isinstance(m.metadata.get_metadata(), FileMetadata)]

            if archivos_validos:
                st.success(f"🔎 Se encontraron {len(archivos_validos)} archivo(s):")
                for match in archivos_validos:
                    metadata = match.metadata.get_metadata()
                    ruta = metadata.path_display
                    st.markdown(f"- 📄 `{ruta}`")
            else:
                st.warning("⚠️ No se encontraron archivos.")
        except Exception as e:
            st.error(f"❌ Error al buscar: {e}")

with tab2:
    st.subheader("📷 Tomar y Guardar Foto en Dropbox")

    # Obtener carpetas disponibles
    carpetas_disponibles = listar_carpetas("/")
    carpeta_seleccionada = st.selectbox("📁 Selecciona carpeta de destino:", carpetas_disponibles)

    # Capturar imagen desde cámara
    foto = st.camera_input("📸 Toma una foto")

    if foto is not None:
        nombre_archivo = f"foto_ot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        ruta_completa = f"{carpeta_seleccionada}/{nombre_archivo}"

        if st.button("📤 Guardar en Dropbox"):
            try:
                dbx.files_upload(foto.getvalue(), ruta_completa, mode=WriteMode("overwrite"))
                st.success(f"✅ Foto guardada en: {ruta_completa}")
            except Exception as e:
                st.error(f"❌ Error al guardar la imagen: {e}")
