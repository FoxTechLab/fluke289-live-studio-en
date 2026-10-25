# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Piotr
# This program comes with NO WARRANTY; see COPYING for license terms.
"""A/B points copied from valid samples of one field, function and unit."""
from dataclasses import dataclass
from .history import valid

@dataclass(frozen=True)
class Marker:
    time: float
    value: float
    reading: dict | None = None

class Markers:
    def __init__(self):
        self.scope = None
        self.points = {}
        self.pending = None

    def clear(self):
        self.points.clear()
        self.pending = None

    def set_scope(self, segment, field, unit):
        scope = (segment, field, unit)
        if scope != self.scope:
            self.clear()
            self.scope = scope

    def set_point(self, name, sample, reading):
        if name not in ('A','B') or self.scope is None:
            raise ValueError('Invalid marker')
        if sample['segment'] != self.scope[0] or reading['id'] != self.scope[1] or reading['unit'] != self.scope[2]:
            raise ValueError('Markers must use the same field, function and unit')
        if not valid(reading): raise ValueError('Marker requires a valid reading')
        self.points[name] = Marker(sample['time'], reading['value'], dict(reading) if 'decimals' in reading else None)
        self.pending = None

    def difference(self):
        if 'A' not in self.points or 'B' not in self.points: return None
        a,b = self.points['A'],self.points['B']
        return b.time-a.time, b.value-a.value
