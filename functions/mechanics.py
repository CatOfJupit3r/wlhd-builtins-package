import inspect
import sys
import types
from typing import List

from engine.entities.entity import Entity
from engine.hook_context import HookContext
from engine.spells.spell import Spell
from engine.utils.extract_hooks import extract_hooks
from models.exceptions import AbortError
from models.game_models import HpChange


def hp_change(self: HookContext, target: Entity, value: HpChange, changed_by: Entity, **kwargs) -> int:
    self.emit_event('on_hp_change', target=target, value=value, changed_by=changed_by, **kwargs)
    if value.type_of_hp_change == 'heal':
        return _heal(self, target, value, changed_by, **kwargs)
    else:
        return _take_damage(self, target, value, changed_by, **kwargs)


def _heal(ctx: HookContext, target: Entity, value: HpChange, changed_by: Entity, **kwargs) -> int:
    ctx.emit_event('on_healed', target=target, value=value, changed_by=changed_by, **kwargs)
    ctx.emit_event('on_heal', target=target, value=value, changed_by=changed_by, **kwargs)
    # if value.value > 0:
    #     if target.has_effect('builtins:fainted'):
    #         target.status_effects['builtins:fainted'].dispel(ctx, target, True)
    target.increment_attribute('current_health', value.value)
    if target.get_attribute('current_health') > target.get_attribute('max_health'):
        target.set_attribute('current_health', target.get_attribute('max_health'))
    ctx.add_cmd("builtins:creature_healed", [target.get_name()], value.value)
    return value.value


def _take_damage(ctx: HookContext, target: Entity, value: HpChange, changed_by: Entity, **kwargs) -> int:
    ctx.emit_event('on_damaged', target=target, value=value, changed_by=changed_by, **kwargs)
    ctx.emit_event('on_deal_damage', target=target, value=value, changed_by=changed_by, **kwargs)
    ctx.emit_event('shield', target=target, value=value, changed_by=changed_by, **kwargs)
    if target.get_state('builtins:damageable') is False or value.value == 0:
        ctx.add_cmd("builtins:creature_takes_no_damage", [target.get_name()])
        return 0
    if value.value < 0:
        raise ValueError
    else:
        if target.get_attribute("current_armor") > 0:
            remaining_armor = target.get_attribute("current_armor") - value.value
            if remaining_armor <= 0:
                value.value = abs(remaining_armor)
                ctx.add_cmd("builtins:creature_takes_damage_shield_broken", [target.get_name()], target.get_attribute("current_armor"), value.value)
                target.set_attribute('current_armor', 0)
            else:
                target.set_attribute('current_armor', remaining_armor)
                value.value = 0
                ctx.add_cmd("builtins:creature_takes_damage_shield", [target.get_name()], target.get_attribute("current_armor"), value.value)
        ctx.add_cmd("builtins:creature_takes_damage", [target.get_name()], value.value, [value.element_of_hp_change])
        target.increment_attribute('current_health', -(value.value - target.get_attribute(value.element_of_hp_change + '_defense')))
        if target.get_attribute("current_health") < 0:
            target.set_attribute('current_health', 0)
    return value.value


def attribute_change(self: HookContext, target: Entity, name_of_attribute: str, value_to_increment: int, **kwargs) -> int:
    target.increment_attribute(name_of_attribute, value_to_increment)
    # "NAME changed ATTRIBUTE_NAME by VALUE_TO_INCREMENT."
    self.add_cmd("builtins:creature_attribute_changed", [target.get_name()], [name_of_attribute], value_to_increment)
    return value_to_increment


def spend_action_points(self: HookContext, target: Entity, value: int, **kwargs) -> int:
    target.increment_attribute('current_action_points', -value)
    self.add_cmd("builtins:creature_spent_ap", [target.get_name()], value)
    if target.get_attribute("current_action_points") < 0:
        target.set_attribute("current_action_points", 0)
        # target.status_effects.apply_status_effect("builtins::tired", self, None, target)
        self.add_cmd("builtins:creature_tired", [target.get_name()])
    return value


def cast_spell(self: HookContext, caster: Entity, spell_id: str, **requires_parameters) -> int:
    if caster.get_state("builtins:can_spell") is False:
        raise AbortError("creature_cant_spell", caster.get_name())
    caster.spell_book.check_spell(spell_id, caster)
    spell: Spell = caster.spell_book[spell_id]
    spell.current_consecutive_uses += 1
    if spell.max_consecutive_uses is not None and spell.current_consecutive_uses >= spell.max_consecutive_uses:
        spell.turns_until_usage = spell.cooldown_value
        spell.current_consecutive_uses = 0
    self.add_cmd("builtins::spell_usage", [caster.get_name()], [spell.get_name()]) # will probably need a way to pass parameters to this
    usage_result = self.use_hook("SPELL", spell.effect_hook, caster=caster, **requires_parameters)
    if usage_result is None:
        return spell.usage_cost
    return usage_result


def use_item(self: HookContext, user: Entity, item_id: str, **requires_parameters) -> int:
    if user.get_state("builtins:can_item") is False:
        raise AbortError("creature_cant_item", user.get_name())
    user.inventory.check_item(item_id, user)
    item = user.inventory[item_id]
    item.current_consecutive_uses += 1
    if item.max_consecutive_uses is not None and item.current_consecutive_uses >= item.max_consecutive_uses:
        item.turns_until_usage = item.cooldown_value
        item.current_consecutive_uses = 0
    self.add_cmd("builtins::item_usage", [user.get_name()], [item.get_name()]) # will probably need a way to pass parameters to this
    usage_result = self.use_hook("ITEM", item.effect_hook, user=user, **requires_parameters)
    if usage_result is None:
        return item.usage_cost
    return usage_result


def use_attack(self: HookContext, user: Entity, **requires_parameters) -> int:
    if user.get_state("builtins:can_attack") is False:
        raise AbortError("creature_cant_attack", user.get_name())
    self.add_cmd("builtins::attack_usage", [user.get_name()]) # will probably need a way to pass parameters to this
    weapon = user.weaponry.active_weapon_id
    usage_result = self.use_hook("ATTACK", weapon, user=user, **requires_parameters)
    if usage_result is None:
        return 1
    return usage_result


HOOKS = extract_hooks(inspect.getmembers(sys.modules[__name__]))
