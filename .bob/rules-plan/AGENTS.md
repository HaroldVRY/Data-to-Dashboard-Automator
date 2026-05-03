# Plan Mode Rules - Data-to-Dashboard Automator

## Critical Non-Obvious Architectural Patterns

### "La Guillotina" SQL Cleaning Pattern (services.py:138-148)
watsonx.ai returns SQL with extra text despite prompts. System uses aggressive cleaning:
```python
start_idx = generated_code.upper().find("SELECT")
generated_code = generated_code[start_idx:]
end_idx = generated_code.find(";")
generated_code = generated_code[:end_idx + 1]
```
**Architectural implication**: Cannot trust model output format, must always post-process.

### Self-Healing Retry Architecture (services.py:212-273)
System implements automatic SQL correction by feeding errors back to watsonx.ai:
- Attempt 1: Generate SQL from natural language
- Attempt 2-3: Pass previous SQL + error to model for self-correction
- **Critical design**: `ValueError` triggers retry, `HTTPException` stops retry (intentional error type separation)
- **Critical design**: `sql_query = ""` initialized before try block (prevents UnboundLocalError in retry logic)

### Database Path Architecture
SQLite uses `'sqlite:///backend/test_data.db'` (3 slashes + relative path from project root)
- All commands must run from project root, not backend/ directory
- This affects Docker volume mounts and CI/CD pipelines

### Hardcoded Project ID Constraint
watsonx.ai requires `project_id: "ad58536c-3b21-437c-a44b-5a73fbab9609"` in payload (services.py:106)
- NOT in .env (intentional - tied to specific IBM Cloud project)
- Cannot be made configurable without breaking API contract
- Deployment to different IBM Cloud projects requires code change

### Schema Synchronization Issue
Database schema is hardcoded in services.py:98-102, NOT read from database
- Changes to mock_db.py schema require manual update in services.py
- No automatic schema discovery or validation
- Schema drift between database and prompt is possible
- Uses Spanish table names: usuarios, productos, transacciones

## IBM watsonx.ai Authentication Architecture
Two-step auth (non-standard OAuth):
1. POST to `https://iam.cloud.ibm.com/identity/token` with API Key → IAM token
2. Use token in watsonx.ai calls (expires, implement refresh on 401)

Model: `ibm/granite-8b-code-instruct` (mandatory, not configurable)

## Architectural Constraints for Planning
- Token refresh logic must be implemented (tokens expire)
- SQL cleaning is mandatory (model output unreliable)
- Retry logic uses error types for control flow (ValueError vs HTTPException)
- Schema changes require updates in two places (database + prompt)
- Project ID is environment-specific (affects multi-environment deployments)