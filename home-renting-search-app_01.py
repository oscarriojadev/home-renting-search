import os
import platform
import sys
import time
import base64
import streamlit as st
import pandas as pd
import numpy as np  
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException
from bs4 import BeautifulSoup

# ================== CONSTANTES ==============
TIMEOUT = 30
MAX_RESULTADOS = 50

# ================== MEJORAS DE UI ==================
def _max_width_():
    max_width_str = "max-width: 1100px;"
    st.markdown(
        f"""
    <style>
    .reportview-container .main .block-container{{
        {max_width_str}
    }}
    </style>    
    """,
        unsafe_allow_html=True,
    )

_max_width_()

# ================== CONFIGURACIÓN MEJORADA ==================
def configurar_entorno():
    if platform.system() == 'Linux':
        os.environ['CHROME_BIN'] = '/usr/bin/chromium-browser'
        os.environ['CHROMEDRIVER_PATH'] = '/usr/bin/chromedriver'
        sys.path.extend(['/usr/lib/chromium-browser', '/usr/bin'])
        
        # Configuración de display virtual
        if "DISPLAY" not in os.environ:
            os.system('Xvfb :99 -screen 0 1920x1080x24 &')
            os.environ['DISPLAY'] = ':99'

# ================== SISTEMA DE DRIVER MEJORADO ==================
@st.cache_resource
def obtener_driver():
    try:
        configurar_entorno()
        
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920x1080")
        
        service_config = {
            'service_args': ['--verbose', '--log-path=/tmp/chromedriver.log']
        } if platform.system() == 'Linux' else {}
        
        service = Service(
            executable_path=os.getenv('CHROMEDRIVER_PATH', 'chromedriver'),
            **service_config
        )
        
        if platform.system() == 'Linux':
            options.binary_location = os.getenv('CHROME_BIN')
        
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(45)
        return driver
        
    except Exception as e:
        st.error(f"🚨 Error crítico: {str(e)}")
        st.stop()

# ================== VISUALIZACIÓN DE RESULTADOS MEJORADA ==================
def mostrar_resultados(df):
    st.subheader(f"📊 Resultados encontrados: {len(df)}")
    
    vista = st.radio("Modo de visualización:", ["Tarjetas", "Tabla"])
    
    if vista == "Tarjetas":
        for _, propiedad in df.iterrows():
            with st.expander(f"{propiedad['Título']} - {propiedad['Precio']}"):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**Ubicación:** {propiedad['Ubicación']}")
                    st.markdown(f"**Portal:** {propiedad['Portal']}")
                    if 'Habitaciones' in propiedad:
                        st.markdown(f"**Habitaciones:** {propiedad['Habitaciones']}")
                    if 'Metros' in propiedad:
                        st.markdown(f"**Metros cuadrados:** {propiedad['Metros']}")
                with col2:
                    st.markdown(f"[Ver propiedad]({propiedad['Enlace']})", unsafe_allow_html=True)
    else:
        st.dataframe(df.replace(np.nan, 'Sin dato'))
    
    csv = df.to_csv(index=False).encode('utf-8')
    b64 = base64.b64encode(csv).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="propiedades.csv">⬇️ Descargar CSV</a>'
    st.markdown(href, unsafe_allow_html=True)

# ================== FUNCIONES DE SCRAPING ACTUALIZADAS =================
def construir_url(portal, filtros):
    base_urls = {
        'Idealista': f"https://www.idealista.com/alquiler-viviendas/con-precio-hasta_{filtros['max_precio']},metros-cuadrados-mas-de_{filtros['min_metros']},de-{filtros['min_habitaciones']}-dormitorios/mapa-google",
        'Fotocasa': f"https://www.fotocasa.es/es/alquiler/viviendas/{filtros['ubicacion']}/todas-las-zonas/l?maxPrice={filtros['max_precio']}&minRooms={filtros['min_habitaciones']}&minSurface={filtros['min_metros']}",
        'Spotahome': f"https://www.spotahome.com/es/s/{filtros['ubicacion']}/for-rent:apartments/bedrooms:{filtros['min_habitaciones']}/budget=0-{filtros['max_precio']}",
        'Yaencontre': f"https://www.yaencontre.com/alquiler/pisos/custom/f-{filtros['min_habitaciones']}-habitaciones,-{filtros['max_precio']}euros,{filtros['min_metros']}m2/mapa"
    }
    return base_urls.get(portal)

