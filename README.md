# Image Background Remover

A web application that allows users to remove backgrounds from images using AI technology. Built with Flask, SQLite, and Tailwind CSS.

## Features

- User authentication (register/login)
- Image upload with drag-and-drop support
- AI-powered background removal
- Image management dashboard
- Download processed images
- Responsive design

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Image-Background-Remover
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

4. Create the necessary directories:
```bash
mkdir -p static/uploads
```

## Running the Application

1. Make sure your virtual environment is activated
2. Run the Flask application:
```bash
python app.py
```
3. Open your web browser and navigate to `http://localhost:5000`

## Usage

1. Register a new account or login with existing credentials
2. Upload an image using the dashboard
3. Wait for the background removal process to complete
4. Download the processed image with transparent background

## Technologies Used

- Flask - Web framework
- SQLite - Database
- Flask-SQLAlchemy - Database ORM
- Flask-Login - User authentication
- rembg - Background removal library
- Tailwind CSS - Styling
- Font Awesome - Icons

## License

This project is licensed under the MIT License - see the LICENSE file for details.