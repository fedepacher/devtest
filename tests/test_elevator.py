from fastapi.testclient import TestClient
from api.main import app


def test_create_elevator_element():
    """Create element in the DB"""
    client = TestClient(app)

    element = {
                "id": 1,
                "next_floor": 0,
                "demand_floor": 5,
                "call_datetime": "2023-11-04T14:52:54.869802"
            }

    response = client.post(
        '/api/v1/elevator/',
        json=element
    )

    assert response.status_code == 201, response.text
    response = client.get(
            '/api/v1/elevator/1'
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data['next_floor'] == element['next_floor']


def test_delete_elevator_element():
    """Delete element from the DB."""
    client = TestClient(app)
    ID = 2

    element = {
                "id": ID,
                "next_floor": 0,
                "demand_floor": 5,
                "call_datetime": "2023-11-04T14:52:54.869802"
            }

    response = client.post(
        '/api/v1/elevator/',
        json=element
    )

    assert response.status_code == 201, response.text

    response = client.delete(
        f'/api/v1/elevator/{ID}'
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data['msg'] == f'Element {ID} has been deleted successfully'
