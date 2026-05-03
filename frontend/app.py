"""
Streamlit Frontend for Data-to-Dashboard Automator.
Converts natural language queries to SQL and visualizes results.
"""
import streamlit as st
import streamlit.components.v1 as components
import requests
import pandas as pd
from datetime import datetime
import inspect

# Configure page
st.set_page_config(
    page_title="Data-to-Dashboard Automator",
    page_icon="📊",
    layout="wide"
)

# Title and description
st.title("📊 Data-to-Dashboard Automator")
st.markdown("""
Convierte tus consultas en lenguaje natural a SQL usando **IBM watsonx.ai** 
y visualiza los resultados instantáneamente.
""")

# Inicializar variable de estado para la consulta
if 'query_text' not in st.session_state:
    st.session_state.query_text = ""

# Sidebar with interactive examples
with st.sidebar:
    st.header("💡 Pruebas Unitarias (One-Click)")
    st.caption("Haz clic para cargar la consulta:")
    ejemplos = [
        "¿Cuáles son los ingresos totales por categoría de producto?",
        "¿Cuál es el precio promedio de los productos por categoría?",
        "Muestra el nombre del usuario, el nombre del producto que compró y la fecha de la transacción.",
        "Lista los productos de la categoría 'Electrónica' que fueron comprados por usuarios de 'Colombia'.",
        "Encuentra a los usuarios que han gastado más de 1000 en total y muestra cuánto gastaron."
    ]
    for ej in ejemplos:
        if st.button(ej, use_container_width=True):
            st.session_state.query_text = ej
    
    st.divider()
    st.markdown("**Powered by:**")
    st.markdown("- IBM watsonx.ai")
    st.markdown("- FastAPI")
    st.markdown("- Streamlit")

# Create tabs
tab_consultas, tab_esquema, tab_futuro = st.tabs(["💬 Realizar Consultas", "🗺️ Esquema de Datos", "🚀 Futuro y Escalabilidad"])

# Tab 1: Query Interface
with tab_consultas:
    st.divider()
    
    # Text area for user query with session_state
    query = st.text_area(
        "🔍 Ingresa tu consulta en lenguaje natural:",
        value=st.session_state.query_text,
        height=100
    )
    
    # Generate button
    if st.button("🚀 Generar Dashboard", type="primary", use_container_width=True):
        if not query.strip():
            st.warning("⚠️ Por favor ingresa una consulta.")
        else:
            # Show spinner while processing
            with st.spinner("🤖 Procesando consulta con IBM watsonx.ai..."):
                try:
                    # Make POST request to backend
                    response = requests.post(
                        "http://localhost:8000/process-query",
                        json={"query": query},
                        timeout=60
                    )
                    
                    # Check if request was successful
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Display success message
                        st.success("✅ Consulta procesada exitosamente!")
                        
                        # Create two columns for layout
                        col1, col2 = st.columns([1, 1])
                        
                        with col1:
                            st.subheader("📝 SQL Generado")
                            st.code(data['generated_code'], language='sql')
                        
                        with col2:
                            st.subheader("📊 Información")
                            st.metric("Filas retornadas", len(data['data']))
                            st.metric("Columnas", len(data['columns']))
                        
                        st.divider()
                        
                        # Convert response to DataFrame
                        if data['data'] and data['columns']:
                            df = pd.DataFrame(data['data'], columns=data['columns'])
                            
                            # Display data table
                            st.subheader("📋 Datos")
                            st.dataframe(df, use_container_width=True)
                            
                            st.divider()
                            
                            # Automatic Dashboard Visualization
                            with st.expander("📊 Visualización Gráfica", expanded=True):
                                if len(df) > 0 and len(df.columns) > 1:
                                    # Identify numeric columns
                                    numeric_cols = df.select_dtypes(include='number').columns.tolist()
                                    
                                    # Identify categorical/text columns (object, string, datetime)
                                    categorical_cols = df.select_dtypes(include=['object', 'string']).columns.tolist()
                                    date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
                                    
                                    # Try to detect date columns by name if not already datetime
                                    if not date_cols:
                                        potential_date_cols = [col for col in df.columns if 'fecha' in col.lower() or 'date' in col.lower()]
                                        if potential_date_cols:
                                            try:
                                                df[potential_date_cols[0]] = pd.to_datetime(df[potential_date_cols[0]])
                                                date_cols = potential_date_cols
                                            except:
                                                pass
                                    
                                    # Combine categorical and date columns
                                    x_axis_candidates = categorical_cols + date_cols
                                    
                                    # Automatic visualization logic
                                    if numeric_cols and x_axis_candidates:
                                        # Get first numeric column for y-axis
                                        y_col = numeric_cols[0]
                                        # Get first categorical/date column for x-axis
                                        x_col = x_axis_candidates[0]
                                        
                                        # Create visualization
                                        try:
                                            # If x-axis is date, use line chart
                                            if x_col in date_cols:
                                                df_sorted = df.sort_values(x_col)
                                                st.line_chart(
                                                    data=df_sorted,
                                                    x=x_col,
                                                    y=y_col,
                                                    use_container_width=True
                                                )
                                                st.caption(f"📈 Serie temporal: {y_col} a lo largo de {x_col}")
                                            else:
                                                # Use bar chart for categorical data
                                                st.bar_chart(
                                                    data=df,
                                                    x=x_col,
                                                    y=y_col,
                                                    use_container_width=True
                                                )
                                                st.caption(f"📊 Gráfico de barras: {y_col} por {x_col}")
                                        except Exception as e:
                                            st.warning(f"⚠️ No se pudo generar la visualización automática: {str(e)}")
                                    
                                    elif numeric_cols:
                                        # Only numeric columns - show first one as bar chart
                                        st.bar_chart(df[numeric_cols[0]], use_container_width=True)
                                        st.caption(f"📊 Distribución de {numeric_cols[0]}")
                                    
                                    else:
                                        st.info("💡 No se encontraron columnas numéricas para visualizar.")
                                
                                elif len(df) == 0:
                                    st.info("📭 La consulta no retornó datos para visualizar.")
                                else:
                                    st.info("💡 Se necesitan al menos 2 columnas para generar visualizaciones.")
                        else:
                            st.warning("⚠️ No se recibieron datos del backend.")
                    
                    else:
                        # Handle error responses
                        error_data = response.json()
                        st.error(f"❌ Error {response.status_code}: {error_data.get('detail', 'Error desconocido')}")
                        
                except requests.exceptions.Timeout:
                    st.error("⏱️ Timeout: La solicitud tardó demasiado. Por favor intenta de nuevo.")
                except requests.exceptions.ConnectionError:
                    st.error("🔌 Error de conexión: No se pudo conectar al backend. Asegúrate de que el servidor esté corriendo en http://localhost:8000")
                except Exception as e:
                    st.error(f"❌ Error inesperado: {str(e)}")

