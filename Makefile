# YouTube Niche Discovery Engine - Project Makefile
# Author: Project Manager
# Version: 1.0
# Description: Comprehensive build, test, and deployment automation

# Variables
PROJECT_NAME := niche-discovery-engine
DOCKER_REGISTRY := your-registry.com
VERSION := $(shell git describe --tags --always --dirty)
TIMESTAMP := $(shell date +%Y%m%d_%H%M%S)

# Environment Variables
DEV_ENV_FILE := .env.dev
STAGING_ENV_FILE := .env.staging
PROD_ENV_FILE := .env.prod

# Colors for output
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

# Default target
.DEFAULT_GOAL := help

##@ Development Environment

.PHONY: help
help: ## Display this help message
	@echo "$(GREEN)YouTube Niche Discovery Engine - Build System$(NC)"
	@echo "=============================================="
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

.PHONY: dev-setup
dev-setup: ## Complete development environment setup
	@echo "$(GREEN)Setting up development environment...$(NC)"
	@if [ ! -f $(DEV_ENV_FILE) ]; then \
		cp .env.example $(DEV_ENV_FILE); \
		echo "$(YELLOW)Created $(DEV_ENV_FILE). Please update with your configuration.$(NC)"; \
	fi
	@make install-deps
	@make setup-pre-commit
	@make docker-build-dev
	@make db-setup
	@echo "$(GREEN)Development environment setup complete!$(NC)"

.PHONY: install-deps
install-deps: ## Install all project dependencies
	@echo "$(GREEN)Installing backend dependencies...$(NC)"
	@cd backend && python -m venv venv
	@cd backend && . venv/bin/activate && pip install --upgrade pip
	@cd backend && . venv/bin/activate && pip install -r requirements.txt -r requirements-dev.txt
	@echo "$(GREEN)Installing frontend dependencies...$(NC)"
	@cd frontend && npm install
	@echo "$(GREEN)Dependencies installed successfully!$(NC)"

.PHONY: setup-pre-commit
setup-pre-commit: ## Set up pre-commit hooks
	@echo "$(GREEN)Setting up pre-commit hooks...$(NC)"
	@cd backend && . venv/bin/activate && pre-commit install
	@echo "$(GREEN)Pre-commit hooks installed!$(NC)"

.PHONY: dev-start
dev-start: ## Start development environment
	@echo "$(GREEN)Starting development environment...$(NC)"
	@docker-compose -f docker-compose.dev.yml up -d
	@echo "$(GREEN)Development environment started!$(NC)"
	@echo "$(YELLOW)Services available at:$(NC)"
	@echo "  - API Documentation: http://localhost:8000/docs"
	@echo "  - Frontend: http://localhost:3000"
	@echo "  - PgAdmin: http://localhost:8080"
	@echo "  - Redis Commander: http://localhost:8081"
	@echo "  - Flower (Celery): http://localhost:5555"

.PHONY: dev-stop
dev-stop: ## Stop development environment
	@echo "$(GREEN)Stopping development environment...$(NC)"
	@docker-compose -f docker-compose.dev.yml down
	@echo "$(GREEN)Development environment stopped!$(NC)"

.PHONY: dev-clean
dev-clean: ## Clean development environment and volumes
	@echo "$(RED)Cleaning development environment (this will remove all data)...$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose -f docker-compose.dev.yml down -v --remove-orphans; \
		docker system prune -f; \
		echo "$(GREEN)Development environment cleaned!$(NC)"; \
	else \
		echo "$(YELLOW)Operation cancelled.$(NC)"; \
	fi

##@ Testing

.PHONY: test
test: ## Run all tests
	@echo "$(GREEN)Running all tests...$(NC)"
	@make test-backend
	@make test-frontend
	@make test-integration
	@echo "$(GREEN)All tests completed!$(NC)"

.PHONY: test-backend
test-backend: ## Run backend tests
	@echo "$(GREEN)Running backend tests...$(NC)"
	@cd backend && . venv/bin/activate && pytest -v --cov=app --cov-report=html --cov-report=term

.PHONY: test-frontend
test-frontend: ## Run frontend tests
	@echo "$(GREEN)Running frontend tests...$(NC)"
	@cd frontend && npm test -- --coverage --watchAll=false

.PHONY: test-integration
test-integration: ## Run integration tests
	@echo "$(GREEN)Running integration tests...$(NC)"
	@cd tests && python -m pytest integration/ -v

.PHONY: test-e2e
test-e2e: ## Run end-to-end tests
	@echo "$(GREEN)Running E2E tests...$(NC)"
	@cd frontend && npm run test:e2e

