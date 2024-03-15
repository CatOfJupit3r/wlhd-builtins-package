import copy
import inspect
import sys

from engine.entities.entity import Entity
from engine.hook_context import HookContext
from engine.status_effects.status_effect import StatusEffect
from engine.utils.extract_hooks import extract_hooks
from models.game import HpChange, Dice


def default_apply_function(hooks: HookContext, applied_to: Entity, applied_by: Entity, status_effect: StatusEffect, **kwargs) -> None:
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
        

def default_dispel_function(hooks: HookContext, status_effect: StatusEffect, **kwargs) -> None:
    target = kwargs.get("target")
    if target is not None:
        target.status_effects.remove_effect(status_effect)
    return None


def default_activate_function(hooks: HookContext, status_effect: StatusEffect, **kwargs) -> None:
    print(f"Default activate function for {status_effect.descriptor} called")
    return None


def default_update_function(hooks: HookContext, status_effect: StatusEffect, **kwargs) -> None:
    if status_effect.duration is not None:
        status_effect.duration -= 1
        if status_effect.duration <= 0:
            status_effect.dispel(hooks, **kwargs)


"""

STATUS EFFECTS THAT APPLY ANOTHER STATUS EFFECT

"""


def apply_status_effect_activate(hooks: HookContext, status_effect: StatusEffect, **kwargs):
    status_effect_data = status_effect.method_variables['debuff']
    status_effect_to_apply = StatusEffect(status_effect_data['descriptor']).fromJson(status_effect_data)
    entity_had_status_effect = (
            status_effect_to_apply.update_type == status_effect_to_apply.activation_type and
            hooks.battlefield.get_entity_by_id(status_effect.applied_to_id) is not None and  # check if target is even valid
            hooks.battlefield.get_entity_by_id(status_effect.applied_to_id).status_effects.get_effect_by_descriptor(status_effect_to_apply.descriptor) is not None # and if it has the status effect
    )
    # its either this or I make delayed activation in trigger_status_effect
    # if SE applies inner SE to target that already has it and update_type is the same, then it will not treat them as separate SEs

    # okay, maybe I should use delay eventually... This can cause unexpected behavior when some
    # maybe I get delayed array in trigger_status_effect, add them here and then go over them in trigger (if there are any)
    status_effect_to_apply.apply(hooks, applied_by=status_effect.owner, applied_by_effect=status_effect, **kwargs)
    if entity_had_status_effect is not None:
        applied_status = hooks.battlefield.get_entity_by_id(status_effect.applied_to_id).status_effects.get_effect_by_descriptor(status_effect_to_apply.descriptor)
        if applied_status is None:
            return None
        applied_status.duration += 1
    return None


"""

ATTRIBUTE CHANGING STATUS EFFECTS

"""


def attribute_change_activate(hooks: HookContext, status_effect: StatusEffect, **kwargs):
    target: Entity = kwargs.get("target")
    if target is None:
        return 0
    target.change_attribute(hooks, status_effect.method_variables['attribute'], status_effect.method_variables['value'])
    return status_effect.method_variables['value']


def attribute_change_dispel(hooks: HookContext, status_effect: StatusEffect, **kwargs):
    target: Entity = kwargs.get("target")
    if target is None:
        return 0
    target.change_attribute(hooks, status_effect.method_variables['attribute'], -status_effect.method_variables['value'])
    return default_dispel_function(hooks, status_effect, **kwargs)


"""

STATUSES THAT CHANGE HEALTH OF TARGET BY A CERTAIN VALUE

"""


def hp_change_by_value_activate(hooks: HookContext, status_effect: StatusEffect, **kwargs):
    target = kwargs.get("target")
    if target is None:
        return 0
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
    target.process_hp_change(hooks, hp_change, status_effect.owner)
    return damage


"""

STATUSES THAT CHANGE HEALTH OF TARGET BY A DICE ROLL VALUE

"""


def hp_change_dice_activate(hooks: HookContext, status_effect: StatusEffect, **kwargs):
    target = kwargs.get("target")
    if target is None:
        return None
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
    target.process_hp_change(hooks, hp_change, status_effect.owner)
    return damage


"""

SHIELD STATUS EFFECT

"""


def shield_activate(hooks: HookContext, status_effect: StatusEffect, **kwargs): # TODO: Test if lowers damage
    target = kwargs.get("target")
    if target is None:
        return 0
    if kwargs.get("hp_change") is not None:
        hp_change = kwargs.get("hp_change")
    else:
        print(f"No hp change in kwargs for shield_activate. {status_effect.descriptor} for {target.descriptor} ID {target.id}")
        return 0
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
    return status_effect.dispel(hooks, **kwargs) if needs_to_be_dispelled else None


"""

STATUSES THAT CHANGE STATE OF TARGET

"""


def state_change_activate(hooks: HookContext, status_effect: StatusEffect, **kwargs):
    target = kwargs.get("target")
    if target is None:
        return None
    target.change_state(status_effect.method_variables['state'], "+")


def state_change_dispel(hooks: HookContext, status_effect: StatusEffect, **kwargs):
    target = kwargs.get("target")
    if status_effect.descriptor in target.status_effects and status_effect.static is False:
        target.change_state(status_effect.method_variables['state'], "-")
    return default_dispel_function(hooks, status_effect, **kwargs)


"""

SUMMON-RELATED STATUS EFFECTS

"""


def summoned_with_deletion_apply(hooks: HookContext, applied_to: Entity, applied_by: Entity, status_effect: StatusEffect, **kwargs):
    debuff_duration = kwargs.get("debuff_duration", status_effect.method_variables["turns_until_deletion"])
    status_effect.duration = debuff_duration
    return default_apply_function(
        hooks, applied_to, applied_by, status_effect, **kwargs
    )


def summoned_with_deletion_dispel(hooks: HookContext, status_effect: StatusEffect, **kwargs):
    target = kwargs.get("target")
    if target is None:
        return None
    for _ in range(10):
        target.change_state("builtins:alive", "-")
    return default_dispel_function(hooks, status_effect, **kwargs)


"""

DICTIONARY WITH EASY ACCESS TO FUNCTIONS

"""


HOOKS = extract_hooks(inspect.getmembers(sys.modules[__name__]))

    