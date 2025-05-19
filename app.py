
import streamlit as st
import dropbox
from dropbox.files import SearchOptions, FileMetadata

st.set_page_config(page_title="Revisión de OT", layout="wide")

st.title("📁 Revisión de OT")
st.write("Busca, visualiza y descarga archivos desde una OT")

# Autenticación con Dropbox
DROPBOX_TOKEN = st.secrets["DROPBOX_TOKEN"] if "DROPBOX_TOKEN" in st.secrets else "YOUR_DROPBOX_ACCESS_TOKEN"
dbx = dropbox.Dropbox(DROPBOX_TOKEN)

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
