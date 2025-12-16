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
 
 # ============================================
 # SETUP
 # ============================================
 
 setup: setup-backend setup-frontend
 	@echo "$(GREEN)✓ Setup complete!$(RESET)"
 	@echo "$(YELLOW)Run 'make dev' to start development servers$(RESET)"
 
 setup-backend:
 	@echo "$(CYAN)Setting up backend...$(RESET)"
 	cd backend && uv venv
 	cd backend && uv pip install -r requirements.txt
 	@echo "$(GREEN)✓ Backend setup complete$(RESET)"
 
 setup-frontend:
 	@echo "$(CYAN)Setting up frontend...$(RESET)"
 	cd frontend && pnpm install
 	@echo "$(GREEN)✓ Frontend setup complete$(RESET)"
 
 install: setup
 
 # ============================================
 # DEVELOPMENT SERVERS
 # ============================================
 
dev:
	@echo "$(YELLOW)Starting development servers...$(RESET)"
	@echo "$(GREEN)Backend:$(RESET)  http://localhost:8000"
	@echo "$(GREEN)Frontend:$(RESET) http://localhost:3000"
	@echo "$(GREEN)API Docs:$(RESET) http://localhost:8000/docs"
	@echo "$(CYAN)Press Ctrl+C to stop both servers$(RESET)"
	@echo ""
	@bash -c ' \
		trap "kill 0" EXIT INT TERM; \
		(cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000) & \
		(cd frontend && pnpm dev) & \
		wait'
 
 backend:
 	@echo "$(CYAN)Starting backend server...$(RESET)"
 	cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
 
 frontend:
 	@echo "$(CYAN)Starting frontend server...$(RESET)"
 	cd frontend && pnpm dev
 
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
 	cd frontend && pnpm lint
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
 	rm -rf backend/__pycache__
 	rm -rf backend/.pytest_cache
 	rm -rf backend/.ruff_cache
 	rm -f backend/demo.db
 	rm -rf frontend/node_modules
 	rm -rf frontend/.next
 	rm -rf frontend/.turbo
 	@echo "$(GREEN)✓ Cleanup complete$(RESET)"
 
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

