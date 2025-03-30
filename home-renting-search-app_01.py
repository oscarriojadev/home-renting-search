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
st.set_page_config(page_title="Buscador Avanzado de Alquileres", layout="wide")
st.title("🏠 Buscador Multiplataforma de Alquileres")

# --- Configuración de scraping ---
HEADERS = {
    'User-Agent': UserAgent().random,
    'Accept-Language': 'es-ES,es;q=0.9',
    'Referer': 'https://www.google.com/'
}

# URLs específicas actualizadas
PORTAL_URLS = {
    'Idealista': 'https://www.idealista.com/areas/alquiler-viviendas/con-precio-hasta_1100,metros-cuadrados-mas-de_60,de-dos-dormitorios,de-tres-dormitorios,de-cuatro-cinco-habitaciones-o-mas/mapa-google?shape=((%7BpzuF%7ElsUaLeAg%40gQ%7BWhCia%40qNaW%7DS_%5C_U%7BLen%40ZgQj%7DCvI_FxjBcGdAuBhR))',
    'Fotocasa': 'https://www.fotocasa.es/es/alquiler/viviendas/madrid-capital/todas-las-zonas/l?maxPrice=1100&minRooms=2&minSurface=60&searchArea=i-z07ghvjBwlYs0mHsxiGzrzWi8tE057Gs2mUgr_Gih8B5z3B415Bxj1CuuG2jRhmqJ9hM-tiBiyGz8-B5zRxgmHysqLp_zVu2mwB-1V-28Ejh8BknrCzhkK1l_GsqrD7s1Bz1xDl_5DjysDz18Ci2_BhiqC7qG&zoom=14',
    'Spotahome': 'https://www.spotahome.com/es/s/madrid--spain/for-rent:apartments/for-rent:studios/bedrooms:1/bedrooms:2?move-in=2025-04-26&bed=double,single-group&budget=0-1100&rentalType[]=longTerm&moveInFrom=2025-04-26&moveInTo=2030-04-26&includeBlockedProperties=1&mapCenter=40.44767441477353,-3.7002290341000643',
    'Yaencontre': 'https://www.yaencontre.com/alquiler/pisos/custom/f-2-habitaciones,-1100euros,50m2/mapa?polygon=utzuFvytU%7BLse%40r%40yRwZwBwZmEgs%40io%40iFoc%40lAa%5E%7EiC%60K_HllBvF%7Cq%40%7BK%60K'
}

