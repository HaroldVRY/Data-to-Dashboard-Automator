# 📊 Data-to-Dashboard Automator (IBM Hackathon 2026)

**Desarrollado por:** Harold Victor Reyna Yangali (Estudiante de Ingeniería de Sistemas - UNI)
**Tecnologías:** IBM watsonx.ai, IBM Bob, FastAPI, Streamlit, SQLite.

## 🚀 Visión General
Data-to-Dashboard Automator es una solución de **IA Generativa** diseñada para democratizar el acceso a los datos. Permite a usuarios sin conocimientos técnicos transformar lenguaje natural en consultas SQL precisas y dashboards visuales interactivos en tiempo real.

## 🧠 Innovación y Características Clave
*   **Auto-healing SQL Engine:** Implementa un loop de reintentos agénticos que detecta errores de ejecución y proporciona feedback automático a **watsonx.ai** para corregir la consulta.
*   **Lienzo de Datos Interactivo:** Integra un diagrama de Entidad-Relación dinámico (Mermaid.js) para que el usuario visualice la estructura de la base de datos antes de preguntar.
*   **Prompt Injection Architecture:** Utiliza técnicas de *Few-Shot Prompting* y *Context Injection* para garantizar que el modelo Granite-8b se mantenga estrictamente dentro del esquema de datos real.
*   **Visualización Inteligente:** Selección automatizada de gráficos basada en el tipo de datos devuelto (Categórico vs. Numérico).

## 🛠️ Arquitectura Técnica
*   **Backend:** FastAPI (Python) gestionando la lógica de negocio y la conexión con la base de datos SQLite.
*   **IA:** Integración con **IBM watsonx.ai** utilizando el modelo `granite-8b-code-instruct`.
*   **Frontend:** Streamlit con componentes personalizados e Iframes aislados para visualización de esquemas en entornos seguros de 2026.

## 📦 Instalación y Uso
1. Clonar el repositorio.
2. Crear un entorno virtual: `python -m venv venv`.
3. Instalar dependencias: `pip install -r requirements.txt`.
4. Configurar variables de entorno en `.env`: `IBM_API_KEY=tu_llave_aqui`.
5. Iniciar Backend: `python backend/main.py`.
6. Iniciar Frontend: `streamlit run frontend/app.py`.

---
*Proyecto creado para el Desafío de IBM Bob y watsonx.ai - Mayo 2026*
