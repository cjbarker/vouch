.PHONY: help build up down logs clean restart status health shell

help: ## Show this help message
	@echo "Vouch Docker Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

build: ## Build the Docker images
	docker-compose build

up: ## Start all services
	docker-compose up -d
	@echo ""
	@echo "Services are starting..."
	@echo "Note: Ollama model pull may take several minutes on first run."
	@echo ""
	@echo "Check status with: make status"
	@echo "View logs with: make logs"
	@echo "Access application at: http://localhost:8000"

down: ## Stop all services
	docker-compose down

logs: ## View logs from all services
	docker-compose logs -f

logs-app: ## View logs from vouch application only
	docker-compose logs -f vouch

logs-ollama: ## View logs from Ollama service
	docker-compose logs -f ollama ollama-init

status: ## Show status of all services
	docker-compose ps

health: ## Check health of all services
	@echo "Checking service health..."
	@echo ""
	@echo "MongoDB:"
	@curl -s http://localhost:27017 > /dev/null 2>&1 && echo "  ✓ Running" || echo "  ✗ Not accessible"
	@echo ""
	@echo "Elasticsearch:"
	@curl -s http://localhost:9200/_cluster/health | grep -q "status" && echo "  ✓ Running" || echo "  ✗ Not accessible"
	@echo ""
	@echo "Ollama:"
	@curl -s http://localhost:11434/api/tags > /dev/null 2>&1 && echo "  ✓ Running" || echo "  ✗ Not accessible"
	@echo ""
	@echo "Vouch Application:"
	@curl -s http://localhost:8000/health | grep -q "status" && echo "  ✓ Running" || echo "  ✗ Not accessible"
	@echo ""

restart: ## Restart all services
	docker-compose restart

restart-app: ## Restart vouch application only
	docker-compose restart vouch

shell: ## Open shell in vouch application container
	docker-compose exec vouch /bin/bash

shell-mongodb: ## Open MongoDB shell
	docker-compose exec mongodb mongosh vouch

clean: ## Stop and remove all containers, networks, and volumes
	docker-compose down -v
	docker system prune -f

clean-all: ## Remove everything including images
	docker-compose down -v --rmi all
	docker system prune -af

install: build up ## Build and start all services (first time setup)
	@echo ""
	@echo "Installation complete!"
	@echo ""
	@echo "Waiting for services to initialize..."
	@sleep 10
	@make status

dev: ## Start services and follow logs
	docker-compose up

pull: ## Pull latest images
	docker-compose pull

update: pull build restart ## Update images and restart services

backup-mongodb: ## Backup MongoDB data
	@echo "Creating MongoDB backup..."
	@mkdir -p backups
	docker-compose exec -T mongodb mongodump --db=vouch --archive > backups/mongodb-backup-$$(date +%Y%m%d-%H%M%S).archive
	@echo "Backup created in backups/ directory"

restore-mongodb: ## Restore MongoDB from backup (usage: make restore-mongodb FILE=backups/mongodb-backup-xxx.archive)
	@echo "Restoring MongoDB from $(FILE)..."
	docker-compose exec -T mongodb mongorestore --db=vouch --archive < $(FILE)
	@echo "Restore complete"

test-upload: ## Test file upload (requires a test receipt image)
	@echo "Testing file upload..."
	@if [ -f "test-receipt.jpg" ]; then \
		curl -X POST "http://localhost:8000/api/upload" -F "file=@test-receipt.jpg"; \
	else \
		echo "Error: test-receipt.jpg not found. Please provide a test receipt image."; \
	fi

open: ## Open application in browser
	@echo "Opening http://localhost:8000 in browser..."
	@open http://localhost:8000 2>/dev/null || xdg-open http://localhost:8000 2>/dev/null || echo "Please open http://localhost:8000 in your browser"
