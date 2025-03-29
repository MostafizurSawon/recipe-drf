# Recipe Hub
## Live (Frontend): [Recipe Hub](https://recipe-hubb.netlify.app/)

![Recipe Hub Banner](https://img.freepik.com/free-photo/chicken-stir-fried-chili-along-with-bell-pepper-tomatoes-carrots_1150-27216.jpg)

Welcome to **Recipe Hub**, a recipe-sharing platform where users can create, share, and discover delicious recipes! This project is built with **Django REST Framework (DRF)** for the backend and is designed to work with modern frontend frameworks like React, Vue, or Angular. Users can register, manage their profiles, post recipes, add reviews, comments, and reactions, and even request role changes (e.g., to become a Chef).

## Table of Contents
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Clone the Repository](#clone-the-repository)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Environment Variables](#environment-variables)
  - [Running the Project](#running-the-project)
- [API Documentation](#api-documentation)
- [Suggestions for Improvement](#suggestions-for-improvement)
- [Contributing](#contributing)
- [License](#license)

## Features
### **User Management**
- Register and verify email.
- Login with JWT authentication.
- Manage user profiles (update details, upload profile image).
- Role-based access (User, Chef, Admin).
- Request role changes (e.g., from User to Chef).

### **Recipe Management**
- Create, update, and delete recipes.
- Categorize recipes.
- Like, save, and comment on recipes.
- Add reviews with ratings.
- Filter recipes by category or search terms.

### **Contact Us**
- Submit contact form messages.
- Admins can view all messages.

### **API Documentation**
- Interactive Swagger UI for exploring endpoints.
- Detailed API documentation in this README for frontend developers.

## Tech Stack
- **Backend**: Django, Django REST Framework (DRF)
- **Database**: SQLite (default; can be switched to PostgreSQL for production)
- **Authentication**: JWT (JSON Web Token) via `rest_framework_simplejwt`
- **API Documentation**: Swagger UI via `drf-yasg`
- **Email**: SMTP (configured for Gmail)
- **CORS**: Enabled for frontend integration

## Project Structure
```
recipe-hub/
├── recipe_config/        # Main Django project settings
│   ├── settings.py       # Project settings (database, email, etc.)
│   ├── urls.py           # Root URL configurations
│   ├── wsgi.py           # WSGI entry point for deployment
├── users/               # App for user management
│   ├── models.py         # User and UserProfile models
│   ├── views.py          # User authentication and management views
├── recipe/              # App for recipe management
│   ├── models.py         # Recipe, Category, Review, Comment, Reaction models
│   ├── views.py          # Views for recipe operations
├── contact_us/          # App for contact form submissions
│   ├── models.py         # ContactUs model
│   ├── views.py          # Contact form views
├── media/               # Directory for uploaded files (e.g., profile images)
├── static/              # Directory for static files (e.g., CSS, JS)
├── templates/           # Directory for custom templates (e.g., 404 page)
├── manage.py            # Django management script
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation
```

## Getting Started

### **Clone the Repository**
To get a copy of this project on your local machine, follow these steps:

```bash
git clone https://github.com/MostafizurSawon/recipe-drf.git
cd recipe-hub
```

### **Prerequisites**
Before setting up the project, ensure you have the following installed:
- **Python**: Version 3.8 or higher
- **pip**: Python package manager
- **Git**: For cloning the repository
- **A Gmail Account**: For sending emails (e.g., email verification, OTP)

### **Installation**
1. **Create a Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Apply Migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

4. **Create a Superuser (Optional, for admin access)**
```bash
python manage.py createsuperuser
```
Follow the prompts to create an admin user.

### **Environment Variables**
The project uses environment variables for sensitive settings. Create a `.env` file in the project root and add:
```ini
EMAIL=your-email@gmail.com
EMAIL_PASSWORD=your-app-specific-password
```
To generate an app-specific password:
- Go to your Google Account settings.
- Enable **2-Step Verification** if not already enabled.
- Navigate to "Security" > "App passwords" > Generate a new app password for "Mail".

### **Running the Project**
Start the Development Server:
```bash
python manage.py runserver
```

The server will start at `http://127.0.0.1:8000/`.

## API Documentation

### **Base URL**
- **Local Development**: `http://127.0.0.1:8000/`
- **Production**: `https://recipe-drf.onrender.com/`

### **Swagger UI**
- **Local**: [http://127.0.0.1:8000/swagger/](http://127.0.0.1:8000/swagger/)
- **Production**: [https://recipe-drf.onrender.com/swagger/](https://recipe-drf.onrender.com/swagger/)

### **Authentication**
The API uses **JWT authentication** for protected endpoints.
- Login to obtain a token using `/accounts/login/`
- Include the token in the `Authorization` header:
```http
Authorization: Bearer <your_token>
```

### **Example: Register a User**
#### Request:
```http
POST /accounts/register/
Content-Type: application/json
```
```json
{
  "email": "newuser@example.com",
  "firstName": "John",
  "lastName": "Doe",
  "password": "password123",
  "mobile": "1234567890"
}
```
#### Response (201 Created):
```json
{
  "status": "success",
  "message": "User Registration Successful. Please check your email to verify your account."
}
```

## Suggestions for Improvement
- **Switch to PostgreSQL for production**:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'recipehub',
        'USER': 'youruser',
        'PASSWORD': 'yourpassword',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```
- **Implement rate limiting** to prevent abuse.
- **Enhance email templates** for better branding and UX.

## Contributing
Contributions are welcome! Feel free to open issues or submit pull requests.

## License
This project is licensed under the **MIT License**.

