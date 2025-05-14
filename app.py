
import streamlit as st
import dropbox
import pandas as pd
import requests
from datetime import datetime
from dropbox.files import SearchOptions
from dropbox.exceptions import ApiError

# Configuración inicial
st.set_page_config(page_title="Revisión de OT", layout="wide", page_icon="📁")

# Logo y encabezado
st.image("logo_inamar.png", width=180)
st.markdown(
    '''
    <div style="background-color:#003366; padding:10px">
        <h1 style="color:white; text-align:center;">Área Planificación</h1>
    </div>
    ''',
    unsafe_allow_html=True
)

st.title("📁 Revisión de OT")
st.write("Busca, visualiza y descarga archivos desde una OT")

ACCESS_TOKEN = st.secrets["dropbox"]["access_token"]
dbx = dropbox.Dropbox(ACCESS_TOKEN)

tab1, tab2 = st.tabs(["🔍 Revisión de Archivos", "📸 Cargar Foto a OT"])

# TAB 1 - Revisión de Archivos
with tab1:
    col1, col2 = st.columns(2)
    consulta = col1.text_input("🔎 Nombre del archivo")
    carpeta = col2.text_input("📁 Buscar dentro de carpeta específica (ej: /Proyectos)", value="")

    if st.button("Buscar"):
        if not consulta.strip():
            st.warning("Por favor ingrese un texto para buscar.")
        else:
            try:
                path_scope = carpeta.strip() if carpeta.strip() else ""
                opciones = SearchOptions(filename_only=False, path=path_scope)
                resultados = dbx.files_search_v2(query=consulta, options=opciones)

                if not resultados.matches:
                    st.info("No se encontraron archivos.")
                else:
                    archivos = []
                    for match in resultados.matches:
                        meta = match.metadata.get_metadata()
                        nombre = meta.name
                        ruta = meta.path_display
                        carpeta_padre = '/' + '/'.join(ruta.split('/')[:-1])
                        fecha = meta.server_modified.strftime('%Y-%m-%d %H:%M') if hasattr(meta, "server_modified") else "N/A"
                        ext = nombre.split('.')[-1].lower() if '.' in nombre else "sin_extension"

                        archivos.append({
                            "Nombre": nombre,
                            "Ruta": ruta,
                            "Extensión": ext,
                            "Carpeta": carpeta_padre,
                            "Fecha modif.": fecha
                        })

                    df = pd.DataFrame(archivos)
                    st.success(f"🔎 {len(df)} archivo(s) encontrados")

                    for i, fila in df.iterrows():
                        st.subheader(f"📄 {fila['Nombre']}")
                        st.write(f"📁 Carpeta: `{fila['Carpeta']}`")
                        st.write(f"🕒 Fecha modificación: `{fila['Fecha modif.']}`")

                        try:
                            try:
                                enlace = dbx.sharing_create_shared_link_with_settings(fila['Ruta']).url
                            except ApiError as e:
                                if "shared_link_already_exists" in str(e):
                                    enlaces = dbx.sharing_list_shared_links(path=fila['Ruta'], direct_only=True)
                                    enlace = enlaces.links[0].url
                                else:
                                    raise e

                            enlace_vista = enlace.replace("?dl=0", "?raw=1")
                            enlace_descarga = enlace.replace("?dl=0", "?dl=1")

                            st.markdown(f"[🔗 Ver archivo]({enlace_vista})  |  [⬇️ Descargar {fila['Nombre']}]({enlace_descarga})", unsafe_allow_html=True)

                            if fila["Extensión"] == "pdf":
                                st.markdown(f'<iframe src="{enlace_vista}" width="100%" height="500px"></iframe>', unsafe_allow_html=True)
                            else:
                                st.info("Vista previa solo disponible para archivos PDF. Use el botón de descarga.")

                        except Exception as e:
                            st.error(f"No se pudo generar el enlace: {e}")

            except Exception as e:
                st.error(f"Ocurrió un error: {e}")

# TAB 2 - Cámara para cargar fotos
with tab2:
    st.subheader("📷 Toma una foto y guárdala en una carpeta")

    folder = st.text_input("📁 Carpeta de destino en Dropbox (ej: /Fotos_OT/20628)", key="folder_foto")
    nombre_foto = st.text_input("📝 Nombre del archivo (sin extensión)", value=f"foto_{datetime.now().strftime('%Y%m%d_%H%M%S')}", key="nombre_foto")
    img = st.camera_input("📸 Captura con tu cámara")

    if img and folder and nombre_foto:
        ruta_destino = f"{folder}/{nombre_foto}.jpg"
        try:
            dbx.files_upload(img.getvalue(), ruta_destino, mode=dropbox.files.WriteMode("overwrite"))
            st.success(f"✅ Foto guardada correctamente en `{ruta_destino}`")
        except Exception as e:
            st.error(f"❌ Error al guardar la imagen: {e}")
