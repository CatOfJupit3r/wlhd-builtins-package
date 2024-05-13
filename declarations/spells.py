from engine.requirements import RequiresTemplates
from engine.spells import Spell
from models.decorations import Decoration
from models.game import Ranges

spell_error = Spell(
    descriptor="builtins:spell_error",
    decoration=Decoration(name="builtins:spell_error", sprite="builtins:spell_error", description="builtins:spell_error.desc"),
    cost=999,
    cooldown_value=999,
    school="builtins:pyromancy"
)


fireball = Spell(
    descriptor="builtins:fireball",
    decoration=Decoration(name="builtins:fireball", sprite="builtins:pyromancy", description="builtins:fireball.desc"),
    cost=1,
    caster_must_be_in_range=Ranges.ALL_EXCEPT_SAFE,
    cooldown_value=0,
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
