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
        "turns_until_usage": 0,
        "current_consecutive_uses": 0,
        'effect_hook': 'builtins:item_effect_template',
        'is_consumable': False,
        'requirements': RequiresTemplates.ANY_SQUARE.toJson(),
    }
)

healing_potion = ItemGameComponent(
    'healing_potion',
    {
        "decorations": Decoration("builtins:healing_potion.name", "builtins:healing_potion",
                                  "builtins:healing_potion.desc"),
        "quantity": 1,
        "turns_until_usage": 0,
        "current_consecutive_uses": 0,
        'effect_hook': 'builtins:hp_change_item',
        'is_consumable': True,
        'usage_cost': 1,
        'caster_must_be_in_range': Ranges.ALL,
        'requirements': RequiresTemplates.ANY_SQUARE.toJson(),
        'tags': ['builtins:healing', 'builtins:physical'],
    }
).with_memory(
    dice=MemoryFactory.dice(1, 6, "builtins:healing_potion.dice", False),
)

holder.add(healing_potion, 'healing_potion')
holder.add(item_error, 'error')
