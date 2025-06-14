# PM Users API

![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![Flask](https://img.shields.io/badge/flask-%3E=2.0-green.svg)
![License](https://img.shields.io/badge/license-AGPLv3-blue.svg)
![CI](https://img.shields.io/github/actions/workflow/status/bengeek06/pm-users-api/ci.yml?branch=main)
![Coverage](https://img.shields.io/badge/coverage-pytest-yellow.svg)
![Docker](https://img.shields.io/badge/docker-ready-blue.svg)

A production-ready RESTful API for user management, built with Flask.  
This project provides a solid foundation for user CRUD operations, authentication, configuration, import/export, and more.  
It is designed for extensibility, security, and easy deployment in modern environments.

---

## Features

- **User Management**: Full CRUD for users with company and role associations.
- **Authentication**: Internal endpoint for password verification, ready for integration with an authentication service.
- **Environment-based Configuration**: Easily switch between development, testing, staging, and production.
- **OpenAPI 3.0 Documentation**: See [`openapi.yml`](openapi.yml) for the full API specification.
- **Docker-ready**: Includes a `Dockerfile` and healthcheck script.
- **Database Migrations**: Managed with Alembic/Flask-Migrate.
- **Testing**: Pytest-based test suite.
- **Logging**: Structured logging for all environments.
- **Import/Export**: Endpoints for CSV and JSON import/export.

---

## Environments

The application behavior is controlled by the `FLASK_ENV` environment variable.  
Depending on its value, different configuration classes and `.env` files are loaded:

- **development** (default):  
  Loads `.env.development` and uses `app.config.DevelopmentConfig`.  
  Debug mode is enabled.

- **testing**:  
  Loads `.env.test` and uses `app.config.TestingConfig`.  
  Testing mode is enabled.

- **staging**:  
  Loads `.env.staging` and uses `app.config.StagingConfig`.  
  Debug mode is enabled.

- **production**:  
  Loads `.env.production` and uses `app.config.ProductionConfig`.  
  Debug mode is disabled.

See `app/config.py` for details.  
You can use `env.example` as a template for your environment files.

---

## API Endpoints

| Method | Path                 | Description                        |
|--------|----------------------|------------------------------------|
| GET    | /version             | Get API version                    |
| GET    | /config              | Get current app configuration      |
| GET    | /users               | List all users                     |
| POST   | /users               | Create a new user                  |
| GET    | /users/{id}          | Get a user by ID                   |
| PUT    | /users/{id}          | Replace a user by ID               |
| PATCH  | /users/{id}          | Partially update a user by ID      |
| DELETE | /users/{id}          | Delete a user by ID                |
| POST   | /users/verify_password | Verify user password (internal)   |
| GET    | /export/csv          | Export all users as CSV            |
| POST   | /import/csv          | Import users from a CSV file       |
| POST   | /import/json         | Import users from a JSON file      |

See [`openapi.yml`](openapi.yml) for full documentation and schema details.

---

## Project Structure

```
.
├── app
│   ├── config.py
│   ├── __init__.py
│   ├── logger.py
│   ├── models.py
│   ├── resources
│   │   ├── config.py
│   │   ├── export_to.py
│   │   ├── import_from.py
│   │   ├── __init__.py
│   │   ├── users.py
│   │   ├── verify.py
│   │   └── version.py
│   ├── routes.py
│   ├── schemas.py
│   └── utils.py
├── CODE_OF_CONDUCT.md
├── COMMERCIAL-LICENCE.txt
├── Dockerfile
├── env.example
├── LICENCE.md
├── LICENSE
├── openapi.yml
├── pytest.ini
├── README.md
├── requirements-dev.txt
├── requirements.txt
├── run.py
├── tests
│   ├── conftest.py
│   ├── __init__.py
│   ├── test_api.py
│   ├── test_config.py
│   ├── test_export_to.py
│   ├── test_import_from.py
│   ├── test_init.py
│   ├── test_run.py
│   ├── test_version.py
│   └── test_wsgi.py
├── wait-for-it.sh
└── wsgi.py
```

---
## Usage

### Local Development

1. Copy `env.example` to `.env.development` and set your variables.
2. Install dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```
3. Run database migrations:
   ```bash
   flask db upgrade
   ```bash
4. Start the server:
   ```bash
   FLASK_ENV=development python run.py
   ```

### Docker

Build and run the container:
```bash
docker build -t pm-users-api .
docker run --env-file .env.development -p 5000:5000 pm-users-api
```

### Testing

Run all tests with:
```bash
pytest
```

---

## License

This project is licensed under the GNU AGPLv3.  
See [LICENSE](LICENSE) and [COMMERCIAL-LICENCE.txt](COMMERCIAL-LICENCE.txt) for details.

---

## Code of Conduct

See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
