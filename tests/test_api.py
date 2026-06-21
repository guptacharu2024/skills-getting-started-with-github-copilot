import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)
INITIAL_ACTIVITIES = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    # Arrange
    activities.clear()
    activities.update(copy.deepcopy(INITIAL_ACTIVITIES))

    # Act happens in the test
    yield

    # Assert cleanup state is restored for the next test
    activities.clear()
    activities.update(copy.deepcopy(INITIAL_ACTIVITIES))


def test_root_redirects_to_static_index():
    # Arrange
    path = "/"

    # Act
    response = client.get(path, follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_all_data():
    # Arrange
    path = "/activities"

    # Act
    response = client.get(path)

    # Assert
    assert response.status_code == 200
    data = response.json()

    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data
    assert data["Chess Club"]["max_participants"] == 12


def test_signup_adds_new_participant():
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup?email={email}"
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {email} for {activity_name}"
    }

    updated = client.get("/activities").json()
    assert email in updated[activity_name]["participants"]


def test_signup_rejects_duplicate_email():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup?email={email}"
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student already signed up for this activity"
    }


def test_signup_unknown_activity_returns_404():
    # Arrange
    activity_name = "Unknown Activity"
    email = "student@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup?email={email}"
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_removes_participant():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/unregister?email={email}"
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Unregistered {email} from {activity_name}"
    }

    updated = client.get("/activities").json()
    assert email not in updated[activity_name]["participants"]


def test_unregister_unknown_participant_returns_404():
    # Arrange
    activity_name = "Chess Club"
    email = "missing@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/unregister?email={email}"
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Participant not found"}


def test_unregister_unknown_activity_returns_404():
    # Arrange
    activity_name = "Unknown Activity"
    email = "student@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/unregister?email={email}"
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}
