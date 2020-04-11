# -*- coding: utf-8 -*-
__all__ = ('escape', 'escape_if_not_none')

from typing import Any, Optional


def escape(val: Any) -> str:
    """Escapes a primitive value for inclusion within a Daikon file."""
    if isinstance(val, str):
        val = val.replace('\\', '\\\\').replace('"', '\\"')
        return f'"{val}"'
    if isinstance(val, bool):
        return 'true' if val else 'false'
    return val


def escape_if_not_none(val: Any) -> Optional[str]:
    return val if val is None else escape(val)
