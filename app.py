
import streamlit as st
import dropbox
from datetime import datetime
from dropbox.files import FolderMetadata, SearchOptions, SearchV2Arg

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

def obtener_todas_las_carpetas(base="/"):
    carpetas = []
    try:
        resultado = dbx.files_list_folder('' if base == '/' else base, recursive=True)
        for entry in resultado.entries:
            if isinstance(entry, FolderMetadata):
                carpetas.append(entry.path_display)
        return carpetas
    except Exception as e:
        st.error(f"No se pudo cargar la lista de carpetas: {e}")
        return []

# TAB 1 - Búsqueda de Archivos
with tab1:
    st.subheader("🔍 Buscar archivos en Dropbox")
    nombre = st.text_input("🔍 Nombre del archivo a buscar:")
    carpeta = st.text_input("📁 Carpeta dentro de Dropbox (ej: /Proyectos)", value="/")

    if st.button("Buscar archivo"):
        if not nombre:
            st.warning("Debes ingresar un nombre de archivo para buscar.")
        else:
            try:
                options = SearchOptions(filename_only=True)
                path = "" if carpeta.strip() in ["/", ""] else carpeta.strip()
                search_arg = SearchV2Arg(query=nombre, path=path, options=options)
                resultados = dbx.files_search_v2(search_arg)

                if resultados.matches:
                    st.success(f"✅ {len(resultados.matches)} archivo(s) encontrado(s)")
                    for match in resultados.matches:
                        metadata = match.metadata.get_metadata()
                        st.write(f"📄 **{metadata.name}**")
                        st.write(f"📁 Carpeta: `{metadata.path_display}`")
                        st.write(f"🕒 Fecha modificación: {metadata.client_modified}")
                        try:
                            enlace = dbx.sharing_create_shared_link_with_settings(metadata.path_display).url
                            st.markdown(f"[🔗 Ver archivo]({enlace.replace('?dl=0','?raw=1')}) | [⬇️ Descargar]({enlace})", unsafe_allow_html=True)
                            if metadata.name.lower().endswith(".pdf"):
                                st.markdown(f'<iframe src="{enlace.replace("?dl=0","?raw=1")}" width="100%" height="400"></iframe>', unsafe_allow_html=True)
                        except Exception as e:
                            st.warning(f"No se pudo crear enlace: {e}")
                        st.markdown("---")
                else:
                    st.info("No se encontraron archivos con ese nombre.")
            except Exception as e:
                st.error(f"❌ Error al buscar: {e}")

# TAB 2 - Carga de Foto
with tab2:
    st.subheader("📷 Toma una foto y guárdala en una carpeta")
    carpetas = obtener_todas_las_carpetas("/")
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
