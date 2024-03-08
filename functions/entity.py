from engine.entity import Entity
from engine.hook_context import HookContext
from models.game_models import HpChange

"""

def process_hp_change(self, battlefield: Battlefield, creature_who_changes, value: int = 0, type_of_hp_change: str = 'damage', element_of_hp_change: str = 'builtins::physical'):  # TODO: Move
    HpChange = basic_classes.HpChange(value, type_of_hp_change, element_of_hp_change)
    battlefield.trigger_effects((self.line, self.column), activate_type='on_hp_change', update_type='on_hp_change', hp_change=HpChange, triggered_by=creature_who_changes)
    if type_of_hp_change == 'heal':
        battlefield.trigger_effects((self.line, self.column), activate_type='on_healed', update_type='on_healed', hp_change=HpChange, triggered_by=creature_who_changes)
        battlefield.trigger_effects((creature_who_changes.line, creature_who_changes.column), activate_type='on_heal', update_type='on_heal', hp_change=HpChange)
        if HpChange.value > 0:
            if "builtins::fainted" in self.status_effects:
                self.status_effects["builtins::fainted"].dispell(battlefield, self, True)
        self._heal(HpChange.value, battlefield=battlefield)
    else:
        battlefield.trigger_effects((self.line, self.column), activate_type='on_damaged', update_type='on_damaged', hp_change=HpChange, triggered_by=creature_who_changes)
        battlefield.trigger_effects((creature_who_changes.line, creature_who_changes.column), activate_type='on_deal_damage', update_type='on_deal_damage', hp_change=HpChange)
        battlefield.trigger_effects((self.line, self.column), activate_type='shield', update_type='shield', hp_change=HpChange, triggered_by=creature_who_changes)
        self._take_damage(battlefield, HpChange.value, HpChange.element_of_hp_change)


def _take_damage(self, battlefield, damage_number: int, damage_type: str = 'builtins::physical'): # TODO: Move
    if self.get_state('builtins::damageable') is False or damage_number == 0:
        # "CREATURE_NAME takes no damage."
        battlefield.add_cmd("builtins::creature_takes_no_damage", [self.get_name()])
        return 0
    if damage_number < 0:
        raise ValueError
    else:
        if self.get_bonus("current_armor") > 0:
            remaining_armor = self.get_bonus("current_armor") - damage_number
            if remaining_armor <= 0:
                damage_number = abs(remaining_armor)
                # "Armor of NAME broke, blocking BLOCKED_DAMAGE damage. Remaining damage: REMAINING_DAMAGE."
                battlefield.add_cmd("builtins::creature_takes_damage_shield_broken", [self.get_name()], self.get_bonus("current_armor"), damage_number)
                self.set_bonus('current_armor', 0)
            else:
                self.set_bonus('current_armor', remaining_armor)
                damage_number = 0
                # "NAME blocked BLOCKED_DAMAGE damage. Remaining armor: REMAINING_ARMOR."
                battlefield.add_cmd("builtins::creature_takes_damage_shield", [self.get_name()], self.get_bonus("current_armor"), damage_number)
        battlefield.add_cmd("builtins::creature_takes_damage", [self.get_name()], damage_number, [damage_type])
        self.increment_bonus('current_health', -(damage_number - self.get_bonus(damage_type + '_defense')))
        self.adrenaline_fainted_dead_mechanic(battlefield)
        if self.get_bonus("current_health") < 0:
            self.set_bonus('current_health', 0)
    return damage_number


def _heal(self, heal_amount: int, battlefield=None) -> int:  # TODO: Move
    self.increment_bonus("current_health", heal_amount)
    if self.get_bonus('current_health') > self.get_bonus('max_health'):
        self.set_bonus('current_health', self.get_bonus('max_health'))
    # "NAME healed HEAL_AMOUNT hp."
    battlefield.add_cmd("builtins::creature_healed", [self.get_name()], heal_amount) if battlefield is not None else None
    return heal_amount

"""


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


HOOKS = {
    "hp_change": hp_change,
    "attribute_change": attribute_change,
    "spent_action_points": spend_action_points
}
