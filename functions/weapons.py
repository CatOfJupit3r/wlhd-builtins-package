from typing import List

from engine.entities import Entity
from engine.game_hooks import HookContext, WeaponHooks
from engine.weapons import Weapon
from models.exceptions import AbortError
from models.game import Square, Dice, HpChange

custom_hooks = WeaponHooks()


def get_weapon_target(ctx: HookContext, item: Weapon, square: Square) -> List[Entity]:
    return ctx.battlefield.get_entities_by_string(
        item.memory.get('type_of_radius', 'single_target'),
        square
    )


@custom_hooks.hook(name="hp_change_weapon", schema_name="HP_CHANGE")
def hp_change_weapon(self: HookContext, weapon: Weapon, weapon_user: Entity, square: str, **_) -> None:
    square: Square = Square.from_str(square)
    targets = get_weapon_target(self, weapon, square)
    for target in targets:
        if weapon.memory['time_thrown_dice'] is not None:  # if it is a dice roll, then we roll it
            damage_dice_roll = Dice(weapon.memory['time_thrown_dice'],
                                    weapon.memory['sides_of_dice'])
            if weapon_user is not None:
                damage = damage_dice_roll.roll(
                    weapon_user.get_attribute(weapon.memory['element_of_hp_change'] + '_attack'))
            else:
                damage = damage_dice_roll.roll()
        else:  # if it is a value, then we take it
            damage = weapon.memory['value']
        if weapon.memory.get('type_of_hp_change') is None:
            raise AbortError("Type of hp change is not defined")
        hp_change_type = weapon.memory['type_of_hp_change']
        if hp_change_type == "damage":
            damage += weapon_user.get_attribute("weapon_attack_bonus")
        elif hp_change_type == "heal":
            damage += weapon_user.get_attribute("weapon_heal_bonus")
        hp_change = HpChange(damage,
                             weapon.memory['type_of_hp_change'],
                             weapon.memory['element_of_hp_change'],
                             source="weapon")
        target.process_hp_change(
            self, hp_change, weapon_user
        )


@custom_hooks.hook(name="applies_status_effect_weapon", schema_name="APPLIES_STATUS_EFFECT")
def applies_status_effect_weapon(self: HookContext, weapon: Weapon, weapon_user: Entity, square: str, **_) -> None:
    square: Square = Square.from_str(square)
    targets = get_weapon_target(self, weapon, square)
    for target in targets:
        if weapon.memory.get('status_effect') is not None:
            target.add_status_effect(weapon.memory['status_effect'], owner=weapon_user)


@custom_hooks.hook(name="change_attribute_weapon", schema_name="CHANGE_ATTRIBUTE")
def change_attribute_weapon(self: HookContext, weapon: Weapon, weapon_user: Entity, square: str, **_) -> None:
    square: Square = Square.from_str(square)
    targets = get_weapon_target(self, weapon, square)
    for target in targets:
        if weapon.memory.get('attribute') is not None:
            target.change_attribute(self, weapon.memory['attribute'], weapon.memory['value'])


@custom_hooks.hook(name="add_item_weapon", schema_name="ADD_ITEM")
def add_item_weapon(self: HookContext, weapon: Weapon, weapon_user: Entity, square: str, **_) -> None:
    square: Square = Square.from_str(square)
    targets = get_weapon_target(self, weapon, square)
    for target in targets:
        if weapon.memory.get('item') is not None:
            target.inventory.add_item(weapon.memory['item'])
