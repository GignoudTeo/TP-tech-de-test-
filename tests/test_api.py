"""Tests de l'API du Triangulator, avec le PointSetManager simulé par un mock."""

from unittest.mock import MagicMock, patch
from urllib.error import HTTPError, URLError

import pytest
from outils import decoder_triangles

from triangulateur.app import app

UUID_VALIDE = "123e4567-e89b-12d3-a456-426614174000"
URL_TRIANGULATION = f"/triangulation/{UUID_VALIDE}"


@pytest.fixture
def client():
    """Fournit un client de test Flask."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def reponse_psm(contenu):
    """Renvoie une fausse réponse 200 du PSM, utilisable avec ou sans `with`."""
    reponse = MagicMock()
    reponse.status = 200
    reponse.read.return_value = contenu
    # `with urlopen(...) as r` doit donner cette même réponse dans `r`.
    reponse.__enter__.return_value = reponse
    return reponse


# --- TESTS DE COMMUNICATION RÉUSSIE ---


@patch("urllib.request.urlopen")
def test_api_triangulation_reussi(mock_urlopen, client):
    """Vérifie la réponse et l'appel au PSM pour un UUID valide."""
    # Mock de la réponse du PointSetManager (3 points)
    point_set_bytes = (
        b"\x00\x00\x00\x03"
        b"\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x3f\x80\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x3f\x80\x00\x00"
    )
    mock_urlopen.return_value = reponse_psm(point_set_bytes)

    response = client.get(URL_TRIANGULATION)

    # La réponse contient le PointSet reçu du PSM, suivi d'un seul triangle.
    assert response.status_code == 200
    assert response.data.startswith(point_set_bytes)
    assert len(decoder_triangles(response.data)) == 1
    # Le PSM a été appelé une seule fois, sur la route de ses spécifications.
    mock_urlopen.assert_called_once()
    assert mock_urlopen.call_args.args[0].endswith(f"/pointset/{UUID_VALIDE}")


# --- TESTS DE COMMUNICATION ÉCHOUÉE ---


def test_api_uuid_vide(client):
    """Vérifie qu'une route sans UUID répond 404."""
    response = client.get("/triangulation/")
    assert response.status_code == 404


def test_api_format_uuid_invalide(client):
    """Vérifie qu'un UUID mal formé répond 400."""
    response = client.get("/triangulation/pas-un-uuid")
    assert response.status_code == 400


@patch("urllib.request.urlopen")
def test_api_psm_injoignable(mock_urlopen, client):
    """Vérifie qu'un PSM injoignable répond 503."""
    mock_urlopen.side_effect = URLError("Connection error")
    response = client.get(URL_TRIANGULATION)
    assert response.status_code == 503


@patch("urllib.request.urlopen")
def test_api_uuid_inexistant(mock_urlopen, client):
    """Vérifie qu'un UUID inconnu du PSM répond 404."""
    mock_urlopen.side_effect = HTTPError(
        f"/pointset/{UUID_VALIDE}", 404, "Not Found", None, None
    )
    response = client.get(URL_TRIANGULATION)
    assert response.status_code == 404
    # Sans cet appel, le 404 viendrait de Flask et non du PSM.
    mock_urlopen.assert_called_once()


@patch("urllib.request.urlopen")
def test_api_donnees_corrompues(mock_urlopen, client):
    """Vérifie que des données invalides venant du PSM répondent 503."""
    mock_urlopen.return_value = reponse_psm(b"mauvaises donnees non binaires")
    response = client.get(URL_TRIANGULATION)
    assert response.status_code == 503


@patch("urllib.request.urlopen")
def test_api_pointset_vide(mock_urlopen, client):
    """Vérifie qu'un PointSet valide mais sans point répond 500."""
    mock_urlopen.return_value = reponse_psm(b"\x00\x00\x00\x00")
    response = client.get(URL_TRIANGULATION)
    assert response.status_code == 500


@patch("urllib.request.urlopen")
def test_api_reponse_psm_vide(mock_urlopen, client):
    """Vérifie qu'une réponse sans aucun octet venant du PSM répond 503."""
    mock_urlopen.return_value = reponse_psm(b"")
    response = client.get(URL_TRIANGULATION)
    assert response.status_code == 503