def extraer_idealista(driver, url):
    try:
        driver.get(url)
        WebDriverWait(driver, TIMEOUT).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "article.item-info-container"))
        )
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        resultados = []
        
        for propiedad in soup.select('article.item-info-container'):
            titulo = propiedad.select_one('a.item-link')['title']
            precio = propiedad.select_one('span.price').get_text(strip=True)
            detalles = [span.get_text(strip=True) for span in propiedad.select('span.item-detail')]
            ubicacion = propiedad.select_one('span.location').get_text(strip=True)
            link = propiedad.select_one('a.item-link')['href']
            
            resultados.append({
                'Título': titulo,
                'Precio': precio,
                'Habitaciones': detalles[0] if len(detalles) > 0 else 'N/A',
                'Metros': detalles[1] if len(detalles) > 1 else 'N/A',
                'Ubicación': ubicacion,
                'Enlace': f"https://www.idealista.com{link}",
                'Portal': 'Idealista'
            })
        
        return resultados[:MAX_RESULTADOS]
    
    except (TimeoutException, WebDriverException) as e:
        st.error(f"Error en Idealista: {str(e)}")
        return []

def extraer_fotocasa(driver, url):
    try:
        driver.get(url)
        WebDriverWait(driver, TIMEOUT).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.re-Card")))
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        resultados = []
        
        for propiedad in soup.select('div.re-Card'):
            titulo = propiedad.select_one('h3.re-Card-title').get_text(strip=True)
            precio = propiedad.select_one('span.re-Card-price').get_text(strip=True)
            detalles = propiedad.select_one('span.re-Card-feature').get_text(strip=True)
            ubicacion = propiedad.select_one('span.re-Card-location').get_text(strip=True)
            link = propiedad.select_one('a.re-Card-link')['href']
            
            resultados.append({
                'Título': titulo,
                'Precio': precio,
                'Detalles': detalles,
                'Ubicación': ubicacion,
                'Enlace': f"https://www.fotocasa.es{link}",
                'Portal': 'Fotocasa'
            })
        
        return resultados[:MAX_RESULTADOS]
    
    except (TimeoutException, WebDriverException) as e:
        st.error(f"Error en Fotocasa: {str(e)}")
        return []

# ================== FUNCIÓN PRINCIPAL MEJORADA ==================
def main():
    # Configuración inicial DEBE SER PRIMERO
    st.set_page_config(page_title="Buscador Inmobiliario", layout="wide")
    _max_width_()  # Llamada a configuración de ancho después de set_page_config
    
    st.title("🏡 Buscador Inteligente de Propiedades")
    
    with st.sidebar:
        st.header("⚙️ Filtros de Búsqueda")
        ubicacion = st.text_input("Ubicación (ej: Madrid)", "madrid").lower()
        max_precio = st.slider("Precio máximo (€)", 500, 3000, 1100)
        min_habitaciones = st.slider("Mínimo habitaciones", 1, 5, 2)
        min_metros = st.slider("Mínimo metros cuadrados", 40, 200, 60)
        portales = st.multiselect(
            "Portales a buscar",
            ['Idealista', 'Fotocasa', 'Spotahome', 'Yaencontre'],
            default=['Idealista', 'Fotocasa']
        )
    
    if st.button("🔍 Buscar propiedades"):
        driver = obtener_driver()
        todas_propiedades = []
        
        try:
            with st.spinner("🔎 Analizando portales..."):
                filtros = {
                    'ubicacion': ubicacion,
                    'max_precio': max_precio,
                    'min_habitaciones': min_habitaciones,
                    'min_metros': min_metros
                }
                
                for portal in portales:
                    url = construir_url(portal, filtros)
                    if url:
                        if portal == 'Idealista':
                            resultados = extraer_idealista(driver, url)
                        elif portal == 'Fotocasa':
                            resultados = extraer_fotocasa(driver, url)
                        # Añadir lógica para otros portales aquí
                        
                        if resultados:
                            todas_propiedades.extend(resultados)
                            time.sleep(1.5)  # Espera anti-detection
                
            if not todas_propiedades:
                st.warning("⚠️ No se encontraron resultados")
            else:
                df = pd.DataFrame(todas_propiedades)
                mostrar_resultados(df)
                
        except Exception as e:
            st.error(f"Error general: {str(e)}")
        finally:
            if driver:
                driver.quit()

if __name__ == "__main__":
    main()
