import sys
import inspect
from typing import Literal

from engine.entities.entity import Entity
from engine.hook_context import HookContext
from engine.spells.spell import Spell
from engine.status_effects.status_effect import StatusEffect
from engine.utils.extract_hooks import extract_hooks
from engine.weapons.weapon import Weapon
from models.exceptions import AbortError
from models.game import HpChange, Square, Dice


def hp_change(self: HookContext, target: Entity, value: HpChange, changed_by: Entity, **kwargs) -> int:
    self.emit_event('on_hp_change', target=target, value=value, changed_by=changed_by, **kwargs)
    if value.type_of_hp_change == 'heal':
        return _heal(self, target, value, changed_by, **kwargs)
    else:
        return _take_damage(self, target, value, changed_by, **kwargs)


def _heal(ctx: HookContext, target: Entity, value: HpChange, changed_by: Entity, **kwargs) -> int:
    ctx.emit_event('on_healed', changed_for=target, value=value, changed_by=changed_by, **kwargs)
    ctx.emit_event('on_heal', changed_for=target, value=value, changed_by=changed_by, **kwargs)
    if value.value > 0:
        if target.has_effect('builtins:fainted'):
            target.status_effects['builtins:fainted'].dispel(ctx)
    target.increment_attribute('current_health', value.value)
    if target.get_attribute('current_health') > target.get_attribute('max_health'):
        target.set_attribute('current_health', target.get_attribute('max_health'))
    ctx.add_cmd(
        "builtins:creature_healed",
        entity_name=target.get_name(),
        value=str(value.value),
        element_of_hp_change=value.element_of_hp_change
    )
    return value.value


def _take_damage(ctx: HookContext, target: Entity, value: HpChange, changed_by: Entity, **kwargs) -> int:
    ctx.emit_event('on_damaged', changed_for=target, value=value, changed_by=changed_by, **kwargs)
    ctx.emit_event('on_deal_damage', changed_for=target, value=value, changed_by=changed_by, **kwargs)
    ctx.emit_event('shield', changed_for=target, value=value, changed_by=changed_by, **kwargs)
    if target.get_state('builtins:damageable') is False or value.value == 0:
        ctx.add_cmd(
            "builtins:creature_takes_no_damage",
            entity_name=target.get_name()
        )
        return 0
    if value.value < 0:
        value.value = 0
    if target.get_attribute("current_armor") > 0:
        remaining_armor = target.get_attribute("current_armor") - value.value
        if remaining_armor <= 0:
            value.value = abs(remaining_armor)
            ctx.add_cmd(
                "builtins:creature_takes_damage_shield_broken",
                entity_name=target.get_name(),
                armor=str(target.get_attribute("current_armor")),
                damage=str(value.value)
            )
            target.set_attribute('current_armor', 0)
        else:
            target.set_attribute('current_armor', remaining_armor)
            value.value = 0
            ctx.add_cmd(
                "builtins:creature_takes_damage_shield",
                entity_name=target.get_name(),
                armor=str(target.get_attribute("current_armor")),
                damage=str(value.value)
            )
    fainted_dead_mechanic(ctx, target, changed_by, **kwargs)
    ctx.add_cmd(
        "builtins:creature_takes_damage",
        entity_name=target.get_name(),
        value=str(value.value),
        element_of_hp_change=value.element_of_hp_change
    )
    target.increment_attribute('current_health', -(value.value - target.get_attribute(value.element_of_hp_change + '_defense')))
    if target.get_attribute("current_health") < 0:
        target.set_attribute('current_health', 0)
    return value.value


def attribute_change(self: HookContext, target: Entity, name_of_attribute: str, value_to_increment: int, **kwargs) -> int:
    target.increment_attribute(name_of_attribute, value_to_increment)
    # "NAME changed ATTRIBUTE_NAME by VALUE_TO_INCREMENT."
    self.add_cmd(
        "builtins:creature_attribute_changed",
        entity_name=target.get_name(),
        attribute_name=name_of_attribute,
        value=str(value_to_increment)
    )
    return value_to_increment


