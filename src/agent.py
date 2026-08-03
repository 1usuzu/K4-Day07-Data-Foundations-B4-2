import os
import importlib

pkg = os.getenv("LAB_SOLUTION_PACKAGE", "src.trang")
_m = importlib.import_module(pkg + ".agent")
globals().update({k: v for k, v in _m.__dict__.items() if not k.startswith('__')})
