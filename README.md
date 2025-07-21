# whAtIs.sh API

A FastAPI service that mimics the Unix 'whatis' command using an LLM backend. This API provides HTTP endpoints that accept commands and return `whatis`-style responses in plain text format.

## Directory Structure

```
api/
├── main.py                 # FastAPI application
├── requirements.txt        # Python dependencies
├── start.sh               # Quick start script
├── .gitignore            # Git ignore patterns
├── ecs/                  # Container deployment files
│   ├── Dockerfile        # Container image definition
│   ├── docker-compose.yml # Full stack with LLM service
│   └── ecs-task-definition.json # AWS ECS configuration
├── serverless/           # Serverless deployment files
│   ├── lambda_handler.py # AWS Lambda adapter
│   └── serverless.yml    # Serverless Framework config
└── tests/               # Test files
    └── test_api.py      # API test suite
```

## Features

- **Headless requests**: `GET /{command}` (e.g., `/ls`, `/grep`)
- **JSON body requests**: `GET/POST /` with JSON payload
- **Verbose mode**: Add `?v=true` for headless or `"verbose": true` in JSON
- **Health check**: `GET /health` for monitoring
- **Plain text responses**: Mimics the original `whatis` command output
- **Multiple deployment options**: Local, Docker, ECS, Lambda

## Quick Start

```bash
# Install dependencies and start the server
./start.sh

# Or manually:
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## API Endpoints

| Method | Endpoint | Description | Example |
|--------|----------|-------------|---------|
| GET | `/` | Usage instructions or JSON body processing | `curl http://whatis.sh:2095/` |
| GET | `/{command}` | Headless command query | `curl http://whatis.sh:2095/ls` |
| GET | `/{command}?v=true` | Verbose headless query | `curl http://whatis.sh:2095/grep?v=true` |
| POST | `/` | JSON body command query | See examples below |
| GET | `/health` | Service health check | `curl http://whatis.sh:2095/health` |

## Usage Examples

### Headless Requests (Recommended)
```bash
# Basic command query
curl http://whatis.sh:2095/ls

# Verbose command query
curl http://whatis.sh:2095/grep?v=true

# Function or programming command
curl http://whatis.sh:2095/print
```

### JSON Body Requests
```bash
# GET with JSON body
curl -X GET http://whatis.sh:2095/ \
   -H "Content-Type: application/json" \
   -d '{
     "cmd_or_func": "print()",
     "verbose": false
   }'

# POST request
curl -X POST http://whatis.sh:2095/ \
   -H "Content-Type: application/json" \
   -d '{
     "cmd_or_func": "awk",
     "verbose": true
   }'
```

### Health Check
```bash
# Basic health check
curl http://whatis.sh:2095/health

# Health check with status verification
curl -f http://whatis.sh:2095/health || echo "Service unhealthy"
```

## Development

### Local Development
```bash
# Clone and setup
git clone <repository>
cd api/

# Install dependencies
pip install -r requirements.txt

# Start development server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Testing
```bash
# Run tests with pytest
pip install pytest pytest-asyncio
pytest tests/test_api.py -v

# Run manual tests
python tests/test_api.py
```

## Deployment Options

### Container Deployment (ECS)

All container-related files are in the `ecs/` directory:

```bash
# Build and run locally
cd ecs/
docker build -t whatis-api .
docker run -p 8000:8000 -e LLM_BASE_URL=http://your-llm-host:11434 whatis-api

# Full stack with LLM service
docker-compose up

# Deploy to AWS ECS
# Use ecs-task-definition.json for ECS deployment
```

### Serverless Deployment (Lambda)

All serverless files are in the `serverless/` directory:

```bash
# Install serverless framework
npm install -g serverless
npm install serverless-python-requirements

# Deploy to AWS Lambda
cd serverless/
serverless deploy

# Set environment variables in serverless.yml before deployment
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LLM_BASE_URL` | URL of the LLM service | `http://localhost:11434` |
| `LLM_MODEL` | Model name to use | `whatis.sh` |

## LLM Backend Integration

The API communicates with an LLM service (typically Ollama) that hosts the `whatis.sh` model:

```bash
# Example LLM request that the API makes internally
curl -X POST http://localhost:11434/api/generate \
   -H "Content-Type: application/json" \
   -d '{
     "model": "whatis.sh",
     "prompt": "ls",
     "stream": false
   }'
```

## Error Handling

- **503**: LLM service unavailable
- **502**: LLM service error
- **400**: Invalid JSON in request body
- **422**: Invalid request body schema
- **500**: Internal server error

## Monitoring

The `/health` endpoint provides service status for:
- Load balancers
- Container orchestrators (Docker, Kubernetes, ECS)
- Monitoring systems
- CI/CD pipelines

Returns: `{"status": "healthy", "service": "whatis.sh"}`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass: `pytest tests/ -v`
5. Submit a pull request

## Support

- **Health Check**: `GET /health` to verify service status
- **Usage Help**: `GET /` for API usage instructions
- **Issues**: Report via GitHub Issues