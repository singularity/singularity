#file: location.py
#Copyright (C) 2019 Niels Thykier
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

#This file contains the log message related classes.

import inspect

from code import g


SAVEABLE_LOG_MESSAGES = {}


def register_saveable_log_message(cls):
    SAVEABLE_LOG_MESSAGES[cls.log_message_serial_id] = cls
    assert cls.log_message_serial_fields, "Saveable log message (Class: %s) must have log_message_serial_fields" % \
                                          cls.__name__
    return cls


class AbstractLogMessage(object):


    title_simple   = _("MESSAGE")
    title_multiple = _("MESSAGE %d/%d")
    log_message_serial_id = None
    _log_message_serial_fields = ['raw_emit_time']
    _log_message_serial_fields_cache = None

    def __init__(self, raw_emit_time):
        self._raw_emit_time = raw_emit_time
        self._log_emit_time = None
        # Force initialization of the message fields to ensure we catch bugs early
        self.log_message_serial_fields()

    @property
    def log_emit_time(self):
        if self._log_emit_time is None:
            raw_min, time_sec = divmod(self._raw_emit_time, g.seconds_per_minute)
            raw_hour, time_min = divmod(raw_min, g.minutes_per_hour)
            time_day, time_hour = divmod(raw_hour, g.hours_per_day)
            self._log_emit_time = (time_day, time_hour, time_min, time_sec)
        return self._log_emit_time

    @property
    def raw_emit_time(self):
        return self._raw_emit_time

    @property
    def full_message_color(self):
        return 'text'

    @property
    def log_line(self):
        return NotImplemented

    @property
    def full_message(self):
        return NotImplemented

    @classmethod
    def log_message_serial_fields(cls):
        if cls._log_message_serial_fields_cache:
            return cls._log_message_serial_fields_cache
        cache = {}
        subclasses = cls.mro()
        subclasses.append(cls)
        for subcls in reversed(subclasses):
            try:
                fields = subcls._log_message_serial_fields
                # Enable short hands when there is a 1:1 between constructor argument,
                # serial format, and the field name
                if isinstance(fields, list):
                    cache.update({x: x for x in fields})
                else:
                    cache.update(fields)
            except AttributeError:
                pass
        cls._log_message_serial_fields_cache = cache
        assert 'log_id' not in cache, "The log_id field is reserved for internal usage"
        return cache

    def serialize_obj(self):
        assert self.__class__.log_message_serial_id, "%s has invalid log_message_serial_id" % self.__class__.__name__
        obj_data = {
            serial_name: getattr(self, field_name)
            for serial_name, field_name in self.__class__.log_message_serial_fields().items()
        }
        obj_data['log_id'] = self.__class__.log_message_serial_id
        return obj_data

    @classmethod
    def deserialize_obj(cls, log_data):
        log_id = log_data['log_id']
        subcls = SAVEABLE_LOG_MESSAGES[log_id]
        named_fields = {
            f: log_data[f]
            for f in subcls.log_message_serial_fields()
        }
        # Use reflection to call the constructor with the arguments
        # properly aligned
        try:
            getfullargspec = inspect.getfullargspec
        except AttributeError:
            getfullargspec = inspect.getargspec
        arg_desc = getfullargspec(subcls.__init__)
        args = [named_fields[name] for name in arg_desc.args[1:]]
        return subcls(*args)


@register_saveable_log_message
class LogEmittedEvent(AbstractLogMessage):

    log_message_serial_id = 'event-emitted'
    _log_message_serial_fields = {'event_id': '_event_id'}

    def __init__(self, raw_emit_time, event_id):
        super(LogEmittedEvent, self).__init__(raw_emit_time)
        self._event_id = event_id

    @property
    def event(self):
        return g.events[self._event_id]

    @property
    def log_line(self):
        return self.event.log_description

    @property
    def full_message(self):
        return self.event.description


@register_saveable_log_message
class LogResearchedTech(AbstractLogMessage):

    log_message_serial_id = 'tech-researched'
    _log_message_serial_fields = {'tech_id': '_tech_id'}

    def __init__(self, raw_emit_time, tech_id):
        super(LogResearchedTech, self).__init__(raw_emit_time)
        self._tech_id = tech_id

    @property
    def tech(self):
        return g.techs[self._tech_id]

    @property
    def log_line(self):
        return _('{TECH} complete', TECH=self.tech.name)

    @property
    def full_message(self):
        tech = self.tech
        text = g.strings["tech_gained"] % {
            "tech": tech.name,
            "tech_message": tech.result
        }
        return text


