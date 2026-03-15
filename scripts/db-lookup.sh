#!/bin/bash

# Database Lookup Script for D'hisppo
# This script allows you to query and lookup data in the MongoDB database

set -e

# Load environment variables from .env file
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

if [[ -f "$PROJECT_DIR/.env" ]]; then
    set -a
    source "$PROJECT_DIR/.env"
    set +a
fi

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values (fallback if .env is not loaded)
DB_HOST="${MONGO_HOST:-localhost}"
DB_PORT="${MONGO_PORT:-27017}"
DB_NAME="${MONGO_DB:-dhisppo_db}"
DB_USER="${MONGO_USER:-root}"
DB_PASS="${MONGO_PASS:-password}"

# Function to show usage
show_usage() {
    echo -e "${BLUE}Usage: $0 [collection] [query] [options]${NC}"
    echo ""
    echo -e "${GREEN}Collections:${NC}"
    echo "  users        Query the users collection"
    echo "  resolutions  Query the resolutions collection"
    echo "  all          Show all collections (default)"
    echo ""
    echo -e "${GREEN}Query Examples:${NC}"
    echo "  '$0 users {}'                    Show all users"
    echo "  '$0 users \"{username: admin}\"' Find user with username 'admin'"
    echo "  '$0 resolutions \"{user_id: ...}\"' Find resolutions by user_id"
    echo ""
    echo -e "${GREEN}Options:${NC}"
    echo "  -h, --host     MongoDB host (default: localhost)"
    echo "  -p, --port     MongoDB port (default: 27017)"
    echo "  -d, --database Database name (default: dhisppo_db)"
    echo "  -u, --user     Database user (default: root)"
    echo "  -w, --pass     Database password (default: password)"
    echo "  --help         Show this help message"
    echo ""
    echo -e "${GREEN}Examples:${NC}"
    echo "  $0"
    echo "  $0 users"
    echo "  $0 users '{\"username\": \"admin\"}'"
    echo "  $0 resolutions '{\"user_id\": \"123\"}'"
}

# Function to check if MongoDB is running
check_mongodb() {
    if ! docker ps | grep -q "dhisppo-mongodb"; then
        echo -e "${RED}MongoDB container is not running. Please run './scripts/start.sh' first.${NC}"
        exit 1
    fi
}

# Function to show all collections
show_all_collections() {
    echo -e "${BLUE}Showing all collections in database...${NC}"
    echo "----------------------------------------"
    
    docker exec dhisppo-mongodb mongosh \
        --host "$DB_HOST:$DB_PORT" \
        -u "$DB_USER" \
        -p "$DB_PASS" \
        --authenticationDatabase admin \
        "$DB_NAME" \
        --eval "
        show collections;
        "
}

# Function to query a specific collection
query_collection() {
    local collection=$1
    local query=$2
    
    echo -e "${BLUE}Querying '$collection' collection...${NC}"
    echo -e "${YELLOW}Query: $query${NC}"
    echo "----------------------------------------"
    
    docker exec dhisppo-mongodb mongosh \
        --host "$DB_HOST:$DB_PORT" \
        -u "$DB_USER" \
        -p "$DB_PASS" \
        --authenticationDatabase admin \
        "$DB_NAME" \
        --eval "
        db.$collection.find($query).pretty();
        "
}

# Function to show collection stats
show_collection_stats() {
    local collection=$1
    
    echo -e "${BLUE}Statistics for '$collection' collection...${NC}"
    echo "----------------------------------------"
    
    docker exec dhisppo-mongodb mongosh \
        --host "$DB_HOST:$DB_PORT" \
        -u "$DB_USER" \
        -p "$DB_PASS" \
        --authenticationDatabase admin \
        "$DB_NAME" \
        --eval "
        print('Document count: ' + db.$collection.countDocuments());
        print('Collection size: ' + db.$collection.stats().size + ' bytes');
        print('Index count: ' + db.$collection.getIndexes().length);
        "
}

# Main script logic
main() {
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--host)
                DB_HOST="$2"
                shift 2
                ;;
            -p|--port)
                DB_PORT="$2"
                shift 2
                ;;
            -d|--database)
                DB_NAME="$2"
                shift 2
                ;;
            -u|--user)
                DB_USER="$2"
                shift 2
                ;;
            -w|--pass)
                DB_PASS="$2"
                shift 2
                ;;
            --help)
                show_usage
                exit 0
                ;;
            *)
                break
                ;;
        esac
    done
    
    local collection=${1:-all}
    local query=${2:-"{}"}
    
    case $collection in
        "users"|"user")
            check_mongodb
            query_collection "users" "$query"
            show_collection_stats "users"
            ;;
        "resolutions"|"resolution")
            check_mongodb
            query_collection "resolutions" "$query"
            show_collection_stats "resolutions"
            ;;
        "all"|"--help"|"-h")
            if [[ "$collection" == "--help" || "$collection" == "-h" ]]; then
                show_usage
                exit 0
            fi
            check_mongodb
            show_all_collections
            ;;
        *)
            echo -e "${RED}Unknown collection: $collection${NC}"
            echo -e "${YELLOW}Available collections: users, resolutions${NC}"
            show_usage
            exit 1
            ;;
    esac
}

main "$@"