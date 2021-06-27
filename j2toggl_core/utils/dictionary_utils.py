#!/usr/bin/env python3


def get_first_not_null(d: dict, *keys):
    for key in keys:
        value = d.get(key)
        if value is not None:
            return value

    return None

