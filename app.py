import streamlit as st
import dropbox
import pandas as pd
from datetime import datetime
from dropbox.files import FolderMetadata, SearchOptions, WriteMode

st.set_page_config(page_title="Revisión de OT", layout="wide", page_icon="📁")
ACCESS_TOKEN = st.secrets["dropbox"]["access_token"]
dbx = dropbox.Dropbox(ACCESS_TOKEN)

st.image("logo_inamar.png", width=180)
st.markdown('<div style="background-color:#003366; padding:10px"><h1 style="color:white; text-align:center;">Área Planificación</h1></div>', unsafe_allow_html=True)
st.title("📁 Revisión de OT")
st.write("Busca, visualiza y descarga archivos desde una OT")

tab1, tab2 = st.tabs(["🔍 Revisión de Archivos", "📸 Cargar Foto a OT"])

def obtener_todas_las_carpetas():
    try:
        resultado = dbx.files_list_folder("", recursive=True)
        return [e.path_display for e in resultado.entries if isinstance(e, FolderMetadata)]
    except Exception as e:
        st.error(f"No se pudo cargar la lista de carpetas: {e}")
        return []

def buscar_archivos(nombre, carpeta=""):
    try:
        resultados = dbx.files_search_v2(
            query=nombre,
            options=SearchOptions(path=carpeta, filename_only=True)
        )
        archivos = [match.metadata.get_metadata() for match in resultados.matches]
        return archivos
    except Exception as e:
        st.error(f"Error al buscar: {e}")
        return []

# TAB 1: Buscar archivos
with tab1:
    st.subheader("🔎 Buscar archivos")
    col1, col2 = st.columns(2)
    nombre = col1.text_input("🔍 Nombre del archivo a buscar")
    carpeta = col2.text_input("📁 Carpeta dentro de Dropbox", "/")

    if st.button("Buscar"):
        resultados = buscar_archivos(nombre, carpeta)
        if resultados:
            st.success(f"{len(resultados)} archivo(s) encontrados")
            for archivo in resultados:
                st.markdown(f"**📄 {archivo.name}**")
                st.write(f"📁 Carpeta: `{archivo.path_display.rsplit('/', 1)[0]}`")
                st.write(f"🕒 Modificado: {archivo.client_modified.strftime('%Y-%m-%d %H:%M')}")
                try:
                    link = dbx.sharing_create_shared_link_with_settings(archivo.path_display).url
                    vista = link.replace("?dl=0", "?raw=1")
                    descarga = link.replace("?dl=0", "?dl=1")
                    st.markdown(f"[🔗 Ver archivo]({vista}) | [⬇️ Descargar]({descarga})", unsafe_allow_html=True)
                    if archivo.name.lower().endswith(".pdf"):
                        st.markdown(f'<iframe src="{vista}" width="100%" height="400"></iframe>', unsafe_allow_html=True)
                except:
                    st.warning("No se pudo generar el enlace para este archivo.")
                st.markdown("---")
        else:
            st.info("No se encontraron archivos.")

# TAB 2: Tomar foto y guardar
with tab2:
    st.subheader("📷 Tomar y guardar foto")
    carpetas = obtener_todas_las_carpetas()
    destino = st.selectbox("📁 Selecciona carpeta destino:", carpetas) if carpetas else None
    nombre_foto = st.text_input("📝 Nombre del archivo (sin extensión)", f"foto_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    imagen = st.camera_input("📸 Captura desde cámara")

    if imagen and destino and nombre_foto:
        ruta_final = f"{destino}/{nombre_foto}.jpg"
        try:
            dbx.files_upload(imagen.getvalue(), ruta_final, mode=WriteMode("overwrite"))
            st.success(f"✅ Foto guardada en: `{ruta_final}`")
        except Exception as e:
            st.error(f"❌ Error al guardar imagen: {e}")