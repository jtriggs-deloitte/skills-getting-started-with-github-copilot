import pytest
from fastapi.testclient import TestClient
from src.app import app

# Initialize test client
client = TestClient(app)


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_all_activities_returns_dict(self):
        """
        Arrange: No setup needed
        Act: GET /activities
        Assert: Response is 200 and returns a dictionary
        """
        # Arrange
        # (no setup needed)

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        assert len(activities) > 0

    def test_activity_structure_is_correct(self):
        """
        Arrange: Fetch activities
        Act: Validate structure of returned activities
        Assert: Each activity has required fields
        """
        # Arrange
        # (no setup needed)

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_successful_signup(self):
        """
        Arrange: Get initial participant count
        Act: Sign up new student
        Assert: Student is added to participants list
        """
        # Arrange
        activity_name = "Chess Club"
        new_email = "test.student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={new_email}"
        )

        # Assert
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert new_email in result["message"]

    def test_signup_for_nonexistent_activity(self):
        """
        Arrange: Use activity name that doesn't exist
        Act: Attempt to sign up
        Assert: 404 error returned
        """
        # Arrange
        fake_activity = "Nonexistent Activity"
        test_email = "test@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{fake_activity}/signup?email={test_email}"
        )

        # Assert
        assert response.status_code == 404
        result = response.json()
        assert "Activity not found" in result["detail"]

    def test_duplicate_signup_rejected(self):
        """
        Arrange: Sign up a student first time
        Act: Attempt to sign up the same student again
        Assert: 400 error returned
        """
        # Arrange
        activity_name = "Programming Class"
        duplicate_email = "emma@mergington.edu"  # Already registered

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={duplicate_email}"
        )

        # Assert
        assert response.status_code == 400
        result = response.json()
        assert "already signed up" in result["detail"]

    def test_signup_with_special_characters_in_email(self):
        """
        Arrange: Email with special characters
        Act: Sign up with encoded email
        Assert: Special characters handled correctly
        """
        # Arrange
        activity_name = "Art Studio"
        special_email = "user+test@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={special_email}"
        )

        # Assert
        assert response.status_code == 200


class TestUnregisterParticipant:
    """Tests for DELETE /activities/{activity_name}/participants/{email} endpoint"""

    def test_successful_unregister(self):
        """
        Arrange: Get a registered participant
        Act: Unregister them from activity
        Assert: Participant is removed
        """
        # Arrange
        activity_name = "Gym Class"
        participant_email = "john@mergington.edu"  # Pre-registered

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{participant_email}"
        )

        # Assert
        assert response.status_code == 200
        result = response.json()
        assert "Unregistered" in result["message"]

    def test_unregister_from_nonexistent_activity(self):
        """
        Arrange: Use activity name that doesn't exist
        Act: Attempt to unregister
        Assert: 404 error returned
        """
        # Arrange
        fake_activity = "Fake Activity"
        test_email = "test@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{fake_activity}/participants/{test_email}"
        )

        # Assert
        assert response.status_code == 404
        result = response.json()
        assert "Activity not found" in result["detail"]

    def test_unregister_nonparticipant(self):
        """
        Arrange: Email of someone not registered
        Act: Attempt to unregister them
        Assert: 400 error returned
        """
        # Arrange
        activity_name = "Tennis Club"
        unregistered_email = "notregistered@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{unregistered_email}"
        )

        # Assert
        assert response.status_code == 400
        result = response.json()
        assert "not registered" in result["detail"]

    def test_unregister_then_signup_again(self):
        """
        Arrange: Unregister a participant
        Act: Sign them up again
        Assert: They can re-register successfully
        """
        # Arrange
        activity_name = "Music Ensemble"
        participant_email = "lucas@mergington.edu"  # Pre-registered

        # Act - unregister
        unregister_response = client.delete(
            f"/activities/{activity_name}/participants/{participant_email}"
        )

        # Act - re-signup
        signup_response = client.post(
            f"/activities/{activity_name}/signup?email={participant_email}"
        )

        # Assert
        assert unregister_response.status_code == 200
        assert signup_response.status_code == 200
