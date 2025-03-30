import streamlit as st
import pandas as pd
import time

# Configuración básica
st.set_page_config(page_title="MVP Buscador Alquileres", layout="centered")
st.title("🔍 MVP Buscador de Alquileres")

# Datos de ejemplo (simulados)
def generar_datos_ejemplo():
    return pd.DataFrame([
        {"Portal": "Idealista", "Título": "Piso luminoso en centro", "Precio": 850, "Habitaciones": 2, "Zona": "Centro", "Enlace": "#"},
        {"Portal": "Fotocasa", "Título": "Apartamento con terraza", "Precio": 950, "Habitaciones": 1, "Zona": "Salamanca", "Enlace": "#"},
        {"Portal": "Habitaclia", "Título": "Estudio céntrico", "Precio": 650, "Habitaciones": 1, "Zona": "Chamberí", "Enlace": "#"},
        {"Portal": "Idealista", "Título": "Ático con vistas", "Precio": 1100, "Habitaciones": 3, "Zona": "Retiro", "Enlace": "#"},
        {"Portal": "Fotocasa", "Título": "Casa con jardín", "Precio": 1050, "Habitaciones": 2, "Zona": "Fuencarral", "Enlace": "#"}
    ])

# Interfaz minimalista
with st.form(key='buscador_form'):
    st.subheader("Filtros Básicos")
    
    ubicacion = st.text_input("Zona (ej: Centro, Salamanca...)", "Madrid")
    precio_max = st.slider("Precio máximo (€)", 400, 1500, 1100)
    habitaciones = st.radio("Habitaciones", ["Todas", "1", "2", "3+"])
    
    if st.form_submit_button("Buscar Alquileres"):
        with st.spinner("Buscando propiedades..."):
            time.sleep(1.5)  # Simular tiempo de búsqueda
            
            datos = generar_datos_ejemplo()
            
            # Aplicar filtros
            if habitaciones != "Todas":
                if habitaciones == "3+":
                    datos = datos[datos["Habitaciones"] >= 3]
                else:
                    datos = datos[datos["Habitaciones"] == int(habitaciones)]
            
            datos = datos[datos["Precio"] <= precio_max]
            datos = datos[datos["Zona"].str.contains(ubicacion, case=False)]
            
            # Mostrar resultados
            if len(datos) > 0:
                st.success(f"🏡 {len(datos)} propiedades encontradas")
                
                # Mostrar las propiedades como tarjetas
                for _, row in datos.iterrows():
                    with st.expander(f"{row['Título']} - {row['Precio']}€"):
                        st.markdown(f"""
                        **Portal:** {row['Portal']}  
                        **Zona:** {row['Zona']}  
                        **Habitaciones:** {row['Habitaciones']}  
                        [Ver detalles]({row['Enlace']})
                        """)
            else:
                st.warning("No se encontraron propiedades con esos filtros")

# Sección de feedback
st.divider()
st.subheader("💬 Ayúdanos a mejorar")
feedback = st.selectbox(
    "¿Cómo valoras esta versión inicial?",
    ["", "👍 Muy útil", "👎 Poco útil", "💡 Tengo ideas para mejorar"]
)

if feedback:
    st.text_area("Cuéntanos más (opcional)")
    if st.button("Enviar feedback"):
        st.toast("¡Gracias por tu ayuda! Tomaremos en cuenta tus comentarios")
        time.sleep(1)
        st.rerun()

# Notas de versión
with st.expander("📌 Notas de la versión MVP"):
    st.markdown("""
    **Esta es una versión mínima para validar el concepto:**
    
    - ✅ Búsqueda básica por zona, precio y habitaciones
    - ✅ Resultados simulados (no scraping real aún)
    - ✅ Interfaz simple y rápida
    
    **Próximas mejoras planeadas:**
    
    1. Añadir más portales inmobiliarios
    2. Implementar búsqueda con datos reales
    3. Permitir guardar búsquedas favoritas
    4. Añadir filtros avanzados
    """)