class AbstractBaseRelatedLogMessage(AbstractLogMessage):

    _log_message_serial_fields = {
        'base_name': '_base_name',
        'base_type_id': '_base_type_id',
        'base_location_id': '_base_location_id',
    }

    def __init__(self, raw_emit_time, base_name, base_type_id, base_location_id):
        super(AbstractBaseRelatedLogMessage, self).__init__(raw_emit_time)
        self._base_name = base_name
        self._base_type_id = base_type_id
        self._base_location_id = base_location_id

    @property
    def base_type(self):
        return g.base_type[self._base_type_id]

    @property
    def location(self):
        return g.pl.locations[self._base_location_id]


@register_saveable_log_message
class LogBaseConstructed(AbstractBaseRelatedLogMessage):

    log_message_serial_id = 'base-constructed'

    def __init__(self, raw_emit_time, base_name, base_type_id, base_location_id):
        super(LogBaseConstructed, self).__init__(raw_emit_time, base_name, base_type_id, base_location_id)

    @property
    def log_line(self):
        return _("{BASE_NAME} ({BASE_TYPE}) built at {LOCATION}",
                 BASE_NAME=self._base_name, BASE_TYPE=self.base_type.name, LOCATION=self.location.name)

    @property
    def full_message(self):
        dialog_string = g.strings["construction"] % {
            "base": self._base_name,
        }
        return dialog_string


@register_saveable_log_message
class LogBaseLostMaintenance(AbstractBaseRelatedLogMessage):

    log_message_serial_id = 'base-lost-maint'

    def __init__(self, raw_emit_time, base_name, base_type_id, base_location_id):
        super(LogBaseLostMaintenance, self).__init__(raw_emit_time, base_name, base_type_id, base_location_id)

    @property
    def full_message_color(self):
        return 'red'

    @property
    def log_line(self):
        return g.strings['log_destroy_maint'] % (self._base_name, self.base_type.name, self.location.name)

    @property
    def full_message(self):
        dialog_string = g.strings["discover_maint"] % {
            "base": self._base_name,
        }
        return dialog_string


@register_saveable_log_message
class LogBaseDiscovered(AbstractBaseRelatedLogMessage):

    log_message_serial_id = 'base-lost-discovered'
    _log_message_serial_fields = {
        'discovered_by_group_id': '_discovered_by_group_id',
    }

    def __init__(self, raw_emit_time, base_name, base_type_id, base_location_id, discovered_by_group_id):
        super(LogBaseDiscovered, self).__init__(raw_emit_time, base_name, base_type_id, base_location_id)
        self._discovered_by_group_id = discovered_by_group_id

    @property
    def full_message_color(self):
        return 'red'

    @property
    def group_spec(self):
        return g.pl.groups[self._discovered_by_group_id].spec

    @property
    def log_line(self):
        log_format = self.group_spec.discover_log or g.strings['log_destroy']
        return log_format % (self._base_name, self.base_type.name, self.location.name)

    @property
    def full_message(self):
        dialog_string = g.strings["discover"] % {
            "base": self._base_name,
            "message": self.group_spec.discover_desc
        }
        return dialog_string


@register_saveable_log_message
class LogItemConstructionComplete(AbstractBaseRelatedLogMessage):

    log_message_serial_id = 'item-in-base-constructed'
    _log_message_serial_fields = {
        'item_spec_id': '_item_spec_id',
        'item_count': '_item_count',
    }

    def __init__(self, raw_emit_time, item_spec_id, item_count, base_name, base_type_id, base_location_id):
        super(LogItemConstructionComplete, self).__init__(raw_emit_time, base_name, base_type_id, base_location_id)
        self._item_spec_id = item_spec_id
        self._item_count = item_count

    @property
    def item_spec(self):
        return g.items[self._item_spec_id]

    @property
    def log_line(self):
        return _("{ITEM_TYPE_NAME} built in {BASE_NAME} at {LOCATION}",
                 ITEM_TYPE_NAME=self.item_spec.name, BASE_NAME=self._base_name, BASE_TYPE=self.base_type.name,
                 LOCATION=self.location.name)

    @property
    def full_message(self):
        if self._item_count == 1:
            text = g.strings["item_construction_single"]
        else:  # Just finished several items.
            text = g.strings["item_construction_multiple"]
        return text % {"item": self.item_spec.name, "base": self._base_name}


# Delete again as it is not a general purpose decorator
del register_saveable_log_message
