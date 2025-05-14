import streamlit as st
import dropbox
import pandas as pd
import requests
import tempfile
from collections import Counter
from datetime import datetime
from dropbox.files import SearchOptions

st.set_page_config(page_title="Revisión de OT", layout="wide", page_icon="📁")

st.title("🔍 Revisión de OT")
st.write("Busca archivos dentro de Dropbox y visualiza resultados avanzados")

ACCESS_TOKEN = st.secrets["dropbox"]["access_token"]
dbx = dropbox.Dropbox(ACCESS_TOKEN)

# --- Filtros ---
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
                    extension = nombre.split('.')[-1].lower() if '.' in nombre else "sin extensión"
                    carpeta_padre = '/' + '/'.join(ruta.split('/')[:-1])
                    fecha = meta.server_modified.strftime('%Y-%m-%d %H:%M') if hasattr(meta, "server_modified") else "N/A"

                    archivos.append({
                        "Nombre": nombre,
                        "Ruta": ruta,
                        "Extensión": extension,
                        "Carpeta": carpeta_padre,
                        "Fecha modif.": fecha
                    })

                df = pd.DataFrame(archivos)
                st.success(f"🔎 Se encontraron {len(df)} archivos.")

                # Conteo por tipo de archivo
                tipo_counts = df["Extensión"].value_counts()
                st.subheader("📊 Archivos por tipo")
                st.bar_chart(tipo_counts)

                # Ranking carpetas más utilizadas
                carpeta_counts = df["Carpeta"].value_counts().head(10)
                st.subheader("📁 Carpetas con más archivos encontrados")
                st.dataframe(carpeta_counts)

                # Mostrar resultados agrupados por carpeta
                st.subheader("📂 Archivos encontrados")
                for carpeta, grupo in df.groupby("Carpeta"):
                    with st.expander(f"{carpeta} ({len(grupo)} archivo/s)"):
                        st.dataframe(grupo[["Nombre", "Extensión", "Fecha modif.", "Ruta"]])

        except Exception as e:
            st.error(f"Ocurrió un error: {e}")