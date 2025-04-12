# Restaurant Management System

A comprehensive restaurant management system built with FastAPI and MySQL, based on MVC architecture.

## Features

- Customer Management
- Table Management
- Menu Management
- Order Processing
- Payment Handling
- Feedback Collection
- Staff Management

## Technology Stack

- **Backend**: FastAPI (Python)
- **Database**: MySQL
- **Authentication**: JWT
- **Architecture**: Model-View-Controller (MVC)

## API Endpoints

The API provides the following endpoints:

- `/api/v1/auth`: Authentication
- `/api/v1/categories`: Menu Categories
- `/api/v1/menu-items`: Menu Items
- `/api/v1/customers`: Customers
- `/api/v1/waitstaff`: Restaurant Staff
- `/api/v1/tables`: Tables
- `/api/v1/orders`: Orders
- `/api/v1/order-items`: Order Items
- `/api/v1/payments`: Payments
- `/api/v1/feedback`: Customer Feedback

## Project Structure

```
restaurant_management_system/
├── app/
│   ├── __init__.py
│   ├── main.py               # FastAPI entry point
│   ├── core/                 # Core settings
│   ├── models/               # Database models
│   ├── schemas/              # Pydantic schemas
│   ├── controllers/          # Business logic
│   ├── routers/              # API endpoints
│   └── static/               # Static files
├── requirements.txt          # Dependencies
├── db_setup.py               # Database setup
└── README.md
```

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd restaurant-management-system
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Configure the database:
   - Create a MySQL database
   - Update the database URL in `app/core/config.py` or use environment variables

5. Initialize the database:
   ```
   python db_setup.py
   ```

6. Run the application:
   ```
   uvicorn app.main:app --reload
   ```

7. Access the API at http://localhost:8000
   - API documentation: http://localhost:8000/docs or http://localhost:8000/redoc

## Default Credentials

- Username: admin
- Password: admin123

## License

This project is licensed under the MIT License.