from fastapi.testclient import TestClient
import pytest
from src.app import app, activities

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def sample_activity():
    return {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        }
    }

def test_read_root(client):
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307  # Status code for redirect
    assert response.headers["location"] == "/static/index.html"

def test_get_activities(client):
    response = client.get("/activities")
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert "Chess Club" in response.json()
    assert "Programming Class" in response.json()

def test_signup_for_activity_success(client):
    new_email = "test@mergington.edu"
    response = client.post(f"/activities/Chess Club/signup?email={new_email}")
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {new_email} for Chess Club"}
    
    # Verify the participant was actually added
    activities_response = client.get("/activities")
    assert new_email in activities_response.json()["Chess Club"]["participants"]

def test_signup_for_activity_already_registered(client):
    existing_email = "michael@mergington.edu"  # This email is already registered in Chess Club
    response = client.post(f"/activities/Chess Club/signup?email={existing_email}")
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"

def test_signup_for_nonexistent_activity(client):
    response = client.post("/activities/NonexistentClub/signup?email=test@mergington.edu")
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"