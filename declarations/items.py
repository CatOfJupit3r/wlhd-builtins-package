from engine.items import Item
from engine.requirements import RequiresTemplates
from models.decorations import Decoration
from models.game import Ranges

item_error = Item(
    descriptor="builtins:error",
    decoration=Decoration(name="builtins:error", sprite="builtins:error"),
    usage_cost=1,
    cooldown_value=999,
    is_consumable=False,
    quantity=1,
    caster_must_be_in_range=Ranges.ALL,
)


healing_potion = Item(
    descriptor="builtins:healing_potion",
    decoration=Decoration(name="builtins:healing_potion", sprite="builtins:potion"),
    usage_cost=1,
    cooldown_value=1,
    is_consumable=True,
    quantity=1,
    caster_must_be_in_range=Ranges.ALL,
    effect_hook="builtins:hp_change_item",
    method_variables={
        "time_thrown_dice": 1,
        "sides_of_dice": 6,
        "type_of_hp_change": "heal",
        "element_of_hp_change": "builtins:physical"
    },
    requirements=RequiresTemplates.ANY_SQUARE
)
