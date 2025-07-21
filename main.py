import os
import httpx
from typing import Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

# Configuration
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://X")
LLM_MODEL = os.getenv("LLM_MODEL", "whatis.sh")

app = FastAPI(
    title="whAtIs.sh API",
    description="A simple API that mimics the Unix 'whatis' command using an LLM",
    version="1.0.0"
)

class CommandRequest(BaseModel):
    """
    Pydantic model for command requests with JSON body.
    
    This model validates incoming JSON requests containing a command or function
    name and an optional verbose flag. Used for both GET and POST endpoints
    that accept JSON payloads.
    
    Attributes:
        cmd_or_func (str): The command, function, or term to query.
                          Examples: "ls", "grep", "print()", "awk"
        verbose (bool): Whether to request verbose/detailed output.
                       Defaults to False. When True, appends "-v" to the prompt.
    
    Example:
        {
            "cmd_or_func": "grep",
            "verbose": true
        }
    """
    cmd_or_func: str
    verbose: bool = False

async def call_llm(prompt: str) -> str:
    """
    Call the LLM service and return the generated text response.
    
    This function sends a request to the configured LLM service (typically Ollama)
    using the whatis.sh model to generate responses that mimic the Unix 'whatis'
    command. The function handles HTTP communication, error handling, and response
    parsing.
    
    Args:
        prompt (str): The command or function name to send to the LLM.
                     May include "-v" suffix for verbose mode.
                     Examples: "ls", "grep -v", "print()"
    
    Returns:
        str: The LLM's response text, stripped of leading/trailing whitespace.
             Should be a brief description similar to Unix 'whatis' output.
    
    Raises:
        HTTPException: 503 if LLM service is unavailable or connection fails
        HTTPException: 502 if LLM service returns an HTTP error status
    
    Environment Variables:
        LLM_BASE_URL: Base URL of the LLM service (default: "http://X")
        LLM_MODEL: Model name to use (default: "whatis.sh")
    
    Note:
        Uses a 60-second timeout for LLM requests to accommodate slower responses.
        The LLM service is expected to be an Ollama-compatible API endpoint.
    """
    llm_payload = {
        "model": LLM_MODEL,
        "prompt": prompt,
        "stream": False
    }
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                f"{LLM_BASE_URL}/api/generate",
                json=llm_payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            
            # Extract the response text from the LLM response
            llm_response = response.json()
            return llm_response.get("response", "").strip()
            
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"LLM service unavailable: {str(e)}")
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=502, detail=f"LLM service error: {str(e)}")

