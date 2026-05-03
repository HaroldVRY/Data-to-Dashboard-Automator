# Especificación del Proyecto: Data-to-Dashboard Automator

## Objetivo Principal
Construir una herramienta que acelere el proceso de análisis de datos (Turn idea into impact faster). El sistema debe recibir una consulta en lenguaje natural del usuario, utilizar IBM watsonx.ai para traducirla a código/SQL, procesar los datos estructurados en el backend y enviarlos listos para ser visualizados en el frontend.

## Arquitectura y Stack Tecnológico
*   **Backend (Mi rol):** Python, FastAPI, Pandas, SQLAlchemy.
*   **Frontend (Compañero):** Streamlit o React (consumirá el endpoint de FastAPI).
*   **IA / LLM:** IBM watsonx.ai API (Modelo: `ibm/granite-8b-code-instruct`).
*   **Infraestructura:** Contenedores Docker (Docker Compose).

## Reglas de Desarrollo Estrictas
1.  **Seguridad:** Las credenciales de IBM Cloud (API Key) NUNCA deben estar en el código fuente (Hardcoded). Deben leerse desde variables de entorno (`.env`).
2.  **Autenticación IBM:** Para usar watsonx.ai, el backend debe generar primero un token IAM temporal (haciendo POST a `https://iam.cloud.ibm.com/identity/token`) usando la API Key.
3.  **Modularidad:** El código debe estar separado (ej. `main.py` para endpoints, `services.py` para lógica de IA y Pandas, `database.py` para la DB SQLite de prueba).
4.  **Eficiencia:** Escribir código limpio, con docstrings, y manejo de errores (Try/Except) especialmente en las llamadas HTTP a IBM Cloud.