.PHONY: test-load
test-load: ## Run load tests
	@echo "$(GREEN)Running load tests...$(NC)"
	@cd tests/load && locust -f locustfile.py --headless -u 10 -r 2 -t 60s --host=http://localhost:8000

.PHONY: test-security
test-security: ## Run security tests
	@echo "$(GREEN)Running security tests...$(NC)"
	@cd backend && . venv/bin/activate && bandit -r app/
	@cd frontend && npm audit --audit-level moderate

##@ Code Quality

.PHONY: lint
lint: ## Run linters for all code
	@echo "$(GREEN)Running linters...$(NC)"
	@make lint-backend
	@make lint-frontend

.PHONY: lint-backend
lint-backend: ## Run backend linters
	@echo "$(GREEN)Linting backend code...$(NC)"
	@cd backend && . venv/bin/activate && flake8 app/
	@cd backend && . venv/bin/activate && mypy app/
	@cd backend && . venv/bin/activate && black --check app/
	@cd backend && . venv/bin/activate && isort --check-only app/

.PHONY: lint-frontend
lint-frontend: ## Run frontend linters
	@echo "$(GREEN)Linting frontend code...$(NC)"
	@cd frontend && npm run lint

.PHONY: format
format: ## Format all code
	@echo "$(GREEN)Formatting code...$(NC)"
	@make format-backend
	@make format-frontend

.PHONY: format-backend
format-backend: ## Format backend code
	@echo "$(GREEN)Formatting backend code...$(NC)"
	@cd backend && . venv/bin/activate && black app/
	@cd backend && . venv/bin/activate && isort app/

.PHONY: format-frontend
format-frontend: ## Format frontend code
	@echo "$(GREEN)Formatting frontend code...$(NC)"
	@cd frontend && npm run format

.PHONY: security
security: ## Run security scans
	@echo "$(GREEN)Running security scans...$(NC)"
	@cd backend && . venv/bin/activate && bandit -r app/ -f json -o security-report.json || true
	@cd frontend && npm audit --json > security-audit.json || true
	@echo "$(GREEN)Security scans completed!$(NC)"

##@ Database Operations

.PHONY: db-setup
db-setup: ## Set up database
	@echo "$(GREEN)Setting up database...$(NC)"
	@make db-start
	@sleep 10
	@make db-migrate
	@make db-seed
	@echo "$(GREEN)Database setup complete!$(NC)"

.PHONY: db-start
db-start: ## Start database services
	@echo "$(GREEN)Starting database services...$(NC)"
	@docker-compose -f docker-compose.dev.yml up -d postgres redis

.PHONY: db-migrate
db-migrate: ## Run database migrations
	@echo "$(GREEN)Running database migrations...$(NC)"
	@cd backend && . venv/bin/activate && alembic upgrade head

.PHONY: db-seed
db-seed: ## Seed database with development data
	@echo "$(GREEN)Seeding database...$(NC)"
	@cd backend && . venv/bin/activate && python scripts/seed_dev_data.py

.PHONY: db-reset
db-reset: ## Reset database (WARNING: destroys all data)
	@echo "$(RED)Resetting database (this will destroy all data)...$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose -f docker-compose.dev.yml down -v postgres redis; \
		docker-compose -f docker-compose.dev.yml up -d postgres redis; \
		sleep 10; \
		make db-migrate; \
		make db-seed; \
		echo "$(GREEN)Database reset complete!$(NC)"; \
	else \
		echo "$(YELLOW)Operation cancelled.$(NC)"; \
	fi

.PHONY: db-backup
db-backup: ## Backup database
	@echo "$(GREEN)Backing up database...$(NC)"
	@mkdir -p backups
	@docker exec -t niche_postgres pg_dump -U niche_user niche_discovery_db > backups/backup_$(TIMESTAMP).sql
	@echo "$(GREEN)Database backed up to backups/backup_$(TIMESTAMP).sql$(NC)"

##@ Docker Operations

.PHONY: docker-build
docker-build: ## Build all Docker images
	@echo "$(GREEN)Building Docker images...$(NC)"
	@make docker-build-backend
	@make docker-build-frontend

.PHONY: docker-build-dev
docker-build-dev: ## Build development Docker images
	@echo "$(GREEN)Building development Docker images...$(NC)"
	@docker-compose -f docker-compose.dev.yml build

.PHONY: docker-build-prod
docker-build-prod: ## Build production Docker images
	@echo "$(GREEN)Building production Docker images...$(NC)"
	@docker-compose -f docker-compose.prod.yml build

