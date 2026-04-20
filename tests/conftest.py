"""
Pytest configuration and shared fixtures for API tests.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """
    Provide a FastAPI TestClient for API endpoints.
    """
    return TestClient(app)


@pytest.fixture
def sample_activities():
    """
    Provide sample activity data for testing.
    Returns a dictionary matching the activities structure in app.py.
    """
    return {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": []
        }
    }


@pytest.fixture
def test_email():
    """Provide a test email address."""
    return "test@mergington.edu"


@pytest.fixture
def new_test_email():
    """Provide a new test email address not yet registered."""
    return "newstudent@mergington.edu"
