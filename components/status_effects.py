from engine.component_memory import GameMemory, MemoryFactory
from engine.game_hooks import StatusEffectComponentsHolder
from engine.game_hooks.component_holder.game_component import StatusEffectGameComponent
from engine.status_effects.status_effect import MethodHooks
from models.decorations import Decoration

holder = StatusEffectComponentsHolder()

status_effect_error = StatusEffectGameComponent(
    'status_effect_error',
    {
        "decorations": Decoration(name="builtins:status_effect_error", sprite="builtins:status_effect_error",
                                  description="builtins:status_effect_error.desc"),
        "duration": 1,
        "update_type": "round_beginning",
        "activation_type": "round_beginning",
        "method_hooks": None,
        "static": False,
    },
)

moved = StatusEffectGameComponent(
    'moved',
    {
        "decorations": Decoration(name="builtins:moved", sprite="builtins:moved",
                                  description="builtins:moved.desc"),
        "duration": 1,
        "update_type": "round_beginning",
        "activation_type": "round_beginning",
        "method_hooks": None,
        "static": False,
    },
)

fainted = StatusEffectGameComponent(
    'fainted',
    {
        "decorations": Decoration(name="builtins:fainted", sprite="builtins:fainted",
                                  description="builtins:fainted.desc"),
        "duration": 1,
        "update_type": "round_beginning",
        "activation_type": "one_time",
        "method_hooks": MethodHooks(
            dispel="builtins:state_change_dispel",
            activate="builtins:state_change_activate",
        ),
        "static": False
    },
).with_memory(
    state=MemoryFactory.string("builtins:can_act", "builtins:state_changed", False),
    mode=MemoryFactory.string("-", "builtins:state_change_mode", False),
    times=MemoryFactory.number(5, internal=True),
)

summoned = StatusEffectGameComponent(
    'summoned',
    {
        "decorations": Decoration(name="builtins:summoned", sprite="builtins:summoned",
                                  description="builtins:summoned.desc"),
        "duration": None,
        "update_type": "one_time",
        "activation_type": "one_time",
        "method_hooks": None,
        "static": False,
    },
)

summoned_with_deletion = StatusEffectGameComponent(
    'summoned_with_deletion',
    {
        "decorations": Decoration(name="builtins:summoned_with_deletion", sprite="builtins:summoned_with_deletion",
                                  description="builtins:summoned_with_deletion.desc"),
        "duration": None,
        "update_type": "round_beginning",
        "activation_type": "one_time",
        "method_hooks": MethodHooks(
            dispel="builtins:summoned_with_deletion_dispel",
            apply="summoned_with_deletion_apply",
        ),
        "static": False,
    },
)

holder.add(status_effect_error, 'status_effect_error')
holder.add(moved, 'moved')
holder.add(fainted, 'fainted')
holder.add(summoned, 'summoned')
holder.add(summoned_with_deletion, 'summoned_with_deletion')