def spend_action_points(self: HookContext, target: Entity, value: int, **kwargs) -> int:
    target.increment_attribute('current_action_points', -value)
    self.add_cmd(
        "builtins:creature_spent_ap",
        entity_name=target.get_name(),
        value=str(value)
    )
    if target.get_attribute("current_action_points") < 0:
        target.set_attribute("current_action_points", 0)
        apply_status_effect(
            self,
            target,
            "builtins:exhausted"
        )
        self.add_cmd(
            "builtins:creature_exhausted",
            entity_name=target.get_name()
        )
    return value


def cast_spell(self: HookContext, caster: Entity, spell_id: str, **requires_parameters) -> int:
    if caster.get_state("builtins:can_spell") is False:
        raise AbortError(
            "creature_cant_spell",
            entity_name=caster.get_name()
        )
    caster.spell_book.check_spell(spell_id, caster)
    spell: Spell = caster.spell_book[spell_id]
    spell.current_consecutive_uses += 1
    if spell.max_consecutive_uses is not None and spell.current_consecutive_uses >= spell.max_consecutive_uses:
        spell.turns_until_usage = spell.cooldown_value
        spell.current_consecutive_uses = 0
    self.add_cmd(
        "builtins:spell_usage",
        entity_name=caster.get_name(),
        spell_name=spell.get_name()
    ) # will look into passing parameters to this.
    usage_result = self.use_hook("SPELL", spell.effect_hook, caster=caster, **requires_parameters)
    self.trigger_on_spell_cast(spell_=spell, caster=caster, **requires_parameters)
    if usage_result is None:
        return spell.usage_cost
    return usage_result


def use_item(self: HookContext, user: Entity, item_id: str, **requires_parameters) -> int:
    if user.get_state("builtins:can_item") is False:
        raise AbortError(
            "creature_cant_item",
            entity_name=user.get_name()
        )
    user.inventory.check_item(item_id, user)
    item = user.inventory[item_id]
    item.current_consecutive_uses += 1
    if item.max_consecutive_uses is not None and item.current_consecutive_uses >= item.max_consecutive_uses:
        item.turns_until_usage = item.cooldown_value
        item.current_consecutive_uses = 0
    self.add_cmd(
        "builtins:item_usage",
        entity_name=user.get_name(),
        item_name=item.get_name()
    )
    usage_result = self.use_hook("ITEM", item.effect_hook, user=user, **requires_parameters)
    self.trigger_on_item_use(item_=item, used_by=user, **requires_parameters)
    if usage_result is None:
        return item.usage_cost
    return usage_result


def use_attack(self: HookContext, user: Entity, **requires_parameters) -> int:
    if user.get_state("builtins:can_attack") is False:
        raise AbortError(
            "builtins:creature_cant_attack",
            entity_name=user.get_name())
    self.add_cmd(
        "builtins:attack_usage",
        entity_name=user.get_name()
    )
    weapon_d: str = user.weaponry.active_weapon_id
    user.weaponry.check_weapon(weapon_d, user)
    weapon: Weapon = user.weaponry[weapon_d]
    usage_result = self.use_hook(
        "WEAPON",
        weapon.effect_hook,
        weapon=weapon,
        weapon_user=user,
        **requires_parameters,
    )
    self.trigger_on_attack(weapon_=weapon, attacker=user, **requires_parameters)
    if usage_result is None:
        return 1
    return usage_result


def use_defense(self: HookContext, user: Entity, **requires_parameters) -> int:
    if user.get_state("builtins:can_defend") is False:
        raise AbortError(
            "creature_cant_defend",
            entity_name=user.get_name()
        )
    self.add_cmd(
        "builtins:defense_usage",
        entity_name=user.get_name()
    )
    user.change_attribute(self, "current_armor", 10+user.get_attribute("builtins:armor_bonus"))
    return 1


def use_change_weapon(self: HookContext, user: Entity, weapon_id: str, **_) -> int:
    if user.get_state("builtins:can_change_weapon") is False:
        raise AbortError(
            "creature_cant_change_weapon",
            entity_name=user.get_name()
        )
    self.add_cmd(
        "builtins:change_weapon_usage",
        entity_name=user.get_name()
    )
    if weapon_id not in user.weaponry:
        raise ValueError(f"Weapon with id {weapon_id} not found.")
    weapon = user.weaponry[weapon_id]
    if weapon.cost_to_switch > user.get_attribute("current_action_points"):
        raise ValueError(f"User {user.get_name()} does not have enough action points to switch to weapon {weapon_id}.")
    self.trigger_on_change_weapon(changed_for=user, weapon_=weapon,
                                  previous_weapon=user.weaponry.active_weapon_id)
    user.weaponry.set_active_weapon(weapon_id)
    return weapon.cost_to_switch


