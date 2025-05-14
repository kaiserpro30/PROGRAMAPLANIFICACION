import streamlit as st
import dropbox
from datetime import datetime
from PIL import Image

# Configurar la página
st.set_page_config(page_title="Revisión de OT", layout="wide", page_icon="📁")

# Cargar el logo
logo = "logo_inamar.png"
col1, col2 = st.columns([1, 8])
with col1:
    st.image(logo, width=100)
with col2:
    st.markdown("<h1 style='color: white; background-color: #003865; padding: 10px;'>Área Planificación</h1>", unsafe_allow_html=True)

# Separador visual
st.markdown("---")

# Autenticación de Dropbox (el token debe estar seguro)
DROPBOX_TOKEN = st.secrets["DROPBOX_TOKEN"]
dbx = dropbox.Dropbox(DROPBOX_TOKEN)

# Pestañas
tabs = st.tabs(["📂 Revisión de Archivos", "📸 Cargar Foto a OT"])

# --- TAB 1: Revisión de Archivos ---
with tabs[0]:
    st.subheader("🔍 Buscar archivos")

    nombre_archivo = st.text_input("🔎 Nombre del archivo a buscar")
    carpeta_busqueda = st.text_input("📂 Carpeta dentro de Dropbox", value="/")

    if st.button("Buscar"):
        try:
            resultados = dbx.files_search_v2(query=nombre_archivo, options=dropbox.files.SearchOptions(path=carpeta_busqueda)).matches
            if resultados:
                st.success(f"{len(resultados)} archivo(s) encontrados")
                for archivo_metadata in resultados:
                    archivo = archivo_metadata.metadata.get_metadata()
                    st.markdown(f"**📄 {archivo.name}**")
                    st.write(f"📁 Carpeta: `{archivo.path_display.rsplit('/', 1)[0]}`")
                    fecha_modificacion = getattr(archivo, 'client_modified', None) or archivo.server_modified
                    st.write(f"🕒 Modificado: {fecha_modificacion.strftime('%Y-%m-%d %H:%M')}")
                    try:
                        link = dbx.sharing_create_shared_link_with_settings(archivo.path_display).url
                        st.markdown(f"[🔗 Descargar archivo]({link})")
                    except Exception as e:
                        st.warning("No se pudo generar el enlace de descarga.")
            else:
                st.warning("No se encontraron archivos.")
        except Exception as e:
            st.error(f"❌ Error al buscar: {e}")