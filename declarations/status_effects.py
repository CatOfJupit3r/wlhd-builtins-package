from engine.status_effects import StatusEffect

status_effect_error = StatusEffect(
    descriptor="builtins:status_effect_error",
)

moved = StatusEffect(
    "builtins:moved",
    duration=1,
    update_type="round_beginning",
    activation_type="round_beginning",
    activate_on_use=False
)

fainted = StatusEffect(
    "builtins:fainted",
    duration=1,
    update_type="round_beginning",
    activation_type="one_time",
    activate_on_use=True,
    visibility=True,
    method_variables={
        "state": "builtins:can_act",
        "mode": "-",
        "times": 5
    },
    method_hooks={
        "dispel": "builtins:state_change_dispel",
        "activate": "builtins:state_change_activate",
        "update": None,
        "apply": None
    }
)


summoned = StatusEffect(
    "builtins:summoned",
    duration=None,
    update_type="one_time",
    activation_type="one_time",
    activate_on_use=False,
    visibility=True,
)

summoned_with_deletion = StatusEffect(
    "builtins:summoned_with_deletion",
    duration=None,
    update_type="round_beginning",
    activation_type="one_time",
    activate_on_use=False,
    visibility=True,
    method_hooks={
        "dispel": "builtins:summoned_with_deletion_dispel",
        "activate": None,
        "update": None,
        "apply": "summoned_with_deletion_apply"
    }
)
