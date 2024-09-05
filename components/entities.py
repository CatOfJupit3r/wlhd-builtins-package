from engine.component_memory import MemoryFactory
from engine.game_hooks import EntityComponentsHolder
from engine.game_hooks.component_holder.game_component import EntityGameComponent
from models.decorations import Decoration

holder = EntityComponentsHolder()

entity_error = EntityGameComponent(
    'entity_error',
    {
        "decorations": Decoration("builtins:error.name", "builtins:error", "builtins:error.desc"),
        "attributes": {
            "builtins:current_health": -1,
            "builtins:max_health": 1,
            "builtins:max_action_points": 1,
        },
        'states': {
            "builtins:can_act": -1,
            "builtins:alive": -1,
        }
    }
)

hero = EntityGameComponent(
    'hero',
    {
        "decorations": Decoration("builtins:hero.name", "builtins:hero", "builtins:hero.desc"),
        "attributes": {
            "builtins:current_health": -1,
            "builtins:max_health": 100,
            "builtins:max_action_points": 10,
            "builtins:base_armor": 50,
            "builtins:physical_attack": 10,
            "builtins:physical_defense": 10,
        },
        "spell_book": {
            "known_spells": [{
                "descriptor": "builtins:fireball",
                "is_active": True,
                "memory": {
                    "linked_item_id": MemoryFactory.component_id("1", "builtins:linked_item_id"),
                    "dice": MemoryFactory.dice(1, 6, "builtins:fireball.dice", False),
                }
            }],
            "max_active_spells": 12,
        },
        "weaponry": [{
            "descriptor": "builtins:hero_sword",
            "quantity": 1,
            "turns_until_usage": 0,
            "current_consecutive_uses": 0,
            "is_active": True,
        }],
        "inventory": [{
            "descriptor": "builtins:healing_potion",
            "quantity": 5,
            "turns_until_usage": 0,
            "current_consecutive_uses": 0,
            "id_": "1",
        },
        ],
        "tags": ["builtins:humanoid"],
    }
)

target_dummy = EntityGameComponent(
    'target_dummy',
    {
        "decorations": Decoration("builtins:target_dummy.name", "builtins:target_dummy", "builtins:target_dummy.desc"),
        "attributes": {
            "builtins:current_health": -1,
            "builtins:max_health": 100,
            "builtins:max_action_points": 10,
            "builtins:base_armor": 50,
            "builtins:physical_attack": 10,
            "builtins:physical_defense": 5,
        },
        "inventory": [{
            "descriptor": "builtins:healing_potion",
            "quantity": 5,
            "turns_until_usage": 0,
            "current_consecutive_uses": 0,
        }],
        "tags": ["builtins:mechanoid"],
    }
)

target_dummy_large = EntityGameComponent(
    'target_dummy_large',
    {
        "decorations": Decoration("builtins:target_dummy.name", "builtins:target_dummy", "builtins:target_dummy.desc"),
        "attributes": {
            "builtins:current_health": -1,
            "builtins:max_health": 250,
            "builtins:max_action_points": 10,
            "builtins:base_armor": 100,
            "builtins:physical_attack": 20,
            "builtins:physical_defense": 10,
        },
        "inventory": [
            {
                "descriptor": "builtins:healing_potion",
                "quantity": 5,
            }
        ],
        "tags": ["builtins:mechanoid"],
    })

holder.add(entity_error, "entity_error")
holder.add(hero, "hero")
holder.add(target_dummy, "target_dummy")
holder.add(target_dummy_large, "target_dummy_large")
