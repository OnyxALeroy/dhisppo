# D'hisppo

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
- MongoDB URL: `mongodb://root:password@localhost:27017/dhisppo_db?authSource=admin`
- Default admin user will be created on first startup

## API Documentation
Once running, visit http://localhost:8000/docs for interactive API documentation.

## Roadmap

* [ ] Adding visibility to events: private event can't be joined except if invited by an admin or any of the event organizers ; public is joinable by anyone, and findable in the Event screen.
* [ ] Updating the User page, and **make (public) events joinable**
* [ ] Double-checking the different menu / filters values
