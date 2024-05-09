import copy
import inspect
import sys

from engine.entities.entity import Entity
from engine.hook_context import HookContext
from engine.hook_holder.status_effect_hooks import StatusEffectHooks
from engine.status_effects.status_effect import StatusEffect
from engine.utils.extract_hooks import extract_hooks
from models.game import HpChange, Dice


custom_hooks: StatusEffectHooks = StatusEffectHooks()


@custom_hooks.apply_hook(name="default_apply_function")
def default_apply_function(hooks: HookContext, applied_to: Entity, applied_by: Entity, status_effect: StatusEffect, **_) -> None:
    if applied_to is None:
        raise ValueError("No target!")
    status_effect.owner = copy.deepcopy(applied_by)
    status_effect.applied_to_id = applied_to.id
    if status_effect.descriptor not in applied_to.status_effects:
        applied_to.status_effects.add_effect(status_effect)
        if status_effect.activates_when_applied is True:
            return status_effect.activate(hooks)
        return None
    else:
        if status_effect.duration is not None:
            if status_effect.duration > applied_to.status_effects[status_effect.descriptor].duration:
                applied_to.status_effects[status_effect.descriptor].duration = status_effect.duration
        return None
        

@custom_hooks.dispel_hook(name="default_dispel_function")
def default_dispel_function(hooks: HookContext, status_effect: StatusEffect, applied_to: Entity, **_) -> None:
    if applied_to is not None:
        applied_to.status_effects.remove_effect(status_effect)
    return None


@custom_hooks.activate_hook(name="default_activate_function")
def default_activate_function(hooks: HookContext, status_effect: StatusEffect, **_) -> None:
    return None


@custom_hooks.update_hook(name="default_update_function")
def default_update_function(hooks: HookContext, status_effect: StatusEffect, **_) -> None:
    if status_effect.duration is not None:
        status_effect.duration -= 1
        if status_effect.duration <= 0:
            status_effect.dispel(hooks)


"""

STATUS EFFECTS THAT APPLY ANOTHER STATUS EFFECT

"""


@custom_hooks.activate_hook(name="apply_status_effect_activate")
def apply_status_effect_activate(hooks: HookContext, status_effect: StatusEffect, **_):
    status_effect_data = status_effect.method_variables['debuff']
    status_effect_to_apply = StatusEffect(status_effect_data['descriptor']).fromJson(status_effect_data)
    apply_to = hooks.battlefield.get_entity_by_id(status_effect["apply_to_id"])

    entity_had_status_effect = (
            status_effect_to_apply.update_type == status_effect_to_apply.activation_type and
            apply_to is not None and  # check if target is even valid
            apply_to.status_effects.get_effect_by_descriptor(status_effect_to_apply.descriptor) is not None # and if it has the status effect
    )
    # its either this or I make delayed activation in trigger_status_effect
    # if SE applies inner SE to target that already has it and update_type is the same, then it will not treat them as separate SEs

    # okay, maybe I should use delay eventually... This can cause unexpected behavior when some
    # maybe I get delayed array in trigger_status_effect, add them here and then go over them in trigger (if there are any)
    status_effect_to_apply.apply(hooks, applied_by=status_effect.owner, applied_by_effect=status_effect, applied_to=apply_to)
    if entity_had_status_effect is not None:
        applied_status = apply_to.status_effects.get_effect_by_descriptor(status_effect_to_apply.descriptor)
        if applied_status is None:
            return None
        applied_status.duration += 1
    return None


"""

ATTRIBUTE CHANGING STATUS EFFECTS

"""


@custom_hooks.activate_hook(name="attribute_change_activate")
def attribute_change_activate(hooks: HookContext, status_effect: StatusEffect, changed_for: Entity, **_):
    changed_for.change_attribute(hooks, status_effect.method_variables['attribute'], status_effect.method_variables['value'])
    return status_effect.method_variables['value']


@custom_hooks.dispel_hook(name="attribute_change_dispel")
def attribute_change_dispel(hooks: HookContext, status_effect: StatusEffect, applied_to: Entity, *_):
    applied_to.change_attribute(hooks, status_effect.method_variables['attribute'], -status_effect.method_variables['value'])
    return default_dispel_function(hooks, status_effect, applied_to=applied_to)


"""

STATUSES THAT CHANGE HEALTH OF TARGET BY A CERTAIN VALUE

"""