def use_movement(self: HookContext, user: Entity, uses_action_points: bool = False, **requires_parameters) -> int:
    if user.get_state("builtins:can_move") is False:
        raise AbortError(
            "creature_cant_move",
            entity_name=user.get_name()
        )
    square = Square().from_str(requires_parameters.get("square", "0/0"))
    if square is None or square.line == 0 or square.column == 0:
        raise AbortError("No square provided")
    if square.line == user.square.line and square.column == user.square.column:
        return user.cost_dictionary["builtins:move"] if uses_action_points else 0
    if uses_action_points and (user.get_attribute("current_action_points") < user.cost_dictionary["builtins:move"]):
        raise AbortError(f"User {user.get_name()} does not have enough action points to move.")
    if self.battlefield.move_entity(user, square) == -1:
        raise AbortError(f"User {user.get_name()} cannot move to square {square}.")
    apply_status_effect(self, user, "builtins:moved", **requires_parameters)
    self.trigger_on_move(square=square, moved_entity=user, moved_by=user)
    self.add_cmd(
        "builtins:movement_usage",
        entity_name=user.get_name(),
        square=str(square)
    )
    return user.cost_dictionary["builtins:move"] if uses_action_points else 0


def use_swap(self: HookContext, first: Square, second: Square) -> int:
    if self.battlefield.swap_entities(first, second) == -1:
        raise AbortError(f"Entities cannot be swapped.")
    self.add_cmd(
        "builtins:swap_usage",
        first=str(first),
        second=str(second)
        )
    apply_status_effect(
        self,
        self.battlefield[first.line, first.column],
        "builtins:moved"
    )
    apply_status_effect(
        self,
        self.battlefield[second.line, second.column],
        "builtins:moved"
    )
    return 1


def add_spell(self: HookContext, user: Entity, spell_id: str, **kwargs):
    spell_preset = self.import_data("SPELL", spell_id)
    if spell_preset is None:
        raise ValueError(f"Spell with id {spell_id} not found.")
    spell = Spell().fromPreset(spell_preset)
    if kwargs.get("silent") is not None:
        self.add_cmd(
            "builtins:add_spell_usage",
            entity_name=user.get_name(),
            spell_name=spell.get_name()
        )
    user.spell_book.add_spell(spell)
    return None


def add_item(self: HookContext, user: Entity, item_id: str, **kwargs):
    item_preset = self.import_data("ITEM", item_id)
    if item_preset is None:
        raise ValueError(f"Item with id {item_id} not found.")
    item = Weapon().fromPreset(item_preset)
    if kwargs.get("silent") is not None and kwargs.get("silent") is True:
        self.add_cmd(
            "builtins:add_item_usage",
            entity_name=user.get_name(),
            item_name=item.get_name()
        )
    user.inventory.add_item(item)
    return None


def add_weapon(self: HookContext, user: Entity, weapon_descriptor: str, **kwargs):
    weapon_preset = self.import_data("WEAPON", weapon_descriptor)
    if weapon_preset is None:
        raise ValueError(f"Weapon with id {weapon_descriptor} not found.")
    weapon = Weapon().fromPreset(weapon_preset)
    if kwargs.get("silent") is not None:
        self.add_cmd(
            "builtins:add_weapon_usage",
            entity_name=user.get_name(),
            weapon_name=weapon.get_name()
        )
    user.weaponry.add_weapon(weapon)
    return None


def apply_status_effect(self: HookContext, applied_to: Entity, status_effect_descriptor: str, applied_by: Entity | None = None, **kwargs):
    status_effect_preset = self.import_data("STATUS_EFFECT", status_effect_descriptor)
    if status_effect_preset is None:
        raise ValueError(f"Status effect with descriptor {status_effect_descriptor} not found.")
    status_effect = StatusEffect().fromPreset(status_effect_preset)
    status_effect.apply(self, applied_to, applied_by, **kwargs)
    return None