# Tab 2: Database Schema
with tab_esquema:
    st.markdown("### Estructura de la Base de Datos")
    
    # Usamos cleandoc para eliminar cualquier espacio de indentación de Python
    mermaid_definition = inspect.cleandoc("""
        erDiagram
            usuarios ||--o{ transacciones : realiza
            productos ||--o{ transacciones : incluye
            usuarios {
                int id
                string nombre
                string email
                string pais
            }
            productos {
                int id_producto
                string nombre_producto
                string categoria
                float precio
            }
            transacciones {
                int id_transaccion
                int id_usuario
                int id_producto
                float monto
                date fecha_compra
            }
    """)
    
    # HTML autocontenido para el Iframe
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <script>
        mermaid.initialize({{ startOnLoad: true, theme: 'default' }});
    </script>
</head>
<body>
    <div class="mermaid">
{mermaid_definition}
    </div>
</body>
</html>
"""
    
    # Renderizar en iframe aislado
    components.html(html_content, height=450, scrolling=True)
    
    st.divider()
    st.markdown("#### 📋 Descripción de las Tablas")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**👥 USUARIOS**")
        st.markdown("""
        - `id`: Identificador único
        - `nombre`: Nombre completo
        - `email`: Correo electrónico
        - `pais`: País de residencia
        """)
    
    with col2:
        st.markdown("**📦 PRODUCTOS**")
        st.markdown("""
        - `id_producto`: Identificador único
        - `nombre_producto`: Nombre del producto
        - `categoria`: Categoría del producto
        - `precio`: Precio en moneda local
        """)
    
    with col3:
        st.markdown("**💳 TRANSACCIONES**")
        st.markdown("""
        - `id_transaccion`: Identificador único
        - `id_usuario`: Referencia al usuario
        - `id_producto`: Referencia al producto
        - `monto`: Monto de la transacción
        - `fecha_compra`: Fecha de la compra
        """)

# Tab 3: Future and Scalability
with tab_futuro:
    st.markdown("### 🔮 Próximos Pasos y Visión de Escalabilidad")
    
    st.info("""
    Este software ha sido diseñado como un MVP robusto. Con más tiempo de desarrollo, las siguientes funciones potenciarían su impacto comercial y técnico:
    """)
    
    st.markdown("""
    #### 🎯 Funcionalidades Futuras
    
    **🗄️ BYOS (Bring Your Own Schema)**
    - Permitir que el usuario cargue su propio archivo `.sql` o `.db` para que la IA aprenda instantáneamente nuevas estructuras y responda sobre ellas.
    - Análisis automático de esquemas y generación de prompts optimizados.
    
    **📊 Exportación Multiformato**
    - Descarga directa de los resultados en PDF (reporte ejecutivo), Excel avanzado o formato JSON para integración con otras APIs.
    - Templates personalizables para reportes corporativos.
    
    **📈 Dashboard Multi-gráfico**
    - Capacidad de generar no uno, sino un tablero completo de visualizaciones (KPIs, líneas y barras) a partir de una sola petición compleja.
    - Layouts inteligentes basados en el tipo de datos.
    
    **💾 Historial y Favoritos**
    - Implementar una base de datos de usuario para guardar consultas exitosas, permitiendo crear una biblioteca de "Query Assets" personalizados.
    - Sistema de etiquetado y búsqueda de consultas guardadas.
    
    **🌍 Soporte Multi-Lenguaje Nativo**
    - Optimizar los prompts para que el sistema detecte y responda con la misma precisión en Inglés, Portugués y Quechua, eliminando barreras de acceso.
    - Detección automática del idioma del usuario.
    """)
    
    st.divider()
    
    st.markdown("#### 🚀 Impacto Potencial")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **💼 Comercial**
        - Reducción del 80% en tiempo de análisis de datos
        - Democratización del acceso a insights empresariales
        - ROI medible en semanas, no meses
        """)
    
    with col2:
        st.markdown("""
        **🔧 Técnico**
        - Arquitectura escalable basada en microservicios
        - API RESTful lista para integraciones
        - Modelo de IA auto-mejorable con feedback
        """)

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: gray;'>
    <small>Data-to-Dashboard Automator | IBM Hackathon 2024</small>
</div>
""", unsafe_allow_html=True)

# Made with Bob
