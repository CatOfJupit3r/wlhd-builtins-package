from engine.items import Item
from installed.builtins.declarations.items import healing_potion
from installed.builtins.declarations.spells import fireball
from installed.builtins.declarations.weapons import hero_sword
from engine.entities import Entity
from models.decorations import Decoration

hero_stats = {
    "builtins:max_health": 100,
    "builtins:max_action_points": 10,
    "builtins:base_armor": 50,
    "builtins:physical_attack": 10,
    "builtins:physical_defense": 10,
}

hero = Entity("builtins:hero",
              Decoration("builtins:hero",
                         "builtins:hero"),
              None,
              None,
              "humanoid",
              attributes=hero_stats,
              )


hero.weaponry.add_weapon(hero_sword)
hero.inventory.add_item(healing_potion)

hero.inventory.add_item(Item(**healing_potion.toJson()))
hero.inventory.add_item(Item(**healing_potion.toJson()))
hero.inventory.add_item(Item(**healing_potion.toJson()))

hero.spell_book.add_spell(fireball)
