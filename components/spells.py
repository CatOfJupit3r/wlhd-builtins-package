from engine.component_memory import MemoryFactory
from engine.game_hooks import SpellComponentsHolder
from engine.game_hooks.component_holder.game_component import SpellGameComponent
from engine.requirements import RequiresTemplates
from models.decorations import Decoration
from models.game import Ranges

holder = SpellComponentsHolder()

spell_error = SpellGameComponent(
    'spell_error',
    {
        "decorations": Decoration(name="builtins:spell_error", sprite="builtins:spell_error",
                                  description="builtins:spell_error.desc"),
        "usage_cost": 999,
        "cooldown_value": 999,
        "effect_hook": "builtins:default_spell_hook",
    },
)

fireball = SpellGameComponent(
    'fireball',
    {
        "decorations": Decoration(name="builtins:fireball", sprite="builtins:pyromancy",
                                  description="builtins:fireball.desc"),
        "usage_cost": 1,
        "caster_must_be_in_range": Ranges.ALL_EXCEPT_SAFE,
        "cooldown_value": 0,
        "requirements": RequiresTemplates.ANY_SQUARE.toJson(),
        "max_consecutive_uses": 1,
        "consecutive_uses_reset_on_cooldown_update": True,
        "effect_hook": "builtins:hp_change_spell",
        "tags": ["builtins:pyromancy"],
    },
).with_memory(
    dice=MemoryFactory.dice(3, 8, "builtins:fireball.dice", False),
    type_of_hp_change=MemoryFactory.string("damage", "builtins:type_of_hp_change", False),
    element_of_hp_change=MemoryFactory.string("builtins:fire", "builtins:element_of_hp_change", False),
)

holder.add(fireball, 'fireball')
holder.add(spell_error, 'spell_error')
