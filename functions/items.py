from typing import List

from engine.components.entities import Entity
from engine.game_hooks import HookContext, ItemHooks
from engine.components.items import Item
from engine.models import Square, HpChange, Dice, AbortError

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
        if (element_of_hp_change := item.memory.get('element_of_hp_change')) is None:
            raise AbortError(
                "builtins:element_of_hp_change_undefined",
                component_name=item.get_name()
            )

        if (dice := item.memory.get('dice')) is not None:
            dice: Dice
            if item_user is not None:
                damage = dice.roll(
                    item_user.get_attribute(element_of_hp_change + '_attack'))
            else:
                damage = dice.roll()
        else:  # if it is a value, then we take it
            damage = item.memory.get('value', None)

        if damage is None:
            raise AbortError(
                "builtins:bad_hp_change_value",
                component_name=item.get_name()
            )

        if (type_of_hp_change := item.memory.get('type_of_hp_change')) is None:
            raise AbortError(
                "builtins:hp_change_type_undefined",
                component_name=item.get_name()
            )

        hp_change = HpChange(
            damage,
            type_of_hp_change,
            element_of_hp_change,
            source="item"
        )

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
    item_attribute = item.memory.get('attribute')

    if item_attribute is None:
        raise AbortError(
            'builtins:attribute_changing_not_defined',
            component_name=item.get_name()
        )
    item_attribute_change = item.memory.get('value')
    if item_attribute_change is None:
        raise AbortError(
            'builtins:attribute_change_value_not_defined',
            component_name=item.get_name()
        )

    for target in targets:
        if item_attribute is not None:
            target.change_attribute(self, item_attribute, item_attribute_change)


@custom_hooks.hook(name="add_item_item", schema_name="ADD_ITEM")
def add_item_item(self: HookContext, item: Item, item_user: Entity, square: str, **_) -> None:
    # square: Square = Square.from_str(square)
    # targets = get_weapon_target(self, item, square)
    # for target in targets:
    #     if item.memory.get('item') is not None:
    #         target.inventory.add_item(item.memory['item'])
    pass
