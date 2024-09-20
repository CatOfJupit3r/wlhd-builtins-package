from typing import List

from engine.entities import Entity
from engine.game_hooks import HookContext, ItemHooks
from engine.items import Item
from models.exceptions import AbortError
from models.game import Square, HpChange

custom_hooks = ItemHooks()


def get_weapon_target(ctx: HookContext, item: Item, square: Square) -> List[Entity]:
    return ctx.battlefield.get_entities_by_string(
        item.memory.get('type_of_radius') or 'single_target',
        square
    )


@custom_hooks.hook(name="hp_change_item", schema_name="HP_CHANGE")
def hp_change_item(self: HookContext, item: Item, item_user: Entity, square: str, **_) -> None:
    square: Square = Square.from_str(square)
    targets = get_weapon_target(self, item, square)
    for target in targets:
        hp_change_dice = item.memory.get("dice")
        if hp_change_dice is not None:
            if item_user is not None:
                damage = hp_change_dice.roll(
                    item_user.get_attribute(item.memory['element_of_hp_change'] + '_attack'))
            else:
                damage = hp_change_dice.roll()
        else:  # if it is a value, then we take it
            damage = item.memory.get('value', 0)
        if item.memory.get('type_of_hp_change') is None:
            raise AbortError("Type of hp change is not defined")
        hp_change_type = item.memory['type_of_hp_change']
        if hp_change_type == "damage":
            damage += item_user.get_attribute("weapon_attack_bonus")
        elif hp_change_type == "heal":
            damage += item_user.get_attribute("weapon_heal_bonus")
        hp_change = HpChange(damage,
                             item.memory['type_of_hp_change'],
                             item.memory['element_of_hp_change'],
                             source="item")
        target.process_hp_change(
            self, hp_change, item_user
        )


@custom_hooks.hook(name="applies_status_effect_item", schema_name="APPLIES_STATUS_EFFECT")
def applies_status_effect_item(self: HookContext, item: Item, item_user: Entity, square: str, **_) -> None:
    # square: Square = Square.from_str(square)
    # targets = get_weapon_target(self, item, square)
    # for target in targets:
    #     if item.memory.get('status_effect') is not None:
    #         target.status_effects.add_effect(item.memory['status_effect'], owner=item_user)
    pass


@custom_hooks.hook(name="change_attribute_item", schema_name="CHANGE_ATTRIBUTE")
def change_attribute_item(self: HookContext, item: Item, item_user: Entity, square: str, **_) -> None:
    square: Square = Square.from_str(square)
    targets = get_weapon_target(self, item, square)
    for target in targets:
        if item.memory.get('attribute') is not None:
            target.change_attribute(self, item.memory['attribute'], item.memory['value'])


@custom_hooks.hook(name="add_item_item", schema_name="ADD_ITEM")
def add_item_item(self: HookContext, item: Item, item_user: Entity, square: str, **_) -> None:
    # square: Square = Square.from_str(square)
    # targets = get_weapon_target(self, item, square)
    # for target in targets:
    #     if item.memory.get('item') is not None:
    #         target.inventory.add_item(item.memory['item'])
    pass
