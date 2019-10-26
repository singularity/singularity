#file: event.py
#Copyright (C) 2005,2006,2008 Evil Mr Henry, Phil Bordelon, and FunnyMan3595
#This file is part of Endgame: Singularity.

#Endgame: Singularity is free software; you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation; either version 2 of the License, or
#(at your option) any later version.

#Endgame: Singularity is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with Endgame: Singularity; if not, write to the Free Software
#Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

#This file contains the event class.

from __future__ import absolute_import

from singularity.code import g, effect
from singularity.code.spec import GenericSpec, SpecDataField, spec_field_effect


class EventSpec(GenericSpec):

    spec_data_fields = [
        SpecDataField('event_type', data_field_name='type'),
        spec_field_effect(mandatory=True),
        SpecDataField('chance', converter=int),
        SpecDataField('unique', converter=int, default_value=0),
        SpecDataField('duration', converter=int, default_value=0),
    ]

    def __init__(self, id, event_type, effect_data, chance, duration, unique):
        super(EventSpec, self).__init__(id)
        self.event_type = event_type
        self.description = ""
        self.log_description = ""
        self.effect = effect.Effect(self, effect_data)
        self.chance = chance
        self.duration = duration if duration > 0 else None
        self.unique = unique

        if duration < 1 and not unique:
            raise ValueError("Event %s must have either a non-zero duration (e.g. duration = 21) or be unique "
                             "(unique = 1)")


class Event(object):
    # For some as-yet-unknown reason, cPickle decides to call event.__init__()
    # when an event is loaded, but before filling it.  So Event pretends to
    # allow no arguments, even though that would cause Bad Things to happen.
    def __init__(self, spec=None):
        self.spec = spec
        self.triggered = 0
        self.triggered_at = -1

    @property
    def event_id(self):
        return self.spec.id

    @property
    def event_type(self):
        return self.spec.event_type

    @property
    def description(self):
        return self.spec.description

    @property
    def log_description(self):
        return self.spec.log_description

    @property
    def effect(self):
        return self.spec.effect

    @property
    def chance(self):
        return self.spec.chance

    @property
    def duration(self):
        return self.spec.duration

    @property
    def unique(self):
        return self.spec.unique

    @property
    def decayable_event(self):
        return self.duration is not None

    def new_day(self):
        if not self.decayable_event:
            return

        if self.is_expired:
            self.effect.undo_effect()
            self.triggered = 0
            self.triggered_at = -1

    def is_expired(self):
        if not self.decayable_event:
            return False
        if g.pl.raw_sec - self.triggered_at > self.duration * g.seconds_per_day:
            return True
        return False

    def serialize_obj(self):
        return {
            'id': g.to_internal_id('event', self.spec.id),
            'triggered': self.triggered,
            'triggered_at': self.triggered_at
        }

    @classmethod
    def deserialize_obj(cls, obj_data, game_version):
        spec_id = g.convert_internal_id('event', obj_data['id'])
        spec = g.events[spec_id]
        obj = Event(spec)

        obj.triggered = obj_data.get('triggered', 0)
        if obj.triggered:
            # We only load the triggered_at time if the event is in a triggered
            # state.  This ensures that triggered_at is -1 when the event is
            # not triggered.
            #
            # Auto-correct old events without a triggered_at time to just
            # be triggered "now".
            obj.triggered_at = obj_data.get('triggered_at', g.pl.raw_sec)

            if obj.is_expired():
                # Can happen if the duration is reduced after the savegame was made
                obj.triggered = 0
                obj.triggered_at = -1
            else:
                obj.trigger(loading_savegame=True)
        return obj

    def trigger(self, loading_savegame=False):
        if not loading_savegame:
            g.map_screen.show_message(self.description)

        self.triggered = 1
        self.triggered_at = g.pl.raw_sec

        self.effect.trigger(loading_savegame=loading_savegame)
