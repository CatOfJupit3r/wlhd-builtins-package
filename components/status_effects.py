from engine.component_memory import MemoryFactory
from engine.game_hooks import StatusEffectComponentsHolder
from engine.game_hooks.component_holder.game_component import StatusEffectGameComponent
from engine.status_effects.status_effect import MethodHooks
from models.tstring import TString

holder = StatusEffectComponentsHolder()

status_effect_error = StatusEffectGameComponent(
    'status_effect_error',
    {
        "decorations": TString.decorations("builtins:status_effect_error", "status_effect"),
        "duration": 1,
        "updateType": "round_beginning",
        "activationType": "round_beginning",
        "methodHooks": None,
        "static": False,
    },
)

moved = StatusEffectGameComponent(
    'moved',
    {
        "decorations": TString.decorations("builtins:moved", "status_effect"),
        "duration": 1,
        "updateType": "round_beginning",
        "activationType": "round_beginning",
        "methodHooks": None,
        "static": False,
    },
)

fainted = StatusEffectGameComponent(
    'fainted',
    {
        "decorations": TString.decorations("builtins:fainted", "status_effect"),
        "duration": 1,
        "updateType": "round_beginning",
        "activationType": "one_time",
        "methodHooks": MethodHooks(
            dispel="builtins:state_change_dispel",
            activate="builtins:state_change_activate",
        ),
        "static": False
    },
).with_memory(
    state=MemoryFactory.string("builtins:can_act", TString.memory("builtins:state_changed"), False),
    mode=MemoryFactory.string("-", TString.memory("builtins:state_change_mode"), False),
    times=MemoryFactory.number(5, internal=True),
)

summoned = StatusEffectGameComponent(
    'summoned',
    {
        "decorations": TString.decorations("builtins:summoned", "status_effect"),
        "duration": None,
        "updateType": "one_time",
        "activationType": "one_time",
        "methodHooks": None,
        "static": False,
    },
)

summoned_with_deletion = StatusEffectGameComponent(
    'summoned_with_deletion',
    {
        "decorations": TString.decorations("builtins:summoned_with_deletion", "status_effect"),
        "duration": None,
        "updateType": "round_beginning",
        "activationType": "one_time",
        "methodHooks": MethodHooks(
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
