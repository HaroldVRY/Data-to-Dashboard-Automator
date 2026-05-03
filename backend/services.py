"""
IBM watsonx.ai integration service.
Handles authentication and code/SQL generation.
"""
import os
import requests
import json
import re
from typing import Optional, Dict
from dotenv import load_dotenv
import pandas as pd
from sqlalchemy import create_engine, text
from fastapi import HTTPException

# Load environment variables
load_dotenv()


class WatsonxService:
    """Service for interacting with IBM watsonx.ai API."""
    
    IAM_TOKEN_URL = "https://iam.cloud.ibm.com/identity/token"
    WATSONX_URL = "https://us-south.ml.cloud.ibm.com/ml/v1/text/chat?version=2023-05-29"
    MODEL_ID = "ibm/granite-8b-code-instruct"
    
    def __init__(self):
        """Initialize the service with API key from environment."""
        self.api_key = os.getenv('IBM_API_KEY')
        if not self.api_key:
            raise ValueError("IBM_API_KEY not found in environment variables")
    
    async def get_iam_token(self) -> str:
        """
        Generate IAM token from IBM Cloud API Key.
        
        Returns:
            str: IAM access token
            
        Raises:
            requests.exceptions.Timeout: If request times out
            requests.exceptions.HTTPError: If authentication fails
        """
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = {
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
            "apikey": self.api_key
        }
        
        try:
            response = requests.post(
                self.IAM_TOKEN_URL,
                headers=headers,
                data=data,
                timeout=10
            )
            response.raise_for_status()
            token_data = response.json()
            return token_data["access_token"]
            
        except requests.exceptions.Timeout:
            raise requests.exceptions.Timeout(
                "Timeout while generating IAM token. Please retry."
            )
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise requests.exceptions.HTTPError(
                    "Invalid API Key. Please check your IBM_API_KEY in .env file.",
                    response=e.response
                )
            raise
    
    async def generate_sql(self, query: str, token: str, previous_sql: str = None, error_msg: str = None) -> str:
        """
        Generate SQL code from natural language query using watsonx.ai.
        
        Args:
            query: Natural language query from user
            token: IAM access token
            previous_sql: Previous SQL that failed (for retry logic)
            error_msg: Error message from previous attempt (for retry logic)
            
        Returns:
            str: Generated SQL code
            
        Raises:
            requests.exceptions.Timeout: If request times out
            requests.exceptions.HTTPError: If API call fails
        """
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        system_prompt = """You are a strict SQL Database Agent. You translate Spanish natural language into SQLite.
CRITICAL RULE: DO NOT invent tables like 'log' or 'hiking_trip'. You are RESTRICTED to this schema:

SCHEMA:
CREATE TABLE usuarios (id INTEGER PRIMARY KEY, nombre TEXT, email TEXT, pais TEXT);
CREATE TABLE productos (id_producto INTEGER PRIMARY KEY, nombre_producto TEXT, categoria TEXT, precio REAL);
CREATE TABLE transacciones (id_transaccion INTEGER PRIMARY KEY, id_usuario INTEGER, id_producto INTEGER, monto REAL, fecha_compra DATE);

EXAMPLES (Follow this exact pattern):
Input: Muestra todos los usuarios de Colombia
<razonamiento>
Piden usuarios de Colombia. Usaré la tabla 'usuarios' y filtraré donde 'pais' sea 'Colombia'.
</razonamiento>
```sql
SELECT * FROM usuarios WHERE pais = 'Colombia';
```

Input: Lista las últimas 10 transacciones
<razonamiento>
Piden las últimas transacciones. Usaré la tabla 'transacciones', ordenaré por 'fecha_compra' de forma descendente y limitaré a 10.
</razonamiento>
```sql
SELECT * FROM transacciones ORDER BY fecha_compra DESC LIMIT 10;
```"""
        
        # Prompt Injection: Move all context to user message to avoid System Prompt Neglect
        if previous_sql and error_msg:
            user_content = f"{system_prompt}\n\nCRITICAL ERROR in your previous attempt: {error_msg}. You MUST fix the SQL using ONLY the provided tables. DO NOT explain, just output the reasoning tags and the SQL block.\n\nInput: {query}"
        else:
            user_content = f"{system_prompt}\n\nNow, process this request strictly following the exact pattern above.\nInput: {query}"
        
        payload = {
            "project_id": "ad58536c-3b21-437c-a44b-5a73fbab9609",
            "model_id": self.MODEL_ID,
            "messages": [
                {
                    "role": "user",
                    "content": user_content
                }
            ],
            "parameters": {
                "max_tokens": 500,
                "temperature": 0.0
            }
        }
        
        try:
            response = requests.post(
                self.WATSONX_URL,
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            
            # Extract generated code from response
            generated_code = result.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            generated_code = generated_code.replace("```sql", "").replace("```", "")
            
            # La Guillotina: Buscar dónde empieza realmente la consulta
            start_idx = generated_code.upper().find("SELECT")
            if start_idx != -1:
                generated_code = generated_code[start_idx:]
                # Cortar todo lo que haya después del primer punto y coma
                end_idx = generated_code.find(";")
                if end_idx != -1:
                    generated_code = generated_code[:end_idx + 1]
            else:
                raise ValueError("El modelo no generó la palabra clave SELECT.")
            
            return generated_code
            
        except ValueError:
            # Allow ValueError to propagate to Retry Loop without modification
            raise
        except HTTPException:
            # Re-raise HTTPException to propagate to client with correct status code
            raise
        except requests.exceptions.Timeout:
            raise requests.exceptions.Timeout(
                "Timeout while calling watsonx.ai API. Please retry."
            )
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise requests.exceptions.HTTPError(
                    "IAM token expired. Token will be regenerated on next request.",
                    response=e.response
                )
            elif e.response.status_code == 429:
                raise requests.exceptions.HTTPError(
                    "Rate limit exceeded. Please wait before retrying.",
                    response=e.response
                )
            raise
        except Exception as e:
            raise Exception(f"Error generating SQL: {str(e)}")
    
    def execute_sql_and_format(self, sql_query: str) -> Dict:
        """
        Execute SQL query against SQLite database and format results.
        
        Args:
            sql_query: SQL query string to execute
            
        Returns:
            Dict with 'columns' and 'data' keys containing query results
            
        Raises:
            ValueError: If SQL execution fails (for internal retry logic)
        """
        try:
            # Connect to SQLite database
            engine = create_engine('sqlite:///backend/test_data.db')
            
            # Execute query using Pandas
            with engine.connect() as connection:
                df = pd.read_sql(text(sql_query), connection)
            
            # Fill null values with empty strings
            df = df.fillna("")
            
            # Format result as dictionary
            result = {
                "columns": df.columns.tolist(),
                "data": df.values.tolist()
            }
            
            return result
            
        except Exception as e:
            # Raise ValueError for internal retry logic
            raise ValueError(str(e))

    async def process_query_with_retry(self, query: str, max_retries: int = 3) -> dict:
        """
        Process query with automatic retry logic for self-healing SQL generation.
        
        Args:
            query: Natural language query from user
            max_retries: Maximum number of retry attempts
            
        Returns:
            dict: Result with data, columns, and generated_code
            
        Raises:
            HTTPException: If unable to generate valid SQL after max_retries
        """
        # Get IAM token internally
        try:
            token = await self.get_iam_token()
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Authentication error: {str(e)}"
            )
        
        # Initialize retry variables
        last_sql = None
        last_error = None
        
        # Retry loop
        for attempt in range(max_retries):
            sql_query = ""  # Initialize variable BEFORE try to avoid UnboundLocalError
            try:
                # Generate SQL (with error feedback if retrying)
                sql_query = await self.generate_sql(query, token, last_sql, last_error)
                
                # Try to execute the SQL
                result = self.execute_sql_and_format(sql_query)
                
                # Success! Return the result
                return {
                    "data": result["data"],
                    "columns": result["columns"],
                    "generated_code": sql_query
                }
                
            except ValueError as e:
                # If fails, keep previous last_sql if no new one was generated
                last_sql = sql_query if sql_query else last_sql
                last_error = str(e)
                continue
            
            except Exception as e:
                # Unexpected error - don't retry
                raise HTTPException(
                    status_code=500,
                    detail=f"Error inesperado: {str(e)}"
                )
        
        # If loop completes without success, raise error
        raise HTTPException(
            status_code=400,
            detail=f"No se pudo generar SQL válido tras {max_retries} intentos. Último error: {last_error}"
        )

# Made with Bob
