# Advanced Mode Rules - Data-to-Dashboard Automator

## Critical Non-Obvious Patterns

### "La Guillotina" SQL Cleaning (services.py:138-148)
watsonx.ai returns SQL with extra text/comments. MUST use this exact pattern:
```python
# Find SELECT keyword, cut everything before
start_idx = generated_code.upper().find("SELECT")
generated_code = generated_code[start_idx:]
# Cut everything after first semicolon
end_idx = generated_code.find(";")
generated_code = generated_code[:end_idx + 1]
```
**Why**: Model adds explanations despite "output ONLY SQL" prompt. This is NOT optional.

### Self-Healing Retry Loop (services.py:212-273)
System retries failed SQL up to 3 times, passing previous error to watsonx.ai:
- Attempt 1: Generate SQL from natural language
- Attempt 2+: Pass previous SQL + error message to model for correction
- **Critical**: Initialize `sql_query = ""` BEFORE try block to avoid UnboundLocalError
- **Critical**: Use `ValueError` for SQL execution errors (triggers retry), `HTTPException` for fatal errors (stops retry)

### Database Path Quirk
SQLite path is `'sqlite:///backend/test_data.db'` (3 slashes + relative path from project root)
- NOT `sqlite:////absolute/path` (4 slashes)
- NOT `sqlite://backend/test_data.db` (2 slashes)
- Commands must run from project root, not backend/ directory

### Hardcoded Project ID
watsonx.ai requires `project_id: "ad58536c-3b21-437c-a44b-5a73fbab9609"` in payload (services.py:106)
- This is NOT in .env (intentional - tied to IBM Cloud project)
- Changing it will break API calls

### Schema Embedded in System Prompt
Database schema is hardcoded in services.py:98-102, NOT read from database
- Changes to mock_db.py schema require manual update in services.py
- Schema uses Spanish table names: usuarios, productos, transacciones

## IBM watsonx.ai Authentication
Two-step auth (non-standard):
1. POST to `https://iam.cloud.ibm.com/identity/token` with API Key → get IAM token
2. Use token in watsonx.ai calls (expires, implement refresh on 401)

Model: `ibm/granite-8b-code-instruct` (mandatory, not configurable)

## Access To
- MCP tools
- Browser tools