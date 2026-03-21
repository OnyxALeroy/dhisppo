#!/bin/bash

# Docker Compose Script for D'hisppo
# This script builds and starts services: database, backend, and frontend
# Usage: ./start.sh [--all]

set -e

# Load environment variables from .env file
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

if [[ -f "$PROJECT_DIR/.env" ]]; then
    set -o noglob
    while IFS='=' read -r key value || [[ -n "$key" ]]; do
        key="${key#"${key%%[![:space:]]*}"}"
        key="${key%"${key##*[![:space:]]}"}"
        value="${value//$'\r'/}"
        if [[ -n "$key" ]] && [[ ! "$key" =~ ^[[:space:]]*# ]]; then
            export "$key=$value"
        fi
    done < "$PROJECT_DIR/.env"
    set +o noglob
fi

# Set defaults for MongoDB if not defined in .env
MONGO_HOST="${MONGO_HOST:-localhost}"
MONGO_PORT="${MONGO_PORT:-27017}"
MONGO_DB="${MONGO_DB:-dhisppo_db}"
MONGO_USER="${MONGO_USER:-root}"
MONGO_PASS="${MONGO_PASS:-password}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse command line arguments
RESTART_ALL=false
if [[ "$1" == "--all" ]]; then
    RESTART_ALL=true
    echo -e "${BLUE}Starting D'hisppo with Docker Compose (--all flag: restart all services)...${NC}"
else
    echo -e "${BLUE}Starting D'hisppo with Docker Compose (without --all: preserve database if running)...${NC}"
fi

# Function to check if MongoDB container is running
is_mongodb_running() {
    docker ps --format "{{.Names}} {{.Status}}" | grep -q "dhisppo-mongodb.*Up"
    return $?
}

# Function to check if MongoDB container exists (even if stopped)
mongodb_exists() {
    docker ps -a --format "{{.Names}}" | grep -q "dhisppo-mongodb"
    return $?
}

# Function to stop specific containers
stop_services() {
    if [[ "$RESTART_ALL" == true ]]; then
        echo -e "${YELLOW}Stopping all containers...${NC}"
        docker-compose down 2>/dev/null || {
            echo -e "${YELLOW}Using direct Docker commands...${NC}"
            docker stop dhisppo-frontend dhisppo-backend dhisppo-mongodb 2>/dev/null || true
            docker rm dhisppo-frontend dhisppo-backend dhisppo-mongodb 2>/dev/null || true
        }
    else
        echo -e "${YELLOW}Stopping frontend and backend containers (preserving database if running)...${NC}"
        docker-compose stop frontend backend 2>/dev/null || {
            echo -e "${YELLOW}Using direct Docker commands...${NC}"
            docker stop dhisppo-frontend dhisppo-backend 2>/dev/null || true
        }
        docker-compose rm -f frontend backend 2>/dev/null || {
            docker rm dhisppo-frontend dhisppo-backend 2>/dev/null || true
        }
    fi
}

# Function to start database if needed
start_database_if_needed() {
    if [[ "$RESTART_ALL" == false ]]; then
        if is_mongodb_running; then
            echo -e "${GREEN}✓ MongoDB already running, preserving existing data${NC}"
        elif mongodb_exists; then
            echo -e "${YELLOW}MongoDB container exists but stopped, starting it...${NC}"
            docker start dhisppo-mongodb
            echo -e "${BLUE}Waiting for MongoDB to be ready...${NC}"
            sleep 10
        else
            echo -e "${YELLOW}Database not running, starting MongoDB...${NC}"
            docker-compose up -d mongodb 2>/dev/null || {
                echo -e "${YELLOW}Using direct Docker command for MongoDB...${NC}"
                docker network inspect dhisppo-network >/dev/null 2>&1 || docker network create dhisppo-network
                docker volume inspect mongodb_data >/dev/null 2>&1 || docker volume create mongodb_data
                docker run -d --name dhisppo-mongodb --restart unless-stopped \
                    -e MONGO_INITDB_ROOT_USERNAME="$MONGO_USER" \
                    -e MONGO_INITDB_ROOT_PASSWORD="$MONGO_PASS" \
                    -e MONGO_INITDB_DATABASE="$MONGO_DB" \
                    -p "${MONGO_PORT:-27017}:27017" \
                    -v mongodb_data:/data/db \
                    --network dhisppo-network \
                    mongo:7
            }
            echo -e "${BLUE}Waiting for MongoDB to be ready...${NC}"
            sleep 10
        fi
    fi
}

# Function to start application services
start_app_services() {
    if [[ "$RESTART_ALL" == true ]]; then
        echo -e "${BLUE}Building and starting all services...${NC}"
        docker-compose up --build -d
    else
        echo -e "${BLUE}Building and starting frontend and backend services...${NC}"
        docker-compose up --build -d frontend backend
    fi
}

# Stop services based on flag
stop_services

# Start database if needed (only when --all flag is not used)
if [[ "$RESTART_ALL" == false ]]; then
    start_database_if_needed
fi

# Start application services
start_app_services

# Health checks
echo -e "${YELLOW}Performing health checks...${NC}"

# Function to check service health
check_health() {
    local service=$1
    local url=$2
    local max_attempts=30
    local attempt=1
    
    echo -e "${BLUE}Checking $service health...${NC}"
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s -f -o /dev/null "$url"; then
            echo -e "${GREEN}✓ $service is healthy${NC}"
            return 0
        fi
        
        echo -e "${YELLOW}Attempt $attempt/$max_attempts: $service not ready yet...${NC}"
        sleep 2
        ((attempt++))
    done
    
    echo -e "${RED}✗ $service failed health check${NC}"
    return 1
}

# Check backend health (give it more time to start)
sleep 10
if ! check_health "backend" "http://localhost:8000/health"; then
    echo -e "${RED}Backend health check failed. Check logs with ./scripts/logs.sh backend${NC}"
    exit 1
fi

# Check frontend health  
if ! check_health "frontend" "http://localhost:3000"; then
    echo -e "${RED}Frontend health check failed. Check logs with ./scripts/logs.sh frontend${NC}"
    exit 1
fi

# Show running containers
echo -e "${BLUE}Running containers:${NC}"
docker ps --filter "name=dhisppo-"

echo ""
if [[ "$RESTART_ALL" == true ]]; then
    echo -e "${GREEN}All services restarted and healthy!${NC}"
else
    echo -e "${GREEN}Application services started and healthy!${NC}"
fi
echo -e "${GREEN}Frontend: http://localhost:3000${NC}"
echo -e "${GREEN}Backend API: http://localhost:8000${NC}"
echo -e "${GREEN}Database: mongodb://localhost:27017${NC}"
echo ""
echo -e "${BLUE}Usage:${NC}"
echo -e "${BLUE}  ./start.sh        - Restart frontend/backend only (preserve database)${NC}"
echo -e "${BLUE}  ./start.sh --all  - Restart all services including database${NC}"
echo ""
echo -e "${BLUE}To view logs: docker-compose logs -f${NC}"
echo -e "${BLUE}To stop services: docker-compose down${NC}"