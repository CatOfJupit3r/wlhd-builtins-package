from engine.requirements import RequiresTemplates
from engine.weapons.weapon import Weapon
from models.decorations import Decoration
from models.game import Ranges

weapon_error = Weapon(
    descriptor="builtins:weapon_error",
    decoration=Decoration(name="builtins:weapon_error", sprite="builtins:weapon_error"),
    usage_cost=0,
    cooldown=0,
    is_consumable=False,
    quantity=1,
    caster_must_be_in_range=Ranges.ALL,
    method_variables={},
    applies=[],
    effect_hook="builtins:dummy_weapon",
    cost_to_switch=1,
    requirements=None
)

regular_sword = Weapon(
    descriptor="builtins:sword",
    decoration=Decoration(name="builtins:sword", sprite="builtins:sword"),
    usage_cost=1,
    cooldown=0,
    is_consumable=False,
    quantity=1,
    caster_must_be_in_range=Ranges.MELEE,
    method_variables={
        "time_thrown_dice": 1,
        "sides_of_dice": 6,
        "type_of_hp_change": "damage",
        "element_of_hp_change": "builtins:physical"
    },
    applies=[],
    effect_hook="builtins:hp_change_weapon",
    cost_to_switch=1,
    requirements=RequiresTemplates.ANY_MELEE
)

hero_sword = Weapon(
    descriptor="builtins:hero_sword",
    decoration=Decoration(name="builtins:sword", sprite="builtins:sword"),
    usage_cost=1,
    cooldown=0,
    is_consumable=False,
    quantity=1,
    caster_must_be_in_range=Ranges.MELEE,
    method_variables={
        "time_thrown_dice": 3,
        "sides_of_dice": 8,
        "type_of_hp_change": "damage",
        "element_of_hp_change": "builtins:fire"
    },
    applies=[],
    effect_hook="builtins:hp_change_weapon",
    cost_to_switch=1,
    requirements=RequiresTemplates.ANY_MELEE
)
