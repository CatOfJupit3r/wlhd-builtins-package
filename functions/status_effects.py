import copy
from typing import Literal


from engine.entities import Entity
from engine.game_hooks import HookContext, StatusEffectHooks
from engine.status_effects import StatusEffect
from models.exceptions import AbortError
from models.game import HpChange, Dice

custom_hooks: StatusEffectHooks = StatusEffectHooks()


@custom_hooks.hook(name="default_apply_function", schema_name="APPLY")
def default_apply_function(hooks: HookContext, applied_to: Entity, applied_by: Entity, status_effect: StatusEffect,
                           **kwargs) -> None:
    if applied_to is None:
        raise AbortError(
            "builtins:apply_effect_has_no_target",
            component_name=status_effect.get_name()
        )
    status_effect.owner = copy.deepcopy(applied_by)
    status_effect.applied_to_id = applied_to.id
    if status_effect.descriptor not in applied_to.status_effects:
        hooks.add_status_effect(status_effect, applied_to)
        if status_effect.activates_on_apply is True:
            return status_effect.activate(hooks, **kwargs)
        return None
    else:
        if status_effect.duration is not None:
            if status_effect.duration > applied_to.status_effects[status_effect.descriptor].duration:
                applied_to.status_effects[status_effect.descriptor].duration = status_effect.duration
        return None


@custom_hooks.hook(name="default_dispel_function", schema_name="DISPEL")
def default_dispel_function(hooks: HookContext, status_effect: StatusEffect, applied_to: Entity, **_) -> None:
    if applied_to is not None:
        hooks.remove_status_effect(status_effect, applied_to)
    return None


@custom_hooks.hook(name="default_activate_function", schema_name="ACTIVATE")
def default_activate_function(hooks: HookContext, status_effect: StatusEffect, applied_to: Entity, **_) -> None:
    return None


@custom_hooks.hook(name="default_update_function", schema_name="UPDATE")
def default_update_function(hooks: HookContext, status_effect: StatusEffect, applied_to: Entity, **_) -> None:
    if status_effect.duration is not None:
        status_effect.duration -= 1
        if status_effect.duration <= 0:
            status_effect.dispel(hooks)


"""

STATUS EFFECTS THAT APPLY ANOTHER STATUS EFFECT

"""


@custom_hooks.hook(name="apply_status_effect_activate", schema_name="ACTIVATE")
def apply_status_effect_activate(hooks: HookContext, status_effect: StatusEffect, applied_to: Entity, **_):
    # status_effect_data = status_effect.memory['debuff']
    # status_effect_to_apply = StatusEffect.fromJson(status_effect_data)
    # apply_to = hooks.battlefield.get_entity_by_id(status_effect["apply_to_id"])

    # entity_had_status_effect = (
    #         status_effect_to_apply.update_type == status_effect_to_apply.activation_type and
    #         apply_to is not None and  # check if target is even valid
    #         apply_to.status_effects.get_effect_by_descriptor(status_effect_to_apply.descriptor) is not None
    # # and if it has the status effect
    # )
    # # its either this or I make delayed activation in trigger_status_effect
    # # if SE applies inner SE to target that already has it and update_type is the same, then it will not treat them as separate SEs
    #
    # # okay, maybe I should use delay eventually... This can cause unexpected behavior when some
    # # maybe I get delayed array in trigger_status_effect, add them here and then go over them in trigger (if there are any)
    # status_effect_to_apply.apply(hooks, applied_by=status_effect.owner, applied_by_effect=status_effect,
    #                              applied_to=apply_to)
    # if entity_had_status_effect is not None:
    #     applied_status = apply_to.status_effects.get_effect_by_descriptor(status_effect_to_apply.descriptor)
    #     if applied_status is None:
    #         return None
    #     applied_status.duration += 1

    """

    For now, this hook is broken due to new API changes.

    """

    return None


"""

ATTRIBUTE CHANGING STATUS EFFECTS

"""


@custom_hooks.hook(name="attribute_change_activate", schema_name="ACTIVATE")
def attribute_change_activate(hooks: HookContext, status_effect: StatusEffect, applied_to: Entity, changed_for: Entity,
                              **_):
    changed_for.change_attribute(hooks, status_effect.memory['attribute'],
                                 status_effect.memory['value'])
    return status_effect.memory['value']


@custom_hooks.hook(name="attribute_change_dispel", schema_name="DISPEL")
def attribute_change_dispel(hooks: HookContext, status_effect: StatusEffect, applied_to: Entity, **_):
    applied_to.change_attribute(hooks, status_effect.memory['attribute'],
                                -status_effect.memory['value'])
    return default_dispel_function(hooks, status_effect, applied_to=applied_to)


"""

STATUSES THAT CHANGE HEALTH OF TARGET BY A CERTAIN VALUE

"""


