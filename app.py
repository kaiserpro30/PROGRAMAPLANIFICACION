
import streamlit as st
import dropbox
from dropbox.files import WriteMode, SearchOptions, FileMetadata

import io
from datetime import datetime

st.set_page_config(page_title="Revisión de OT", layout="wide")

st.title("📁 Revisión de OT")
st.write("Busca, visualiza y descarga archivos desde una OT")

# Autenticación con Dropbox
DROPBOX_TOKEN = st.secrets["DROPBOX_TOKEN"] if "DROPBOX_TOKEN" in st.secrets else "sl.u.AFuXWGM2_m0kyj5pJ8KqW9I7-b_c-JRKNBrF-gJCxQdvw4Ki6pkpd8fpakWB1731em4HufAB3ISBxP40AY4KcJ1mlbbVSBLTLQG4f7yb1Fvf3ARQMzijgRWkx-7OBNT8vBnYn6d1ariJWa3W3Wgu6XUrZOGhmRum6DlQGuyZi9RvtjNPRWHTDSvqioTUg8qqiFkiqHbg5kidjjkfpjqh01Ymtre41pYSP1B_ZhKNvRVbDO5XQsJVLjEJXykfqLdPAH-bDm-4CQjKIjbooO7d8rl2akJLFJfG1YJIQMm1sDlupIxA6yMC7Rv9ZbMbI7pAnOutah-_KeRS7D6--i19_4OkSmUu5flcxGNescOoWi3wNhGla3AWzThUori2VznyaU4RqKVCyxHS0xP6Gtrluoih5YvC9tcfz6XAgtbiJtSJ-yIgvcwSR4vWNUlKLtM4wecM1Qw7u9WJ1MGHdnXHo2UnUPMDTntu7TXOoIf-Giojo66FrAoXt6p_29CFzpEOPMk1_XF_xeT5tHP-bBYv5vzbLm2Ya1ofjVD9pLdl4onMCnCFgFfYmGna9sY4a71PB3I0Z1ZhjptQgDdFjNWhdte_CxRv9ki8qGCxCBBz9vv9geeuCp_vpAAWkeG5gaMwMg3rVhC1gra9ZkW4upVbKcNUAfs-RfZZd1XxrezY3Pbl9QLk0QrNNbhmaCXadFFuQhumDV20uzQwPozHQaWZE0imApXcewP6SiuIMJfRg2pLWCsF25JLCHEhVnghEi-XDXds6PbieyhKy_wkj8ovY4vdFhy4GKuX1IHDC-zdeWoDu9-Nu6uWaUp9d52HEEStaRuL8N2odI2Pm43XLnPUyqpwjcyZJCoPaogC4i5LHe6h36mQwx-y9qaAmRBxfhlUbbbySq84pzt5iqxE8EducNlcieSoow1EMvw2Lg-dfXRmCsR1IwrHc3vR9y6iXKKa22yWzHpb45nTzAISJe_bxz7DPvwAB1bMG_H5-aB-zQlp2NgIKsS2dyJ2O0_VfKqStnYSe50zaobgflWe6MlMHT4afXjxiiqGbV-9kyDoaNd2olDM4tYpv9dfLX7B7697IZMdPZQNA8QFF8G_qwwL-NZ3Zo7GP2veNrBgUkP2fSGBAOEC7lyA4qJqyM7KAz5WGK6X7D0cOHX9q0Nt6bKrpkLK7K1Y0Vdv6DOByu7WRnBOiBssH7eb2Sjqvqegr8Ev2CvntBCAa14xpVktTZwElKigKuXGxfh0ZUklpsYZ6zU23GSlISFk5yJ-WxqPpa1bhQrw5McL1mRW6_JF9kKNwfCXNqxIgr4LluvYBi-2wt6nQx39U9Ts85f-u0_jobLnkifRf-YZnHXGu4I7jIIGulkD8s64VEPM4Xl0XtUZQJAnv3gQSvS5OK7Bz9n9lqH6_vVFvtkcaZsVZVc5et7bIR9wTRvYyw6ElBeLaLUDOGZfNrH23e-QYoc2AsolQRpDvnY"
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
