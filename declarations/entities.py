from engine.entities import Entity
from engine.items import Item
from installed.builtins.declarations.items import healing_potion
from installed.builtins.declarations.spells import fireball
from installed.builtins.declarations.weapons import hero_sword
from models.decorations import Decoration

hero_stats = {
    "builtins:current_health": -1,
    "builtins:max_health": 100,
    "builtins:max_action_points": 10,
    "builtins:base_armor": 50,
    "builtins:physical_attack": 10,
    "builtins:physical_defense": 10,
}

hero = Entity(
    "builtins:hero",
    Decoration("builtins:hero.name",
               "builtins:hero", "builtins:hero.desc"),
    None,
    None,
    "humanoid",
    attributes=hero_stats,

)

hero.weaponry.add_weapon(hero_sword)
hero.weaponry.set_active_weapon(hero_sword.id)
hero.inventory.add_item(healing_potion)

hero.inventory.add_item(Item(**healing_potion.toJson()))
hero.inventory.add_item(Item(**healing_potion.toJson()))
hero.inventory.add_item(Item(**healing_potion.toJson()))

hero.spell_book.add_spell(fireball)

target_dummy = Entity(
    "builtins:target_dummy",
    Decoration("builtins:target_dummy.name", "builtins:target_dummy", "builtins:target_dummy.desc"),
    None,
    None,
    "mechanoid",
    attributes={
        "builtins:current_health": -1,
        "builtins:max_health": 100,
        "builtins:max_action_points": 10,
        "builtins:base_armor": 50,
        "builtins:physical_attack": 10,
        "builtins:physical_defense": 5,
    },
)

target_dummy.inventory.add_item(Item(**healing_potion.toJson()))
