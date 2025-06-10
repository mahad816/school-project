# School App  
A simple role-based application for students, teachers, and parents.  

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
