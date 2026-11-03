"""Outils partagés par les tests : lecture de la réponse binaire Triangles."""

import struct


def encoder_pointset(points):
    """Encode une liste de points (x, y) au format binaire PointSet."""
    donnees = [struct.pack(">I", len(points))]
    donnees.extend(struct.pack(">ff", x, y) for x, y in points)
    return b"".join(donnees)


def _produit_vectoriel(a, b, c):
    """Renvoie le double de l'aire signée du triangle (a, b, c)."""
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def aire_triangle(a, b, c):
    """Renvoie l'aire du triangle (a, b, c)."""
    return abs(_produit_vectoriel(a, b, c)) / 2


def _arete_separe(premier, second):
    """Indique si une arête de `premier` laisse `second` entièrement à l'extérieur.

    Si une telle arête existe, elle sépare les deux triangles : ils peuvent se
    toucher sur un bord ou un sommet, mais leurs intérieurs ne se recouvrent pas.
    """
    # En sens direct, l'intérieur du triangle est à gauche de chaque arête.
    a, b, c = premier
    if _produit_vectoriel(a, b, c) < 0:
        b, c = c, b
    # Un produit vectoriel négatif ou nul place le sommet à droite de l'arête ou dessus.
    return any(
        all(_produit_vectoriel(p, q, sommet) <= 0 for sommet in second)
        for p, q in ((a, b), (b, c), (c, a))
    )


def triangles_se_chevauchent(premier, second):
    """Indique si les intérieurs de deux triangles se recouvrent."""
    return not (_arete_separe(premier, second) or _arete_separe(second, premier))


def decoder_triangles(donnees):
    """Décode strictement une réponse Triangles en liste de triangles.

    La réponse se compose de deux parties :
    - les sommets : nombre de points (4 octets), puis 8 octets par point ;
    - les triangles : nombre de triangles (4 octets), puis 12 octets par triangle.

    Lève une AssertionError si la réponse ne respecte pas ce format.
    """
    assert isinstance(donnees, bytes), "Triangles doit être de type bytes"

    # Première partie : on calcule où finissent les sommets.
    assert len(donnees) >= 4, "Entête des sommets incomplète"
    nb_points = struct.unpack_from(">I", donnees, 0)[0]
    fin_points = 4 + 8 * nb_points

    # Seconde partie : la taille doit être exacte, sans octet manquant ni en trop.
    assert len(donnees) >= fin_points + 4, "Nombre de triangles absent"
    nb_triangles = struct.unpack_from(">I", donnees, fin_points)[0]
    assert len(donnees) == fin_points + 4 + 12 * nb_triangles, "Taille incohérente"

    # Chaque triangle est un triplet d'indices de sommets.
    return list(struct.iter_unpack(">III", donnees[fin_points + 4 :]))


def triangles_normalises(donnees):
    """Renvoie les triangles triés, pour comparer sans imposer d'ordre."""
    return sorted(tuple(sorted(t)) for t in decoder_triangles(donnees))