.PHONY: docker-build-backend
docker-build-backend: ## Build backend Docker image
	@echo "$(GREEN)Building backend Docker image...$(NC)"
	@cd backend && docker build -f Dockerfile.prod -t $(PROJECT_NAME)-backend:$(VERSION) .

.PHONY: docker-build-frontend
docker-build-frontend: ## Build frontend Docker image
	@echo "$(GREEN)Building frontend Docker image...$(NC)"
	@cd frontend && docker build -f Dockerfile.prod -t $(PROJECT_NAME)-frontend:$(VERSION) .

.PHONY: docker-push
docker-push: ## Push Docker images to registry
	@echo "$(GREEN)Pushing Docker images to registry...$(NC)"
	@docker tag $(PROJECT_NAME)-backend:$(VERSION) $(DOCKER_REGISTRY)/$(PROJECT_NAME)-backend:$(VERSION)
	@docker tag $(PROJECT_NAME)-frontend:$(VERSION) $(DOCKER_REGISTRY)/$(PROJECT_NAME)-frontend:$(VERSION)
	@docker push $(DOCKER_REGISTRY)/$(PROJECT_NAME)-backend:$(VERSION)
	@docker push $(DOCKER_REGISTRY)/$(PROJECT_NAME)-frontend:$(VERSION)

.PHONY: docker-clean
docker-clean: ## Clean Docker resources
	@echo "$(GREEN)Cleaning Docker resources...$(NC)"
	@docker system prune -af
	@docker volume prune -f

##@ Deployment

.PHONY: deploy-dev
deploy-dev: ## Deploy to development environment
	@echo "$(GREEN)Deploying to development environment...$(NC)"
	@docker-compose -f docker-compose.dev.yml up -d --build
	@make health-check-dev

.PHONY: deploy-staging
deploy-staging: ## Deploy to staging environment
	@echo "$(GREEN)Deploying to staging environment...$(NC)"
	@if [ ! -f $(STAGING_ENV_FILE) ]; then \
		echo "$(RED)Staging environment file not found!$(NC)"; \
		exit 1; \
	fi
	@cp $(STAGING_ENV_FILE) .env
	@make docker-build-prod
	@docker-compose -f docker-compose.prod.yml up -d
	@make health-check-staging

.PHONY: deploy-prod
deploy-prod: ## Deploy to production environment
	@echo "$(RED)Deploying to production environment...$(NC)"
	@read -p "Are you sure you want to deploy to production? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		if [ ! -f $(PROD_ENV_FILE) ]; then \
			echo "$(RED)Production environment file not found!$(NC)"; \
			exit 1; \
		fi; \
		cp $(PROD_ENV_FILE) .env; \
		make docker-build-prod; \
		make docker-push; \
		docker-compose -f docker-compose.prod.yml up -d; \
		make health-check-prod; \
		echo "$(GREEN)Production deployment complete!$(NC)"; \
	else \
		echo "$(YELLOW)Production deployment cancelled.$(NC)"; \
	fi

##@ Health Checks

.PHONY: health-check-dev
health-check-dev: ## Check development environment health
	@echo "$(GREEN)Checking development environment health...$(NC)"
	@sleep 30
	@curl -f http://localhost:8000/health || (echo "$(RED)Backend health check failed!$(NC)" && exit 1)
	@curl -f http://localhost:3000 || (echo "$(RED)Frontend health check failed!$(NC)" && exit 1)
	@echo "$(GREEN)Development environment is healthy!$(NC)"

.PHONY: health-check-staging
health-check-staging: ## Check staging environment health
	@echo "$(GREEN)Checking staging environment health...$(NC)"
	@sleep 60
	@curl -f https://staging-api.nichediscovery.com/health || (echo "$(RED)Staging backend health check failed!$(NC)" && exit 1)
	@curl -f https://staging.nichediscovery.com || (echo "$(RED)Staging frontend health check failed!$(NC)" && exit 1)
	@echo "$(GREEN)Staging environment is healthy!$(NC)"

.PHONY: health-check-prod
health-check-prod: ## Check production environment health
	@echo "$(GREEN)Checking production environment health...$(NC)"
	@sleep 60
	@curl -f https://api.nichediscovery.com/health || (echo "$(RED)Production backend health check failed!$(NC)" && exit 1)
	@curl -f https://nichediscovery.com || (echo "$(RED)Production frontend health check failed!$(NC)" && exit 1)
	@echo "$(GREEN)Production environment is healthy!$(NC)"

##@ Monitoring & Logs

.PHONY: logs
logs: ## View development logs
	@docker-compose -f docker-compose.dev.yml logs -f

.PHONY: logs-backend
logs-backend: ## View backend logs
	@docker-compose -f docker-compose.dev.yml logs -f backend

