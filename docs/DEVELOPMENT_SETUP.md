# Development Environment Setup Guide

This comprehensive guide will help you set up the YouTube Niche Discovery Engine development environment on your local machine.

## 📋 Prerequisites

### System Requirements
- **OS**: macOS 10.15+, Ubuntu 18.04+, or Windows 10/11 with WSL2
- **RAM**: Minimum 8GB, Recommended 16GB+
- **Storage**: Minimum 10GB free space, Recommended 20GB+
- **Network**: Stable internet connection for API access

### Required Software

#### 1. Python 3.10+
```bash
# macOS (using Homebrew)
brew install python@3.10

# Ubuntu/Debian
sudo apt update
sudo apt install python3.10 python3.10-venv python3.10-dev

# Windows (WSL2)
sudo apt update && sudo apt install python3.10 python3.10-venv python3.10-dev

# Verify installation
python3 --version  # Should show 3.10.x
```

#### 2. Node.js 18+
```bash
# Using Node Version Manager (recommended)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc
nvm install 18
nvm use 18

# Verify installation
node --version  # Should show v18.x.x
npm --version   # Should show 9.x.x
```

#### 3. Docker & Docker Compose
```bash
# macOS
brew install --cask docker

# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version          # Should show 24.x.x+
docker-compose --version  # Should show 2.x.x+
```

#### 4. Git
```bash
# macOS
brew install git

# Ubuntu/Debian
sudo apt install git

# Configure Git (first time only)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Verify installation
git --version  # Should show 2.x.x+
```

#### 5. Make (Build Tool)
```bash
# macOS (usually pre-installed)
# Ubuntu/Debian
sudo apt install build-essential

# Windows (WSL2)
sudo apt install build-essential
```

## 🚀 Quick Setup

### Option 1: Automated Setup (Recommended)
```bash
# Clone the repository
git clone https://github.com/your-org/niche-discovery-engine.git
cd niche-discovery-engine

# Run automated setup
make dev-setup

# Start development environment
make dev-start
```

### Option 2: Manual Setup

#### Step 1: Clone Repository
```bash
git clone https://github.com/your-org/niche-discovery-engine.git
cd niche-discovery-engine
```

#### Step 2: Backend Setup
```bash
# Create Python virtual environment
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Set up pre-commit hooks
pre-commit install
```

#### Step 3: Frontend Setup
```bash
# Navigate to frontend directory
cd ../frontend

# Install Node.js dependencies
npm install

# Install development dependencies
npm install --save-dev
```

#### Step 4: Database Setup
```bash
# Start PostgreSQL and Redis using Docker
docker-compose -f docker-compose.dev.yml up -d postgres redis

# Wait for databases to be ready
sleep 10

# Run database migrations
cd backend
source venv/bin/activate
alembic upgrade head

# Seed development data
python scripts/seed_dev_data.py
```

#### Step 5: Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit environment variables (see configuration section below)
nano .env  # or use your preferred editor
```

## ⚙️ Configuration

### Environment Variables
Create a `.env` file in the project root with the following variables:

```bash
# Application Settings
APP_NAME=Niche Discovery Engine
APP_VERSION=1.0.0
DEBUG=true
LOG_LEVEL=INFO

# Database Configuration
DATABASE_URL=postgresql://niche_user:niche_pass@localhost:5432/niche_discovery_db
REDIS_URL=redis://localhost:6379/0

# External APIs (Get your API keys)
YOUTUBE_API_KEY=your_youtube_data_api_key_here
GOOGLE_TRENDS_PROXY_LIST=proxy1.com:8080,proxy2.com:8080
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret

# Security
JWT_SECRET_KEY=your-super-secret-jwt-key-here-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30
ENCRYPTION_KEY=your-32-character-encryption-key!!

# Scraping Configuration
SCRAPING_MAX_CONCURRENT=10
SCRAPING_DELAY_MIN=1
SCRAPING_DELAY_MAX=3
SCRAPING_TIMEOUT=30
SCRAPING_USER_AGENT=Mozilla/5.0 (compatible; NicheDiscovery/1.0)

# Rate Limiting
RATE_LIMIT_REQUESTS=1000
RATE_LIMIT_WINDOW=3600

# Monitoring
GRAFANA_ADMIN_PASSWORD=admin
PROMETHEUS_RETENTION_TIME=15d

# Development Settings
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000
CORS_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000"]
```

### API Keys Setup

#### YouTube Data API
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable YouTube Data API v3
4. Create credentials (API Key)
5. Restrict the API key to YouTube Data API
6. Add the key to your `.env` file

#### Reddit API
1. Go to [Reddit Apps](https://www.reddit.com/prefs/apps)
2. Click "Create App"
3. Choose "script" type
4. Note down client ID and secret
5. Add to your `.env` file

### Development Database Setup
```bash
# Create development database
docker exec -it niche_postgres psql -U postgres -c "CREATE DATABASE niche_discovery_db;"
docker exec -it niche_postgres psql -U postgres -c "CREATE USER niche_user WITH PASSWORD 'niche_pass';"
docker exec -it niche_postgres psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE niche_discovery_db TO niche_user;"

