import requests
import json
from datetime import datetime, time

BASE_URL = "http://localhost:8014"

def test_auth():
    print("\n=== Testing Authentication ===")
    
    # Sign up
    signup_data = {
        "username": "teacher1",
        "password": "password123",
        "role": "teacher"
    }
    response = requests.post(f"{BASE_URL}/auth/signup", json=signup_data)
    print(f"Signup Response: {response.status_code}")
    print(response.json() if response.ok else response.text)
    
    # Login
    login_data = {
        "username": "teacher1",
        "password": "password123"
    }
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"Login Response: {response.status_code}")
    if response.ok:
        token = response.json().get("access_token")
        print(f"Token received: {token[:20]}...")
        return token
    else:
        print(response.text)
        return None

def test_assignments(token):
    print("\n=== Testing Assignments ===")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create assignment
    assignment_data = {
        "title": "Math Quiz 1",
        "description": "Basic algebra quiz",
        "due_date": datetime.utcnow().isoformat(),
        "class_id": 1
    }
    response = requests.post(f"{BASE_URL}/assignments/", json=assignment_data, headers=headers)
    print(f"Create Assignment Response: {response.status_code}")
    print(response.json() if response.ok else response.text)

def test_timetable(token):
    print("\n=== Testing Timetable ===")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create timetable entry
    timetable_data = {
        "class_id": 1,
        "day_of_week": 1,
        "start_time": "09:00:00",
        "end_time": "10:30:00"
    }
    response = requests.post(f"{BASE_URL}/timetable/", json=timetable_data, headers=headers)
    print(f"Create Timetable Entry Response: {response.status_code}")
    print(response.json() if response.ok else response.text)

def test_grades(token):
    print("\n=== Testing Grades ===")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create grade
    grade_data = {
        "assignment_id": 1,
        "student_id": 1,
        "score": 85.5,
        "feedback": "Good work!"
    }
    response = requests.post(f"{BASE_URL}/grades/", json=grade_data, headers=headers)
    print(f"Create Grade Response: {response.status_code}")
    print(response.json() if response.ok else response.text)

def main():
    # Test authentication
    token = test_auth()
    if not token:
        print("Authentication failed. Stopping tests.")
        return
    
    # Test other endpoints
    test_assignments(token)
    test_timetable(token)
    test_grades(token)

if __name__ == "__main__":
    main() 