#!/bin/bash

# Docker Logs Script for D'hisppo
# This script shows continuous logs for frontend and backend containers

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to show usage
show_usage() {
    echo -e "${BLUE}Usage: $0 [service]${NC}"
    echo ""
    echo -e "${GREEN}Services:${NC}"
    echo "  frontend     Show logs for frontend container"
    echo "  backend      Show logs for backend container"
    echo "  all          Show logs for both frontend and backend (default)"
    echo ""
    echo -e "${GREEN}Examples:${NC}"
    echo "  $0 frontend"
    echo "  $0 backend"
    echo "  $0 all"
    echo "  $0"
}

# Check if docker-compose is running
check_containers() {
    if ! docker-compose ps | grep -q "Up"; then
        echo -e "${RED}No containers are running. Please run './start.sh' first.${NC}"
        exit 1
    fi
}

# Show logs for specified service
show_logs() {
    local service=$1
    echo -e "${BLUE}Showing logs for $service container...${NC}"
    echo -e "${YELLOW}Press Ctrl+C to stop watching logs${NC}"
    echo "----------------------------------------"
    docker-compose logs -f "$service"
}

# Show logs for both services
show_all_logs() {
    echo -e "${BLUE}Showing logs for both frontend and backend containers...${NC}"
    echo -e "${YELLOW}Press Ctrl+C to stop watching logs${NC}"
    echo "----------------------------------------"
    docker-compose logs -f frontend backend
}

# Main script logic
main() {
    local service=${1:-all}
    
    case $service in
        "frontend"|"front")
            check_containers
            show_logs "frontend"
            ;;
        "backend"|"back")
            check_containers
            show_logs "backend"
            ;;
        "all"|"--help"|"-h")
            if [[ "$service" == "--help" || "$service" == "-h" ]]; then
                show_usage
                exit 0
            fi
            check_containers
            show_all_logs
            ;;
        *)
            echo -e "${RED}Unknown service: $service${NC}"
            show_usage
            exit 1
            ;;
    esac
}

main "$@"