# New Year's Event Organization App

A web application for organizing New Year's events with user authentication and role-based access control.

## Architecture

- **Backend**: FastAPI with Pydantic and MongoDB
- **Frontend**: Vue 3 with TypeScript and Vite
- **Database**: MongoDB
- **Deployment**: Docker containers with docker-compose

## Features

- User registration and authentication
- Role-based access control (Unauthenticated, User, Admin)
- Event management capabilities (to be expanded)

## Quick Start

```bash
# Clone and start all services
docker-compose up --build

# The application will be available at:
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# MongoDB: localhost:27017
```

## Development

### Backend Development
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

### Database Access
- MongoDB URL: `mongodb://root:password@localhost:27017/newyears_db?authSource=admin`
- Default admin user will be created on first startup

## API Documentation
Once running, visit http://localhost:8000/docs for interactive API documentation.

## Roadmap

[ ] Création d'Event : visibilité (public / privé):
  - un organisateur peut tjs ajouter quelqu'un
  - seuls les events publics peuvent être vu par les users normaux
[ ] Update la page utilisateurs
[ ] Faire des fix sur les différents menus et filtres
