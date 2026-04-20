"""
API endpoint tests using Arrange-Act-Assert (AAA) pattern.
Tests cover GET /activities, POST /signup, and DELETE /unregister endpoints.
"""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        """
        Arrange: No setup needed
        Act: Send GET request to /activities
        Assert: Response contains all activities with correct structure
        """
        # Arrange
        # (no additional setup required)

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        assert len(activities) > 0
        # Verify structure of each activity
        for activity_name, details in activities.items():
            assert isinstance(activity_name, str)
            assert "description" in details
            assert "schedule" in details
            assert "max_participants" in details
            assert "participants" in details
            assert isinstance(details["participants"], list)

    def test_get_activities_includes_expected_fields(self, client):
        """
        Arrange: No setup needed
        Act: Send GET request to /activities
        Assert: Each activity has all required fields
        """
        # Arrange
        # (no additional setup required)

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, details in activities.items():
            assert details["max_participants"] > 0
            assert isinstance(details["participants"], list)
            assert all(isinstance(p, str) for p in details["participants"])


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_success_adds_participant(self, client, new_test_email):
        """
        Arrange: Select an activity with available slots (Gym Class has 0 participants)
        Act: Send POST signup request with new email
        Assert: Email is added to participants and response confirms signup
        """
        # Arrange
        activity_name = "Gym Class"
        email = new_test_email

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]

    def test_signup_updates_participant_list(self, client, new_test_email):
        """
        Arrange: Fetch initial activities state
        Act: Signup a new participant
        Assert: Participant count increases and email appears in list
        """
        # Arrange
        activity_name = "Gym Class"
        email = new_test_email
        initial_response = client.get("/activities")
        initial_participants = initial_response.json()[activity_name]["participants"]
        initial_count = len(initial_participants)

        # Act
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        updated_response = client.get("/activities")
        updated_participants = updated_response.json()[activity_name]["participants"]

        # Assert
        assert len(updated_participants) == initial_count + 1
        assert email in updated_participants

    def test_signup_duplicate_email_rejected(self, client):
        """
        Arrange: Select an activity with existing participants (Programming Class)
        Act: Try to signup with an email already registered for this activity
        Assert: Request returns 400 status and error message
        """
        # Arrange
        activity_name = "Programming Class"
        email = "emma@mergington.edu"  # Already registered for Programming Class

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "already" in data["detail"].lower()

    def test_signup_nonexistent_activity_returns_404(self, client, new_test_email):
        """
        Arrange: Prepare a non-existent activity name
        Act: Try to signup for a non-existent activity
        Assert: Request returns 404 status
        """
        # Arrange
        activity_name = "NonExistent Activity"
        email = new_test_email

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_signup_success_message_format(self, client, new_test_email):
        """
        Arrange: Prepare activity and email
        Act: Send signup request
        Assert: Response message contains both activity name and email
        """
        # Arrange
        activity_name = "Gym Class"
        email = new_test_email

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        data = response.json()

        # Assert
        assert response.status_code == 200
        assert email in data["message"]
        assert activity_name in data["message"]
        assert "Signed up" in data["message"]


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint."""

    def test_unregister_success_removes_participant(self, client):
        """
        Arrange: Select an activity with known participants (Chess Club)
        Act: Send DELETE unregister request for existing participant
        Assert: Email is removed and response confirms unregistration
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Known participant

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]

    def test_unregister_updates_participant_list(self, client):
        """
        Arrange: Get initial participant count for Chess Club
        Act: Unregister a participant
        Assert: Participant count decreases and email is removed
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        initial_response = client.get("/activities")
        initial_participants = initial_response.json()[activity_name]["participants"]
        initial_count = len(initial_participants)

        # Act
        client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        updated_response = client.get("/activities")
        updated_participants = updated_response.json()[activity_name]["participants"]

        # Assert
        assert len(updated_participants) == initial_count - 1
        assert email not in updated_participants

    def test_unregister_nonregistered_participant_returns_400(self, client, new_test_email):
        """
        Arrange: Prepare activity and email not registered for that activity
        Act: Try to unregister an email not in the participant list
        Assert: Request returns 400 status with error message
        """
        # Arrange
        activity_name = "Chess Club"
        email = new_test_email  # Not registered for Chess Club

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "not registered" in data["detail"].lower()

    def test_unregister_nonexistent_activity_returns_404(self, client, test_email):
        """
        Arrange: Prepare a non-existent activity name
        Act: Try to unregister from a non-existent activity
        Assert: Request returns 404 status
        """
        # Arrange
        activity_name = "NonExistent Activity"
        email = test_email

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_unregister_success_message_format(self, client):
        """
        Arrange: Prepare activity and existing participant
        Act: Send unregister request
        Assert: Response message contains both activity name and email
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        data = response.json()

        # Assert
        assert response.status_code == 200
        assert email in data["message"]
        assert activity_name in data["message"]
        assert "Unregistered" in data["message"]


class TestSignupAndUnregisterFlow:
    """Integration tests for signup and unregister flows."""

    def test_signup_then_unregister_flow(self, client, new_test_email):
        """
        Arrange: Prepare activity and new email
        Act: Signup, then unregister the same email
        Assert: Both operations succeed and participant list is restored
        """
        # Arrange
        activity_name = "Gym Class"
        email = new_test_email
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity_name]["participants"])

        # Act - Signup
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert signup_response.status_code == 200

        # Assert signup worked
        after_signup = client.get("/activities")
        assert len(after_signup.json()[activity_name]["participants"]) == initial_count + 1

        # Act - Unregister
        unregister_response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        assert unregister_response.status_code == 200

        # Assert unregister restored state
        final_response = client.get("/activities")
        assert len(final_response.json()[activity_name]["participants"]) == initial_count

    def test_cannot_signup_twice_for_same_activity(self, client, new_test_email):
        """
        Arrange: Prepare activity and new email
        Act: Signup twice with the same email and activity
        Assert: First signup succeeds, second signup fails with 400
        """
        # Arrange
        activity_name = "Gym Class"
        email = new_test_email

        # Act - First signup
        first_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert first_response.status_code == 200

        # Act - Second signup (should fail)
        second_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert second_response.status_code == 400
        data = second_response.json()
        assert "already" in data["detail"].lower()
