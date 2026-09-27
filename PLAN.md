# TODO

On doit realiser le plan des tests pour le composant Triangulator 
Test Unitaires:
   - Tests Triangulation:
    -    Test de triangulation réussi 
        -   différents cas : 3 points qui forment bien un seul triangle; 
            4 points forment bien 2 triangles distincts qui ne se chevauchent pas;
            plus de points tout les points sont bien utilisé et toute la surface est recouverte les triangles ne se chevauchent pas.
            certains points sont alignés mais la triangulation fonctionne bien pour autant;
            Les Triangles correspond bien au PointSet initial
            Les Triangles est bien le resultat attendu 
            Les Triangles est le bon format
            PointSet non conforme nombre de points dans l'entête != nombre points dans le reste du PointSet -> erreur Point set non conforme
    -   Test de triangulation raté 
        -   différents cas :  pas de points -> erreur de PointSet taille insuffisante pas de calcul
            un point -> erreur de PointSet taille insuffisante pas de calcul 
            deux points -> erreur de PointSet taille insuffisante pas de calcul 
            tout les points sont alignés -> erreur de PointSet pas de création de triangle possible
            certains des points ont des coordonnées similaires -> Si moins de 3 poins distincts restant retours aux cas 0,1 ou 2 points pas de calculs, Sinon erreur Triangles superposé pas de calcul. 
            tout les points ont des coordonnées similaires -> taille = 1 retour cas 1 point pas de calcul 
            le Triangle ne correspond pas au PointSet initial -> erreur de Triangulation
            Le Triangle n'a pas la bonne taille -> erreur de Triangulation
            les Triangles est vide -> Erreur Triangulation
            les Triangles pas dans le bon format -> Erreur conversion Triangle 

   
   
   - Tests de Communications/API:
        - Communication avec le client réussi : 
            le UUID n'est pas vide;
            le UUID est dans le bon format
        - Communication avec le client raté :
            Le UUID est vide -> Erreur UUID vide 
            Le UUID n'est pas dans le bon format -> Erreur de Format UUID
            Le point Set Manager est injoignable -> erreur de communication / service injoignable 
            PSM bien repondu mais données corronpu ou mauvais format -> erreur de communcation 

            
            

        
        - Communication avec le SetPointManager reussi :
            Le SPM renvoie bien un SetPoint en echange du UUID
            Le SetPoint est dans le bon format
            Le SetPoint n'est pas vide 
        - Communication avec le SetPointManager raté : 
            Le UUID n'est correspond avec aucun SetPoint -> erreur de UUID


    -   

Tests de Performance :
    -Temps d'exec pour 10; 100 ; 1000; 100000 ;

Test de Couverture
    - coverage run tout le code doit etre couvert
Tests de Qualité et doc 

    -ruff check et pdoc3