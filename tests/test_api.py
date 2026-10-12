import pytest
from unittest.mock import patch
from triangulateur.app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# --- TESTS DE COMMUNICATION RÉUSSIE ---

@patch('triangulator.app.requests.get')
def test_api_triangulation_reussi(mock_get, client):
    # Mock de la réponse du PointSetManager (3 points)
    mock_get.return_value.status_code = 200
    mock_get.return_value.content = (
        b"\x00\x00\x00\x03"
        b"\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x3f\x80\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x3f\x80\x00\x00"
    )

    response = client.get('/triangulate/123e4567-e89b-12d3-a456-426614174000')
    
    assert response.status_code == 200
    assert response.data.startswith(b"\x00\x00\x00\x03")
    mock_get.assert_called_once()

# --- TESTS DE COMMUNICATION ÉCHOUÉE ---

def test_api_uuid_vide(client):
    response = client.get('/triangulate/')
    assert response.status_code == 404

def test_api_format_uuid_invalide(client):
    response = client.get('/triangulate/pas-un-uuid')
    assert response.status_code == 400

@patch('triangulator.app.requests.get')
def test_api_psm_injoignable(mock_get, client):
    mock_get.side_effect = Exception("Connection error")
    response = client.get('/triangulate/123e4567-e89b-12d3-a456-426614174000')
    assert response.status_code == 503

@patch('triangulator.app.requests.get')
def test_api_uuid_inexistant(mock_get, client):
    mock_get.return_value.status_code = 404
    response = client.get('/triangulate/123e4567-e89b-12d3-a456-426614174000')
    assert response.status_code == 404

@patch('triangulator.app.requests.get')
def test_api_donnees_corrompues(mock_get, client):
    mock_get.return_value.status_code = 200
    mock_get.return_value.content = b"mauvaises donnees non binaires"
    response = client.get('/triangulate/123e4567-e89b-12d3-a456-426614174000')
    assert response.status_code == 500