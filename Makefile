.PHONY: help setup setup-backend setup-frontend install dev backend frontend db-init db-reset seed test test-backend lint clean demo

# Colors for terminal output
CYAN := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RESET := \033[0m

# Default target
help:
	@echo "$(CYAN)Invoice LangGraph Agent - Development Commands$(RESET)"
	@echo ""
	@echo "$(GREEN)Setup:$(RESET)"
	@echo "  make setup          - Setup both backend and frontend"
	@echo "  make setup-backend  - Setup backend only"
	@echo "  make setup-frontend - Setup frontend only"
	@echo ""
	@echo "$(GREEN)Development:$(RESET)"
	@echo "  make dev            - Run both backend and frontend together"
	@echo "  make backend        - Run backend only (port 8000)"
	@echo "  make frontend       - Run frontend only (port 3000)"
	@echo ""
	@echo "$(GREEN)Database:$(RESET)"
	@echo "  make db-init        - Initialize database tables"
	@echo "  make db-reset       - Reset database (drop all tables)"
	@echo "  make seed           - Seed demo data"
	@echo ""
	@echo "$(GREEN)Testing:$(RESET)"
	@echo "  make test           - Run all tests"
	@echo "  make test-backend   - Run backend tests only"
	@echo "  make lint           - Run linters"
	@echo ""
	@echo "$(GREEN)Demo:$(RESET)"
	@echo "  make demo           - Run complete demo scenario"
	@echo ""
	@echo "$(GREEN)Cleanup:$(RESET)"
	@echo "  make clean          - Remove all generated files"
	@echo "  make git-clean-pyc  - Remove Python cache files from git tracking"

# ============================================
# SETUP
# ============================================

setup: setup-backend setup-frontend
	@echo "$(GREEN)✓ Setup complete!$(RESET)"
	@echo "$(YELLOW)Run 'make dev' to start development servers$(RESET)"

setup-backend: check-python
	@echo "$(CYAN)Setting up backend...$(RESET)"
	@if [ ! -d "backend/.venv" ]; then \
		echo "$(CYAN)Creating virtual environment...$(RESET)"; \
		cd backend && python3 -m venv .venv; \
	fi
	@echo "$(CYAN)Installing dependencies...$(RESET)"
	cd backend && source .venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt
	@echo "$(GREEN)✓ Backend setup complete$(RESET)"

check-python:
	@if ! command -v python3 >/dev/null 2>&1; then \
		echo "$(YELLOW)⚠ python3 not found$(RESET)"; \
		echo "$(CYAN)Please install Python 3.11+ first$(RESET)"; \
		exit 1; \
	fi

setup-frontend:
	@echo "$(CYAN)Setting up frontend...$(RESET)"
	cd frontend && npm install
	@echo "$(GREEN)✓ Frontend setup complete$(RESET)"

install: setup

# ============================================
# DEVELOPMENT SERVERS
# ============================================

dev: check-prerequisites
	@echo "$(YELLOW)Starting development servers...$(RESET)"
	@echo "$(GREEN)Backend:$(RESET)  http://localhost:8000"
	@echo "$(GREEN)Frontend:$(RESET) http://localhost:3000"
	@echo "$(GREEN)API Docs:$(RESET) http://localhost:8000/docs"
	@echo "$(CYAN)Press Ctrl+C to stop both servers$(RESET)"
	@echo ""
	@bash -c ' \
		trap "kill 0" EXIT INT TERM; \
		(cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000) & \
		(cd frontend && npm run dev) & \
		wait'

check-prerequisites:
	@echo "$(CYAN)Checking prerequisites...$(RESET)"
	@if [ ! -d "backend/.venv" ]; then \
		echo "$(YELLOW)⚠ Backend virtual environment not found$(RESET)"; \
		echo "$(CYAN)Run 'make setup-backend' first$(RESET)"; \
		exit 1; \
	fi
	@if ! command -v npm >/dev/null 2>&1; then \
		echo "$(YELLOW)⚠ npm not found$(RESET)"; \
		echo "$(CYAN)Please install Node.js and npm first$(RESET)"; \
		exit 1; \
	fi
	@echo "$(GREEN)✓ Prerequisites check passed$(RESET)"
	@echo ""

backend: check-backend-prereq
	@echo "$(CYAN)Starting backend server...$(RESET)"
	cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

check-backend-prereq:
	@if [ ! -d "backend/.venv" ]; then \
		echo "$(YELLOW)⚠ Backend virtual environment not found$(RESET)"; \
		echo "$(CYAN)Run 'make setup-backend' first$(RESET)"; \
		exit 1; \
	fi

frontend:
	@echo "$(CYAN)Starting frontend server...$(RESET)"
	cd frontend && npm run dev

# ============================================
# DATABASE
# ============================================

db-init:
	@echo "$(CYAN)Initializing database...$(RESET)"
	cd backend && source .venv/bin/activate && python scripts/init_db.py
	@echo "$(GREEN)✓ Database initialized$(RESET)"

db-reset:
	@echo "$(YELLOW)Resetting database...$(RESET)"
	rm -f backend/demo.db
	$(MAKE) db-init
	@echo "$(GREEN)✓ Database reset complete$(RESET)"

seed:
	@echo "$(CYAN)Seeding demo data...$(RESET)"
	cd backend && source .venv/bin/activate && python scripts/seed_data.py
	@echo "$(GREEN)✓ Demo data seeded$(RESET)"

# ============================================
# TESTING
# ============================================

test: test-backend
	@echo "$(GREEN)✓ All tests passed$(RESET)"

test-backend:
	@echo "$(CYAN)Running backend tests...$(RESET)"
	cd backend && source .venv/bin/activate && pytest -v

lint:
	@echo "$(CYAN)Running linters...$(RESET)"
	cd backend && source .venv/bin/activate && ruff check app/
	cd frontend && npm run lint
	@echo "$(GREEN)✓ Linting complete$(RESET)"

# ============================================
# DEMO
# ============================================

demo: db-reset seed
	@echo "$(CYAN)Running demo scenario...$(RESET)"
	cd backend && source .venv/bin/activate && python scripts/run_demo.py
	@echo "$(GREEN)✓ Demo complete$(RESET)"

# ============================================
# CLEANUP
# ============================================

clean:
	@echo "$(YELLOW)Cleaning up...$(RESET)"
	rm -rf backend/.venv
	find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type f -name "*.pyd" -delete 2>/dev/null || true
	rm -rf backend/.pytest_cache
	rm -rf backend/.ruff_cache
	rm -f backend/demo.db
	rm -rf frontend/node_modules
	rm -rf frontend/.next
	rm -rf frontend/.turbo
	@echo "$(GREEN)✓ Cleanup complete$(RESET)"

git-clean-pyc:
	@echo "$(CYAN)Removing Python cache files from git tracking...$(RESET)"
	@git rm -r --cached --ignore-unmatch **/__pycache__/ 2>/dev/null || true
	@find . -name "*.pyc" -exec git rm --cached {} \; 2>/dev/null || true
	@find . -name "*.pyo" -exec git rm --cached {} \; 2>/dev/null || true
	@find . -name "*.pyd" -exec git rm --cached {} \; 2>/dev/null || true
	@echo "$(GREEN)✓ Python cache files removed from git$(RESET)"
	@echo "$(YELLOW)Review changes with: git status$(RESET)"

# ============================================
# DOCKER (Optional)
# ============================================

docker-build:
	@echo "$(CYAN)Building Docker images...$(RESET)"
	docker-compose build

docker-up:
	@echo "$(CYAN)Starting Docker containers...$(RESET)"
	docker-compose up -d

docker-down:
	@echo "$(CYAN)Stopping Docker containers...$(RESET)"
	docker-compose down

docker-logs:
	docker-compose logs -f
