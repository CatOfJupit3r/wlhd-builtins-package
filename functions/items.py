from typing import List

from engine.entities import Entity
from engine.game_hooks import HookContext, ItemHooks
from engine.items import Item
from models.exceptions import AbortError
from models.game import Square, Dice, HpChange

custom_hooks = ItemHooks()


def get_weapon_target(ctx: HookContext, item: Item, square: Square) -> List[Entity]:
    return ctx.battlefield.get_entities_by_string(
        item.method_variables.get('type_of_radius', 'single_target'),
        square
    )


@custom_hooks.hook(name="hp_change_item", schema_name="HP_CHANGE")
def hp_change_item(self: HookContext, item: Item, item_user: Entity, square: str, **_) -> None:
    square: Square = Square.from_str(square)
    targets = get_weapon_target(self, item, square)
    for target in targets:
        if item.method_variables['time_thrown_dice'] is not None:  # if it is a dice roll, then we roll it
            damage_dice_roll = Dice(item.method_variables['time_thrown_dice'], item.method_variables['sides_of_dice'])
            if item_user is not None:
                damage = damage_dice_roll.roll(
                    item_user.get_attribute(item.method_variables['element_of_hp_change'] + '_attack'))
            else:
                damage = damage_dice_roll.roll()
        else:  # if it is a value, then we take it
            damage = item.method_variables['value']
        if item.method_variables.get('type_of_hp_change') is None:
            raise AbortError("Type of hp change is not defined")
        hp_change_type = item.method_variables['type_of_hp_change']
        if hp_change_type == "damage":
            damage += item_user.get_attribute("weapon_attack_bonus")
        elif hp_change_type == "heal":
            damage += item_user.get_attribute("weapon_heal_bonus")
        hp_change = HpChange(damage,
                             item.method_variables['type_of_hp_change'],
                             item.method_variables['element_of_hp_change'],
                             source="item")
        target.process_hp_change(
            self, hp_change, item_user
        )


@custom_hooks.hook(name="applies_status_effect_item", schema_name="APPLIES_STATUS_EFFECT")
def applies_status_effect_item(self: HookContext, item: Item, item_user: Entity, square: str, **_) -> None:
    square: Square = Square.from_str(square)
    targets = get_weapon_target(self, item, square)
    for target in targets:
        if item.method_variables.get('status_effect') is not None:
            target.add_status_effect(item.method_variables['status_effect'], owner=item_user)


@custom_hooks.hook(name="change_attribute_item", schema_name="CHANGE_ATTRIBUTE")
def change_attribute_item(self: HookContext, item: Item, item_user: Entity, square: str, **_) -> None:
    square: Square = Square.from_str(square)
    targets = get_weapon_target(self, item, square)
    for target in targets:
        if item.method_variables.get('attribute') is not None:
            target.change_attribute(self, item.method_variables['attribute'], item.method_variables['value'])


@custom_hooks.hook(name="add_item_item", schema_name="ADD_ITEM")
def add_item_item(self: HookContext, item: Item, item_user: Entity, square: str, **_) -> None:
    square: Square = Square.from_str(square)
    targets = get_weapon_target(self, item, square)
    for target in targets:
        if item.method_variables.get('item') is not None:
            target.inventory.add_item(item.method_variables['item'])
