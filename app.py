import streamlit as st
import dropbox
from dropbox.files import SearchOptions

# Configuración de la página
st.set_page_config(page_title="Revisión de OT", layout="wide")

# Conexión a Dropbox
dbx = dropbox.Dropbox("TU_ACCESS_TOKEN")

st.title("📁 Revisión de OT")
st.write("Busca, visualiza y descarga archivos desde una OT")

# Pestañas
tabs = st.tabs(["🔍 Revisión de Archivos", "📷 Cargar Foto a OT"])

with tabs[0]:
    st.header("🔍 Buscar archivos en Dropbox")
    nombre_archivo = st.text_input("🔎 Nombre del archivo a buscar:", "")
    carpeta = st.text_input("📂 Carpeta dentro de Dropbox (ej: /Proyectos)", "/")

    if st.button("Buscar archivo") and nombre_archivo:
        try:
            search_options = SearchOptions(path=carpeta, max_results=100, filename_only=True)
            result = dbx.files_search_v2(query=nombre_archivo, options=search_options)
            matches = result.matches
            if matches:
                st.success(f"Se encontraron {len(matches)} archivo(s):")
                for m in matches:
                    metadata = m.metadata.get_metadata()
                    st.write(f"📄 {metadata.name}")
            else:
                st.warning("No se encontraron archivos.")
        except Exception as e:
            st.error(f"❌ Error al buscar: {e}")