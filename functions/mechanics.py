import inspect
import sys

from engine.entity import Entity
from engine.hook_context import HookContext
from engine.utils.extract_hooks import extract_hooks
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
    target.increment_bonus('current_health', value.value)
    if target.get_bonus('current_health') > target.get_bonus('max_health'):
        target.set_bonus('current_health', target.get_bonus('max_health'))
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
        if target.get_bonus("current_armor") > 0:
            remaining_armor = target.get_bonus("current_armor") - value.value
            if remaining_armor <= 0:
                value.value = abs(remaining_armor)
                ctx.add_cmd("builtins:creature_takes_damage_shield_broken", [target.get_name()], target.get_bonus("current_armor"), value.value)
                target.set_bonus('current_armor', 0)
            else:
                target.set_bonus('current_armor', remaining_armor)
                value.value = 0
                ctx.add_cmd("builtins:creature_takes_damage_shield", [target.get_name()], target.get_bonus("current_armor"), value.value)
        ctx.add_cmd("builtins:creature_takes_damage", [target.get_name()], value.value, [value.element_of_hp_change])
        target.increment_bonus('current_health', -(value.value - target.get_bonus(value.element_of_hp_change + '_defense')))
        if target.get_bonus("current_health") < 0:
            target.set_bonus('current_health', 0)
    return value.value


def attribute_change(self: HookContext, target: Entity, name_of_attribute: str, value_to_increment: int, **kwargs) -> int:
    target.increment_bonus(name_of_attribute, value_to_increment)
    # "NAME changed ATTRIBUTE_NAME by VALUE_TO_INCREMENT."
    self.add_cmd("builtins:creature_attribute_changed", [target.get_name()], [name_of_attribute], value_to_increment)
    return value_to_increment


def spend_action_points(self: HookContext, target: Entity, value: int, **kwargs) -> int:
    target.increment_bonus('current_action_points', -value)
    self.add_cmd("builtins:creature_spent_ap", [target.get_name()], value)
    if target.get_bonus("current_action_points") < 0:
        target.set_bonus("current_action_points", 0)
        # target.status_effects.apply_status_effect("builtins::tired", self, None, target)
        self.add_cmd("builtins:creature_tired", [target.get_name()])
    return value


HOOKS = extract_hooks(inspect.getmembers(sys.modules[__name__]))
