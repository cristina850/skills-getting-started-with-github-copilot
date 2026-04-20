import pytest


class TestEndpoints:
    """Integration tests for API endpoints"""

    def test_root_redirect(self, client):
        """Test root endpoint redirects to static index"""
        response = client.get("/")
        assert response.status_code == 200  # RedirectResponse, but TestClient follows redirects
        # Since it's a redirect to static file, it should serve the HTML
        assert "text/html" in response.headers.get("content-type", "")

    def test_get_activities_endpoint(self, client, reset_activities):
        """Test GET /activities returns activities data"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 9

        # Check structure of one activity
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)

    def test_signup_flow(self, client, reset_activities):
        """Test complete signup workflow"""
        activity_name = "Programming Class"
        email = "newstudent@mergington.edu"

        # Check initial state
        response = client.get("/activities")
        initial_participants = response.json()[activity_name]["participants"]
        assert email not in initial_participants

        # Signup
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response.status_code == 200
        assert f"Signed up {email} for {activity_name}" in response.json()["message"]

        # Verify in activities
        response = client.get("/activities")
        updated_participants = response.json()[activity_name]["participants"]
        assert email in updated_participants

    def test_signup_via_query_params(self, client, reset_activities):
        """Test signup with query parameters"""
        activity_name = "Gym Class"
        email = "querytest@mergington.edu"

        response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
        assert response.status_code == 200
        assert email in response.json()["message"]

    def test_remove_via_path_params(self, client, reset_activities):
        """Test remove participant with path parameters"""
        activity_name = "Basketball Team"
        email = "james@mergington.edu"  # Already in participants

        response = client.delete(f"/activities/{activity_name}/participants/{email}")
        assert response.status_code == 200
        assert f"Removed {email} from {activity_name}" in response.json()["message"]

    def test_state_consistency(self, client, reset_activities):
        """Test that state changes persist across requests"""
        activity_name = "Tennis Club"
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"

        # Add two participants
        client.post(f"/activities/{activity_name}/signup?email={email1}")
        client.post(f"/activities/{activity_name}/signup?email={email2}")

        # Check both are there
        response = client.get("/activities")
        participants = response.json()[activity_name]["participants"]
        assert email1 in participants
        assert email2 in participants

        # Remove one
        client.delete(f"/activities/{activity_name}/participants/{email1}")

        # Check only one remains
        response = client.get("/activities")
        participants = response.json()[activity_name]["participants"]
        assert email1 not in participants
        assert email2 in participants

    def test_error_responses(self, client, reset_activities):
        """Test various error scenarios"""
        # Nonexistent activity signup
        response = client.post("/activities/InvalidActivity/signup?email=test@email.com")
        assert response.status_code == 404

        # Duplicate signup
        response = client.post("/activities/Chess Club/signup?email=michael@mergington.edu")
        assert response.status_code == 400

        # Remove nonexistent participant
        response = client.delete("/activities/Chess Club/participants/nonexistent@email.com")
        assert response.status_code == 404