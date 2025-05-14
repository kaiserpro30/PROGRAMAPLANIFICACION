import streamlit as st
import dropbox
import pandas as pd
import requests
import tempfile
from dropbox.files import SearchOptions

st.set_page_config(page_title="Revisión de OT", layout="wide", page_icon="📁")

st.title("📂 Revisión de OT")
st.write("Busca, visualiza y descarga archivos desde Dropbox")

ACCESS_TOKEN = st.secrets["dropbox"]["access_token"]
dbx = dropbox.Dropbox(ACCESS_TOKEN)

col1, col2 = st.columns(2)
consulta = col1.text_input("🔍 Nombre del archivo")
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
                        enlace = dbx.sharing_create_shared_link_with_settings(fila['Ruta']).url
                        enlace_vista = enlace.replace("?dl=0", "?raw=1")
                        enlace_descarga = enlace.replace("?dl=0", "?dl=1")

                        st.markdown(f"[🔗 Ver archivo]({enlace_vista})  |  [⬇️ Descargar {fila['Nombre']}]({enlace_descarga})", unsafe_allow_html=True)

                        if fila["Extensión"] in ["pdf"]:
                            st.markdown(f'<iframe src="{enlace_vista}" width="100%" height="500px"></iframe>', unsafe_allow_html=True)
                        elif fila["Extensión"] in ["doc", "docx"]:
                            st.markdown(f'<iframe src="https://view.officeapps.live.com/op/view.aspx?src={enlace_vista}" width="100%" height="500px"></iframe>', unsafe_allow_html=True)
                        elif fila["Extensión"] in ["xlsx", "xls"]:
                            st.write("📌 Vista previa de Excel no disponible. Usa el botón de descarga para abrir el archivo.")
                        else:
                            st.write("🔍 Vista previa no compatible para este tipo de archivo.")

                    except Exception as e:
                        st.error(f"No se pudo generar el enlace: {e}")

        except Exception as e:
            st.error(f"Ocurrió un error: {e}")