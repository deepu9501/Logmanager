# Logmanager

A modern and powerful server log management system built with Django, featuring real-time monitoring, analytics, and notifications.

## Features

- **Real-time Log Monitoring**: Monitor server logs in real-time with WebSocket support
- **Advanced Analytics**: Visualize log data with interactive charts and statistics
- **Smart Classification**: ML-based log classification for better organization
- **Instant Notifications**: Get notified about important events through multiple channels
- **Modern UI/UX**: Beautiful and responsive interface built with Bootstrap 5
- **Search & Filter**: Powerful search and filtering capabilities
- **API Support**: RESTful API for integration with other systems

## Tech Stack

- **Backend**: Django 4.2
- **Frontend**: Bootstrap 5, Chart.js
- **Database**: PostgreSQL
- **Real-time**: Django Channels (WebSocket)
- **Task Queue**: Celery with Redis
- **ML**: scikit-learn for log classification

## Prerequisites

- Python 3.8 or higher
- PostgreSQL
- Redis
- Node.js (for static file compilation)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/logmanager.git
cd logmanager
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up the database:
```bash
python manage.py migrate
```

5. Create a superuser:
```bash
python manage.py createsuperuser
```

6. Collect static files:
```bash
python manage.py collectstatic
```

7. Start Redis server (required for WebSocket and Celery)

8. Start Celery worker:
```bash
celery -A logmanager worker -l info
```

9. Run the development server:
```bash
python manage.py runserver
```

## Project Structure

```
logmanager/
├── apps/
│   ├── users/          # User management
│   ├── logs/           # Log management
│   ├── classification/ # ML-based classification
│   ├── notifications/  # Notification system
│   └── dashboard/      # Analytics dashboard
├── static/            # Static files
├── templates/         # HTML templates
├── media/            # User-uploaded files
└── logs/             # Application logs
```

## API Documentation

The API documentation is available at `/api/docs/` when running the server.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Django](https://www.djangoproject.com/)
- [Bootstrap](https://getbootstrap.com/)
- [Chart.js](https://www.chartjs.org/)
- [Celery](https://docs.celeryproject.org/)
- [Redis](https://redis.io/)
- [scikit-learn](https://scikit-learn.org/)

## Support

For support, email support@logmanager.com or create an issue in the repository. 
