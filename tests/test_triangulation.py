"""Tests de l'algorithme de triangulation et du format binaire."""

from itertools import combinations

import pytest
from outils import (
    aire_triangle,
    decoder_triangles,
    encoder_pointset,
    triangles_normalises,
    triangles_se_chevauchent,
)

from triangulateur.triangulation import triangulation

# ==========================================
# TESTS DE SUCCÈS (HAPPY PATH)
# ==========================================


def test_triangulation_3points_reussi():
    """Vérifie que 3 points non alignés forment un seul triangle."""
    # 3 points : (0.0, 0.0), (1.0, 0.0), (0.0, 1.0)
    point_set_bytes = (
        b"\x00\x00\x00\x03"
        b"\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x3f\x80\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x3f\x80\x00\x00"
    )

    result = triangulation(point_set_bytes)

    assert result.startswith(point_set_bytes)
    assert triangles_normalises(result) == [(0, 1, 2)]


def test_triangulation_4points_reussi():
    """Vérifie qu'un carré donne 2 triangles, quelle que soit la diagonale."""
    # 4 points : carré (0,0), (1,0), (0,1), (1,1)
    point_set_bytes = (
        b"\x00\x00\x00\x04"
        b"\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x3f\x80\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x3f\x80\x00\x00"
        b"\x3f\x80\x00\x00\x3f\x80\x00\x00"
    )

    result = triangulation(point_set_bytes)

    assert result.startswith(point_set_bytes)
    # Les deux diagonales du carré donnent une triangulation valide.
    assert triangles_normalises(result) in (
        [(0, 1, 2), (1, 2, 3)],  # Diagonale P1-P2
        [(0, 1, 3), (0, 2, 3)],  # Diagonale P0-P3
    )


def test_triangulation_plus_de4points_reussi():
    """Vérifie 5 points dont un point intérieur : 4 triangles, 2 solutions valides."""
    point_set_bytes = (
        b"\x00\x00\x00\x05"
        b"\x00\x00\x00\x00\x00\x00\x00\x00"  # P0: (0.0, 0.0)
        b"\x3f\x80\x00\x00\x00\x00\x00\x00"  # P1: (1.0, 0.0)
        b"\x00\x00\x00\x00\x3f\x80\x00\x00"  # P2: (0.0, 1.0)
        b"\x3f\x80\x00\x00\x3f\x80\x00\x00"  # P3: (1.0, 1.0), intérieur
        b"\x40\x40\x00\x00\x40\x40\x00\x00"  # P4: (3.0, 3.0)
    )

    result = triangulation(point_set_bytes)

    assert result.startswith(point_set_bytes)
    # P3 est relié à P1, P2 et P4 ; seule la zone autour de P0 peut changer.
    assert triangles_normalises(result) in (
        [(0, 1, 2), (1, 2, 3), (1, 3, 4), (2, 3, 4)],  # Avec l'arête P1-P2
        [(0, 1, 3), (0, 2, 3), (1, 3, 4), (2, 3, 4)],  # Avec l'arête P0-P3
    )


def test_triangulation_plus_de_points_surface_recouverte_reussi():
    """Vérifie points tous utilisés, surface recouverte et aucun chevauchement."""
    # Carré de côté 10 (aire 100) contenant 6 points intérieurs.
    points = [
        (0.0, 0.0),
        (10.0, 0.0),
        (10.0, 10.0),
        (0.0, 10.0),
        (2.0, 3.0),
        (7.0, 2.0),
        (4.0, 5.0),
        (8.0, 6.0),
        (3.0, 8.0),
        (6.0, 8.0),
    ]

    triangles = decoder_triangles(triangulation(encoder_pointset(points)))
    formes = [[points[i] for i in triangle] for triangle in triangles]

    # Nombre de triangles : 2 * 10 points - 2 - 4 points sur le bord de l'enveloppe.
    assert len(triangles) == 14
    # Tous les points sont utilisés.
    assert {i for triangle in triangles for i in triangle} == set(range(10))
    # Aucun triangle n'est plat.
    assert all(aire_triangle(*forme) > 0 for forme in formes)
    # Les triangles recouvrent toute la surface du carré.
    assert sum(aire_triangle(*forme) for forme in formes) == 100
    # Aucune paire de triangles ne se chevauche.
    assert not any(
        triangles_se_chevauchent(a, b) for a, b in combinations(formes, 2)
    )


