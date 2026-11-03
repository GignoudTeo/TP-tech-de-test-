"""Tests de performance de la triangulation, exclus de `make unit_test`."""

import random
import struct
import time

import pytest
from outils import decoder_triangles

from triangulateur.triangulation import triangulation

GRAINE = 42


def generer_pointset_aleatoire(nb_points):
    """Génère un PointSet binaire valide et reproductible de N points."""
    generateur = random.Random(GRAINE)
    data = [struct.pack(">I", nb_points)]  # Entête : nombre de points
    for _ in range(nb_points):
        x = generateur.uniform(0.0, 100.0)
        y = generateur.uniform(0.0, 100.0)
        data.append(struct.pack(">ff", x, y))
    return b"".join(data)


@pytest.mark.perf
@pytest.mark.parametrize("nb_points", [10, 100, 1000, 10000, 100000])
def test_performance_triangulation(nb_points):
    """Mesure le temps de triangulation selon le nombre de points."""
    point_set_bytes = generer_pointset_aleatoire(nb_points)

    start_time = time.perf_counter()
    result = triangulation(point_set_bytes)
    execution_time = time.perf_counter() - start_time

    # Contrôlé hors chronomètre : un résultat vide ne doit pas passer pour rapide.
    assert decoder_triangles(result)

    # Assertions de temps (les seuils seront à ajuster selon votre algo final)
    if nb_points <= 1000:
        assert execution_time < 0.5
    elif nb_points <= 10000:
        assert execution_time < 5.0
    else:
        assert execution_time < 60.0
