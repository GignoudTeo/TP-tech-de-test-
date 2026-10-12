import pytest
from triangulateur.triangulation import triangulation

# ==========================================
# TESTS DE SUCCÈS (HAPPY PATH)
# ==========================================

def test_triangulation_3points_reussi():
    # 3 points : (0.0, 0.0), (1.0, 0.0), (0.0, 1.0)
    point_set_bytes = (
        b"\x00\x00\x00\x03"
        b"\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x3f\x80\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x3f\x80\x00\x00"
    )
    
    resultat_attendu = (
        point_set_bytes +
        b"\x00\x00\x00\x01"  # 1 triangle
        b"\x00\x00\x00\x00"  # Sommet 0
        b"\x00\x00\x00\x01"  # Sommet 1
        b"\x00\x00\x00\x02"  # Sommet 2
    )
    assert triangulation(point_set_bytes) == resultat_attendu


def test_triangulation_4points_reussi():
    # 4 points : carré (0,0), (1,0), (0,1), (1,1)
    point_set_bytes = (
        b"\x00\x00\x00\x04"
        b"\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x3f\x80\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x3f\x80\x00\x00"
        b"\x3f\x80\x00\x00\x3f\x80\x00\x00"
    )
    
    resultat_attendu = (
        point_set_bytes +
        b"\x00\x00\x00\x02"  # 2 triangles
        b"\x00\x00\x00\x00" b"\x00\x00\x00\x01" b"\x00\x00\x00\x03"  # Triangle 1 (0, 1, 3)
        b"\x00\x00\x00\x00" b"\x00\x00\x00\x02" b"\x00\x00\x00\x03"  # Triangle 2 (0, 2, 3)
    )
    assert triangulation(point_set_bytes) == resultat_attendu


def test_triangulation_plus_de4points_reussi():
    # 5 points formant un pentagone (doit générer 3 triangles)
    point_set_bytes = (
        b"\x00\x00\x00\x05" 
        b"\x00\x00\x00\x00\x00\x00\x00\x00"  # P0: (0.0, 0.0)
        b"\x3f\x80\x00\x00\x00\x00\x00\x00"  # P1: (1.0, 0.0)
        b"\x00\x00\x00\x00\x3f\x80\x00\x00"  # P2: (0.0, 1.0)
        b"\x3f\x80\x00\x00\x3f\x80\x00\x00"  # P3: (1.0, 1.0)
        b"\x40\x40\x00\x00\x40\x40\x00\x00"  # P4: (3.0, 3.0)
    )
    
    result = triangulation(point_set_bytes)
    assert result is not None
    # On vérifie au moins qu'il y a 3 triangles (4 octets après le point_set_bytes)
    assert result[len(point_set_bytes):len(point_set_bytes)+4] == b"\x00\x00\x00\x03"


def test_triangulation_coordonnees_negatives_reussi():
    # 3 points avec des coordonnées négatives : (-1.0, 0.0), (1.0, 0.0), (0.0, -1.0)
    point_set_bytes = (
        b"\x00\x00\x00\x03"
        b"\xbf\x80\x00\x00\x00\x00\x00\x00"  # (-1.0, 0.0)
        b"\x3f\x80\x00\x00\x00\x00\x00\x00"  # (1.0, 0.0)
        b"\x00\x00\x00\x00\xbf\x80\x00\x00"  # (0.0, -1.0)
    )
    
    resultat_attendu = (
        point_set_bytes +
        b"\x00\x00\x00\x01"  # 1 triangle
        b"\x00\x00\x00\x00" b"\x00\x00\x00\x01" b"\x00\x00\x00\x02"
    )
    assert triangulation(point_set_bytes) == resultat_attendu


def test_triangulation_certainspoints_alignes_reussi():
    # 4 points : 3 alignés sur l'axe X (0,0), (1,0), (2,0) et 1 décalé (1,1)
    # La triangulation reste possible et doit former 2 triangles
    point_set_bytes = (
        b"\x00\x00\x00\x04"
        b"\x00\x00\x00\x00\x00\x00\x00\x00"  # (0.0, 0.0)
        b"\x3f\x80\x00\x00\x00\x00\x00\x00"  # (1.0, 0.0)
        b"\x40\x00\x00\x00\x00\x00\x00\x00"  # (2.0, 0.0)
        b"\x3f\x80\x00\x00\x3f\x80\x00\x00"  # (1.0, 1.0)
    )
    result = triangulation(point_set_bytes)
    assert result is not None
    # Doit contenir 2 triangles
    assert result[len(point_set_bytes):len(point_set_bytes)+4] == b"\x00\x00\x00\x02"


# ==========================================
# TESTS DE FORMAT ET DE STRUCTURE
# ==========================================

def test_triangulation_debutTriangles_PointSetinitial_reussi():
    # Vérifie que la réponse commence bien EXACTEMENT par les bytes envoyés (le PointSet)
    point_set_bytes = (
        b"\x00\x00\x00\x03"
        b"\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x3f\x80\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x3f\x80\x00\x00"
    )
    result = triangulation(point_set_bytes)
    assert result.startswith(point_set_bytes)


def test_triangulation_bonformat_reussi():
    # Vérifie que le retour est bien au format binaire (bytes) et que sa taille totale est cohérente
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
    # 0 points (entête seule)
    point_set_bytes = b"\x00\x00\x00\x00"
    with pytest.raises(ValueError, match="Taille insuffisante"):
        triangulation(point_set_bytes)


def test_un_point_echec():
    # 1 point (0.0, 0.0)
    point_set_bytes = b"\x00\x00\x00\x01" + b"\x00\x00\x00\x00\x00\x00\x00\x00"
    with pytest.raises(ValueError, match="Taille insuffisante"):
        triangulation(point_set_bytes)


def test_deux_points_echec():
    # 2 points (ne peuvent pas former de triangle)
    point_set_bytes = (
        b"\x00\x00\x00\x02"
        b"\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x3f\x80\x00\x00\x00\x00\x00\x00"
    )
    with pytest.raises(ValueError, match="Taille insuffisante"):
        triangulation(point_set_bytes)


def test_points_alignes_echec():
    # 3 points alignés sur l'axe X : (0,0), (1,0), (2,0) (impossible de faire un triangle)
    point_set_bytes = (
        b"\x00\x00\x00\x03"
        b"\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x3f\x80\x00\x00\x00\x00\x00\x00"
        b"\x40\x00\x00\x00\x00\x00\x00\x00"
    )
    with pytest.raises(ValueError, match="Points alignés"):
        triangulation(point_set_bytes)


def test_points_superposes_echec():
    # 3 points fournis, mais 2 sont parfaitement identiques (0,0), (1,1), (1,1)
    point_set_bytes = (
        b"\x00\x00\x00\x03"
        b"\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x3f\x80\x00\x00\x3f\x80\x00\x00"
        b"\x3f\x80\x00\x00\x3f\x80\x00\x00"
    )
    with pytest.raises(ValueError, match="Points superposés ou insuffisants"):
        triangulation(point_set_bytes)


def test_pointset_non_conforme_echec():
    # Entête annonce 3 points, mais les données binaires n'en contiennent qu'un seul
    point_set_bytes = b"\x00\x00\x00\x03" + b"\x00\x00\x00\x00\x00\x00\x00\x00"
    with pytest.raises(ValueError, match="PointSet non conforme"):
        triangulation(point_set_bytes)