from typing import List

from engine.entities import Entity
from engine.game_hooks import HookContext, WeaponHooks
from engine.weapons import Weapon
from models.exceptions import AbortError
from models.game import Square, HpChange

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
        hp_change_dice = weapon.memory.get("dice")
        if hp_change_dice is not None:
            if weapon_user is not None:
                damage = hp_change_dice.roll(
                    weapon_user.get_attribute(weapon.memory['element_of_hp_change'] + '_attack'))
            else:
                damage = hp_change_dice.roll()
        else:  # if it is a value, then we take it
            damage = weapon.memory.get('value', 0)
        if weapon.memory.get('type_of_hp_change') is None:
            raise AbortError(
                "builtins:hp_change_type_undefined",
                component_name=weapon.get_name()
            )
        hp_change = HpChange(damage,
                             weapon.memory['type_of_hp_change'],
                             weapon.memory['element_of_hp_change'],
                             source="weapon")
        target.process_hp_change(
            self, hp_change, weapon_user
        )


@custom_hooks.hook(name="change_attribute_weapon", schema_name="CHANGE_ATTRIBUTE")
def change_attribute_weapon(self: HookContext, weapon: Weapon, weapon_user: Entity, square: str, **_) -> None:
    square: Square = Square.from_str(square)
    targets = get_weapon_target(self, weapon, square)
    weapon_attribute = weapon.memory.get('attribute')

    if weapon_attribute is None:
        raise AbortError(
            'builtins:attribute_changing_not_defined',
            component_name=weapon.get_name()
        )
    weapon_attribute_change = weapon.memory.get('value')
    if weapon_attribute_change is None:
        raise AbortError(
            'builtins:attribute_change_value_not_defined',
            component_name=weapon.get_name()
        )

    for target in targets:
        if weapon_attribute is not None:
            target.change_attribute(self, weapon_attribute, weapon_attribute_change)
    # square: Square = Square.from_str(square)
    # targets = get_weapon_target(self, weapon, square)
    # for target in targets:
    #     if weapon.memory.get('attribute') is not None:
    #         target.change_attribute(self, weapon.memory['attribute'], weapon.memory['value'])


@custom_hooks.hook(name="applies_status_effect_weapon", schema_name="APPLIES_STATUS_EFFECT")
def applies_status_effect_weapon(self: HookContext, weapon: Weapon, weapon_user: Entity, square: str, **_) -> None:
    pass
    # square: Square = Square.from_str(square)
    # targets = get_weapon_target(self, weapon, square)
    # for target in targets:
    #     if weapon.memory.get('status_effect') is not None:
    #         target.add_status_effect(weapon.memory['status_effect'], owner=weapon_user)


@custom_hooks.hook(name="add_item_weapon", schema_name="ADD_ITEM")
def add_item_weapon(self: HookContext, weapon: Weapon, weapon_user: Entity, square: str, **_) -> None:
    pass
    # square: Square = Square.from_str(square)
    # targets = get_weapon_target(self, weapon, square)
    # for target in targets:
    #     if weapon.memory.get('item') is not None:
    #         target.inventory.add_item(weapon.memory['item'])
