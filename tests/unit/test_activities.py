import pytest
from src.app import activities


class TestActivitiesOperations:
    """Unit tests for activities dictionary operations"""

    def test_get_activities_returns_all(self, client, reset_activities):
        """Test that get_activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 9  # Number of activities
        assert "Chess Club" in data
        assert "Programming Class" in data

    def test_signup_successful(self, client, reset_activities):
        """Test successful signup adds participant to activity"""
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"

        # Initial count
        initial_count = len(activities[activity_name]["participants"])

        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response.status_code == 200
        assert email in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_count + 1

    def test_signup_duplicate_email(self, client, reset_activities):
        """Test signup fails when email already exists"""
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already in participants

        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_activity_not_found(self, client, reset_activities):
        """Test signup fails for nonexistent activity"""
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"

        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_remove_participant_successful(self, client, reset_activities):
        """Test successful removal of participant"""
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Initial count
        initial_count = len(activities[activity_name]["participants"])

        response = client.delete(f"/activities/{activity_name}/participants/{email}")
        assert response.status_code == 200
        assert email not in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_count - 1

    def test_remove_participant_not_found_activity(self, client, reset_activities):
        """Test remove fails for nonexistent activity"""
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"

        response = client.delete(f"/activities/{activity_name}/participants/{email}")
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_remove_participant_not_found_email(self, client, reset_activities):
        """Test remove fails when participant not in activity"""
        activity_name = "Chess Club"
        email = "notparticipant@mergington.edu"

        response = client.delete(f"/activities/{activity_name}/participants/{email}")
        assert response.status_code == 404
        assert "Participant not found" in response.json()["detail"]