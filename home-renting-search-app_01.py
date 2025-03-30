import streamlit as st
import time
import pandas as pd
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Configuración de la página
st.set_page_config(page_title="Buscador Avanzado de Alquileres", layout="wide")
st.title("🏠 Buscador Multiplataforma de Alquileres")

# --- Configuración de Selenium ---
@st.cache_resource
def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=chrome_options)

# URLs específicas
PORTAL_URLS = {
    'Idealista': 'https://www.idealista.com/areas/alquiler-viviendas/con-precio-hasta_1100,metros-cuadrados-mas-de_60,de-dos-dormitorios,de-tres-dormitorios,de-cuatro-cinco-habitaciones-o-mas/mapa-google?shape=((%7BpzuF%7ElsUaLeAg%40gQ%7BWhCia%40qNaW%7DS_%5C_U%7BLen%40ZgQj%7DCvI_FxjBcGdAuBhR))',
    'Fotocasa': 'https://www.fotocasa.es/es/alquiler/viviendas/madrid-capital/todas-las-zonas/l?maxPrice=1100&minRooms=2&minSurface=60&searchArea=i-z07ghvjBwlYs0mHsxiGzrzWi8tE057Gs2mUgr_Gih8B5z3B415Bxj1CuuG2jRhmqJ9hM-tiBiyGz8-B5zRxgmHysqLp_zVu2mwB-1V-28Ejh8BknrCzhkK1l_GsqrD7s1Bz1xDl_5DjysDz18Ci2_BhiqC7qG&zoom=14',
    'Spotahome': 'https://www.spotahome.com/es/s/madrid--spain/for-rent:apartments/for-rent:studios/bedrooms:1/bedrooms:2?move-in=2025-04-26&bed=double,single-group&budget=0-1100&rentalType[]=longTerm&moveInFrom=2025-04-26&moveInTo=2030-04-26&includeBlockedProperties=1&mapCenter=40.44767441477353,-3.7002290341000643',
    'Yaencontre': 'https://www.yaencontre.com/alquiler/pisos/custom/f-2-habitaciones,-1100euros,50m2/mapa?polygon=utzuFvytU%7BLse%40r%40yRwZwBwZmEgs%40io%40iFoc%40lAa%5E%7EiC%60K_HllBvF%7Cq%40%7BK%60K'
}

# --- Funciones de scraping con Selenium ---
def scrape_idealista():
    try:
        driver = get_driver()
        driver.get(PORTAL_URLS['Idealista'])
        time.sleep(5)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        propiedades = []
        
        for item in soup.find_all('article', class_='item-info-container'):
            try:
                detalles = {
                    'Portal': 'Idealista',
                    'Título': item.find('a', class_='item-link').get_text(strip=True),
                    'Precio': int(re.sub(r'\D', '', item.find('span', class_='price').text)),
                    'Habitaciones': item.find('span', class_='rooms').text.strip(),
                    'Metros': item.find('span', class_='area').text.strip(),
                    'Zona': item.find('span', class_='location').text.strip(),
                    'Enlace': urljoin(PORTAL_URLS['Idealista'], item.find('a')['href']),
                    'Fecha': datetime.now().strftime('%Y-%m-%d')
                }
                propiedades.append(detalles)
            except Exception as e:
                st.warning(f"Error procesando propiedad en Idealista: {str(e)}")
        return propiedades
    except Exception as e:
        st.error(f"Error scraping Idealista: {str(e)}")
        return []

def scrape_fotocasa():
    try:
        driver = get_driver()
        driver.get(PORTAL_URLS['Fotocasa'])
        time.sleep(5)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        propiedades = []
        
        for item in soup.find_all('div', class_='re-Card'):
            try:
                detalles = {
                    'Portal': 'Fotocasa',
                    'Título': item.find('a', class_='re-Card-title').get_text(strip=True),
                    'Precio': int(re.sub(r'\D', '', item.find('span', class_='re-Card-price').text)),
                    'Habitaciones': item.find_all('span', class_='detail-info')[0].text.strip(),
                    'Metros': item.find_all('span', class_='detail-info')[1].text.strip(),
                    'Zona': item.find('span', class_='location').text.strip(),
                    'Enlace': urljoin(PORTAL_URLS['Fotocasa'], item.find('a')['href']),
                    'Fecha': datetime.now().strftime('%Y-%m-%d')
                }
                propiedades.append(detalles)
            except Exception as e:
                st.warning(f"Error procesando propiedad en Fotocasa: {str(e)}")
        return propiedades
    except Exception as e:
        st.error(f"Error scraping Fotocasa: {str(e)}")
        return []

