"""Compatibility namespace exposing src packages under taxi_fare.* imports."""

from importlib import import_module
import sys

_EXPORTED_MODULES = (
    "data",
    "deployment",
    "features",
    "models",
    "utils",
)

for _module_name in _EXPORTED_MODULES:
    _module = import_module(_module_name)
    globals()[_module_name] = _module
    sys.modules[f"{__name__}.{_module_name}"] = _module

__all__ = list(_EXPORTED_MODULES)
