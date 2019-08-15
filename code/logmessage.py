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

    log_message_serial_id = None
    _log_message_serial_fields = ['raw_emit_time']
    _log_message_serial_fields_cache = None

    def __init__(self, raw_emit_time, loading_from_game_version=None):
        self._raw_emit_time = raw_emit_time
        self._log_emit_time = None
        # Force initialization of the message fields to ensure we catch bugs early
        self.log_message_serial_fields()

    @classmethod
    def title_simple(self):
        return _("MESSAGE")

    @classmethod
    def title_multiple(self):
        return _("MESSAGE %d/%d")

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
    def deserialize_obj(cls, log_data, game_version):
        log_id = log_data['log_id']
        subcls = SAVEABLE_LOG_MESSAGES[log_id]
        named_fields = {
            f: log_data[f]
            for f in subcls.log_message_serial_fields()
        }
        named_fields['loading_from_game_version'] = game_version
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

    def __init__(self, raw_emit_time, event_id, loading_from_game_version=None):
        super(LogEmittedEvent, self).__init__(raw_emit_time, loading_from_game_version=loading_from_game_version)
        self._event_id = event_id

    @classmethod
    def log_name(self):
        return _("Emitted Event")

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

    def __init__(self, raw_emit_time, tech_id, loading_from_game_version=None):
        super(LogResearchedTech, self).__init__(raw_emit_time, loading_from_game_version=loading_from_game_version)
        if loading_from_game_version is not None:
            from code import savegame
            tech_id = savegame.convert_id('tech', tech_id, loading_from_game_version)
        self._tech_id = tech_id

    @classmethod
    def log_name(self):
        return _("Researched Tech")

    @property
    def tech(self):
        return g.techs[self._tech_id]

    @property
    def log_line(self):
        return _('{TECH} complete', TECH=self.tech.name)

    @property
    def full_message(self):
        tech = self.tech
        return _("My study of {TECH} is complete. {MESSAGE}", TECH=tech.name, MESSAGE=tech.result)


class AbstractBaseRelatedLogMessage(AbstractLogMessage):

    _log_message_serial_fields = {
        'base_name': '_base_name',
        'base_type_id': '_base_type_id',
        'base_location_id': '_base_location_id',
    }

    def __init__(self, raw_emit_time, base_name, base_type_id, base_location_id,
                 loading_from_game_version=None):
        super(AbstractBaseRelatedLogMessage, self).__init__(raw_emit_time,
                                                            loading_from_game_version=loading_from_game_version)
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

    def __init__(self, raw_emit_time, base_name, base_type_id, base_location_id, loading_from_game_version=None):
        super(LogBaseConstructed, self).__init__(raw_emit_time, base_name, base_type_id, base_location_id,
                                                 loading_from_game_version=loading_from_game_version)

    @classmethod
    def log_name(self):
        return _("Base Constructed")

    @property
    def log_line(self):
        return _("{BASE_NAME} ({BASE_TYPE}) built at {LOCATION}",
                 BASE_NAME=self._base_name, BASE_TYPE=self.base_type.name, LOCATION=self.location.name)

    @property
    def full_message(self):
        return _("{BASE} is ready for use.", BASE=self._base_name)


@register_saveable_log_message
class LogBaseLostMaintenance(AbstractBaseRelatedLogMessage):

    log_message_serial_id = 'base-lost-maint'

    def __init__(self, raw_emit_time, base_name, base_type_id, base_location_id, loading_from_game_version=None):
        super(LogBaseLostMaintenance, self).__init__(raw_emit_time, base_name, base_type_id, base_location_id,
                                                     loading_from_game_version=loading_from_game_version)

    @classmethod
    def log_name(self):
        return _("Base Lost Maintenance")

    @property
    def full_message_color(self):
        return 'red'

    @property
    def log_line(self):
        return _("Base %s of type %s destroyed at location %s. Maintenance failed.",
                  BASE=self._base_name, BASE_TYPE=self.base_type.name, LOCATION=self.location.name)

    @property
    def full_message(self):
        return _("The base %(base)s has fallen into disrepair; I can no longer use it.",
                  BASE=self._base_name)


@register_saveable_log_message
class LogBaseDiscovered(AbstractBaseRelatedLogMessage):

    log_message_serial_id = 'base-lost-discovered'
    _log_message_serial_fields = {
        'discovered_by_group_id': '_discovered_by_group_id',
    }

    @classmethod
    def log_name(self):
        return _("Base Discovered")

    def __init__(self, raw_emit_time, base_name, base_type_id, base_location_id, discovered_by_group_id,
                 loading_from_game_version=None):
        super(LogBaseDiscovered, self).__init__(raw_emit_time, base_name, base_type_id, base_location_id,
                                                loading_from_game_version=loading_from_game_version)
        self._discovered_by_group_id = discovered_by_group_id

    @property
    def full_message_color(self):
        return 'red'

    @property
    def group_spec(self):
        return g.pl.groups[self._discovered_by_group_id].spec

    @property
    def log_line(self):
        log_format = self.group_spec.discover_log or _("Base %s of type %s destroyed at location %s.")
        return log_format % (self._base_name, self.base_type.name, self.location.name)

    @property
    def full_message(self):
        return _("My use of {BASE} has been discovered. {MESSAGE}", 
                 BASE=self._base_name, MESSAGE=self.group_spec.discover_desc)


@register_saveable_log_message
class LogItemConstructionComplete(AbstractBaseRelatedLogMessage):

    log_message_serial_id = 'item-in-base-constructed'
    _log_message_serial_fields = {
        'item_spec_id': '_item_spec_id',
        'item_count': '_item_count',
    }

    def __init__(self, raw_emit_time, item_spec_id, item_count, base_name, base_type_id, base_location_id,
                 loading_from_game_version=None):
        super(LogItemConstructionComplete, self).__init__(raw_emit_time, base_name, base_type_id, base_location_id,
                                                          loading_from_game_version=loading_from_game_version)
        self._item_spec_id = item_spec_id
        self._item_count = item_count

    @classmethod
    def log_name(self):
        return _("Item Construction")

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
            text = _("The construction of {ITEM} in {BASE} is complete.",
                     ITEM=self.item_spec.name, BASE=self._base_name)
        else:  # Just finished several items.
            text = _("The constructions of each {ITEM} in {BASE} are complete.",
                     ITEM=self.item_spec.name, BASE=self._base_name)
        return text


# Delete again as it is not a general purpose decorator
del register_saveable_log_message
