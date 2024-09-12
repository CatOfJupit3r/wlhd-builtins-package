from engine.entities import Entity
from engine.game_hooks import SpellHooks, HookContext
from engine.spells import Spell
from models.exceptions import AbortError
from models.game import Square, Dice, HpChange

custom_hooks = SpellHooks()


@custom_hooks.hook(
    name="hp_change_spell", schema_name="HP_CHANGE"
)
def hp_change_spell(self: HookContext, spell: Spell, caster: Entity, square: str, **_) -> None:
    square = Square.from_str(square)
    target = self.battlefield.get_entity(square)
    if (dice := spell.memory.get('dice')) is not None:
        dice: Dice
        if caster is not None:
            damage = dice.roll(
                caster.get_attribute(spell.memory.get('element_of_hp_change') + '_attack'))
        else:
            damage = dice.roll()
    else:  # if it is a value, then we take it
        damage = spell.memory['value']
    if spell.memory.get('type_of_hp_change') is None:
        raise AbortError("Type of hp change is not defined")
    hp_change = HpChange(damage,
                         spell.memory['type_of_hp_change'] or 'builtins:',
                         spell.memory['element_of_hp_change'],
                         source="spell")
    target.process_hp_change(
        self, hp_change, caster
    )
