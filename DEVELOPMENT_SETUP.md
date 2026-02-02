# Development Environment Setup Guide

This guide will help you set up the complete development environment for the YouTube Niche Discovery Engine.

## 📋 Prerequisites

### Required Software
- **Python 3.11+** - Main backend language
- **Node.js 18+** - Frontend development
- **PostgreSQL 14+** - Primary database
- **Redis 7+** - Caching and session storage
- **Git** - Version control

### Recommended Tools
- **Docker & Docker Compose** - Containerization
- **VSCode** with Python and TypeScript extensions
- **Postman** or **Insomnia** - API testing
- **pgAdmin** - PostgreSQL GUI

## 🚀 Quick Start with Docker

### 1. Clone Repository
```bash
git clone <repository-url>
cd niche-discovery-project
```

### 2. Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your configurations
nano .env
```

### 3. Start Services with Docker
```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps
```

### 4. Initialize Database
```bash
# Run migrations
docker-compose exec backend alembic upgrade head

# Create initial data (optional)
docker-compose exec backend python scripts/init_data.py
```

### 5. Access Applications
- **API Documentation**: http://localhost:8000/docs
- **Frontend Dashboard**: http://localhost:3000
- **Database Admin**: http://localhost:5050 (pgAdmin)
- **Redis Commander**: http://localhost:8081

## 🛠️ Manual Setup (Development)

### Backend Setup

#### 1. Python Environment
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### 2. Database Setup
```bash
# Install PostgreSQL (Ubuntu/Debian)
sudo apt update
sudo apt install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE niche_discovery;
CREATE USER niche_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE niche_discovery TO niche_user;
\q
```

#### 3. Redis Setup
```bash
# Install Redis (Ubuntu/Debian)
sudo apt install redis-server

# Start Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Test Redis
redis-cli ping
```

#### 4. Environment Configuration
```bash
# Copy and edit environment file
cp .env.example .env
nano .env

# Update database credentials and API keys
```

#### 5. Database Migrations
```bash
# Initialize Alembic (first time only)
alembic init alembic

# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Run migrations
alembic upgrade head
```

#### 6. Start Backend Server
```bash
# Development server with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using the script
python app/main.py
```

### Frontend Setup

#### 1. Node.js Environment
```bash
cd frontend

# Install dependencies
npm install

# Or with yarn
yarn install
```

#### 2. Environment Configuration
```bash
# Copy environment template
cp .env.local.example .env.local

# Edit configuration
nano .env.local
```

#### 3. Start Development Server
```bash
# Start React development server
npm start

# Or with yarn
yarn start
```

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```env
# Database
POSTGRES_SERVER=localhost
POSTGRES_USER=niche_user
POSTGRES_PASSWORD=your_password
POSTGRES_DB=niche_discovery

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# API Keys
YOUTUBE_API_KEY=your_youtube_api_key
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
```

#### Frontend (.env.local)
```env
REACT_APP_API_URL=http://localhost:8000/api/v1
REACT_APP_ENVIRONMENT=development
```

### API Keys Setup

#### YouTube Data API
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable YouTube Data API v3
4. Create API key credentials
5. Add key to `.env` file

#### Reddit API
1. Go to [Reddit App Preferences](https://www.reddit.com/prefs/apps)
2. Create a new application (script type)
3. Note the client ID and secret
4. Add credentials to `.env` file

## 🧪 Testing

### Backend Tests
```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_niches.py -v
```

### Frontend Tests
```bash
cd frontend

# Run tests
npm test

# Run tests with coverage
npm test -- --coverage
```

## 📊 Database Management

### Common Operations
```bash
# Create new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# View migration history
alembic history

# Reset database (DANGER!)
alembic downgrade base
alembic upgrade head
```

### Backup and Restore
```bash
# Backup database
pg_dump niche_discovery > backup.sql

# Restore database
psql niche_discovery < backup.sql
```

## 🔍 Debugging and Monitoring

### Backend Debugging
```bash
# Enable debug mode in .env
ENVIRONMENT=development

# View logs
tail -f app.log

# Check database connections
python -c "from app.core.database import engine; print('DB Connected!')"
```

### Redis Monitoring
```bash
# Monitor Redis
redis-cli monitor

# Check Redis status
redis-cli info
```

## 🚀 Production Deployment

### Docker Production Build
```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy to production
docker-compose -f docker-compose.prod.yml up -d
```

### Manual Production Setup
1. Set `ENVIRONMENT=production` in `.env`
2. Use production database credentials
3. Configure reverse proxy (Nginx)
4. Set up SSL certificates
5. Configure monitoring and logging

## 🆘 Troubleshooting

### Common Issues

#### Database Connection Issues
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check if database exists
sudo -u postgres psql -l | grep niche_discovery

# Test connection
psql -h localhost -U niche_user -d niche_discovery
```

#### Redis Connection Issues
```bash
# Check Redis status
sudo systemctl status redis-server

# Test connection
redis-cli ping
```

#### Python Import Issues
```bash
# Verify virtual environment
which python
pip list

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

#### Frontend Build Issues
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://reactjs.org/docs/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Redis Documentation](https://redis.io/documentation)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)

## 🤝 Development Workflow

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Follow coding standards
   - Add tests for new features
   - Update documentation

3. **Test Changes**
   ```bash
   # Backend tests
   cd backend && pytest
   
   # Frontend tests
   cd frontend && npm test
   ```

4. **Commit and Push**
   ```bash
   git add .
   git commit -m "feat: description of your changes"
   git push origin feature/your-feature-name
   ```

5. **Create Pull Request**
   - Ensure all tests pass
   - Update documentation
   - Request code review

---

## 📞 Support

For development support:
- Create an issue in the repository
- Check existing documentation
- Contact the development team

**Happy Coding! 🚀**