def test_triangulation_points_similaires_reussi():
    """Vérifie qu'un doublon est ignoré s'il reste au moins 3 points distincts."""
    point_set_bytes = (
        b"\x00\x00\x00\x04"
        b"\x00\x00\x00\x00\x00\x00\x00\x00"  # P0: (0.0, 0.0)
        b"\x3f\x80\x00\x00\x00\x00\x00\x00"  # P1: (1.0, 0.0)
        b"\x00\x00\x00\x00\x3f\x80\x00\x00"  # P2: (0.0, 1.0)
        b"\x3f\x80\x00\x00\x00\x00\x00\x00"  # P3: (1.0, 0.0), doublon de P1
    )

    result = triangulation(point_set_bytes)

    assert result.startswith(point_set_bytes)
    # P1 et P3 sont le même point : le triangle peut utiliser l'un ou l'autre.
    assert triangles_normalises(result) in ([(0, 1, 2)], [(0, 2, 3)])


def test_triangulation_coordonnees_negatives_reussi():
    """Vérifie que les coordonnées négatives sont bien prises en charge."""
    # 3 points avec des coordonnées négatives
    point_set_bytes = (
        b"\x00\x00\x00\x03"
        b"\xbf\x80\x00\x00\x00\x00\x00\x00"  # (-1.0, 0.0)
        b"\x3f\x80\x00\x00\x00\x00\x00\x00"  # (1.0, 0.0)
        b"\x00\x00\x00\x00\xbf\x80\x00\x00"  # (0.0, -1.0)
    )

    result = triangulation(point_set_bytes)

    assert result.startswith(point_set_bytes)
    assert triangles_normalises(result) == [(0, 1, 2)]


def test_triangulation_certainspoints_alignes_reussi():
    """Vérifie 3 points alignés et 1 décalé : 2 triangles, une seule solution."""
    # 4 points : 3 alignés sur l'axe X (0,0), (1,0), (2,0) et 1 décalé (1,1)
    point_set_bytes = (
        b"\x00\x00\x00\x04"
        b"\x00\x00\x00\x00\x00\x00\x00\x00"  # (0.0, 0.0)
        b"\x3f\x80\x00\x00\x00\x00\x00\x00"  # (1.0, 0.0)
        b"\x40\x00\x00\x00\x00\x00\x00\x00"  # (2.0, 0.0)
        b"\x3f\x80\x00\x00\x3f\x80\x00\x00"  # (1.0, 1.0)
    )

    result = triangulation(point_set_bytes)

    assert result.startswith(point_set_bytes)
    assert triangles_normalises(result) == [(0, 1, 3), (1, 2, 3)]


# ==========================================
# TESTS DE FORMAT ET DE STRUCTURE
# ==========================================


def test_triangulation_debutTriangles_PointSetinitial_reussi():
    """Vérifie que la réponse commence par le PointSet, suivi des triangles."""
    point_set_bytes = (
        b"\x00\x00\x00\x03"
        b"\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x3f\x80\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x3f\x80\x00\x00"
    )
    result = triangulation(point_set_bytes)
    assert result.startswith(point_set_bytes)
    assert len(result) > len(point_set_bytes)


def test_triangulation_bonformat_reussi():
    """Vérifie que le retour est en binaire et que sa taille est cohérente."""
    point_set_bytes = (
        b"\x00\x00\x00\x03"
        b"\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x3f\x80\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x3f\x80\x00\x00"
    )
    result = triangulation(point_set_bytes)

    assert isinstance(result, bytes)

    # Taille attendue :
    # Taille du PointSet initial (4 octets + 3*8 octets = 28 octets)
    # + 4 octets pour le nombre de triangles (1)
    # + 12 octets par triangle (1*12 = 12 octets)
    # = 44 octets au total
    assert len(result) == len(point_set_bytes) + 4 + 12