def scrape_spotahome():
    try:
        driver = get_driver()
        driver.get(PORTAL_URLS['Spotahome'])
        time.sleep(8)  # Más tiempo para carga de React
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        propiedades = []
        
        for item in soup.find_all('div', class_='result-item'):
            try:
                detalles = {
                    'Portal': 'Spotahome',
                    'Título': item.find('span', class_='result-title').get_text(strip=True),
                    'Precio': int(re.sub(r'\D', '', item.find('span', class_='result-price').text)),
                    'Habitaciones': item.find('span', class_='rooms').text.strip() if item.find('span', class_='rooms') else 'No especificado',
                    'Metros': item.find('span', class_='area').text.strip() if item.find('span', class_='area') else 'No especificado',
                    'Zona': item.find('span', class_='result-location').text.strip(),
                    'Enlace': urljoin(PORTAL_URLS['Spotahome'], item.find('a')['href']),
                    'Fecha': datetime.now().strftime('%Y-%m-%d')
                }
                propiedades.append(detalles)
            except Exception as e:
                st.warning(f"Error procesando propiedad en Spotahome: {str(e)}")
        return propiedades
    except Exception as e:
        st.error(f"Error scraping Spotahome: {str(e)}")
        return []

def scrape_yaencontre():
    try:
        driver = get_driver()
        driver.get(PORTAL_URLS['Yaencontre'])
        time.sleep(5)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        propiedades = []
        
        for item in soup.find_all('div', class_='result-item'):
            try:
                detalles = {
                    'Portal': 'Yaencontre',
                    'Título': item.find('a', class_='property-title').get_text(strip=True),
                    'Precio': int(re.sub(r'\D', '', item.find('span', class_='price').text)),
                    'Habitaciones': item.find('span', class_='rooms').text.strip(),
                    'Metros': item.find('span', class_='area').text.strip(),
                    'Zona': item.find('span', class_='location').text.strip(),
                    'Enlace': urljoin(PORTAL_URLS['Yaencontre'], item.find('a')['href']),
                    'Fecha': datetime.now().strftime('%Y-%m-%d')
                }
                propiedades.append(detalles)
            except Exception as e:
                st.warning(f"Error procesando propiedad en Yaencontre: {str(e)}")
        return propiedades
    except Exception as e:
        st.error(f"Error scraping Yaencontre: {str(e)}")
        return []

# --- Interfaz de usuario ---
with st.sidebar:
    st.header("⚙️ Configuración")
    portales = st.multiselect(
        "Seleccionar portales",
        options=list(PORTAL_URLS.keys()),
        default=list(PORTAL_URLS.keys())
    
    st.subheader("Filtros Avanzados")
    min_precio, max_precio = st.slider('Rango de precios (€)', 0, 2000, (600, 1100))
    min_metros = st.number_input('Mínimo de metros cuadrados', 40, 200, 60)

if st.button("🔍 Iniciar Búsqueda"):
    with st.spinner("Escaneando portales inmobiliarios..."):
        resultados = []
        
        if 'Idealista' in portales:
            resultados.extend(scrape_idealista())
        if 'Fotocasa' in portales:
            resultados.extend(scrape_fotocasa())
        if 'Spotahome' in portales:
            resultados.extend(scrape_spotahome())
        if 'Yaencontre' in portales:
            resultados.extend(scrape_yaencontre())
        
        if resultados:
            df = pd.DataFrame(resultados)
            df = df[
                (df['Precio'].between(min_precio, max_precio)) &
                (df['Metros'].apply(lambda x: int(re.sub(r'\D', '', str(x)) >= min_metros)
            ]
            
            st.success(f"✅ {len(df)} propiedades encontradas")
            
            for _, row in df.iterrows():
                with st.expander(f"{row['Portal']} - {row['Título']}"):
                    st.markdown(f"""
                    **Precio:** {row['Precio']}€  
                    **Habitaciones:** {row['Habitaciones']}  
                    **Metros:** {row['Metros']}  
                    **Zona:** {row['Zona']}  
                    **Enlace:** [{row['Portal']}]({row['Enlace']})
                    """)
            
            st.download_button(
                label="📥 Descargar CSV",
                data=df.to_csv(index=False).encode('utf-8'),
                file_name="resultados_alquileres.csv",
                mime='text/csv'
            )
        else:
            st.warning("No se encontraron propiedades con los filtros seleccionados")

# --- Requerimientos ---
st.markdown("""
### 📝 Requisitos técnicos:
1. ChromeDriver instalado y en PATH
2. Python 3.8+
3. Dependencias:  
```bash
pip install streamlit selenium pandas beautifulsoup4
