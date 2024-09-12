from engine.component_memory import MemoryFactory
from engine.game_hooks import WeaponComponentsHolder
from engine.game_hooks.component_holder.game_component import WeaponGameComponent
from engine.requirements import RequiresTemplates
from models.game import Ranges
from models.tstring import TString

holder = WeaponComponentsHolder()

weapon_error = WeaponGameComponent(
    'weapon_error',
    {
        "decorations": TString.decorations("builtins:weapon_error", "weapon"),
        "quantity": 1,
        "usageCost": 0,
        "cooldownValue": 0,
        "costToSwitch": 999,
        'effectHook': 'builtins:item_effect_template',
        'isConsumable': False,
        'requirements': RequiresTemplates.ANY_SQUARE
    }
)

regular_sword = WeaponGameComponent(
    'regular_sword',
    {
        "decorations": TString.decorations("builtins:regular_sword", "weapon"),
        "quantity": 1,
        "usageCost": 1,
        "cooldownValue": 0,
        "costToSwitch": 1,
        'effectHook': 'builtins:hp_change_weapon',
        'isConsumable': False,
        'casterMustBeInRange': Ranges.MELEE,
        'requirements': RequiresTemplates.ANY_MELEE
    }
).with_memory(
    dice=MemoryFactory.dice(1, 6, TString.memory('builtins:dice'), False),
    type_of_hp_change=MemoryFactory.string("damage", TString.memory("builtins:type_of_hp_change"), False),
    element_of_hp_change=MemoryFactory.string("builtins:physical", TString.memory("builtins:element_of_hp_change"),
                                              False, TString.hp_change_type('builtins:physical')),
)

hero_sword = WeaponGameComponent(
    'hero_sword',
    {
        "decorations": TString.decorations("builtins:hero_sword", "weapon"),
        "quantity": 1,
        "usageCost": 1,
        "cooldownValue": 0,
        "costToSwitch": 1,
        'effectHook': 'builtins:hp_change_weapon',
        'isConsumable': False,
        'casterMustBeInRange': Ranges.MELEE,
        'requirements': RequiresTemplates.ANY_MELEE,
        'tags': ['builtins:fire'],
    }
).with_memory(
    dice=MemoryFactory.dice(1, 6, TString.memory('builtins:dice'), False),
    type_of_hp_change=MemoryFactory.string("damage", TString.memory("builtins:type_of_hp_change"), False),
    element_of_hp_change=MemoryFactory.string("builtins:fire", TString.memory("builtins:element_of_hp_change"), False,
                                              TString.hp_change_type('builtins:fire')),
)

holder.add(weapon_error, 'weapon_error')
holder.add(regular_sword, 'regular_sword')
holder.add(hero_sword, 'hero_sword')
