from engine.component_memory import MemoryFactory
from engine.game_hooks import ItemComponentsHolder
from engine.game_hooks.component_holder.game_component import ItemGameComponent
from engine.requirements import RequiresTemplates
from models.decorations import Decoration
from models.game import Ranges

holder = ItemComponentsHolder()

item_error = ItemGameComponent(
    'error',
    {
        "decorations": Decoration("builtins:error.name", "builtins:error", "builtins:error.desc"),
        "quantity": 1,
        "turnsUntilUsage": 0,
        "currentConsecutiveUses": 0,
        'effectHook': 'builtins:item_effect_template',
        'isConsumable': False,
        'requirements': RequiresTemplates.ANY_SQUARE,
    }
)

healing_potion = ItemGameComponent(
    'healing_potion',
    {
        "decorations": Decoration("builtins:healing_potion.name", "builtins:healing_potion",
                                  "builtins:healing_potion.desc"),
        "quantity": 1,
        "turnsUntilUsage": 0,
        "currentConsecutiveUses": 0,
        'effectHook': 'builtins:hp_change_item',
        'isConsumable': True,
        'usageCost': 1,
        'casterMustBeInRange': Ranges.ALL,
        'requirements': RequiresTemplates.ANY_SQUARE,
        'tags': ['builtins:healing', 'builtins:physical'],
    }
).with_memory(
    dice=MemoryFactory.dice(1, 6, "builtins:healing_potion.dice", False),
)

holder.add(healing_potion, 'healing_potion')
holder.add(item_error, 'error')
