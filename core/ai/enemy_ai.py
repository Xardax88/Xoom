# ...existing code...
from utils.visibility import Visibility

# ...existing code...


def can_see_player(enemy_pos, player_pos, obstacles):
    """
    Determina si el enemigo puede ver al jugador usando la clase Visibility.
    """
    return Visibility.is_visible(enemy_pos, player_pos, obstacles)


# ...existing code...
