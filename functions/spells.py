import inspect
import sys

from engine.utils.extract_hooks import extract_hooks


# HOOKS = extract_hooks(inspect.getmembers(sys.modules[__name__]))
HOOKS = {}