# ==========================================
# TESTS D'ÉCHEC ET CAS LIMITES
# ==========================================


def test_pas_de_points_echec():
    """Vérifie qu'un PointSet sans point est refusé."""
    # 0 points (entête seule)
    point_set_bytes = b"\x00\x00\x00\x00"
    with pytest.raises(ValueError, match="Taille insuffisante"):
        triangulation(point_set_bytes)


def test_un_point_echec():
    """Vérifie qu'un seul point est refusé."""
    # 1 point (0.0, 0.0)
    point_set_bytes = b"\x00\x00\x00\x01" + b"\x00\x00\x00\x00\x00\x00\x00\x00"
    with pytest.raises(ValueError, match="Taille insuffisante"):
        triangulation(point_set_bytes)


def test_deux_points_echec():
    """Vérifie que deux points sont refusés."""
    # 2 points (ne peuvent pas former de triangle)
    point_set_bytes = (
        b"\x00\x00\x00\x02"
        b"\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x3f\x80\x00\x00\x00\x00\x00\x00"
    )
    with pytest.raises(ValueError, match="Taille insuffisante"):
        triangulation(point_set_bytes)


def test_points_alignes_echec():
    """Vérifie qu'aucun triangle n'est possible avec des points alignés."""
    # 3 points alignés sur l'axe X : (0,0), (1,0), (2,0)
    point_set_bytes = (
        b"\x00\x00\x00\x03"
        b"\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x3f\x80\x00\x00\x00\x00\x00\x00"
        b"\x40\x00\x00\x00\x00\x00\x00\x00"
    )
    with pytest.raises(ValueError, match="Points alignés"):
        triangulation(point_set_bytes)


def test_points_superposes_echec():
    """Vérifie que moins de 3 points distincts revient à une taille insuffisante."""
    # 3 points fournis, mais 2 sont parfaitement identiques (0,0), (1,1), (1,1)
    point_set_bytes = (
        b"\x00\x00\x00\x03"
        b"\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x3f\x80\x00\x00\x3f\x80\x00\x00"
        b"\x3f\x80\x00\x00\x3f\x80\x00\x00"
    )
    with pytest.raises(ValueError, match="Taille insuffisante"):
        triangulation(point_set_bytes)


def test_tous_points_identiques_echec():
    """Vérifie que des points tous identiques reviennent au cas d'un seul point."""
    point_set_bytes = (
        b"\x00\x00\x00\x03"
        b"\x3f\x80\x00\x00\x3f\x80\x00\x00"
        b"\x3f\x80\x00\x00\x3f\x80\x00\x00"
        b"\x3f\x80\x00\x00\x3f\x80\x00\x00"
    )
    with pytest.raises(ValueError, match="Taille insuffisante"):
        triangulation(point_set_bytes)


def test_pointset_trop_de_donnees_echec():
    """Vérifie qu'un PointSet contenant plus de points qu'annoncé est refusé."""
    # Entête annonce 3 points, mais les données binaires en contiennent 4
    point_set_bytes = (
        b"\x00\x00\x00\x03"
        b"\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x3f\x80\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x3f\x80\x00\x00"
        b"\x3f\x80\x00\x00\x3f\x80\x00\x00"
    )
    with pytest.raises(ValueError, match="PointSet non conforme"):
        triangulation(point_set_bytes)


def test_pointset_non_conforme_echec():
    """Vérifie que l'entête doit correspondre au nombre de points présents."""
    # Entête annonce 3 points, mais les données binaires n'en contiennent qu'un seul
    point_set_bytes = b"\x00\x00\x00\x03" + b"\x00\x00\x00\x00\x00\x00\x00\x00"
    with pytest.raises(ValueError, match="PointSet non conforme"):
        triangulation(point_set_bytes)
