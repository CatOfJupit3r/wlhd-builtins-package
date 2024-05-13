from engine.requirements import RequiresTemplates
from engine.spells import Spell
from models.decorations import Decoration

fireball = Spell(
    descriptor="builtins:fireball",
    decoration=Decoration(name="builtins:fireball", sprite="builtins:pyromancy", description="builtins:fireball.desc"),
    cost=1,
    caster_must_be_in_range=[3, 4, 5, 6],
    cooldown=0,
    requires=RequiresTemplates.ANY_SQUARE,
    max_consecutive_uses=1,
    uses_reset_on_cooldown_update=True,
    method_variables={
        "time_thrown_dice": 3,
        "sides_of_dice": 8,
        "type_of_hp_change": "damage",
        "element_of_hp_change": "builtins:fire"
    },
    effect_hook="builtins:hp_change_spell",
    school="builtins:pyromancy"
)
