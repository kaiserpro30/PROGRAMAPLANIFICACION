
import streamlit as st
import dropbox
from dropbox.files import WriteMode, SearchOptions, FileMetadata

import io
from datetime import datetime

st.set_page_config(page_title="Revisión de OT", layout="wide")

st.title("📁 Revisión de OT")
st.write("Busca, visualiza y descarga archivos desde una OT")

# Autenticación con Dropbox
DROPBOX_TOKEN = st.secrets["DROPBOX_TOKEN"] if "DROPBOX_TOKEN" in st.secrets else "sl.u.AFtWMiFQmM98fkQVhWm4Z8S9F4JhfukjvDH9TW5bhYRSHBMd9cxyJUbK_rdVCsut_Jd22AavyI1bkge_OT-rdsgzd4CBR7zUkT9dLRKVkYSg84VMf4UjKUSNqxsDbOu3xnmv02PxIqY4rKG6_1RFHXms-Upr69ZnO0FbhLND1bNs-F2QZ5U4nbUqIJEMcK_bNCeAajb3Dcdbnpiw5Q9PFy44wQHx2iXoOjZHIyH2fGbHMbv-xLjrra7pwpkuamAoKG7jBMUK88yTFOhkHIWgdpC2RKdLJX2ZmZJ9fWFqnS1QiyQwsQXqOqX6jd6vtN2k-Wmzp1eeIXEpclLm7GYuoyM1YQEsQ2VypM0R16GGmp9O_UgOqjWlPKjl8aMwZnZKgXsWz5RDx0eyowjntDSMs_pNVRjexqsoniQ2UqtVgt2z8R1PRiK9boA0SE0AOGVvL39K8IXJypNxwZ9RpWXOAAmCquhO5IyC640vIj8dvjthzNzvLln2Vg2vulFD-0vqyU5IZbByE4DYrNVdSd_AwbmzpnQEEueymhiRPedy8VDo7-DhZ2JSYJ37dbalT-Ngqxe30q6o0YhEX3FwJJyQi2KtvHOd8nFAhVQxPDO412iVGkF-bfvIKRSS324GOUChqWHSXJ_I7To0H_AEsAlpNwbrTnujUPKUx0iV2JJ86sfDL_5IV6cvW7GklQMKkP2329s0EJbal4akBNlYAuti9EO2XVFOvRyF32-_dG1bcCJZb_HM7O8NE65xC3NFirvtaMP3S66hWJL89oo38uEh9CF7Fnv1iSBkiPpqt8-CvrPtQ8jOpNspgkYcvF_3Kaoj4fE-uGJoPaYz-WU9WOoTEmdwxKrcSTimCP0HKkC9bOFNdr5U8NR3rtCBcokdmYoYqKx5bJ7SDcDtGWb4Xn7VJIk5xfkmyds0VVu2_f7wclM8bPQSSX4NQL4lCs1MszmM_Ws1Qvn0SP1wxX-cQ6yQNHlGngxeYGv9OX-im7_QHQpuvXoXrVFQdGwjAqIn-doPgHPEId0YtfwDIpqCeRK3FtrjNv6PIGefvzNBzKrO97qPiaci5jpqYo0q3s-9cKPsP7rKf_pTCoZkvqg9wxUL6FZJHUuPhlBri11AZgx6aJyGSdi3_td4PRxH6Pc-dWUrfG2Gy9tl48FPi00_Axt_7IVsrsduhBj_F34XwpuuQ7v9fAXZ1tYL5yZPf5LEVY_jVVC6W2BoW_3nX5ptVF-jqBTfxYUuA3G3sRZ-uMKTC23FRA7pegCRSfyssaI0GBEDDXjIC-67LPjOMGjrRzL0NxTkQHLIwZsOXlxiRylJIgyyIwbQ66qQ4N405yGqzj-UZAxJIyu-89H5aBfJGRgTmaEOxHH5AtCkUJCW0n_i_ORckVdxXSP5PRNl7PefSjTMPNPalPxT9CckwlHqk4EIC7CSy6ukihXnhMh-7vkR4Li1O-LI9XlP9aacw00qpB37M9g"
dbx = dropbox.Dropbox(DROPBOX_TOKEN)

# Función para obtener carpetas dentro de una ruta raíz
@st.cache_data
def listar_carpetas(dropbox_path="/"):
    try:
        carpetas = []
        lista = dbx.files_list_folder(dropbox_path)
        for entrada in lista.entries:
            if isinstance(entrada, dropbox.files.FolderMetadata):
                carpetas.append(entrada.path_display)
        return carpetas
    except Exception as e:
        st.error(f"Error al listar carpetas: {e}")
        return []

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

with tab2:
    st.subheader("📷 Tomar y Guardar Foto en Dropbox")

    # Obtener carpetas disponibles
    carpetas_disponibles = listar_carpetas("/")
    carpeta_seleccionada = st.selectbox("📁 Selecciona carpeta de destino:", carpetas_disponibles)

    # Capturar imagen desde cámara
    foto = st.camera_input("📸 Toma una foto")

    if foto is not None:
        nombre_archivo = f"foto_ot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        ruta_completa = f"{carpeta_seleccionada}/{nombre_archivo}"

        if st.button("📤 Guardar en Dropbox"):
            try:
                dbx.files_upload(foto.getvalue(), ruta_completa, mode=WriteMode("overwrite"))
                st.success(f"✅ Foto guardada en: {ruta_completa}")
            except Exception as e:
                st.error(f"❌ Error al guardar la imagen: {e}")