@custom_hooks.activate_hook(name="hp_change_by_value_activate")
def hp_change_by_value_activate(hooks: HookContext, status_effect: StatusEffect, changed_for: Entity, **_):
    if status_effect.owner is not None:
        damage = status_effect.method_variables["value"] + status_effect.owner.get_attribute(status_effect["element_of_hp_change"] + '_attack')
    else:
        damage = status_effect.method_variables["value"]
    hp_change = HpChange(
        value=damage,
        type_of_hp_change=status_effect.method_variables['type_of_hp_change'],
        element_of_hp_change=status_effect.method_variables['element_of_hp_change'],
        source="status_effect",
    )
    changed_for.process_hp_change(hooks, hp_change, status_effect.owner)
    return damage


"""

STATUSES THAT CHANGE HEALTH OF TARGET BY A DICE ROLL VALUE

"""


@custom_hooks.activate_hook(name="hp_change_dice_activate")
def hp_change_dice_activate(hooks: HookContext, status_effect: StatusEffect, changed_for: Entity, **_):
    damage_dice_roll = Dice(status_effect.method_variables['time_thrown_dice'], status_effect.method_variables['sides_of_dice'])
    if status_effect.owner is not None:
        damage = damage_dice_roll.roll(status_effect.owner.get_attribute(status_effect.method_variables['element_of_hp_change'] + '_attack'))
    else:
        damage = damage_dice_roll.roll()
    hp_change = HpChange(
        value=damage,
        type_of_hp_change=status_effect.method_variables['type_of_hp_change'],
        element_of_hp_change=status_effect.method_variables['element_of_hp_change'],
        source="status_effect",
    )
    changed_for.process_hp_change(hooks, hp_change, status_effect.owner)
    return damage


"""

SHIELD STATUS EFFECT

"""


@custom_hooks.activate_hook(name="shield_activate")
def shield_activate(hooks: HookContext, status_effect: StatusEffect, changed_for: Entity, hp_change, **_): # TODO: Test if lowers damage
    shield_doesnt_block_this_type = hp_change.type_of_hp_change not in status_effect.method_variables["absorb_type"]
    if_doesnt_blocks_every_type = status_effect.method_variables["absorb_type"] != "all"
    if shield_doesnt_block_this_type or if_doesnt_blocks_every_type:
        return None
    remaining_hp_of_shield = status_effect.method_variables["shield_hp"] - HpChange.value
    needs_to_be_dispelled = False
    if remaining_hp_of_shield == 0 or remaining_hp_of_shield < 0:
        needs_to_be_dispelled = True
        if remaining_hp_of_shield < 0:
            hp_change.value = abs(remaining_hp_of_shield)
        else:
            hp_change.value = 0
    else:
        status_effect.method_variables["shield_hp"] = remaining_hp_of_shield
        hp_change.value = 0
    return status_effect.dispel(hooks) if needs_to_be_dispelled else None


"""

STATUSES THAT CHANGE STATE OF TARGET

"""


@custom_hooks.activate_hook(name="state_change_activate")
def state_change_activate(hooks: HookContext, status_effect: StatusEffect, changed_for: Entity, **_):
    changed_for.change_state(status_effect.method_variables['state'], "+")


@custom_hooks.dispel_hook(name="state_change_dispel")
def state_change_dispel(hooks: HookContext, status_effect: StatusEffect, applied_to: Entity, **_):
    if status_effect.descriptor in applied_to.status_effects and status_effect.static is False:
        applied_to.change_state(status_effect.method_variables['state'], "-")
    return default_dispel_function(hooks, status_effect, applied_to=applied_to)


"""

SUMMON-RELATED STATUS EFFECTS

"""


@custom_hooks.activate_hook(name="summoned_with_deletion_activate")
def summoned_with_deletion_apply(hooks: HookContext, applied_to: Entity, applied_by: Entity, status_effect: StatusEffect, **kwargs):
    debuff_duration = status_effect.method_variables["turns_until_deletion"]
    status_effect.duration = debuff_duration
    return default_apply_function(
        hooks, applied_to, applied_by, status_effect, **kwargs
    )


@custom_hooks.dispel_hook(name="summoned_with_deletion_dispel")
def summoned_with_deletion_dispel(hooks: HookContext, status_effect: StatusEffect, applied_to: Entity, **kwargs):
    for _ in range(10):
        applied_to.change_state("builtins:alive", "-")
    return default_dispel_function(hooks, status_effect, **kwargs)
