import streamlit as st
import dropbox
from datetime import datetime
from dropbox.files import FolderMetadata

st.set_page_config(page_title="Revisión de OT", layout="wide", page_icon="📁")

st.image("logo_inamar.png", width=180)
st.markdown(
    '<div style="background-color:#003366; padding:10px"><h1 style="color:white; text-align:center;">Área Planificación</h1></div>',
    unsafe_allow_html=True
)

st.title("📁 Revisión de OT")
st.write("Busca, visualiza y descarga archivos desde una OT")

ACCESS_TOKEN = st.secrets["dropbox"]["access_token"]
dbx = dropbox.Dropbox(ACCESS_TOKEN)

tab1, tab2 = st.tabs(["🔍 Revisión de Archivos", "📸 Cargar Foto a OT"])

# Función para listar carpetas
def obtener_carpetas(path_base="/"):
    try:
        resultado = dbx.files_list_folder(path_base)
        carpetas = [entry.path_display for entry in resultado.entries if isinstance(entry, FolderMetadata)]
        return carpetas
    except Exception as e:
        st.error(f"No se pudieron cargar las carpetas: {e}")
        return []

# TAB 2 - Cámara con selección de carpeta
with tab2:
    st.subheader("📷 Toma una foto y guárdala en una carpeta")

    base = st.text_input("📂 Carpeta base de búsqueda", value="/Fotos_OT")
    carpetas_disponibles = obtener_carpetas(base)
    carpeta = st.selectbox("📁 Selecciona carpeta destino:", carpetas_disponibles) if carpetas_disponibles else None

    nombre_foto = st.text_input("📝 Nombre del archivo (sin extensión)", value=f"foto_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    imagen = st.camera_input("📸 Captura con tu cámara")

    if imagen and carpeta and nombre_foto:
        ruta = f"{carpeta}/{nombre_foto}.jpg"
        try:
            dbx.files_upload(imagen.getvalue(), ruta, mode=dropbox.files.WriteMode("overwrite"))
            st.success(f"✅ Foto guardada en `{ruta}`")
        except Exception as e:
            st.error(f"❌ Error al guardar: {e}")