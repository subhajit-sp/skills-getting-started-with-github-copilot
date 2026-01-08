"""
Tests for the Mergington High School Activity Management API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test"""
    # Save original state
    original_activities = {
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
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Sports": {
            "description": "Competitive sports teams and athletic training",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["james@mergington.edu", "isabella@mergington.edu"]
        },
        "Debate Club": {
            "description": "Develop public speaking and argumentation skills",
            "schedule": "Wednesdays, 3:30 PM - 4:30 PM",
            "max_participants": 15,
            "participants": ["lucas@mergington.edu", "ava@mergington.edu"]
        }
    }
    
    # Clear and restore
    activities.clear()
    activities.update(original_activities)
    yield
    # Restore after test
    activities.clear()
    activities.update(original_activities)


class TestRoot:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_static(self, client):
        """Test that the root endpoint redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for the GET /activities endpoint"""
    
    def test_get_all_activities(self, client):
        """Test retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
        assert "Sports" in data
        assert "Debate Club" in data
    
    def test_activity_has_required_fields(self, client):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        data = response.json()
        activity = data["Chess Club"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)
    
    def test_initial_participant_counts(self, client):
        """Test that activities have correct initial participant counts"""
        response = client.get("/activities")
        data = response.json()
        assert len(data["Chess Club"]["participants"]) == 2
        assert len(data["Programming Class"]["participants"]) == 2
        assert len(data["Gym Class"]["participants"]) == 2


class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""
    
    def test_successful_signup(self, client):
        """Test successfully signing up for an activity"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]
    
    def test_signup_adds_participant(self, client):
        """Test that signup actually adds the participant to the activity"""
        client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        response = client.get("/activities")
        data = response.json()
        assert "newstudent@mergington.edu" in data["Chess Club"]["participants"]
        assert len(data["Chess Club"]["participants"]) == 3
    
    def test_signup_duplicate_email(self, client):
        """Test that signing up with duplicate email returns 400"""
        response = client.post(
            "/activities/Chess Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_nonexistent_activity(self, client):
        """Test that signing up for non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent Activity/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]
    
    def test_signup_multiple_activities(self, client):
        """Test that a student can sign up for multiple activities"""
        client.post(
            "/activities/Chess Club/signup?email=student@mergington.edu"
        )
        client.post(
            "/activities/Programming Class/signup?email=student@mergington.edu"
        )
        response = client.get("/activities")
        data = response.json()
        assert "student@mergington.edu" in data["Chess Club"]["participants"]
        assert "student@mergington.edu" in data["Programming Class"]["participants"]


class TestUnregisterFromActivity:
    """Tests for the POST /activities/{activity_name}/unregister endpoint"""
    
    def test_successful_unregister(self, client):
        """Test successfully unregistering from an activity"""
        response = client.post(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "michael@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]
    
    def test_unregister_removes_participant(self, client):
        """Test that unregister actually removes the participant"""
        client.post(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        response = client.get("/activities")
        data = response.json()
        assert "michael@mergington.edu" not in data["Chess Club"]["participants"]
        assert len(data["Chess Club"]["participants"]) == 1
    
    def test_unregister_nonexistent_activity(self, client):
        """Test that unregistering from non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent Activity/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]
    
    def test_unregister_not_signed_up(self, client):
        """Test that unregistering someone not signed up returns 400"""
        response = client.post(
            "/activities/Chess Club/unregister?email=notsignedupstudent@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]
    
    def test_signup_then_unregister(self, client):
        """Test full signup and unregister workflow"""
        # Sign up
        client.post(
            "/activities/Chess Club/signup?email=testuser@mergington.edu"
        )
        response = client.get("/activities")
        assert "testuser@mergington.edu" in response.json()["Chess Club"]["participants"]
        
        # Unregister
        client.post(
            "/activities/Chess Club/unregister?email=testuser@mergington.edu"
        )
        response = client.get("/activities")
        assert "testuser@mergington.edu" not in response.json()["Chess Club"]["participants"]


class TestActivityCapacity:
    """Tests for activity capacity constraints"""
    
    def test_capacity_increases_with_signup(self, client):
        """Test that capacity count increases when user signs up"""
        response = client.get("/activities")
        initial_count = len(response.json()["Programming Class"]["participants"])
        
        client.post(
            "/activities/Programming Class/signup?email=newstudent@mergington.edu"
        )
        response = client.get("/activities")
        new_count = len(response.json()["Programming Class"]["participants"])
        
        assert new_count == initial_count + 1
    
    def test_capacity_decreases_with_unregister(self, client):
        """Test that capacity count decreases when user unregisters"""
        response = client.get("/activities")
        initial_count = len(response.json()["Programming Class"]["participants"])
        
        client.post(
            "/activities/Programming Class/unregister?email=emma@mergington.edu"
        )
        response = client.get("/activities")
        new_count = len(response.json()["Programming Class"]["participants"])
        
        assert new_count == initial_count - 1
