import streamlit as st
import dropbox
from datetime import datetime
from dropbox.files import FolderMetadata, FileMetadata

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

def obtener_todas_las_carpetas():
    carpetas = []
    try:
        resultado = dbx.files_list_folder("", recursive=True)
        for entry in resultado.entries:
            if isinstance(entry, FolderMetadata):
                carpetas.append(entry.path_display)
        return carpetas
    except Exception as e:
        st.error(f"No se pudo cargar la lista de carpetas: {e}")
        return []

def buscar_archivos(nombre, carpeta=""):
    try:
        resultados = dbx.files_search_v2(query=nombre, options={"path": carpeta})
        archivos = []
        for match in resultados.matches:
            metadata = match.metadata.get_metadata()
            if isinstance(metadata, FileMetadata):
                archivos.append(metadata)
        return archivos
    except Exception as e:
        st.error(f"Error al buscar: {e}")
        return []

# TAB 1 - Revisión
with tab1:
    st.subheader("🔎 Buscar archivos dentro de Dropbox y visualizar resultados encontrados")
    col1, col2 = st.columns([2, 2])
    with col1:
        nombre = st.text_input("🔍 Nombre del archivo")
    with col2:
        carpeta = st.text_input("📁 Buscar dentro de carpeta específica (ej: /Proyectos)")

    if st.button("Buscar"):
        resultados = buscar_archivos(nombre, carpeta if carpeta.startswith("/") else f"/{carpeta}")
        if resultados:
            st.success(f"{len(resultados)} archivo(s) encontrados")
            for archivo in resultados:
                st.write(f"📄 {archivo.name}")
                st.write(f"📁 Carpeta: {archivo.path_display.rsplit('/', 1)[0]}")
                st.write(f"🕒 Fecha modificación: {archivo.client_modified}")
                try:
                    link = dbx.sharing_create_shared_link_with_settings(archivo.path_display).url
                    st.markdown(f"[🔗 Ver archivo]({link}) | [⬇️ Descargar {archivo.name}]({link})")
                except:
                    st.warning("No se pudo generar enlace de descarga.")
                st.markdown("---")
        else:
            st.warning("No se encontraron archivos.")

# TAB 2 - Cargar fotos
with tab2:
    st.subheader("📷 Toma una foto y guárdala en una carpeta")

    carpetas = obtener_todas_las_carpetas()
    destino = st.selectbox("📂 Selecciona la carpeta donde guardar la foto", carpetas) if carpetas else None

    nombre_archivo = st.text_input("📝 Nombre del archivo (sin extensión)", f"foto_{datetime.now().strftime('%Y%m%d_%H%M%S')}")

    imagen = st.camera_input("📸 Captura con tu cámara")

    if imagen and destino and nombre_archivo:
        ruta_completa = f"{destino}/{nombre_archivo}.jpg"
        try:
            dbx.files_upload(imagen.getvalue(), ruta_completa, mode=dropbox.files.WriteMode("overwrite"))
            st.success(f"✅ Foto guardada en: {ruta_completa}")
        except Exception as e:
            st.error(f"❌ Error al guardar: {e}")