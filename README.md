# Task Management System

A modern task management system built with Flask and modern UI technologies. The application supports Arabic language interface and provides a beautiful, responsive design with advanced features.

## Features

- Task creation, editing, and deletion
- Task prioritization
- Task completion tracking
- Task filtering and sorting
- Tag system
- Statistics dashboard
- Responsive design
- Arabic language interface
- Modern UI with animations

## Local Development

1. Clone the repository:
```bash
git clone <your-repo-url>
cd task-management-system
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Deployment

This application is configured for deployment on Render.com:

1. Fork/push this repository to GitHub
2. Create a new Web Service on Render
3. Connect your GitHub repository
4. Render will automatically detect the configuration and deploy the application

### Environment Variables

- `PORT`: Set by Render automatically
- `FLASK_ENV`: Set to 'production' for deployment

## Technologies Used

- Backend: Flask (Python)
- Frontend: HTML5, CSS3, JavaScript
- UI Framework: Custom CSS with modern features
- Icons: Font Awesome
- Notifications: Toastify

## License

MIT License 