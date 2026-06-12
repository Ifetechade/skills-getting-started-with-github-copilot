import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)
original_activities = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(copy.deepcopy(original_activities))
    yield


def test_get_activities_returns_activities_list():
    response = client.get("/activities")

    assert response.status_code == 200
    assert "Chess Club" in response.json()
    assert response.json()["Chess Club"]["schedule"] == "Fridays, 3:30 PM - 5:00 PM"


def test_signup_for_activity_adds_participant():
    response = client.post("/activities/Chess%20Club/signup?email=test_student@mergington.edu")

    assert response.status_code == 200
    assert response.json()["message"] == "Signed up test_student@mergington.edu for Chess Club"
    assert "test_student@mergington.edu" in activities["Chess Club"]["participants"]


def test_signup_duplicate_participant_returns_400():
    email = "emma@mergington.edu"
    response = client.post(f"/activities/Programming%20Class/signup?email={email}")

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant_from_activity():
    response = client.delete("/activities/Chess%20Club/participants/michael%40mergington.edu")

    assert response.status_code == 200
    assert response.json()["message"] == "Removed michael@mergington.edu from Chess Club"
    assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]


def test_remove_participant_from_missing_activity_returns_404():
    response = client.delete("/activities/Unknown%20Club/participants/test%40mergington.edu")

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