.PHONY: logs-frontend
logs-frontend: ## View frontend logs
	@docker-compose -f docker-compose.dev.yml logs -f frontend

.PHONY: logs-db
logs-db: ## View database logs
	@docker-compose -f docker-compose.dev.yml logs -f postgres

.PHONY: stats
stats: ## Show container stats
	@docker stats

.PHONY: ps
ps: ## Show running containers
	@docker-compose -f docker-compose.dev.yml ps

##@ Project Management

.PHONY: sprint-start
sprint-start: ## Start new sprint (requires SPRINT_NUM)
	@if [ -z "$(SPRINT_NUM)" ]; then \
		echo "$(RED)Error: SPRINT_NUM is required$(NC)"; \
		echo "Usage: make sprint-start SPRINT_NUM=1"; \
		exit 1; \
	fi
	@echo "$(GREEN)Starting Sprint $(SPRINT_NUM)...$(NC)"
	@mkdir -p docs/sprints/sprint-$(SPRINT_NUM)
	@cp docs/project-management/SPRINT_PLANNING_TEMPLATE.md docs/sprints/sprint-$(SPRINT_NUM)/sprint-$(SPRINT_NUM)-planning.md
	@sed -i 's/\[SPRINT_NUM\]/$(SPRINT_NUM)/g' docs/sprints/sprint-$(SPRINT_NUM)/sprint-$(SPRINT_NUM)-planning.md
	@echo "$(GREEN)Sprint $(SPRINT_NUM) started! Planning document created.$(NC)"

.PHONY: daily-update
daily-update: ## Generate daily progress update
	@echo "$(GREEN)Generating daily progress update...$(NC)"
	@./scripts/daily-update.sh

.PHONY: sprint-review
sprint-review: ## Generate sprint review (requires SPRINT_NUM)
	@if [ -z "$(SPRINT_NUM)" ]; then \
		echo "$(RED)Error: SPRINT_NUM is required$(NC)"; \
		echo "Usage: make sprint-review SPRINT_NUM=1"; \
		exit 1; \
	fi
	@echo "$(GREEN)Generating Sprint $(SPRINT_NUM) review...$(NC)"
	@./scripts/sprint-review.sh $(SPRINT_NUM)

##@ Documentation

.PHONY: docs
docs: ## Generate documentation
	@echo "$(GREEN)Generating documentation...$(NC)"
	@make docs-api
	@make docs-frontend
	@echo "$(GREEN)Documentation generated!$(NC)"

.PHONY: docs-api
docs-api: ## Generate API documentation
	@echo "$(GREEN)Generating API documentation...$(NC)"
	@cd backend && . venv/bin/activate && python scripts/generate_api_docs.py

.PHONY: docs-frontend
docs-frontend: ## Generate frontend documentation
	@echo "$(GREEN)Generating frontend documentation...$(NC)"
	@cd frontend && npm run docs

##@ Utilities

.PHONY: shell-backend
shell-backend: ## Open shell in backend container
	@docker-compose -f docker-compose.dev.yml exec backend bash

.PHONY: shell-frontend
shell-frontend: ## Open shell in frontend container
	@docker-compose -f docker-compose.dev.yml exec frontend sh

.PHONY: shell-db
shell-db: ## Open database shell
	@docker-compose -f docker-compose.dev.yml exec postgres psql -U niche_user -d niche_discovery_db

.PHONY: shell-redis
shell-redis: ## Open Redis shell
	@docker-compose -f docker-compose.dev.yml exec redis redis-cli

.PHONY: version
version: ## Show project version
	@echo "Project: $(PROJECT_NAME)"
	@echo "Version: $(VERSION)"
	@echo "Timestamp: $(TIMESTAMP)"

.PHONY: clean
clean: ## Clean all generated files and caches
	@echo "$(GREEN)Cleaning project...$(NC)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "coverage" -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.pyc" -delete 2>/dev/null || true
	@find . -name "*.pyo" -delete 2>/dev/null || true
	@find . -name ".coverage" -delete 2>/dev/null || true
	@echo "$(GREEN)Project cleaned!$(NC)"

.PHONY: install-tools
install-tools: ## Install development tools globally
	@echo "$(GREEN)Installing development tools...$(NC)"
	@pip install --user cookiecutter pre-commit black flake8 mypy
	@npm install -g @commitlint/cli @commitlint/config-conventional
	@echo "$(GREEN)Development tools installed!$(NC)"

# Create necessary directories
$(shell mkdir -p logs backups docs/sprints tests/load)

# Include environment-specific makefiles if they exist
-include Makefile.local