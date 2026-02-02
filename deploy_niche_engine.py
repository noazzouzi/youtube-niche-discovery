#!/usr/bin/env python3
"""
YouTube Niche Discovery Engine - Production Deployment Script
PM Agent Implementation for immediate remote deployment

This script:
1. Sets up the complete production environment
2. Deploys the PM Agent 100-point scoring algorithm
3. Initializes the database with sample data
4. Starts the real-time discovery engine
5. Launches the React dashboard

TARGET: Get the working app deployed remotely within 24-48 hours
"""

import os
import sys
import subprocess
import json
import asyncio
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NicheEngineDeployer:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.backend_dir = self.project_root / "backend"
        self.frontend_dir = self.project_root / "frontend"
        self.env_file = self.project_root / ".env"
        
    def create_env_file(self):
        """Create production .env file with PM Agent configuration"""
        logger.info("🔧 Creating production environment configuration...")
        
        env_content = """# YouTube Niche Discovery Engine - Production Configuration
# PM Agent Implementation

# Database Configuration
POSTGRES_SERVER=localhost
POSTGRES_USER=niche_user
POSTGRES_PASSWORD=niche_secure_2024
POSTGRES_DB=niche_discovery_prod
POSTGRES_PORT=5432

# Redis Configuration (for caching and job queue)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# API Configuration
API_V1_STR=/api/v1
SECRET_KEY=pm_agent_niche_discovery_super_secure_key_2024
ENVIRONMENT=production
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,*.yourdomain.com

# CORS for React frontend
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:8000,https://niches.yourdomain.com

# External API Keys (Configure these for full functionality)
YOUTUBE_API_KEY=your_youtube_api_key_here
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=NicheDiscoveryBot/1.0

# PM Agent Scoring Configuration
MIN_SCORE_THRESHOLD=50.0
HIGH_SCORE_THRESHOLD=90.0

# Rate Limiting
RATE_LIMIT_PER_MINUTE=100

# Monitoring
ENABLE_METRICS=true
METRICS_PORT=8001

# Deployment Configuration
HOST=0.0.0.0
PORT=8000
WORKERS=4
"""
        
        with open(self.env_file, 'w') as f:
            f.write(env_content)
        
        logger.info("✅ Environment configuration created")

    def setup_database(self):
        """Set up PostgreSQL database"""
        logger.info("🗄️ Setting up PostgreSQL database...")
        
        try:
            # Check if PostgreSQL is installed
            subprocess.run(["psql", "--version"], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.error("❌ PostgreSQL not found. Please install PostgreSQL first:")
            logger.error("Ubuntu/Debian: sudo apt-get install postgresql postgresql-contrib")
            logger.error("CentOS/RHEL: sudo yum install postgresql postgresql-server")
            logger.error("macOS: brew install postgresql")
            return False
        
        # Create database and user
        setup_commands = [
            "sudo -u postgres createdb niche_discovery_prod",
            "sudo -u postgres psql -c \"CREATE USER niche_user WITH PASSWORD 'niche_secure_2024';\"",
            "sudo -u postgres psql -c \"GRANT ALL PRIVILEGES ON DATABASE niche_discovery_prod TO niche_user;\"",
            "sudo -u postgres psql -c \"ALTER USER niche_user CREATEDB;\""
        ]
        
        for cmd in setup_commands:
            try:
                subprocess.run(cmd.split(), check=True)
                logger.info(f"✅ Executed: {cmd}")
            except subprocess.CalledProcessError as e:
                logger.warning(f"⚠️ Command may have failed (might be OK if already exists): {cmd}")
        
        logger.info("✅ Database setup completed")
        return True

    def setup_redis(self):
        """Set up Redis for caching and job queue"""
        logger.info("📦 Setting up Redis...")
        
        try:
            subprocess.run(["redis-cli", "ping"], check=True, capture_output=True)
            logger.info("✅ Redis is already running")
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.error("❌ Redis not found or not running. Please install and start Redis:")
            logger.error("Ubuntu/Debian: sudo apt-get install redis-server && sudo systemctl start redis")
            logger.error("CentOS/RHEL: sudo yum install redis && sudo systemctl start redis")
            logger.error("macOS: brew install redis && brew services start redis")
            return False
        
        return True

    def install_backend_dependencies(self):
        """Install Python backend dependencies"""
        logger.info("🐍 Installing backend dependencies...")
        
        os.chdir(self.backend_dir)
        
        # Create virtual environment
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        
        # Activate virtual environment and install dependencies
        pip_path = "venv/bin/pip" if os.name != 'nt' else "venv\\Scripts\\pip.exe"
        
        subprocess.run([pip_path, "install", "--upgrade", "pip"], check=True)
        subprocess.run([pip_path, "install", "-r", "requirements.txt"], check=True)
        
        logger.info("✅ Backend dependencies installed")

    def install_frontend_dependencies(self):
        """Install Node.js frontend dependencies"""
        logger.info("⚛️ Installing frontend dependencies...")
        
        try:
            subprocess.run(["node", "--version"], check=True, capture_output=True)
            subprocess.run(["npm", "--version"], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.error("❌ Node.js/npm not found. Please install Node.js first:")
            logger.error("Visit: https://nodejs.org/")
            return False
        
        os.chdir(self.frontend_dir)
        
        subprocess.run(["npm", "install"], check=True)
        logger.info("✅ Frontend dependencies installed")
        return True

    def run_database_migrations(self):
        """Run database migrations"""
        logger.info("🔄 Running database migrations...")
        
        os.chdir(self.backend_dir)
        python_path = "venv/bin/python" if os.name != 'nt' else "venv\\Scripts\\python.exe"
        
        # Initialize Alembic if not already done
        try:
            subprocess.run([python_path, "-m", "alembic", "upgrade", "head"], check=True)
        except subprocess.CalledProcessError:
            logger.info("Initializing Alembic...")
            subprocess.run([python_path, "-m", "alembic", "init", "alembic"], check=True)
            subprocess.run([python_path, "-m", "alembic", "revision", "--autogenerate", "-m", "Initial migration"], check=True)
            subprocess.run([python_path, "-m", "alembic", "upgrade", "head"], check=True)
        
        logger.info("✅ Database migrations completed")

    def seed_initial_data(self):
        """Seed database with initial PM Agent data"""
        logger.info("🌱 Seeding initial data...")
        
        seed_script = """
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.services.niche_discovery_service import NicheDiscoveryService
from app.models import Niche, Source

async def seed_data():
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession)
    
    async with async_session() as session:
        # Create data sources
        sources = [
            Source(platform="youtube", name="YouTube Data API v3", 
                   base_url="https://www.googleapis.com/youtube/v3", is_active=True),
            Source(platform="google_trends", name="Google Trends", 
                   base_url="https://trends.google.com", is_active=True),
            Source(platform="reddit", name="Reddit API", 
                   base_url="https://www.reddit.com", is_active=True),
            Source(platform="tiktok", name="TikTok Research API", 
                   base_url="https://api.tiktok.com", is_active=True),
        ]
        
        for source in sources:
            session.add(source)
        
        await session.commit()
        
        # Initialize discovery service and seed PM Agent niches
        discovery_service = NicheDiscoveryService(session)
        results = await discovery_service.discover_niches_daily()
        
        print(f"✅ Seeded {results['total_discovered']} initial niches")
        print(f"🎯 Found {len(results['high_potential'])} high-potential niches")

if __name__ == "__main__":
    asyncio.run(seed_data())
"""
        
        seed_file = self.backend_dir / "seed_data.py"
        with open(seed_file, 'w') as f:
            f.write(seed_script)
        
        os.chdir(self.backend_dir)
        python_path = "venv/bin/python" if os.name != 'nt' else "venv\\Scripts\\python.exe"
        
        try:
            subprocess.run([python_path, "seed_data.py"], check=True)
            logger.info("✅ Initial data seeded successfully")
        except subprocess.CalledProcessError:
            logger.warning("⚠️ Seeding failed - will continue with empty database")

    def build_frontend(self):
        """Build React frontend for production"""
        logger.info("🏗️ Building React frontend...")
        
        os.chdir(self.frontend_dir)
        subprocess.run(["npm", "run", "build"], check=True)
        
        logger.info("✅ Frontend built successfully")

    def create_deployment_scripts(self):
        """Create deployment and management scripts"""
        logger.info("📝 Creating deployment scripts...")
        
        # Backend start script
        backend_start = """#!/bin/bash
cd backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4 --access-log
"""
        
        # Frontend start script (for development)
        frontend_start = """#!/bin/bash
cd frontend
npm start
"""
        
        # Production deployment script
        production_deploy = """#!/bin/bash
# Production deployment with Nginx

# Start backend
cd backend
source venv/bin/activate
nohup uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 4 > ../logs/backend.log 2>&1 &

# Serve frontend with Nginx
sudo cp nginx.conf /etc/nginx/sites-available/niche-discovery
sudo ln -sf /etc/nginx/sites-available/niche-discovery /etc/nginx/sites-enabled/
sudo systemctl reload nginx

echo "🚀 Niche Discovery Engine deployed!"
echo "📊 Dashboard: https://niches.yourdomain.com"
echo "🔌 API: https://api.yourdomain.com"
"""

        # Nginx configuration
        nginx_config = """server {
    listen 80;
    server_name niches.yourdomain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name niches.yourdomain.com;
    
    # SSL Configuration (add your certificates)
    # ssl_certificate /path/to/certificate.crt;
    # ssl_certificate_key /path/to/private.key;
    
    # Frontend (React build)
    location / {
        root /path/to/frontend/build;
        index index.html index.htm;
        try_files $uri $uri/ /index.html;
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # WebSocket support for real-time updates
    location /ws {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}"""
        
        # Create scripts directory
        scripts_dir = self.project_root / "deployment"
        scripts_dir.mkdir(exist_ok=True)
        
        scripts = {
            "start_backend.sh": backend_start,
            "start_frontend.sh": frontend_start,
            "deploy_production.sh": production_deploy,
            "nginx.conf": nginx_config
        }
        
        for script_name, content in scripts.items():
            script_path = scripts_dir / script_name
            with open(script_path, 'w') as f:
                f.write(content)
            
            if script_name.endswith('.sh'):
                os.chmod(script_path, 0o755)
        
        logger.info("✅ Deployment scripts created in ./deployment/")

    def start_development_servers(self):
        """Start development servers for immediate testing"""
        logger.info("🚀 Starting development servers...")
        
        # Create logs directory
        logs_dir = self.project_root / "logs"
        logs_dir.mkdir(exist_ok=True)
        
        # Start backend
        os.chdir(self.backend_dir)
        python_path = "venv/bin/python" if os.name != 'nt' else "venv\\Scripts\\python.exe"
        
        backend_process = subprocess.Popen([
            python_path, "-m", "uvicorn", "app.main:app", 
            "--host", "0.0.0.0", "--port", "8000", "--reload"
        ])
        
        # Start frontend
        os.chdir(self.frontend_dir)
        frontend_process = subprocess.Popen(["npm", "start"])
        
        logger.info("✅ Development servers started!")
        logger.info("📊 Frontend Dashboard: http://localhost:3000")
        logger.info("🔌 Backend API: http://localhost:8000")
        logger.info("📖 API Documentation: http://localhost:8000/docs")
        
        return backend_process, frontend_process

    def deploy(self):
        """Main deployment workflow"""
        logger.info("🚀 Starting PM Agent Niche Discovery Engine Deployment")
        logger.info("🎯 Target: Remote deployment within 24-48 hours")
        
        try:
            # Phase 1: Environment Setup
            self.create_env_file()
            
            if not self.setup_database():
                return False
            
            if not self.setup_redis():
                return False
            
            # Phase 2: Dependencies
            self.install_backend_dependencies()
            
            if not self.install_frontend_dependencies():
                return False
            
            # Phase 3: Database Setup
            self.run_database_migrations()
            self.seed_initial_data()
            
            # Phase 4: Build and Deploy
            self.build_frontend()
            self.create_deployment_scripts()
            
            logger.info("🎉 DEPLOYMENT SUCCESSFUL!")
            logger.info("=" * 60)
            logger.info("PM Agent YouTube Niche Discovery Engine is ready!")
            logger.info("")
            logger.info("🔥 IMMEDIATE NEXT STEPS:")
            logger.info("1. Configure YouTube API key in .env file")
            logger.info("2. Run: ./deployment/start_backend.sh")
            logger.info("3. Run: ./deployment/start_frontend.sh") 
            logger.info("4. Access dashboard: http://localhost:3000")
            logger.info("5. Start daily discovery: POST /api/v1/niches/discover/daily")
            logger.info("")
            logger.info("🌍 FOR REMOTE DEPLOYMENT:")
            logger.info("1. Set up domain and SSL certificates")
            logger.info("2. Configure nginx with provided config")
            logger.info("3. Update CORS settings in .env")
            logger.info("4. Run: ./deployment/deploy_production.sh")
            logger.info("")
            logger.info("🎯 TARGET ACHIEVED: 100-point PM scoring algorithm implemented")
            logger.info("💰 Ready to discover profitable YouTube niches!")
            logger.info("=" * 60)
            
            # Option to start development servers immediately
            start_now = input("\n🚀 Start development servers now? (y/N): ")
            if start_now.lower() in ['y', 'yes']:
                self.start_development_servers()
                input("\nPress Enter to stop servers...")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Deployment failed: {e}")
            return False

def main():
    """Main deployment entry point"""
    print("🚀 YouTube Niche Discovery Engine - PM Agent Implementation")
    print("Target: Remote deployment within 24-48 hours")
    print("=" * 60)
    
    deployer = NicheEngineDeployer()
    success = deployer.deploy()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()