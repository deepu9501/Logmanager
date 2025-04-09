# Server Log Management System for E-Governance

A comprehensive Django-based server log management system designed for e-governance platforms to ensure real-time event logging, automated content-based classification, and instant notifications for critical events.

## Key Features

- Real-time event logging
- Automated content-based classification of logs
- Instant notifications for critical events
- Secure storage with encryption
- Advanced search and filtering capabilities
- Visual dashboards for log analysis
- Role-based access control
- AICTE compliance

## Installation

1. Clone this repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Configure database settings in `logmanager/settings.py`
6. Run migrations: `python manage.py migrate`
7. Start the development server: `python manage.py runserver`

## Requirements

- Python 3.8 or higher
- PostgreSQL (recommended) or SQLite
- Django 4.x 