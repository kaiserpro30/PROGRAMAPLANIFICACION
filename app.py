
import streamlit as st
import dropbox
from dropbox.files import SearchOptions, FileMetadata

st.set_page_config(page_title="Revision de OT", layout="wide")

st.title("Revision de OT")
st.write("Busca, visualiza y descarga archivos desde una OT")

# Autenticacion con Dropbox
DROPBOX_TOKEN = st.secrets["DROPBOX_TOKEN"] if "DROPBOX_TOKEN" in st.secrets else "YOUR_DROPBOX_ACCESS_TOKEN"
dbx = dropbox.Dropbox(DROPBOX_TOKEN)

# Pestañas
tab1, tab2 = st.tabs(["Revision de Archivos", "Cargar Foto a OT"])

with tab1:
    st.subheader("Buscar archivos en Dropbox")
    archivo = st.text_input("Nombre del archivo a buscar:", "")
    carpeta = st.text_input("Carpeta dentro de Dropbox (ej: /Proyectos)", "/")

    if st.button("Buscar archivo"):
        try:
            search_result = dbx.files_search_v2(
                query=archivo,
                options=SearchOptions(
                    path=carpeta,
                    max_results=100,
                    filename_only=True
                )
            )

            matches = search_result.matches if hasattr(search_result, 'matches') else []

            archivos_validos = [m for m in matches if isinstance(m.metadata.get_metadata(), FileMetadata)]

            if archivos_validos:
                st.success(f"Se encontraron {len(archivos_validos)} archivo(s):")
                for match in archivos_validos:
                    metadata = match.metadata.get_metadata()
                    ruta = metadata.path_display
                    fecha_mod = metadata.client_modified.strftime('%Y-%m-%d %H:%M')
                    enlace = dbx.files_get_temporary_link(ruta).link

                    st.markdown(f"- Archivo: `{ruta}`")
                    st.write(f"  Modificado: {fecha_mod}")
                    st.markdown(f"[Descargar archivo]({enlace})")
            else:
                st.warning("No se encontraron archivos.")

        except dropbox.exceptions.ApiError as api_err:
            st.error(f"Error de Dropbox API: {api_err}")
        except Exception as e:
            st.error(f"Error inesperado: {e}")
