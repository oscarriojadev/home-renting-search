import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime
import re
from fake_useragent import UserAgent
from urllib.parse import urljoin

# Configuración de la página
st.set_page_config(page_title="Buscador Real de Alquileres", layout="wide")
st.title("🏠 Buscador Avanzado de Alquileres")

# --- Configuración de scraping ---
HEADERS = {
    'User-Agent': UserAgent().random,
    'Accept-Language': 'es-ES,es;q=0.9',
    'Referer': 'https://www.google.com/'
}

# --- Funciones de scraping actualizadas ---
def scrape_idealista(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        propiedades = []
        
        for item in soup.find_all('article', {'class': 'item'}):
            try:
                # Extraer datos con los nuevos selectores
                titulo = item.find('a', {'class': 'item-link'}).get_text(strip=True)
                precio_raw = item.find('span', {'class': 'item-price'}).get_text(strip=True)
                precio = int(re.sub(r'\D', '', precio_raw))
                
                detalles = item.find_all('span', {'class': 'item-detail'})
                habitaciones = detalles[0].get_text(strip=True) if len(detalles) > 0 else None
                metros = detalles[1].get_text(strip=True) if len(detalles) > 1 else None
                zona = item.find('span', {'class': 'item-town'}).get_text(strip=True) if item.find('span', {'class': 'item-town'}) else None
                enlace = urljoin(url, item.find('a', {'class': 'item-link'})['href'])
                
                propiedades.append({
                    'Portal': 'Idealista',
                    'Título': titulo,
                    'Precio': precio,
                    'Habitaciones': habitaciones,
                    'Metros': metros,
                    'Zona': zona,
                    'Enlace': enlace,
                    'Fecha': datetime.now().strftime('%Y-%m-%d')
                })
            except Exception as e:
                st.warning(f"Error procesando propiedad en Idealista: {str(e)}")
        return propiedades
        
    except Exception as e:
        st.error(f"Error scraping Idealista: {str(e)}")
        return []

def scrape_fotocasa(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        propiedades = []
        
        for item in soup.find_all('div', {'class': 're-CardPackPremium'}):
            try:
                titulo = item.find('a', {'class': 're-Card-title'}).get_text(strip=True)
                precio_raw = item.find('span', {'class': 're-Card-price'}).get_text(strip=True)
                precio = int(re.sub(r'\D', '', precio_raw))
                
                detalles = item.find_all('span', {'class': 're-Card-feature'})
                habitaciones = detalles[0].get_text(strip=True) if len(detalles) > 0 else None
                metros = detalles[1].get_text(strip=True) if len(detalles) > 1 else None
                zona = item.find('span', {'class': 're-Card-title'}).get_text(strip=True).split(',')[-1].strip()
                enlace = urljoin(url, item.find('a')['href'])
                
                propiedades.append({
                    'Portal': 'Fotocasa',
                    'Título': titulo,
                    'Precio': precio,
                    'Habitaciones': habitaciones,
                    'Metros': metros,
                    'Zona': zona,
                    'Enlace': enlace,
                    'Fecha': datetime.now().strftime('%Y-%m-%d')
                })
            except Exception as e:
                st.warning(f"Error procesando propiedad en Fotocasa: {str(e)}")
        return propiedades
        
    except Exception as e:
        st.error(f"Error scraping Fotocasa: {str(e)}")
        return []

def scrape_spotahome(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        propiedades = []
        
        for item in soup.find_all('article', {'class': 'PlaceCard'}):
            try:
                titulo = item.find('h3', {'class': 'PlaceCard-title'}).get_text(strip=True)
                precio_raw = item.find('span', {'class': 'PlaceCard-price'}).get_text(strip=True)
                precio = int(re.sub(r'\D', '', precio_raw))
                
                detalles = item.find_all('li', {'class': 'PlaceCard-feature'})
                habitaciones = detalles[0].get_text(strip=True) if len(detalles) > 0 else None
                metros = detalles[1].get_text(strip=True) if len(detalles) > 1 else None
                zona = item.find('span', {'class': 'PlaceCard-city'}).get_text(strip=True)
                enlace = urljoin(url, item.find('a')['href'])
                
                propiedades.append({
                    'Portal': 'Spotahome',
                    'Título': titulo,
                    'Precio': precio,
                    'Habitaciones': habitaciones,
                    'Metros': metros,
                    'Zona': zona,
                    'Enlace': enlace,
                    'Fecha': datetime.now().strftime('%Y-%m-%d')
                })
            except Exception as e:
                st.warning(f"Error procesando propiedad en Spotahome: {str(e)}")
        return propiedades
        
    except Exception as e:
        st.error(f"Error scraping Spotahome: {str(e)}")
        return []

def scrape_yaencontre(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        propiedades = []
        
        for item in soup.find_all('div', {'class': 'listing-card'}):
            try:
                titulo = item.find('h3').get_text(strip=True)
                precio_raw = item.find('div', {'class': 'listing-card__price'}).get_text(strip=True)
                precio = int(re.sub(r'\D', '', precio_raw))
                
                detalles = item.find_all('span', {'class': 'listing-card__features'})
                habitaciones = detalles[0].get_text(strip=True) if len(detalles) > 0 else None
                metros = detalles[1].get_text(strip=True) if len(detalles) > 1 else None
                zona = item.find('div', {'class': 'listing-card__location'}).get_text(strip=True)
                enlace = urljoin(url, item.find('a')['href'])
                
                propiedades.append({
                    'Portal': 'Yaencontre',
                    'Título': titulo,
                    'Precio': precio,
                    'Habitaciones': habitaciones,
                    'Metros': metros,
                    'Zona': zona,
                    'Enlace': enlace,
                    'Fecha': datetime.now().strftime('%Y-%m-%d')
                })
            except Exception as e:
                st.warning(f"Error procesando propiedad en Yaencontre: {str(e)}")
        return propiedades
        
    except Exception as e:
        st.error(f"Error scraping Yaencontre: {str(e)}")
        return []

# --- Interfaz actualizada ---
with st.sidebar:
    st.header("🔍 Filtros Avanzados")
    ubicacion = st.selectbox("Ciudad", ["Madrid", "Barcelona", "Valencia", "Sevilla"])
    precio_max = st.slider("Precio máximo (€)", 300, 2000, 1100)
    habitaciones = st.selectbox("Habitaciones", ["1", "2", "3", "4+"])
    
    st.subheader("Filtros Adicionales")
    tipo_propiedad = st.selectbox("Tipo de propiedad", ["Todos", "Piso", "Casa", "Apartamento"])
    metros_minimos = st.number_input("Metros cuadrados mínimos", 30, 200, 60)
    
    st.subheader("Portales a buscar")
    idealista_check = st.checkbox("Idealista", True)
    fotocasa_check = st.checkbox("Fotocasa", True)
    spotahome_check = st.checkbox("Spotahome", True)
    yaencontre_check = st.checkbox("Yaencontre", True)

# --- Generación de URLs actualizada ---
def generar_urls():
    urls = []
    ciudad_formateada = ubicacion.lower().replace(' ', '-')
    
    if idealista_check:
        urls.append(("Idealista", f"https://www.idealista.com/buscar/alquiler-viviendas/{ciudad_formateada}/con-precio-hasta_{precio_max},de-{habitaciones}-dormitorios/"))
    
    if fotocasa_check:
        urls.append(("Fotocasa", f"https://www.fotocasa.es/es/alquiler/viviendas/{ciudad_formateada}/todas-las-zonas/l?maxPrice={precio_max}&minRooms={habitaciones[0]}&minSurface={metros_minimos}"))
    
    if spotahome_check:
        urls.append(("Spotahome", f"https://www.spotahome.com/es/s/{ciudad_formateada}--spain/for-rent:apartments/bedrooms:{habitaciones[0]}?budget={precio_max-100}-{precio_max}"))
    
    if yaencontre_check:
        urls.append(("Yaencontre", f"https://www.yaencontre.com/alquiler/pisos/custom/f-{habitaciones[0]}-habitaciones,-{precio_max}euros,{metros_minimos}m2?point=40.46:-3.6852"))
    
    return urls

# --- Búsqueda principal actualizada ---
if st.button("Buscar Propiedades"):
    with st.spinner("Buscando en los portales inmobiliarios..."):
        todas_propiedades = []
        
        for portal, url in generar_urls():
            try:
                st.info(f"Buscando en {portal}...")
                if portal == "Idealista":
                    propiedades = scrape_idealista(url)
                elif portal == "Fotocasa":
                    propiedades = scrape_fotocasa(url)
                elif portal == "Spotahome":
                    propiedades = scrape_spotahome(url)
                elif portal == "Yaencontre":
                    propiedades = scrape_yaencontre(url)
                
                todas_propiedades.extend(propiedades)
                time.sleep(2)  # Respeta politicas de scraping
            
            except Exception as e:
                st.error(f"Error en {portal}: {str(e)}")
        
        if todas_propiedades:
            df = pd.DataFrame(todas_propiedades)
            
            # Aplicar filtros
            if tipo_propiedad != "Todos":
                df = df[df['Título'].str.contains(tipo_propiedad, case=False)]
            
            # Mostrar resultados mejorados
            st.success(f"✅ {len(df)} propiedades encontradas")
            for _, row in df.iterrows():
                with st.expander(f"{row['Portal']} - {row['Título']}"):
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        st.image("https://via.placeholder.com/200x150.png?text=Imagen+Propiedad", width=200)
                    with col2:
                        st.markdown(f"""
                        **Precio:** {row['Precio']}€  
                        **Habitaciones:** {row['Habitaciones']}  
                        **Metros:** {row['Metros']}  
                        **Zona:** {row['Zona']}  
                        **Enlace:** [{row['Portal']}]({row['Enlace']})
                        """)
            
            # Opción de descarga
            st.download_button(
                label="Descargar resultados",
                data=df.to_csv(index=False).encode('utf-8'),
                file_name=f"alquileres_{ubicacion}.csv",
                mime='text/csv'
            )
        else:
            st.warning("No se encontraron propiedades con los filtros seleccionados")

# --- Sección informativa ---
st.sidebar.markdown("""
**Consejos de uso:**
1. Usa filtros específicos para mejores resultados
2. Revisa periódicamente para nuevas propiedades
3. Exporta los resultados para comparar
""")
