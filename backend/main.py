"""
FastAPI backend for Data-to-Dashboard Automator.
Handles natural language queries and returns structured data.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from typing import List, Any

from services import WatsonxService

# Initialize FastAPI app
app = FastAPI(
    title="Data-to-Dashboard Automator",
    description="Convert natural language queries to SQL using IBM watsonx.ai",
    version="1.0.0"
)

# Configure CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class QueryRequest(BaseModel):
    """Request model for natural language query."""
    query: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "Show me all users who registered in the last 30 days"
            }
        }


class QueryResponse(BaseModel):
    """Response model with generated code and data."""
    data: List[List[Any]]
    columns: List[str]
    query: str
    generated_code: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "data": [],
                "columns": [],
                "query": "Show me all users who registered in the last 30 days",
                "generated_code": "SELECT * FROM users WHERE registration_date >= DATE('now', '-30 days')"
            }
        }


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "message": "Data-to-Dashboard Automator API is running",
        "version": "1.0.0"
    }


@app.post("/process-query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Process natural language query with automatic retry logic for self-healing SQL generation.
    
    Args:
        request: QueryRequest with natural language query
        
    Returns:
        QueryResponse with generated SQL code and data
        
    Raises:
        HTTPException: If unable to process query after retries
    """
    try:
        # Initialize watsonx.ai service
        watsonx_service = WatsonxService()
        
        # Process query with automatic retry logic
        result = await watsonx_service.process_query_with_retry(request.query)
        
        # Return complete response
        return QueryResponse(
            data=result["data"],
            columns=result["columns"],
            query=request.query,
            generated_code=result["generated_code"]
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions from service
        raise
    except ValueError as e:
        # Handle missing API key
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    except Exception as e:
        # Catch-all for unexpected errors
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# Made with Bob
