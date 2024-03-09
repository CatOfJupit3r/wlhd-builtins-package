def hp_change_item(item: Item, field: Battlefield, item_user: Entity, line_of_square: int, column_of_square: int, **kwargs) -> None:
    """
    Function, which is used for hp changing items (could be either healing or damage dealing).
    More like a function for a simple weapon with no special effects.

    Uses: ["type_of_hp_change", "element_of_hp_change", "time_thrown_dice", "sides_of_dice", "value"]
    :param item: item, which is used
    :param field: list of all creatures on field
    :param item_user: creature, who uses the item
    :param line_of_square: line of square, where item is used
    :param column_of_square: column of square, where item is used
    :return: None
    """
    targets = get_targets(field, item, line_of_square, column_of_square)
    if targets_are_valid(targets):
        #  now we decide if damage is a value, or a dice roll
        for target in targets:
            if item['time_thrown_dice'] is not None:  # if it is a dice roll, then we roll it
                damage_dice_roll = Dice(item.method_variables['time_thrown_dice'], item.method_variables['sides_of_dice'])
                if item_user is not None:
                    damage = damage_dice_roll.roll(item_user.get_attribute(item.method_variables['element_of_hp_change'] + '_attack'))
                else:
                    damage = damage_dice_roll.roll()
            else:  # if it is a value, then we take it
                damage = item.method_variables['value']
            if item_user is not None and (item.type == "weapon" or item.type == "subweapon"):
                if item.method_variables.get('type_of_hp_change') is not None and item.method_variables.get('type_of_hp_change') == "damage":
                    damage += item_user.get_attribute("weapon_attack_bonus")
                elif item.method_variables.get('type_of_hp_change') is not None and item.method_variables.get('type_of_hp_change') == "heal":
                    damage += item_user.get_attribute("weapon_heal_bonus")
            target.process_hp_change(field, item_user, damage, item.method_variables['type_of_hp_change'], item.method_variables['element_of_hp_change'])


def applies_status_effect_item(item, field: Battlefield, item_user: Entity, line_of_square: int, column_of_square: int, **kwargs) -> None:
    """
    Function, which is used for applying status effect items.

    Uses: ["status_effect"]
    :param item: item, which is used
    :param field: list of all creatures on field
    :param item_user: creature, who uses the item
    :param line_of_square: line of square, where item is used
    :param column_of_square: column of square, where item is used
    :return: None
    """
    targets = get_targets(field, item, line_of_square, column_of_square)
    if targets_are_valid(targets):
        for target in targets:
            if item.method_variables.get('status_effect') is not None:
                target.add_status_effect(item.method_variables['status_effect'], owner=item_user)


def change_attribute_item(item, field: Battlefield, item_user: Entity, line_of_square: int, column_of_square: int, **kwargs) -> None:
    """
    Function, which is used for attribute changing items.
    IT IS NOT TEMPORARY. IT IS PERMANENT.

    Uses: ["attribute", "value"]
    :param item: item, which is used
    :param field: list of all creatures on field
    :param item_user: creature, who uses the item
    :param line_of_square: line of square, where item is used
    :param column_of_square: column of square, where item is used
    :return: None
    """
    targets = get_targets(field, item, line_of_square, column_of_square)
    if targets_are_valid(targets):
        for target in targets:
            if item.method_variables.get('attribute') is not None:
                target.change_attribute(item.method_variables['attribute'], item.method_variables['value'])


def add_item_item(item, field: Battlefield, item_user: Entity, line_of_square: int, column_of_square: int, **kwargs) -> None:
    """
    Function, which is used for adding items to inventory.
    Funny name, I know.

    Uses: ["item"]
    :param item: item, which is used
    :param field: list of all creatures on field
    :param item_user: creature, who uses the item
    :param line_of_square: line of square, where item is used
    :param column_of_square: column of square, where item is used
    :return: None
    """
    targets = get_targets(field, item, line_of_square, column_of_square)
    if targets_are_valid(targets):
        for target in targets:
            if item.method_variables.get('item') is not None:
                target.inventory.add_item(item.method_variables['item'])


def remove_item_item(item, field: Battlefield, item_user: Entity, line_of_square: int, column_of_square: int, **kwargs) -> None:
    """
    Function, which is used for removing items from inventory.
    Yet another funny name. Comedy gold.

    Uses: ["item"]
    :param item: item, which is used
    :param field: list of all creatures on field
    :param item_user: creature, who uses the item
    :param line_of_square: line of square, where item is used
    :param column_of_square: column of square, where item is used
    :return: None
    """
    targets = get_targets(field, item, line_of_square, column_of_square)
    if targets_are_valid(targets):
        for target in targets:
            if item.method_variables.get('item') is not None:
                target.inventory.remove_item(item.method_variables['item'])


def use_weapon_item(item, field: Battlefield, item_user: Entity, line_of_square: int, column_of_square: int, **kwargs) -> None:
    """
    Function, which is used for using weapons.
    Uses: ["weapon", "modes"]
    :param item: item, which is used
    :param field: list of all creatures on field
    :param item_user: creature, who uses the item
    :param line_of_square: line of square, where item is used
    :param column_of_square: column of square, where item is used
    :return: None
    """
    targets = get_targets(field, item, line_of_square, column_of_square)
    if targets_are_valid(targets):
        for target in targets:
            if item.method_variables.get('weapon') is not None:
                target.use_weapon(field, item.method_variables['weapon'], line_of_square, column_of_square)


HOOKS = {}