@custom_hooks.hook(name="hp_change_by_value_activate", schema_name="ACTIVATE")
def hp_change_by_value_activate(hooks: HookContext, status_effect: StatusEffect, changed_for: Entity,
                                applied_to: Entity, **_):
    if status_effect.owner is not None:
        damage = status_effect.memory["value"] + status_effect.owner.get_attribute(
            status_effect["element_of_hp_change"] + '_attack')
    else:
        damage = status_effect.memory["value"]
    hp_change = HpChange(
        value=damage,
        type_of_hp_change=status_effect.memory['type_of_hp_change'],
        element_of_hp_change=status_effect.memory['element_of_hp_change'],
        source="status_effect",
    )
    changed_for.process_hp_change(hooks, hp_change, status_effect.owner)
    return damage


"""

STATUSES THAT CHANGE HEALTH OF TARGET BY A DICE ROLL VALUE

"""


@custom_hooks.hook(name="hp_change_dice_activate", schema_name="ACTIVATE")
def hp_change_dice_activate(hooks: HookContext, status_effect: StatusEffect, applied_to: Entity, changed_for: Entity,
                            **_):
    damage_dice_roll = Dice(status_effect.memory['time_thrown_dice'],
                            status_effect.memory['sides_of_dice'])
    if status_effect.owner is not None:
        damage = damage_dice_roll.roll(
            status_effect.owner.get_attribute(status_effect.memory['element_of_hp_change'] + '_attack'))
    else:
        damage = damage_dice_roll.roll()
    hp_change = HpChange(
        value=damage,
        type_of_hp_change=status_effect.memory['type_of_hp_change'],
        element_of_hp_change=status_effect.memory['element_of_hp_change'],
        source="status_effect",
    )
    changed_for.process_hp_change(hooks, hp_change, status_effect.owner)
    return damage


"""

SHIELD STATUS EFFECT

"""


@custom_hooks.hook(name="shield_activate", schema_name="ACTIVATE")
def shield_activate(hooks: HookContext, status_effect: StatusEffect, applied_to: Entity, changed_for: Entity,
                    hp_change: HpChange,
                    **_):  # TODO: Test if lowers damage
    shield_doesnt_block_this_type = hp_change.type_of_hp_change not in status_effect.memory["absorb_type"]
    if_doesnt_blocks_every_type = status_effect.memory["absorb_type"] != "all"
    if shield_doesnt_block_this_type or if_doesnt_blocks_every_type:
        return None
    remaining_hp_of_shield = status_effect.memory["shield_hp"] - HpChange.value
    needs_to_be_dispelled = False
    if remaining_hp_of_shield == 0 or remaining_hp_of_shield < 0:
        needs_to_be_dispelled = True
        if remaining_hp_of_shield < 0:
            hp_change.value = abs(remaining_hp_of_shield)
        else:
            hp_change.value = 0
    else:
        status_effect.memory.change("shield_hp", remaining_hp_of_shield)
        hp_change.value = 0
    return status_effect.dispel(hooks) if needs_to_be_dispelled else None


"""

STATUSES THAT CHANGE STATE OF TARGET

"""


@custom_hooks.hook(name="state_change_activate", schema_name="ACTIVATE")
def state_change_activate(hooks: HookContext, status_effect: StatusEffect, applied_to: Entity, changed_for: Entity,
                          **kwargs):
    for _ in range(status_effect.memory.get('times')) or 1:
        mode = status_effect.memory.get('mode')
        if mode is None or mode not in ["+", "-"]:
            mode = "+"
        changed_for.change_state(status_effect.memory['state'], mode)


@custom_hooks.hook(name="state_change_dispel", schema_name="DISPEL")
def state_change_dispel(hooks: HookContext, status_effect: StatusEffect, applied_to: Entity, **_):
    if status_effect.descriptor in applied_to.status_effects and status_effect.static is False:
        inverse_mode: Literal["+", "-"] = "-" if status_effect.memory['mode'] == "+" else "+"
        for _ in range(status_effect.memory.get('times')) or 1:
            applied_to.change_state(status_effect.memory['state'], inverse_mode)
    return default_dispel_function(hooks, status_effect, applied_to=applied_to)


"""

SUMMON-RELATED STATUS EFFECTS

"""


@custom_hooks.hook(name="summoned_with_deletion_activate", schema_name="ACTIVATE")
def summoned_with_deletion_apply(hooks: HookContext, applied_to: Entity, applied_by: Entity,
                                 status_effect: StatusEffect, **kwargs):
    debuff_duration = status_effect.memory.get("turns_until_deletion") or 1
    status_effect.duration = debuff_duration
    return default_apply_function(
        hooks, applied_to, applied_by, status_effect, **kwargs
    )


@custom_hooks.hook(name="summoned_with_deletion_dispel", schema_name="DISPEL")
def summoned_with_deletion_dispel(hooks: HookContext, status_effect: StatusEffect, applied_to: Entity, **kwargs):
    for _ in range(10):
        applied_to.change_state("builtins:alive", "-")
    return default_dispel_function(hooks, status_effect, **kwargs)
