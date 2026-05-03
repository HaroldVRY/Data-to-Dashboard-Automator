# 📊 Data-to-Dashboard Automator (IBM Hackathon 2026)

**Developer:** Harold Victor Reyna Yangali (Systems Engineering Student - Universidad Nacional de Ingeniería, Peru)
**Tech Stack:** IBM watsonx.ai, IBM Bob, FastAPI, Streamlit, SQLite.

## 🚀 Overview
Data-to-Dashboard Automator is a **Generative AI** solution designed to democratize data access. It allows non-technical users to transform natural language into precise SQL queries and real-time interactive visual dashboards.

## 🧠 Innovation & Key Features
*   **Self-healing SQL Engine:** Implements an agentic retry loop that detects execution errors and provides automatic feedback to **watsonx.ai** to correct the query in real-time.
*   **Interactive Data Canvas:** Integrates a dynamic Entity-Relationship diagram (Mermaid.js) so users can visualize the database structure before asking questions.
*   **Prompt Injection Architecture:** Utilizes *Few-Shot Prompting* and *Context Injection* techniques to ensure the Granite-8b model strictly adheres to the actual database schema.
*   **Intelligent Visualization:** Automated chart selection based on the returned data type (Categorical vs. Numerical).

## 🛠️ Technical Architecture
*   **Backend:** FastAPI (Python) managing business logic and the SQLite database connection.
*   **AI:** Integration with **IBM watsonx.ai** using the `granite-8b-code-instruct` model.
*   **Frontend:** Streamlit with custom components and isolated Iframes for schema visualization in secure 2026 environments.

## 📦 Installation & Usage
1. Clone the repository.
2. Create a virtual environment: `python -m venv venv`.
3. Install dependencies: `pip install -r requirements.txt`.
4. Set environment variables in `.env`: `IBM_API_KEY=your_key_here`.
5. Start Backend: `python backend/main.py`.
6. Start Frontend: `streamlit run frontend/app.py`.

---
*Project created for the IBM Bob & watsonx.ai Challenge - May 2026*