# Test database connection
cd backend
python -c "from app.core.database import engine; print('Database connection successful!')"
```

## 🏃 Running the Application

### Development Mode (Recommended)
```bash
# Start all services
make dev-start

# Or start services individually:
# Backend API
make start-backend

# Frontend development server
make start-frontend

# Background workers
make start-workers

# Monitoring stack
make start-monitoring
```

### Manual Development Mode
```bash
# Terminal 1: Start databases
docker-compose -f docker-compose.dev.yml up postgres redis

# Terminal 2: Start backend API
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 3: Start frontend
cd frontend
npm run dev

# Terminal 4: Start background workers
cd backend
source venv/bin/activate
celery -A app.core.celery_app worker --loglevel=info

# Terminal 5: Start monitoring (optional)
docker-compose -f docker-compose.monitoring.yml up
```

### Access Points
Once everything is running, you can access:

- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **API Alternative Docs**: http://localhost:8000/redoc (ReDoc)
- **Frontend Application**: http://localhost:3000
- **Grafana Monitoring**: http://localhost:3001 (admin/admin)
- **Prometheus Metrics**: http://localhost:9090
- **Redis Commander**: http://localhost:8081

## 🧪 Testing Setup

### Backend Testing
```bash
cd backend
source venv/bin/activate

# Install test dependencies
pip install -r requirements-test.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test categories
pytest tests/unit/          # Unit tests only
pytest tests/integration/   # Integration tests only
pytest -m "not slow"       # Skip slow tests
```

### Frontend Testing
```bash
cd frontend

# Run unit tests
npm test

# Run tests with coverage
npm run test:coverage

# Run E2E tests (requires backend running)
npm run test:e2e

# Visual regression tests
npm run test:visual
```

### Load Testing
```bash
# Install load testing tools
pip install locust

# Run load tests (requires running backend)
cd tests/load
locust -f locustfile.py --host=http://localhost:8000
```

## 🛠️ Development Tools

### Recommended VS Code Extensions
```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.black-formatter",
    "ms-python.flake8",
    "ms-python.mypy-type-checker",
    "bradlc.vscode-tailwindcss",
    "esbenp.prettier-vscode",
    "ms-vscode.vscode-typescript-next",
    "ms-vscode-remote.remote-containers",
    "GitHub.copilot",
    "ms-python.pylint"
  ]
}
```

### Code Quality Tools
```bash
# Python code formatting
black backend/app/
isort backend/app/

# Python linting
flake8 backend/app/
mypy backend/app/

# JavaScript/TypeScript formatting
cd frontend
npm run lint
npm run format

# Security scanning
bandit -r backend/app/
npm audit
```

### Git Hooks (Pre-commit)
The project uses pre-commit hooks to ensure code quality:

```bash
# Install pre-commit (already included in requirements-dev.txt)
pip install pre-commit

# Install hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

## 🔧 Make Commands

The project includes a comprehensive Makefile for common operations:

```bash
# Development
make dev-setup      # Initial development setup
make dev-start      # Start development environment  
make dev-stop       # Stop development environment
make dev-clean      # Clean up development containers

# Testing
make test           # Run all tests
make test-backend   # Run backend tests only
make test-frontend  # Run frontend tests only
make test-e2e       # Run end-to-end tests
make test-load      # Run load tests

# Code Quality
make lint           # Lint all code
make format         # Format all code
make security       # Run security scans
make coverage       # Generate coverage reports

# Database
make db-migrate     # Run database migrations
make db-seed        # Seed development data
make db-reset       # Reset database
make db-backup      # Backup development database

# Docker
make docker-build   # Build all Docker images
make docker-push    # Push images to registry
make docker-clean   # Clean up Docker resources

# Deployment
make deploy-dev     # Deploy to development environment
make deploy-staging # Deploy to staging environment
make deploy-prod    # Deploy to production environment
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Check what's using the port
lsof -i :8000  # Backend port
lsof -i :3000  # Frontend port

# Kill the process
kill -9 <PID>
```

#### 2. Database Connection Issues
```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Check database logs
docker logs niche_postgres

# Reset database connection
make db-reset
```

#### 3. Python Virtual Environment Issues
```bash
# Recreate virtual environment
cd backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 4. Node.js Dependency Issues
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

#### 5. Docker Issues
```bash
# Restart Docker daemon
sudo systemctl restart docker

# Clean up Docker resources
docker system prune -a

# Rebuild containers
make docker-clean
make dev-setup
```

### Getting Help

If you encounter issues not covered here:

1. Check the [FAQ](docs/FAQ.md)
2. Search [GitHub Issues](https://github.com/your-org/niche-discovery-engine/issues)
3. Create a new issue with:
   - Operating system and version
   - Error messages (full stack trace)
   - Steps to reproduce
   - What you expected to happen

## 📚 Next Steps

After completing the setup:

1. **Explore the API**: Visit http://localhost:8000/docs
2. **Review Architecture**: Read [docs/architecture/system_design.md](docs/architecture/system_design.md)
3. **Understand the Codebase**: Check [docs/code_structure.md](docs/code_structure.md)
4. **Join Development**: Review [CONTRIBUTING.md](CONTRIBUTING.md)
5. **Set Up IDE**: Configure your preferred IDE with the recommended extensions

Happy coding! 🚀