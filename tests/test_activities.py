from src.app import activities


def test_get_activities_returns_activity_data(client):
    response = client.get("/activities")

    assert response.status_code == 200
    activities = response.json()
    assert "Chess Club" in activities
    assert "participants" in activities["Chess Club"]


def test_signup_adds_participant_and_returns_updated_activities(client):
    email = "new.student@mergington.edu"

    response = client.post(
        "/activities/Basketball Club/signup", params={"email": email}
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {email} for Basketball Club"
    }

    activities_response = client.get("/activities")
    assert email in activities_response.json()["Basketball Club"]["participants"]


def test_signup_rejects_duplicate_participant(client):
    email = "michael@mergington.edu"
    original_count = len(
        client.get("/activities").json()["Chess Club"]["participants"]
    )

    response = client.post(
        "/activities/Chess Club/signup", params={"email": email}
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"
    participants = client.get("/activities").json()["Chess Club"]["participants"]
    assert participants.count(email) == 1
    assert len(participants) == original_count


def test_signup_returns_not_found_for_unknown_activity(client):
    response = client.post(
        "/activities/Unknown Club/signup", params={"email": "student@example.com"}
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_participant_including_duplicate_entries(client):
    email = "student@example.com"
    participants = ["keep@mergington.edu", email, email]
    activities["Basketball Club"]["participants"] = participants.copy()

    response = client.delete(
        "/activities/Basketball Club/signup", params={"email": email}
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": f"Unregistered {email} from Basketball Club"
    }
    remaining = client.get("/activities").json()["Basketball Club"]["participants"]
    assert remaining == ["keep@mergington.edu"]


def test_unregister_returns_not_found_for_unregistered_participant(client):
    response = client.delete(
        "/activities/Basketball Club/signup",
        params={"email": "missing@example.com"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"


def test_unregister_returns_not_found_for_unknown_activity(client):
    response = client.delete(
        "/activities/Unknown Club/signup", params={"email": "student@example.com"}
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
