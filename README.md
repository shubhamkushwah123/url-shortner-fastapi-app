# URL Shortener Microservice

A simple and fast URL shortener microservice built with FastAPI and SQLite.

## Features

- ✅ **URL Shortening** - Convert long URLs into short, shareable links
- ✅ **URL Retrieval** - Get original URLs from short codes
- ✅ **URL Management** - View and delete shortened URLs
- ✅ **Modern Web UI** - Dark-themed interface with Tailwind CSS
- ✅ **RESTful API** - Clean JSON API endpoints
- ✅ **SQLite Database** - Lightweight, file-based storage

## Quick Start

### Prerequisites

- Python 3.7+
- Docker & Docker Compose v2
- pip (Python package manager)

### Option 1: Docker (Recommended)

1. **Build and run with Docker Compose:**
   ```bash
   docker compose up --build
   ```

2. **Access the application:**
   - **Web UI:** http://localhost:8000/static/
   - **API Documentation:** http://localhost:8000/docs
   - **Interactive API:** http://localhost:8000/redoc

3. **Stop the container:**
   ```bash
   docker compose down
   ```

### Option 2: Local Development

1. **Clone or navigate to the project directory:**
   ```bash
   cd url-shortner-microservice
   ```

2. **Create and activate virtual environment (recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the server:**
   ```bash
   uvicorn main:app --reload
   ```

5. **Access the application:**
   - **Web UI:** http://localhost:8000/static/
   - **API Documentation:** http://localhost:8000/docs
   - **Interactive API:** http://localhost:8000/redoc

## 🐳 Docker Deployment

### Development
```bash
docker compose up --build
```

### Production (with nginx)
```bash
docker compose --profile production up --build
```

### Stop containers
```bash
docker compose down
```

### View logs
```bash
docker compose logs -f
```

### Rebuild without cache
```bash
docker compose build --no-cache
```

## 🧪 Testing

### Prerequisites
```bash
pip install -r requirements.txt
```

### Quick Start
```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=models --cov=api --cov=main --cov-report=term-missing
```

### Test Commands (Using Makefile)
```bash
# Run all tests
make test

# Unit tests only (database operations)
make test-unit

# Integration tests only (API endpoints)
make test-integration

# Regression tests only (bug prevention)
make test-regression

# Tests with coverage report
make test-cov

# Quick smoke tests
make test-smoke

# Clean test artifacts
make clean
```

### Manual Test Execution
```bash
# Run all tests with verbose output
pytest -v

# Run specific test files
pytest tests/test_models.py -v              # Unit tests
pytest tests/test_api.py -v                 # API tests
pytest tests/test_integration.py -v         # Workflow tests
pytest tests/test_regression.py -v          # Regression tests

# Run with coverage
pytest --cov=models --cov=api --cov=main --cov-report=html --cov-report=term-missing

# Run specific test cases
pytest tests/test_models.py::TestModels::test_init_db -v
pytest tests/test_api.py::TestAPI::test_shorten_url_valid -v

# Run tests by marker
pytest -m "unit" -v
pytest -m "integration" -v
pytest -m "regression" -v
```

### Test Coverage Report
```bash
# Generate HTML coverage report
pytest --cov=models --cov=api --cov=main --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS
# or
xdg-open htmlcov/index.html  # Linux
```

### Test Categories & Coverage

**🔬 Unit Tests (`test_models.py`) - 11 tests**
- Database operations (CRUD)
- Model functions validation
- Data integrity checks
- Edge cases (Unicode, special characters)
- **Coverage:** 100%

**🔗 Integration Tests (`test_api.py`) - 14 tests**
- API endpoint testing
- Request/response validation
- URL encoding/decoding
- Error handling
- Concurrent operations
- **Coverage:** 100%

**🔄 Integration Workflow Tests (`test_integration.py`) - 7 tests**
- Complete user workflows
- Multi-step operations
- Performance benchmarks
- Concurrent access testing
- Error recovery scenarios
- **Coverage:** End-to-end workflows

**🛡️ Regression Tests (`test_regression.py`) - 8 tests**
- Prevent previously fixed bugs
- Memory leak detection
- Performance degradation monitoring
- Data integrity verification
- API response format consistency
- **Coverage:** Critical regression points

### Test Results Summary
```
==================== Test Summary ====================
Total Tests: 40
- Unit Tests: 11 (100% pass rate)
- Integration Tests: 14 (100% pass rate)  
- Workflow Tests: 7 (100% pass rate)
- Regression Tests: 8 (100% pass rate)

Overall Coverage: 97%
- models.py: 100%
- api.py: 100%
- main.py: 89%
===================================================
```

### Docker Testing
```bash
# Run tests in Docker container
make test-docker
docker compose -f docker-compose.test.yml up --build

# Run tests with Docker Compose
docker compose run --rm url-shortener pytest
```

### Continuous Integration
The test suite is designed for CI/CD pipelines:
- ✅ Fast execution (~2 seconds)
- ✅ Isolated test databases
- ✅ No external dependencies
- ✅ Coverage reporting
- ✅ JUnit XML output available

### Test Database
Tests use isolated temporary databases that are:
- Created fresh for each test function
- Automatically cleaned up after tests
- Completely isolated from production data
- Stored in temporary files

### Troubleshooting
```bash
# If tests fail due to import errors
pip install -r requirements.txt

# If database issues occur
make clean  # Clean test artifacts
pytest     # Run tests again

# If coverage report fails
pip install pytest-cov  # Install coverage tool

# View detailed test output
pytest -v --tb=long  # Verbose with full tracebacks
```

## API Endpoints

### Base URL
```
http://localhost:8000
```

### Endpoints

| Method | Endpoint | Description | Example |
|--------|----------|-------------|---------|
| POST | `/shortenURL` | Create shortened URL | `POST /shortenURL?url=https://example.com` |
| GET | `/getAllUrls` | Get all shortened URLs | `GET /getAllUrls` |
| GET | `/s/{shortCode}` | Retrieve original URL | `GET /s/ABC123` |
| DELETE | `/deleteUrl/{shortCode}` | Delete shortened URL | `DELETE /deleteUrl/ABC123` |

### Request/Response Examples

#### 1. Create Shortened URL
```bash
curl -X POST "http://localhost:8000/shortenURL?url=https://www.google.com"
```

**Response:**
```json
{
  "short_code": "xY9zAb"
}
```

#### 2. Get All URLs
```bash
curl "http://localhost:8000/getAllUrls"
```

**Response:**
```json
[
  {
    "url": "https://www.google.com",
    "short_url": "xY9zAb"
  }
]
```

#### 3. Retrieve Original URL
```bash
curl "http://localhost:8000/s/xY9zAb"
```

**Response:**
```json
"https://www.google.com"
```

#### 4. Delete URL
```bash
curl -X DELETE "http://localhost:8000/deleteUrl/xY9zAb"
```

**Response:** `200 OK`

## Interactive API Documentation

### Swagger UI (Recommended)
📖 **Interactive API Docs:** http://localhost:8000/docs

- **Try out API endpoints directly in your browser**
- **Auto-generated request/response examples**
- **Parameter validation and descriptions**
- **Test API calls with live data**

### ReDoc
📚 **Alternative Documentation:** http://localhost:8000/redoc

- **Clean, readable API documentation**
- **Detailed endpoint descriptions**
- **Schema definitions**

## Web Interface

The modern web UI provides:

- **URL Shortening Form** - Enter and shorten URLs instantly
- **URL List** - View all shortened URLs with delete options
- **URL Lookup** - Find original URLs using short codes
- **Copy to Clipboard** - One-click URL copying
- **Toast Notifications** - Real-time feedback for all actions

**Access:** http://localhost:8000/static/

## Project Structure

```
url-shortner-microservice/
├── main.py              # FastAPI application entry point
├── api.py               # API route definitions
├── models.py            # Database operations
├── static/
│   └── index.html       # Web UI
├── requirements.txt     # Python dependencies
├── database.db         # SQLite database (auto-created)
└── README.md           # This file
```

## Database Schema

```sql
CREATE TABLE URLS (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    URL TEXT NOT NULL,
    SHORT_URL TEXT NOT NULL,
    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Development

### Running in Development Mode
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Testing
```bash
# Test the core functionality
python3 test_api.py
```

## Configuration

- **Host:** `0.0.0.0` (default)
- **Port:** `8000` (default)
- **Database:** `database.db` (SQLite)
- **Short Code Length:** 6 characters (alphanumeric)

## API Response Codes

- `200 OK` - Successful request
- `404 Not Found` - Short code not found
- `422 Unprocessable Entity` - Invalid input data
- `500 Internal Server Error` - Server error

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

---

**🚀 Start the server and visit http://localhost:8000/docs to explore the interactive API!**
