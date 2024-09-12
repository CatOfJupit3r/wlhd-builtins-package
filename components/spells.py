from engine.component_memory import MemoryFactory
from engine.game_hooks import SpellComponentsHolder
from engine.game_hooks.component_holder.game_component import SpellGameComponent
from engine.requirements import RequiresTemplates
from models.decorations import Decoration
from models.game import Ranges
from models.tstring import TString

holder = SpellComponentsHolder()

spell_error = SpellGameComponent(
    'spell_error',
    {
        "decorations": TString.decorations("builtins:spell_error", "spell"),
        "usageCost": 999,
        "cooldownValue": 999,
        "effectHook": "builtins:default_spell_hook",
    },
)

fireball = SpellGameComponent(
    'fireball',
    {
        "decorations": TString.decorations("builtins:fireball", "spell"),
        "usageCost": 1,
        "casterMustBeInRange": Ranges.ALL_EXCEPT_SAFE,
        "cooldownValue": 0,
        "requirements": RequiresTemplates.ANY_SQUARE,
        "maxConsecutiveUses": 1,
        "consecutiveUsesResetOnCooldownUpdate": True,
        "effectHook": "builtins:hp_change_spell",
        "tags": ["builtins:pyromancy"],
    },
).with_memory(
    dice=MemoryFactory.dice(3, 8, TString.memory('builtins:dice'), False),
    type_of_hp_change=MemoryFactory.string("damage", TString.memory("builtins:type_of_hp_change"), False),
    element_of_hp_change=MemoryFactory.string("builtins:fire", TString.memory("builtins:element_of_hp_change"), False),
)

holder.add(fireball, 'fireball')
holder.add(spell_error, 'spell_error')