@app.get("/", response_class=PlainTextResponse)
async def whatis_with_body(request: Request):
    """
    Handle GET requests to root endpoint with optional JSON body or return usage instructions.
    
    This endpoint serves dual purposes:
    1. When called with a JSON body, it processes the command request and returns LLM response
    2. When called without a body (simple GET), it returns usage instructions
    
    This design accommodates the requirement for GET requests with JSON bodies while
    providing a user-friendly help interface for API discovery.
    
    Args:
        request (Request): FastAPI Request object containing headers and body
    
    Returns:
        PlainTextResponse: Either the LLM's response to the command or usage instructions
    
    Request Body (optional):
        JSON object matching CommandRequest schema:
        {
            "cmd_or_func": "command_name",
            "verbose": false
        }
    
    Raises:
        HTTPException: 400 for invalid JSON format
        HTTPException: 500 for unexpected server errors
        HTTPException: 503/502 for LLM service issues (propagated from call_llm)
    
    Examples:
        # Get usage instructions
        curl http://whatis.sh:2095/
        
        # Query with JSON body
        curl -X GET http://whatis.sh:2095/ \
          -H "Content-Type: application/json" \
          -d '{"cmd_or_func": "ls", "verbose": false}'
    """
    try:
        # Try to parse JSON body if present
        body = await request.body()
        if body:
            import json
            data = json.loads(body)
            command_request = CommandRequest(**data)
            prompt = command_request.cmd_or_func
            if command_request.verbose:
                prompt += " -v"
            
            response_text = await call_llm(prompt)
            return response_text
        else:
            # No body provided, return usage instructions
            usage_text = """whAtIs.sh - Unix 'whatis' command API

Usage:
  # Headless request (recommended)
  curl http://whatis.sh:2095/ls
  curl http://whatis.sh:2095/grep?v=true

  # With JSON body
  curl -X GET http://whatis.sh:2095/ \\
    -H "Content-Type: application/json" \\
    -d '{"cmd_or_func": "awk", "verbose": false}'

  # POST request
  curl -X POST http://whatis.sh:2095/ \\
    -H "Content-Type: application/json" \\
    -d '{"cmd_or_func": "sed", "verbose": true}'

Examples:
  /ls          - List directory contents command
  /grep        - Global regular expression print
  /awk         - Pattern scanning and processing language
  /sed?v=true  - Stream editor (verbose)

"""
            return usage_text
            
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in request body")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring and container orchestration.
    
    This endpoint provides a simple health status check that can be used by:
    - Load balancers to determine service availability
    - Container orchestrators (Docker, Kubernetes, ECS) for health checks
    - Monitoring systems to track service status
    - CI/CD pipelines to verify deployment success
    
    Returns:
        dict: JSON response containing service status and identification
              Format: {"status": "healthy", "service": "whatis.sh"}
    
    HTTP Status:
        200: Service is operational and ready to handle requests
    
    Examples:
        # Basic health check
        curl http://whatis.sh:2095/health
        
        # Health check with status code verification
        curl -f http://whatis.sh:2095/health || echo "Service unhealthy"
    
    Note:
        This endpoint does not verify LLM service connectivity to avoid
        cascading failures. It only confirms that the API service itself
        is running and responsive.
    """
    return {"status": "healthy", "service": "whatis.sh"}

@app.get("/{command}", response_class=PlainTextResponse)
async def whatis_headless(command: str, v: Optional[bool] = False):
    """
    Handle headless requests for specific commands via URL path.
    
    This endpoint provides the most convenient way to query the whatis service,
    mimicking the original Unix 'whatis' command structure. Commands are specified
    directly in the URL path, with an optional verbose query parameter.
    
    Args:
        command (str): The command or function name to query.
                      Extracted from the URL path (e.g., /ls, /grep, /awk)
        v (Optional[bool]): Verbose flag as query parameter.
                           When True, appends "-v" to the prompt for detailed output.
                           Defaults to False.
    
    Returns:
        PlainTextResponse: The LLM's response describing the command
    
    Raises:
        HTTPException: 503/502 for LLM service issues (propagated from call_llm)
    
    Examples:
        # Basic command query
        curl http://whatis.sh:2095/ls
        
        # Verbose query
        curl http://whatis.sh:2095/grep?v=true
        
        # Function query
        curl http://whatis.sh:2095/print
    
    Note:
        This is the recommended endpoint for simple queries as it most closely
        resembles the original 'whatis' command syntax.
    """
    prompt = command
    if v:
        prompt += " -v"
    
    response_text = await call_llm(prompt)
    return response_text

@app.post("/", response_class=PlainTextResponse)
async def whatis_post(command_request: CommandRequest):
    """
    Handle explicit POST requests with JSON body payload.
    
    This endpoint provides a standard REST API interface for command queries,
    accepting JSON payloads via POST method. It's the most conventional HTTP
    approach for API clients that prefer explicit POST semantics.
    
    Args:
        command_request (CommandRequest): Pydantic model containing the command
                                        and optional verbose flag, automatically
                                        validated from the JSON request body.
    
    Returns:
        PlainTextResponse: The LLM's response describing the command
    
    Raises:
        HTTPException: 422 for invalid request body (handled by FastAPI/Pydantic)
        HTTPException: 503/502 for LLM service issues (propagated from call_llm)
    
    Request Body:
        JSON object matching CommandRequest schema:
        {
            "cmd_or_func": "command_name",
            "verbose": boolean
        }
    
    Examples:
        # Basic POST request
        curl -X POST http://whatis.sh:2095/ \
          -H "Content-Type: application/json" \
          -d '{"cmd_or_func": "sed", "verbose": false}'
        
        # Verbose POST request
        curl -X POST http://whatis.sh:2095/ \
          -H "Content-Type: application/json" \
          -d '{"cmd_or_func": "awk", "verbose": true}'
    
    Note:
        This endpoint provides the same functionality as the GET endpoint with
        JSON body but uses standard POST semantics for better REST compliance.
    """
    prompt = command_request.cmd_or_func
    if command_request.verbose:
        prompt += " -v"
    
    response_text = await call_llm(prompt)
    return response_text

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