# --- Funciones de scraping para todos los portales ---
def scrape_idealista():
    try:
        response = requests.get(PORTAL_URLS['Idealista'], headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        propiedades = []
        
        for item in soup.find_all('article', {'class': 'item'}):
            try:
                detalles = {
                    'Portal': 'Idealista',
                    'Título': item.find('a', {'class': 'item-link'}).get_text(strip=True),
                    'Precio': int(re.sub(r'\D', '', item.find('span', {'class': 'item-price'}).text)),
                    'Habitaciones': item.find_all('span', {'class': 'item-detail'})[0].text,
                    'Metros': item.find_all('span', {'class': 'item-detail'})[1].text,
                    'Zona': item.find('span', {'class': 'item-town'}).text if item.find('span', {'class': 'item-town'}) else None,
                    'Enlace': urljoin(PORTAL_URLS['Idealista'], item.find('a')['href']),
                    'Plantas': item.find('span', text=re.compile(r'\dª planta')).text if item.find('span', text=re.compile(r'\dª planta')) else None,
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
        response = requests.get(PORTAL_URLS['Fotocasa'], headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        propiedades = []
        
        for item in soup.find_all('div', {'class': 're-CardPackPremium'}):
            try:
                detalles = {
                    'Portal': 'Fotocasa',
                    'Título': item.find('a', {'class': 're-Card-title'}).get_text(strip=True),
                    'Precio': int(re.sub(r'\D', '', item.find('span', {'class': 're-Card-price'}).text)),
                    'Habitaciones': item.find_all('span', {'class': 're-Card-feature'})[0].text,
                    'Metros': item.find_all('span', {'class': 're-Card-feature'})[1].text,
                    'Zona': item.find('span', {'class': 're-Card-title'}).text.split(',')[-1].strip(),
                    'Enlace': urljoin(PORTAL_URLS['Fotocasa'], item.find('a')['href']),
                    'Características': [feat.text for feat in item.find_all('span', {'class': 're-Card-feature'})[2:]],
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
        response = requests.get(PORTAL_URLS['Spotahome'], headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        propiedades = []
        
        for item in soup.find_all('article', {'class': 'PlaceCard'}):
            try:
                titulo = item.find('h3', {'class': 'PlaceCard-title'}).get_text(strip=True)
                precio = int(re.sub(r'\D', '', item.find('span', {'class': 'PlaceCard-price'}).text))
                detalles = item.find_all('li', {'class': 'PlaceCard-feature'})
                
                propiedad = {
                    'Portal': 'Spotahome',
                    'Título': titulo,
                    'Precio': precio,
                    'Habitaciones': next((d.text for d in detalles if 'habitación' in d.text), 'No especificado'),
                    'Metros': next((d.text for d in detalles if 'm²' in d.text), 'No especificado'),
                    'Zona': item.find('span', {'class': 'PlaceCard-city'}).text if item.find('span', {'class': 'PlaceCard-city'}) else 'Madrid',
                    'Enlace': urljoin(PORTAL_URLS['Spotahome'], item.find('a', {'class': 'PlaceCard-link'})['href']),
                    'Disponibilidad': item.find('span', {'class': 'PlaceCard-availability'}).text if item.find('span', {'class': 'PlaceCard-availability'}) else 'Disponible',
                    'Fecha': datetime.now().strftime('%Y-%m-%d')
                }
                propiedades.append(propiedad)
            except Exception as e:
                st.warning(f"Error procesando propiedad en Spotahome: {str(e)}")
        return propiedades
    except Exception as e:
        st.error(f"Error scraping Spotahome: {str(e)}")
        return []

def scrape_yaencontre():
    try:
        response = requests.get(PORTAL_URLS['Yaencontre'], headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        propiedades = []
        
        for item in soup.find_all('div', {'class': 'property-info'}):
            try:
                detalles = {
                    'Portal': 'Yaencontre',
                    'Título': item.find('a', {'class': 'property-title'}).get_text(strip=True),
                    'Precio': int(re.sub(r'\D', '', item.find('div', {'class': 'price'}).text)),
                    'Habitaciones': item.find('li', {'class': 'icon-bed'}).text.strip(),
                    'Metros': item.find('li', {'class': 'icon-m2'}).text.strip(),
                    'Zona': item.find('div', {'class': 'location'}).text.strip(),
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

# --- Interfaz mejorada ---
with st.sidebar:
    st.header("⚙️ Configuración de Búsqueda")
    portales = st.multiselect(
        "Selecciona portales a consultar",
        options=list(PORTAL_URLS.keys()),
        default=list(PORTAL_URLS.keys())
    )
    
    st.subheader("Filtros Avanzados")
    with st.expander("Características adicionales"):
        min_metros = st.slider("Metros cuadrados mínimos", 40, 150, 60)
        max_precio = st.slider("Precio máximo (€)", 500, 1500, 1100)
        tipos_propiedad = st.multiselect(
            "Tipo de propiedad",
            options=['Apartamento', 'Piso', 'Estudio', 'Casa'],
            default=['Apartamento', 'Piso']
        )
        parking = st.checkbox("Con parking")
        amueblado = st.checkbox("Amueblado")

# --- Visualización de resultados ---
if st.button("🔍 Iniciar Búsqueda"):
    with st.spinner("Buscando en los portales seleccionados..."):
        resultados = []
        
        if 'Idealista' in portales:
            resultados.extend(scrape_idealista())
            time.sleep(2)
        if 'Fotocasa' in portales:
            resultados.extend(scrape_fotocasa())
            time.sleep(2)
        if 'Spotahome' in portales:
            resultados.extend(scrape_spotahome())
            time.sleep(2)
        if 'Yaencontre' in portales:
            resultados.extend(scrape_yaencontre())
        
        if resultados:
            df = pd.DataFrame(resultados)
            
            # Aplicar filtros dinámicos
            df = df[
                (df['Precio'] <= max_precio) &
                (df['Metros'].apply(lambda x: int(re.sub(r'\D', '', str(x)) if str(x).isdigit() else 0) >= min_metros)) &
                (df['Título'].apply(lambda x: any(tipo in x for tipo in tipos_propiedad)))
            ]
            
            if parking:
                df = df[df.apply(lambda x: 'parking' in str(x.get('Características', '')).lower() or 
                                'parking' in x['Título'].lower(), axis=1)]
            
            if amueblado:
                df = df[df.apply(lambda x: 'amueblado' in str(x.get('Características', '')).lower() or 
                                'amueblado' in x['Título'].lower(), axis=1)]

            # Mostrar resultados mejorados
            st.success(f"✅ {len(df)} propiedades encontradas")
            
            for _, row in df.iterrows():
                with st.expander(f"{row['Portal']} - {row['Título']}", expanded=True):
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        st.image("https://via.placeholder.com/250x150.png?text=Imagen+Propiedad", width=250)
                    with col2:
                        info = f"""
                        **💰 Precio:** {row['Precio']}€  
                        **🚪 Habitaciones:** {row['Habitaciones']}  
                        **📏 Metros:** {row['Metros']}  
                        **📍 Zona:** {row['Zona']}  
                        **🌐 Enlace:** [{row['Portal']}]({row['Enlace']})
                        """
                        
                        if row['Portal'] == 'Spotahome':
                            info += f"\n**📅 Disponibilidad:** {row.get('Disponibilidad', 'N/A')}"
                        if row.get('Características'):
                            info += f"\n**✨ Características:** {', '.join(row['Características'])}"
                        
                        st.markdown(info)
            
            # Opciones de exportación
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="📥 Descargar CSV",
                    data=df.to_csv(index=False).encode('utf-8'),
                    file_name=f"alquileres_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime='text/csv'
                )
            with col2:
                st.download_button(
                    label="📊 Descargar Excel",
                    data=df.to_excel(index=False),
                    file_name=f"alquileres_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime='application/vnd.ms-excel'
                )
        else:
            st.warning("No se encontraron propiedades con los criterios seleccionados")

# --- Notas técnicas ---
st.markdown("""
### 📝 Características principales:
1. **Cobertura completa** de 4 portales principales
2. **Filtros inteligentes** en tiempo real
3. **Datos enriquecidos** con disponibilidad y características
4. **Resultados verificados** en Spotahome
5. **Búsqueda específica** para Madrid centro

### ⚠️ Limitaciones conocidas:
- Los selectores HTML pueden cambiar sin previo aviso
- Algunos filtros varían entre portales
- Los precios no incluyen gastos adicionales en algunos casos
""")
