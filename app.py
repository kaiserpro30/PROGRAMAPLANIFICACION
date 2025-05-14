import streamlit as st
import dropbox
from dropbox.files import SearchOptions

# Configuración de la página
st.set_page_config(page_title="Revisión de OT", layout="wide")

# Conexión a Dropbox
dbx = dropbox.Dropbox("sl.u.AFt16JPPY-Q_CmKf_CWNXn7PZgARG1c3Uq2QMD2Lk2MD-1AD7iirnW0l6MCFWtssG4Y-DAKDKHetw-hSsqOj_9Ke7nOtVCWqm40DQAqFhWGNq-2qaTnfcXZBilxUWmPY6coK7FhgBTPjldaqCTcdD7zJ-B78QB9flGoBcfxjgammftK8D1SJZFsmx89CDvaJxfZir3MUcBq5yRhKk4eWcwXoS0PZLNLOvfjH65l-_PbTxu0LDapKI8d5Uq2UGjuz4aEGKpkPABYQVy4EDj_bHC6Tymi75x46VZ7Op3fjWn9RVu-OdnxQz2qVSa8UDR-9FfIXIObokgbQOb7Fpkv1EWM-MZhk7rHY3nOOl-bwRtSbZLvZiXKkXvzGxFUOooonMJtav4dujPvnPIsNE0RDDRiADCYIYzlBRJJ_S1ITMukz7wAAYjuBXihVR9VYvVcYXE13KlLq2aVhIVCCiSZdeREOBr7wG9uYn-6ojKLExIrvShoRIvYZXd6YnMzI_2nIjtxeYYr3wcH7KKNPGQejUgDOq58ZcN4iO9CWy_Q4Q_OtMzZTW446MZuU6PfbnoKPQsi5T5l1KpPKfD-4fV4YFM18q2hrVjni5vktVIq5eTP6P0_TNIaZZBlAfF4i2hpSLXad2e41B5Zr9DH-q7ZbPAn-Nx-Icw6vbY3yIyHfEJaqXIde6SSe2r_X4icd7yCFOurP-zTYhKj9yPzuswguANMk37zq7HQGL72fvf0gbIM1QNp51gq76LsMx5Bh9wOiQfCaDPGhmR91YrKoKlCMzk8XWfSJQevxC68rV89OpgA8G4G_dfclabrw0F6UtS9IudLWPUsLLK8ocxMFtwYjHZe_TKz0tiD3LeNG6w_STS7AjA0XLl9aHxGUF4j1rs3HQiJ4usIFVjfdHRGTQta6SAmhue3rE87stvKRMeFp85JIlAlxr68hOWYXZxGHKGsIlkh9__ujat-g6SP_HbcO0qHHxB9YlRxp8mQLH3dSxX7911uPEAfeNEc7-8nyWczXdZyWre-M3d5N65GLbn3vPblNFWQ5pBAZCId9inCvkFpaBIhiAeacmLmDoL3LySNebmjsPtIOJ7b5DAiZR76wNqNrRowOPFvw1-or5jgk3u_LAIY3nJSAP9h51glVZIuUuzeuPkTSYrhcx00HMC92x_A97OPA83jLM5QUqiVVIwf8BnNBGnnoipJHw2ASy2OiMRFppkKsqEo2dw1qAwvGB7Bn4Lhz8gk-zq4wnuaws9nYgSAPdmAcBo99vVhaRP4GuWhtKFlM34x2qrlhNYXKJY_O8IvaxX-2woIIJWcavjbnLqH7tNjLBTn6qFerh4iav9VNpoKCoiLtt3-qq7gGIRfNr0pD4s3QMfw8eOIDEdFNiXGuhmKNSjG7XleK_qIEqAo9lercZFsZwAofxIgZOexzH5TGUHX72YOjczFKccE2rLz8jU9mDudK4DAnvn7oNAU")

st.title("📁 Revisión de OT")
st.write("Busca, visualiza y descarga archivos desde una OT")

# Pestañas
tabs = st.tabs(["🔍 Revisión de Archivos", "📷 Cargar Foto a OT"])

with tabs[0]:
    st.header("🔍 Buscar archivos en Dropbox")
    nombre_archivo = st.text_input("🔎 Nombre del archivo a buscar:", "")
    carpeta = st.text_input("📂 Carpeta dentro de Dropbox (ej: /Proyectos)", "/")

    if st.button("Buscar archivo") and nombre_archivo:
        try:
            search_options = SearchOptions(path=carpeta, max_results=100, filename_only=True)
            result = dbx.files_search_v2(query=nombre_archivo, options=search_options)
            matches = result.matches
            if matches:
                st.success(f"Se encontraron {len(matches)} archivo(s):")
                for m in matches:
                    metadata = m.metadata.get_metadata()
                    st.write(f"📄 {metadata.name}")
            else:
                st.warning("No se encontraron archivos.")
        except Exception as e:
            st.error(f"❌ Error al buscar: {e}")