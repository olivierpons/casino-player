# Suivi des Statistiques de Joueur de Casino

Un module d'extension Python C pour le suivi des statistiques des joueurs de roulette avec une gestion optimisée de la mémoire et des performances.

## Aperçu

Ce module fournit une classe `Player` qui suit et analyse efficacement les sessions de jeu de roulette. Toutes les valeurs monétaires sont stockées en centimes pour garantir des calculs précis et éviter les problèmes d'arithmétique à virgule flottante.

## Fonctionnalités

- Suivi des résultats des jeux, des mises et des numéros joués
- Maintien d'un solde bancaire en temps réel
- Génération de statistiques complètes incluant :
  - Nombre total de parties jouées
  - Profit/perte total
  - Profit maximum sur une partie
  - Perte maximale sur une partie
  - Nombre de victoires et pourcentage de réussite

## Détails Techniques

- Écrit en C pour des performances optimales
- Utilise l'API C de Python pour une intégration transparente
- Stockage efficace de l'historique des jeux
- Toutes les valeurs monétaires stockées en centimes pour la précision
- Types et documentation via fichier stub .pyi

## Compilation et Installation

### Option 1 : Utilisation du Script Python (Recommandé)
```bash
# Rendre le script exécutable
chmod +x rebuild.py

# Exécuter le script de build
./rebuild.py
```

### Option 2 : Utilisation de Make
```bash
# Compiler et installer tout
make all

# OU étape par étape :
make clean    # Nettoyer les builds précédents
make build    # Compiler l'extension
make install  # Installer le package
make dev      # Tout construire et lancer les tests
```

### Option 3 : Installation Manuelle
```bash
# Nettoyer les artifacts de build précédents
rm -rf build/ dist/ casino_player.egg-info/

# Compiler et installer
python3 -m pip install -e .
```

## Exemple d'Utilisation

```python
from casino_player import Player

# Créer un joueur avec un solde initial de 1000,00 €
player = Player(100000)  # Montant en centimes

# Ajouter des résultats de jeu (profit/perte en centimes, mise en centimes, numéro joué)
player.add_game(3500, 100, 17)   # Gagné 35,00 € sur une mise de 1,00 € sur le numéro 17
player.add_game(-200, 200, 24)   # Perdu 2,00 € sur une mise de 2,00 € sur le numéro 24

# Obtenir les statistiques
stats = player.get_stats()
print(f"Total des parties : {stats['total_games']}")
print(f"Taux de réussite : {stats['win_rate']}%")

# Accéder à l'historique
history = player.get_history()        # Liste des résultats de jeu
bet_sizes = player.get_bet_sizes()    # Liste des montants des mises
numbers = player.get_numbers_bet()    # Liste des numéros joués
bankroll = player.get_bankroll()      # Solde actuel
```

## Structure du Projet

- `roulette-player.c` : Code source C du module d'extension
- `casino_player.pyi` : Types et documentation détaillée
- `test_memory.py` : Script de test basique
- `setup.py` et `setup.cfg` : Fichiers de configuration de build
- `pyproject.toml` : Métadonnées du projet et exigences du système de build
- `rebuild.py` : Script utilitaire pour la compilation et l'installation
- `Makefile` : Commandes make pour la compilation et les tests

## Outils de Développement

### rebuild.py
Un script Python qui automatise le processus de build :
- Nettoie les anciens artifacts de build
- Met à jour les outils de build
- Recompile l'extension
- Installe le package
- Lance les tests
- Fournit un retour clair sur la progression

### Makefile
Fournit des commandes courantes de développement :
- `make clean` : Supprime les artifacts de build
- `make build` : Compile l'extension
- `make install` : Installe le package
- `make all` : Nettoie, compile et installe
- `make dev` : Construit tout et lance les tests
