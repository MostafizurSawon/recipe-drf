# Recipe Hub
## Live(Frontend): https://recipe-hubb.netlify.app/
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
  - [Base URL](#base-url)
  - [Swagger UI](#swagger-ui)
  - [Authentication](#authentication)
  - [API Endpoints](#api-endpoints)
    - [User Management (`/accounts/`)](#user-management-accounts)
    - [Recipe Management (`/recipes/`)](#recipe-management-recipes)
    - [Contact Us (`/contact/`)](#contact-us-contact)
  - [Error Handling](#error-handling)
  - [Frontend Integration Tips](#frontend-integration-tips)
- [Suggestions for Improvement](#suggestions-for-improvement)
- [Contributing](#contributing)
- [License](#license)

## Features
- **User Management**:
  - Register and verify email.
  - Login with JWT authentication.
  - Manage user profiles (update details, upload profile image).
  - Role-based access (User, Chef, Admin).
  - Request role changes (e.g., from User to Chef).
- **Recipe Management**:
  - Create, update, and delete recipes.
  - Categorize recipes.
  - Like, save, and comment on recipes.
  - Add reviews with ratings.
  - Filter recipes by category or search terms.
- **Contact Us**:
  - Submit contact form messages.
  - Admins can view all messages.
- **API Documentation**:
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
Here’s an overview of the project’s directory structure:
recipe-hub/
├── recipe_config/        # Main Django project settings
│   ├── init.py
│   ├── settings.py       # Project settings (database, email, etc.)
│   ├── urls.py           # Root URL configurations
│   ├── views.py          # Custom views (e.g., 404 handler)
│   └── wsgi.py           # WSGI entry point for deployment
├── users/               # App for user management
│   ├── migrations/       # Database migrations for the users app
│   ├── init.py
│   ├── admin.py          # Admin panel configurations
│   ├── models.py         # User and UserProfile models
│   ├── permissions.py    # Role-based permission logic
│   ├── serializers.py    # Serializers for user-related data
│   ├── signals.py        # Signal to create UserProfile on user creation
│   ├── urls.py           # URL patterns for user endpoints
│   └── views.py          # Views for user management (register, login, etc.)
├── recipe/              # App for recipe management
│   ├── migrations/       # Database migrations for the recipe app
│   ├── init.py
│   ├── admin.py          # Admin panel configurations
│   ├── models.py         # Recipe, Category, Review, Comment, Reaction models
│   ├── serializers.py    # Serializers for recipe-related data
│   ├── urls.py           # URL patterns for recipe endpoints
│   └── views.py          # Views for recipe management (list, create, like, etc.)
├── contact_us/          # App for contact form submissions
│   ├── migrations/       # Database migrations for the contact_us app
│   ├── init.py
│   ├── admin.py          # Admin panel configurations
│   ├── models.py         # ContactUs model
│   ├── serializers.py    # Serializer for contact form data
│   ├── urls.py           # URL patterns for contact endpoints
│   └── views.py          # Views for contact form submissions
├── media/               # Directory for uploaded files (e.g., profile images)
├── static/              # Directory for static files (e.g., CSS, JS)
├── templates/           # Directory for custom templates (e.g., 404 page)
├── manage.py            # Django management script
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation (this file)


## Getting Started

### Clone the Repository
To get a copy of this project on your local machine, follow these steps:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/MostafizurSawon/recipe-drf.git
   cd recipe-hub

2. **Create a Virtual Environment**:
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate

** Prerequisites **
  Before setting up the project, ensure you have the following installed:

  Python: Version 3.8 or higher
  pip: Python package manager
  Git: For cloning the repository
  A Gmail Account: For sending emails (e.g., email verification, OTP)

### Installation
1. Install Dependencies:
The project dependencies are listed in requirements.txt. Install them using pip:
  pip install -r requirements.txt

2. Apply Migrations:
Set up the database by running migrations:
  python manage.py makemigrations
  python manage.py migrate

3. Create a Superuser (optional, for admin access):
  python manage.py createsuperuser
  Follow the prompts to create an admin user. You can use this to access the Django admin panel at /admin/.

4. Environment Variables:
  The project uses environment variables for sensitive settings (e.g., email credentials). Create a .env file in the project root and add the following:
    #.env
    EMAIL=your-email@gmail.com
    EMAIL_PASSWORD=your-app-specific-password

  EMAIL: Your Gmail address for sending emails.
  EMAIL_PASSWORD: An app-specific password for Gmail (not your regular password). To generate this:
  Go to your Google Account settings.
  Enable 2-Step Verification if not already enabled.
  Go to "Security" > "App passwords" > Generate a new app password for "Mail".
  Copy the generated password and use it here.

Running the Project
Start the Development Server:
bash

Collapse

Wrap

Copy
python manage.py runserver
The server will start at http://127.0.0.1:8000/.
Access Key Endpoints:
Swagger UI: http://127.0.0.1:8000/swagger/ (interactive API documentation)
API Root: http://127.0.0.1:8000/ (redirects to Swagger UI)
Admin Panel: http://127.0.0.1:8000/admin/ (login with superuser credentials)
User Endpoints: http://127.0.0.1:8000/accounts/
Recipe Endpoints: http://127.0.0.1:8000/recipes/
API Documentation
Base URL
The base URL for the API depends on the environment:

Local Development: http://127.0.0.1:8000/
Production: https://recipe-drf.onrender.com/
All endpoints are relative to this base URL.

Swagger UI
For an interactive API explorer, visit the Swagger UI:

Local: http://127.0.0.1:8000/swagger/
Production: https://recipe-drf.onrender.com/swagger/
The Swagger UI provides detailed documentation, including request/response schemas, and allows you to test endpoints directly.

Authentication
The API uses JWT (JSON Web Token) authentication for protected endpoints. To authenticate:

Login to obtain a token using the /accounts/login/ endpoint.
Include the token in the Authorization header of your requests:
text

Collapse

Wrap

Copy
Authorization: Bearer <your_token>
Some endpoints (e.g., /accounts/register/, /recipes/lists/) are publicly accessible without authentication, but most require a valid token.

Example: Obtaining a Token
Request:

bash

Collapse

Wrap

Copy
POST /accounts/login/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "yourpassword"
}
Response (200 OK):

json

Collapse

Wrap

Copy
{
  "status": "success",
  "message": "User Login Successful",
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
Use the token in subsequent requests by adding it to the Authorization header.

API Endpoints
User Management (/accounts/)
These endpoints handle user registration, authentication, profile management, and role changes.

Endpoint	Method	Description	Authentication Required	Role Restrictions
/accounts/register/	POST	Register a new user	No	None
/accounts/login/	POST	Login and get a JWT token	No	None
/accounts/activate/<uidb64>/<token>/	GET	Activate a user’s email	No	None
/accounts/resend-verification/	POST	Resend email verification link	No	None
/accounts/send-otp/	POST	Send OTP for password reset	No	None
/accounts/verify-otp/	POST	Verify OTP and get a token	No	None
/accounts/reset-password/	POST	Reset password (after OTP)	Yes	None
/accounts/validate-password/	POST	Validate email and password	No	None
/accounts/profile/	GET	Get the authenticated user’s profile	Yes	None
/accounts/profile/update/	PUT	Update the authenticated user’s profile	Yes	None
/accounts/role-change-request/	POST	Request a role change (e.g., to Chef)	Yes	None
/accounts/profile/all/	GET	List all users	Yes	Admin only
/accounts/profile/<email>/	GET	Get a specific user’s profile	Yes	None
/accounts/profile/<email>/update-role/	PUT	Update a user’s role	Yes	Admin only
Example: Register a User
Request:

bash

Collapse

Wrap

Copy
POST /accounts/register/
Content-Type: application/json

{
  "email": "newuser@example.com",
  "firstName": "John",
  "lastName": "Doe",
  "password": "password123",
  "mobile": "1234567890"
}
Response (201 Created):

json

Collapse

Wrap

Copy
{
  "status": "success",
  "message": "User Registration Successful. Please check your email to verify your account."
}
Example: Get User Profile
Request:

bash

Collapse

Wrap

Copy
GET /accounts/profile/
Authorization: Bearer <your_token>
Response (200 OK):

json

Collapse

Wrap

Copy
{
  "status": "success",
  "message": "Request Successful",
  "data": {
    "email": "user@example.com",
    "firstName": "John",
    "lastName": "Doe",
    "mobile": "1234567890",
    "role": "User",
    "profile": {
      "image": null,
      "age": 18,
      "portfolio": null,
      "sex": "Male",
      "bio": "",
      "facebook": null,
      "user": {
        "email": "user@example.com",
        "firstName": "John",
        "lastName": "Doe",
        "role": "User"
      }
    }
  }
}
Recipe Management (/recipes/)
These endpoints handle recipes, categories, reviews, comments, and reactions.

Endpoint	Method	Description	Authentication Required	Role Restrictions
/recipes/lists/	GET	List all recipes	No	None
/recipes/lists/	POST	Create a new recipe	Yes	None
/recipes/lists/<pk>/	GET	Get a specific recipe	No	None
/recipes/lists/<pk>/	PUT	Update a specific recipe	Yes	Owner or Admin
/recipes/lists/<pk>/	DELETE	Delete a specific recipe	Yes	Owner or Admin
/recipes/lists/<pk>/like/	POST	Like or react to a recipe	Yes	None
/recipes/lists/<pk>/save/	POST	Save or unsave a recipe	Yes	None
/recipes/lists/most_liked/	GET	Get the top 5 most-liked recipes	No	None
/recipes/categories/	GET	List all categories	No	None
/recipes/categories/	POST	Create a new category	Yes	Admin only
/recipes/reviews/	GET	List all reviews	No	None
/recipes/reviews/	POST	Create a new review	Yes	User, Chef, or Admin
/recipes/comments/	GET	List all comments	No	None
/recipes/comments/	POST	Create a new comment	Yes	User, Chef, or Admin
/recipes/lists/<recipe_pk>/comments/	GET	List comments for a specific recipe	No	None
/recipes/lists/<recipe_pk>/comments/	POST	Create a comment for a specific recipe	Yes	User, Chef, or Admin
/recipes/reactions/	GET	List all reactions	No	None
/recipes/reactions/	POST	Create a new reaction	Yes	User, Chef, or Admin
/recipes/by-user/<email>/	GET	Get recipes by a specific user	Yes	Admin only
Example: List Recipes
Request:

bash

Collapse

Wrap

Copy
GET /recipes/lists/
Response (200 OK):

json

Collapse

Wrap

Copy
[
  {
    "id": 1,
    "title": "Chocolate Cake",
    "ingredients": "Flour, sugar, cocoa powder",
    "instructions": "Mix ingredients and bake at 350°F for 30 minutes.",
    "created_on": "2025-03-29",
    "category": [1],
    "category_names": ["Dessert"],
    "img": null,
    "user": {
      "id": 1,
      "email": "user@example.com",
      "firstName": "John",
      "lastName": "Doe",
      "role": "User"
    },
    "comments": [],
    "reaction_counts": {
      "LIKE": 0,
      "WOW": 0,
      "SAD": 0,
      "LOVE": 0,
      "total": 0
    },
    "user_reaction": null,
    "is_liked_by_user": false,
    "is_saved_by_user": false
  }
]
Example: Create a Recipe
Request:

bash

Collapse

Wrap

Copy
POST /recipes/lists/
Authorization: Bearer <your_token>
Content-Type: application/json

{
  "title": "Vanilla Ice Cream",
  "ingredients": "Cream, sugar, vanilla extract",
  "instructions": "Mix ingredients and freeze for 4 hours.",
  "category_ids": [1],
  "img": "https://example.com/icecream.jpg"
}
Response (201 Created):

json

Collapse

Wrap

Copy
{
  "id": 2,
  "title": "Vanilla Ice Cream",
  "ingredients": "Cream, sugar, vanilla extract",
  "instructions": "Mix ingredients and freeze for 4 hours.",
  "created_on": "2025-03-29",
  "category": [1],
  "category_names": ["Dessert"],
  "img": "https://example.com/icecream.jpg",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "firstName": "John",
    "lastName": "Doe",
    "role": "User"
  },
  "comments": [],
  "reaction_counts": {
    "LIKE": 0,
    "WOW": 0,
    "SAD": 0,
    "LOVE": 0,
    "total": 0
  },
  "user_reaction": null,
  "is_liked_by_user": false,
  "is_saved_by_user": false
}
Contact Us (/contact/)
These endpoints handle contact form submissions.

Endpoint	Method	Description	Authentication Required	Role Restrictions
/contact/	POST	Submit a contact form message	No	None
/contact/messages/	GET	List all contact messages	Yes	Admin only
Example: Submit a Contact Form
Request:

bash

Collapse

Wrap

Copy
POST /contact/
Content-Type: application/json

{
  "name": "Jane Doe",
  "email": "jane@example.com",
  "message": "I have a question about the site."
}
Response (201 Created):

json

Collapse

Wrap

Copy
{
  "id": 1,
  "name": "Jane Doe",
  "email": "jane@example.com",
  "message": "I have a question about the site.",
  "created_at": "2025-03-29T12:00:00Z"
}
Error Handling
The API returns standard HTTP status codes and error messages in the following format:

json

Collapse

Wrap

Copy
{
  "status": "failed",
  "message": "Error message here",
  "errors": {
    "field_name": ["Error detail"]
  }
}
Common status codes:

200 OK: Request successful.
201 Created: Resource created successfully.
400 Bad Request: Invalid request data.
401 Unauthorized: Missing or invalid token.
403 Forbidden: Insufficient permissions.
404 Not Found: Resource not found.
429 Too Many Requests: Rate limit exceeded (e.g., resend verification cooldown).
Frontend Integration Tips
Handling JWT Tokens
Store the Token: After a successful login (/accounts/login/), store the token in local storage or a secure cookie.
javascript

Collapse

Wrap

Copy
// Example in JavaScript (React)
localStorage.setItem("token", response.data.token);
Set the Authorization Header: Include the token in the Authorization header for all authenticated requests.
javascript

Collapse

Wrap

Copy
// Example using Axios
axios.defaults.headers.common["Authorization"] = `Bearer ${localStorage.getItem("token")}`;
Handling File Uploads
For endpoints like /accounts/profile/update/ that support file uploads (e.g., profile image), use multipart/form-data:

javascript

Collapse

Wrap

Copy
// Example in JavaScript (React)
const formData = new FormData();
formData.append("firstName", "John");
formData.append("profile.image", imageFile); // imageFile is a File object
axios.put("/accounts/profile/update/", formData, {
  headers: {
    "Authorization": `Bearer ${localStorage.getItem("token")}`,
    "Content-Type": "multipart/form-data"
  }
});
Error Handling
Always check the status field in the response to handle errors appropriately:

javascript

Collapse

Wrap

Copy
// Example in JavaScript
axios.post("/accounts/register/", userData)
  .then(response => {
    if (response.data.status === "success") {
      console.log("Registration successful!");
    } else {
      console.error("Registration failed:", response.data.message);
    }
  })
  .catch(error => {
    console.error("Error:", error.response.data);
  });
Suggestions for Improvement
Here are some suggestions to enhance the project:

Switch to PostgreSQL for Production:
SQLite is fine for development, but for production, consider using PostgreSQL for better performance and scalability.
Update settings.py to use PostgreSQL:
python

Collapse

Wrap

Copy
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
Add Rate Limiting:
Use django-ratelimit or DRF’s throttling to prevent abuse (e.g., limit the number of requests to /accounts/send-otp/).
Example in settings.py:
python

Collapse

Wrap

Copy
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day'
    }
}
Improve Email Templates:
Currently, email verification and OTP emails are plain text. Use HTML templates for a better user experience.
Example: Create a templates/email/verification.html and use it in send_mail.
Add Unit Tests:
Write unit tests for your views, models, and serializers using Django’s TestCase and DRF’s APITestCase.
Example: Test user registration in users/tests.py.
Optimize Performance:
Use select_related and prefetch_related in more queries to reduce database hits.
Example: In RecipeViewSet, you already use prefetch_related('comments'). Add similar optimizations for category and user.
Add File Upload Support for Recipes:
Allow users to upload images for recipes (not just URLs). Store images in media/recipes/ and update the Recipe model and serializer.
Enhance Security:
Set DEBUG = False in production.
Use environment variables for SECRET_KEY.
Add django-secure for additional security headers.
Contributing
Contributions are welcome! To contribute:

Fork the repository.
Create a new branch (git checkout -b feature/your-feature).
Make your changes and commit (git commit -m "Add your feature").
Push to your branch (git push origin feature/your-feature).
Open a Pull Request.
