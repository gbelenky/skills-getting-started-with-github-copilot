"""
Tests for the Mergington High School API
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
    """Reset activities to a known state before each test"""
    # Store original participants
    original_participants = {
        "Programming Class": ["emma@mergington.edu", "sophia@mergington.edu"],
        "Gym Class": ["john@mergington.edu", "olivia@mergington.edu"],
    }
    
    yield
    
    # Restore original participants after each test
    for activity_name, participants in original_participants.items():
        if activity_name in activities:
            activities[activity_name]["participants"] = participants.copy()


class TestGetActivities:
    """Tests for the GET /activities endpoint"""

    def test_get_activities_returns_200(self, client):
        """Test that GET /activities returns a 200 status code"""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_dict(self, client):
        """Test that GET /activities returns a dictionary"""
        response = client.get("/activities")
        assert isinstance(response.json(), dict)

    def test_get_activities_contains_expected_activities(self, client):
        """Test that the response contains expected activities"""
        response = client.get("/activities")
        data = response.json()
        
        assert "Programming Class" in data
        assert "Gym Class" in data

    def test_activity_has_required_fields(self, client):
        """Test that each activity has the required fields"""
        response = client.get("/activities")
        data = response.json()
        
        programming_class = data["Programming Class"]
        assert "description" in programming_class
        assert "schedule" in programming_class
        assert "max_participants" in programming_class
        assert "participants" in programming_class


class TestSignup:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""

    def test_signup_success(self, client):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Programming%20Class/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]

    def test_signup_activity_not_found(self, client):
        """Test signup for a non-existent activity"""
        response = client.post(
            "/activities/Nonexistent%20Activity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_already_registered(self, client):
        """Test signup when student is already registered"""
        response = client.post(
            "/activities/Programming%20Class/signup?email=emma@mergington.edu"
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up"

    def test_signup_adds_participant(self, client):
        """Test that signup actually adds the participant to the activity"""
        email = "brandnew@mergington.edu"
        
        # Sign up
        client.post(f"/activities/Programming%20Class/signup?email={email}")
        
        # Verify participant was added
        response = client.get("/activities")
        participants = response.json()["Programming Class"]["participants"]
        assert email in participants


class TestUnregister:
    """Tests for the DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_success(self, client):
        """Test successful unregistration from an activity"""
        response = client.delete(
            "/activities/Programming%20Class/unregister?email=emma@mergington.edu"
        )
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]

    def test_unregister_activity_not_found(self, client):
        """Test unregister from a non-existent activity"""
        response = client.delete(
            "/activities/Nonexistent%20Activity/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_unregister_not_registered(self, client):
        """Test unregister when student is not registered"""
        response = client.delete(
            "/activities/Programming%20Class/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Student is not registered for this activity"

    def test_unregister_removes_participant(self, client):
        """Test that unregister actually removes the participant from the activity"""
        email = "emma@mergington.edu"
        
        # Unregister
        client.delete(f"/activities/Programming%20Class/unregister?email={email}")
        
        # Verify participant was removed
        response = client.get("/activities")
        participants = response.json()["Programming Class"]["participants"]
        assert email not in participants


class TestRootRedirect:
    """Tests for the root endpoint redirect"""

    def test_root_redirects_to_static(self, client):
        """Test that the root endpoint redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
