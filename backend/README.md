# SiteBuilt Backend

A FastAPI-based backend service for the SiteBuilt application, providing RESTful APIs for managing construction site projects, plans, photos, placements, reviews, GPS data, detections, exports, user profiles, and reports.

## Features

- **Projects Management**: Create and manage construction projects
- **Plans**: Handle project plans and blueprints
- **Photos**: Upload and manage site photos
- **Placements**: Manage equipment or material placements
- **Review**: Review and approval workflows
- **GPS**: GPS data handling for site locations
- **Detections**: Object or anomaly detection features
- **Export**: Data export functionality
- **Profile**: User profile management
- **Reports**: Generate and manage reports

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Migrations**: Alembic
- **Storage**: Supabase
- **Monitoring**: Sentry
- **Testing**: pytest
- **Deployment**: Render

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd sitebuilt/backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file in the root directory with the following variables:
   ```
   ENV=development
   DATABASE_URL=postgresql://user:password@localhost:5432/sitebuilt
   SUPABASE_URL=your-supabase-url
   SUPABASE_ANON_KEY=your-supabase-anon-key
   SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key
   SENTRY_DSN=your-sentry-dsn
   ```

## Running the Application

1. Run database migrations:
   ```bash
   alembic upgrade head
   ```

2. Start the development server:
   ```bash
   uvicorn app.main:app --reload
   ```

3. Access the API documentation at `http://localhost:8000/docs`

## API Endpoints

The API provides the following main endpoints:

- `/` - Root endpoint
- `/health` - Health check
- `/docs` - Interactive API documentation (Swagger UI)
- `/openapi.json` - OpenAPI schema

Additional endpoints are available through the included routers for projects, plans, photos, etc.

## Testing

Run tests with pytest:
```bash
pytest
```

## Deployment

This application is configured for deployment on Render. See `render.yaml` for deployment configuration.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

[Add license information here]