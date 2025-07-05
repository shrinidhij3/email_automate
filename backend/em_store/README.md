# Email Management System - Backend

This is the Django backend for the Email Management System.

## Prerequisites

- Python 3.11+
- PostgreSQL
- Node.js 16+ (for frontend)
- pip

## Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd n8n/backend/em_store
   ```

2. **Set up a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the `em_store` directory with the following variables:
   ```
   DEBUG=True
   SECRET_KEY=your-secret-key
   DB_NAME=em_store
   DB_USER=postgres
   DB_PASSWORD=postgres
   DB_HOST=localhost
   DB_PORT=5432
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

## Deployment to Render

### Prerequisites

- A Render.com account
- A PostgreSQL database on Render
- Your code pushed to a Git repository

### Steps

1. **Prepare your repository**
   - Make sure all changes are committed and pushed to your Git repository

2. **Create a new Web Service on Render**
   - Go to your Render dashboard
   - Click "New" and select "Web Service"
   - Connect your GitHub/GitLab repository

3. **Configure the Web Service**
   - Name: `em-store-backend`
   - Region: Choose the one closest to your users
   - Branch: `main` (or your production branch)
   - Build Command: `pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput`
   - Start Command: `gunicorn em_store.wsgi:application`

4. **Set up environment variables**
   Add these environment variables in the Render dashboard:
   ```
   PYTHON_VERSION=3.11.0
   DJANGO_SETTINGS_MODULE=em_store.production_settings
   DJANGO_PRODUCTION=true
   DJANGO_SECRET_KEY=your-secret-key
   ```
   
   For the database, use the internal database URL provided by Render:
   ```
   DATABASE_URL=postgresql://user:password@host:port/dbname
   ```

5. **Deploy**
   - Click "Create Web Service"
   - Render will build and deploy your application

## Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DEBUG` | Enable debug mode | No | `False` in production |
| `SECRET_KEY` | Django secret key | Yes | - |
| `DB_NAME` | Database name | Yes | - |
| `DB_USER` | Database user | Yes | - |
| `DB_PASSWORD` | Database password | Yes | - |
| `DB_HOST` | Database host | Yes | - |
| `DB_PORT` | Database port | No | `5432` |
| `EMAIL_HOST` | SMTP server | No | - |
| `EMAIL_PORT` | SMTP port | No | `587` |
| `EMAIL_HOST_USER` | SMTP username | No | - |
| `EMAIL_HOST_PASSWORD` | SMTP password | No | - |
| `DEFAULT_FROM_EMAIL` | Default sender email | No | `noreply@yourdomain.com` |

## Project Structure

```
backend/
├── em_store/               # Main project directory
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py         # Development settings
│   ├── production_settings.py  # Production settings
│   ├── urls.py
│   └── wsgi.py
├── accounts/               # User accounts app
├── api/                    # API endpoints
├── campaigns/              # Email campaigns
├── email_entry/            # Email management
├── manage.py
├── requirements.txt
├── runtime.txt
└── static/                 # Static files
```

## API Documentation

API documentation is available at `/api/docs/` when running in development mode.

## License

[Your License Here]
