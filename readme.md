# School Application

A FastAPI-based school management system with authentication and class management.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r backend/requirements.txt
```

3. Run the server:
```bash
python backend/run.py
```

The server will be available at http://127.0.0.1:8016

## API Documentation

Once the server is running, you can access:
- Interactive API docs: http://127.0.0.1:8016/docs
- Alternative API docs: http://127.0.0.1:8016/redoc

## Features

- User authentication (signup/login)
- Role-based access control (teacher/student)
- Class management
- Secure password hashing
- JWT token-based authentication

## Tech Stack  
- Frontend: React (or plain HTML/CSS/JS)  
- Backend: FastAPI (Python)  
- Database: SQLite (or PostgreSQL)  
- Authentication: JWT  
hello
hi from abdullah



## Running the Backend

#Install the Python dependencies and start the FastAPI server:

#```bash
pip install -r backend/requirements.txt
uvicorn backend.app:app --reload --port 8014
```

The API will be available on `http://localhost:8014`. Make sure the
server is running before sending requests such as the signup example
below:

```bash
curl -X POST http://localhost:8014/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"teach1","password":"password123"}'
```