def fainted_dead_mechanic(self: HookContext, target: Entity, damaged_by: Entity = None, **kwargs):
    is_fainted = target.has_effect("builtins:fainted") is not None
    is_alive = target.get_state("builtins:alive") is True
    health_is_zero = target.get_attribute("current_health") <= 0

    if is_fainted is False and is_alive and health_is_zero:
        apply_status_effect(self, target, "builtins:fainted", damaged_by)
        self.trigger_on_fainted(fainted=target, fainted_by=damaged_by)
        self.add_cmd(
            "builtins:creature_fainted",
            entity_name=target.get_name()
        )
        return True

    elif is_fainted and is_alive and health_is_zero:
        self.trigger_on_death(died=target, killed_by=damaged_by)
        self.add_cmd(
            "builtins:creature_died",
            entity_name=target.get_name()
        )
        # dead entities are removed on turn beginning
        target.change_state("builtins:alive", "-")
        target.change_state("builtins:alive", "-")
        target.change_state("builtins:alive", "-")
        target.change_state("builtins:alive", "-")
        return False

    return True


def summon_entity(
        self: HookContext,
        preset_id: str,
        preferred_square: Square,
        summoner: Entity | None,
        initiative_option: Literal["last", "first", "random", "after_summoner"] = "after_summoner",
        permanent: bool = False,
        dismiss_if_occupied: bool = False,
        **kwargs
):
    entity_preset = self.import_data("ENTITY", preset_id)
    if entity_preset is None:
        raise AbortError(f"Entity with id {preset_id} not found.")
    entity = Entity().fromPreset(self, entity_preset)
    if self.battlefield[preferred_square.line, preferred_square.column] is not None:
        if dismiss_if_occupied:
            return None
        else:
            found = False
            for line in range(1, 7):
                for column in range(1, 7):
                    if self.battlefield[line, column] is None:
                        preferred_square = Square(line, column)
                        found = True
                        break
                if found:
                    break
            else:
                raise AbortError(f"Entity with id {preset_id} cannot be summoned because there are no free squares on the field")
    self.battlefield.add_entity(entity, square=preferred_square)
    entity_ptr: Entity | None = self.battlefield[preferred_square.line, preferred_square.column]
    if entity_ptr is None:
        return None
    if permanent is False:
        apply_status_effect(self, entity_ptr, "builtins:summoned_with_deletion", summoner)
    else:
        apply_status_effect(self, entity_ptr, "builtins:summoned", summoner)
    if isinstance(initiative_option, int):
        entity_ptr.initiative = initiative_option
    else:
        match initiative_option:
            case "after_summoner":
                if summoner is None:
                    entity_ptr.initiative = 0
                else:
                    entity_ptr.initiative = self.battlefield[preferred_square.line, preferred_square.column].initiative + 0.5
            case "last":
                entity_ptr.initiative = -1
            case "first":
                entity_ptr.initiative = 999
            case "random":
                entity_ptr.initiative = None # arrange_queue will roll initiative if None
    self.arrange_queue.emit(initiative_reroll=False)
    return None


def make_fortitude_roll(
        self: HookContext,
        target: Entity,
        fortitude_roll_type_name: str = 'strength',
        fortitude_roll_success_number: int = 0
) -> tuple[bool, int]:
    safe_roll_result = Dice(1, 20).roll(
        target.get_attribute(fortitude_roll_type_name)
    )
    safe_roll_result_greater_than_barrier = safe_roll_result > fortitude_roll_success_number
    safe_roll_result_equal_to_20 = safe_roll_result - target.get_attribute(fortitude_roll_type_name) == 20
    safe_roll_is_total_failure = safe_roll_result - target.get_attribute(fortitude_roll_type_name) == 1
    self.trigger_on_fortitude_roll(result_of_safe_roll=safe_roll_result,
                                   type_of_safe_roll=fortitude_roll_type_name,
                                   entity_that_rolls=target
                                   )
    if safe_roll_result_equal_to_20 or (safe_roll_result_greater_than_barrier and not safe_roll_is_total_failure):
        self.add_cmd(
            "builtins:successful_fortitude_roll",
            roll_type=fortitude_roll_type_name,
        )
        return True, safe_roll_result
    else:
        self.add_cmd(
            "builtins:failed_fortitude_roll",
            roll_type=fortitude_roll_type_name,
        )
        return False, safe_roll_result


HOOKS = extract_hooks(inspect.getmembers(sys.modules[__name__]))
