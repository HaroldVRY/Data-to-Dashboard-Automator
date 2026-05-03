# 📊 Data-to-Dashboard Automator (IBM Hackathon 2026)

**Developer:** Harold Victor Reyna Yangali (Systems Engineering Student - Universidad Nacional de Ingeniería, Peru)
**Tech Stack:** IBM watsonx.ai, IBM Bob, FastAPI, Streamlit, SQLite.

## 🚀 Overview
Data-to-Dashboard Automator is a **Generative AI** solution designed to democratize data access[cite: 2]. It allows non-technical users to transform natural language into precise SQL queries and real-time interactive visual dashboards[cite: 2].

## 🧠 Innovation & Key Features
*   **Self-healing SQL Engine:** Implements an agentic retry loop that detects execution errors and provides automatic feedback to **watsonx.ai** to correct the query in real-time[cite: 1, 2].
*   **Interactive Data Canvas:** Integrates a dynamic Entity-Relationship diagram (Mermaid.js) so users can visualize the database structure before asking questions[cite: 2].
*   **Tag-based Isolation Architecture:** Uses `<razonamiento>` tags for Chain-of-Thought processing and markdown SQL blocks to separate logic from executable code[cite: 1, 2].
*   **Intelligent Visualization:** Automated chart selection based on the returned data type (Categorical vs. Numerical)[cite: 2].

## 🤖 IBM Bob Integration (Development Reports)
The development of this software was supported by **IBM Bob**, serving as the Lead Software Architect[cite: 2]. The complete history of tasks, bug fixes (including Mermaid rendering and SQL hallucinations), and architectural decisions can be found in the official reports located in the `docs/` folder[cite: 1, 2]:
*   [**Task Report 1:** SQL Cleaning & Agentic Loop Implementation](docs/bob_task_may-3-2026_12-59-44-am.md)[cite: 1]
*   [**Task Report 2:** Tag-based Isolation & Final Refinement](docs/bob_task_may-3-2026_2-35-02-am.md)[cite: 1]

## 🛠️ Technical Architecture
*   **Backend:** FastAPI (Python) managing business logic and the SQLite database connection[cite: 2].
*   **AI:** Integration with **IBM watsonx.ai** using the `ibm/granite-8b-code-instruct` model with Greedy Decoding (Temperature 0.0)[cite: 1, 2].
*   **Frontend:** Streamlit with custom components and isolated Iframes for schema visualization in secure 2026 environments[cite: 2].

## 📦 Installation & Usage
1. Clone the repository.
2. Create a virtual environment: `python -m venv venv`.
3. Install dependencies: `pip install -r requirements.txt`.
4. Set environment variables in `.env`: `IBM_API_KEY=your_key_here`.
5. Start Backend: `python backend/main.py`.
6. Start Frontend: `streamlit run frontend/app.py`.

---
*Project created for the IBM Bob & watsonx.ai Challenge - May 2026*
