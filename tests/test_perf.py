import pytest
import time
import struct
import random
from triangulateur.triangulation import triangulation

def generer_pointset_aleatoire(nb_points):
    """Génère un PointSet binaire valide de N points"""
    data = struct.pack('>I', nb_points)  # Entête : nombre de points (unsigned long)
    for _ in range(nb_points):
        x = random.uniform(0.0, 100.0)
        y = random.uniform(0.0, 100.0)
        data += struct.pack('>ff', x, y)
    return data

@pytest.mark.perf
@pytest.mark.parametrize("nb_points", [10, 100, 1000, 10000])
def test_performance_triangulation(nb_points):
    point_set_bytes = generer_pointset_aleatoire(nb_points)
    
    start_time = time.time()
    triangulation(point_set_bytes)
    end_time = time.time()
    
    execution_time = end_time - start_time
    
    # Assertions de temps (les seuils seront à ajuster selon votre algo final)
    if nb_points <= 1000:
        assert execution_time < 0.5
    else:
        assert execution_time < 5.0