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

import collections
import inspect

from singularity.code import g


SAVEABLE_LOG_MESSAGES = collections.OrderedDict()


def register_saveable_log_message(cls):
    SAVEABLE_LOG_MESSAGES[cls.log_message_serial_id] = cls
    assert cls.log_message_serial_fields, "Saveable log message (Class: %s) must have log_message_serial_fields" % \
                                          cls.__name__
    return cls


def merge_fields_on_subclasses(cls, field_name):
    cache = {}
    subclasses = cls.mro()
    subclasses.append(cls)
    for subcls in reversed(subclasses):
        try:
            fields = getattr(subcls, field_name)
            cache.update(fields)
        except AttributeError:
            pass
    return cache


class IDConverter(object):

    def __init__(self, id_type):
        self._id_type = id_type

    def serialize(self, value):
        return g.to_internal_id(self._id_type, value)

    def deserialize(self, serial_value):
        return g.convert_internal_id(self._id_type, serial_value)


def id_converter(id_type):
    return IDConverter(id_type)


class AbstractLogMessage(object):

    log_message_serial_id = None
    _log_message_serial_fields = {'raw_emit_time': 'raw_emit_time'}
    _log_message_serial_fields_cache = None
    _log_message_serial_converters = {}
    _log_message_serial_converters_cache = None

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
        return _("MESSAGE {CURRENT_PAGE}/{MAX_PAGE}")

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
        cache = merge_fields_on_subclasses(cls, "_log_message_serial_fields")
        cls._log_message_serial_fields_cache = cache
        assert 'log_id' not in cache, "The log_id field is reserved for internal usage"
        return cache

    @classmethod
    def log_message_serial_converters(cls):
        if cls._log_message_serial_converters_cache:
            return cls._log_message_serial_converters_cache
        cache = merge_fields_on_subclasses(cls, "_log_message_serial_converters")
        cls._log_message_serial_converters_cache = cache
        assert 'log_id' not in cache, "The log_id field is reserved for internal usage"
        return cache

    def serialize_obj(self):
        assert self.__class__.log_message_serial_id, "%s has invalid log_message_serial_id" % self.__class__.__name__
        obj_data = {}
        for serial_name, field_name in self.__class__.log_message_serial_fields().items():
            field = getattr(self, field_name)
            converter = self.__class__.log_message_serial_converters().get(serial_name)
            if converter is not None:
                obj_data[serial_name] = converter.serialize(field)
            else:
                obj_data[serial_name] = field

        obj_data['log_id'] = self.__class__.log_message_serial_id
        return obj_data

    @classmethod
    def deserialize_field(cls, serial_name, value):
        converter = cls.log_message_serial_converters().get(serial_name)
        if converter is not None:
            value = converter.deserialize(value)
        return value

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
        args = [subcls.deserialize_field(name, named_fields[name]) for name in arg_desc.args[1:]]
        return subcls(*args)


@register_saveable_log_message
class LogEmittedEvent(AbstractLogMessage):

    log_message_serial_id = 'event-emitted'
    _log_message_serial_fields = {'event_id': '_event_id'}
    _log_message_serial_converters = {'event_id': id_converter("event")}

    def __init__(self, raw_emit_time, event_id, loading_from_game_version=None):
        super(LogEmittedEvent, self).__init__(raw_emit_time, loading_from_game_version=loading_from_game_version)
        self._event_id = event_id

    @classmethod
    def log_name(self):
        return _("Emitted Event")

    @property
    def event_spec(self):
        return g.events[self._event_id]

    @property
    def log_line(self):
        return self.event_spec.log_description

    @property
    def full_message(self):
        return self.event_spec.description


@register_saveable_log_message
class LogResearchedTech(AbstractLogMessage):

    log_message_serial_id = 'tech-researched'
    _log_message_serial_fields = {'tech_id': '_tech_id'}
    _log_message_serial_converters = {'tech_id': id_converter("tech")}

    def __init__(self, raw_emit_time, tech_id, loading_from_game_version=None):
        super(LogResearchedTech, self).__init__(raw_emit_time, loading_from_game_version=loading_from_game_version)
        self._tech_id = tech_id

    @classmethod
    def log_name(self):
        return _("Researched Tech")

    @property
    def tech_spec(self):
        return g.techs[self._tech_id]

    @property
    def log_line(self):
        return _('{TECH} complete').format(TECH=self.tech_spec.name)

    @property
    def full_message(self):
        tech = self.tech_spec
        return _("My study of {TECH} is complete. {MESSAGE}").format(TECH=tech.name, MESSAGE=tech.result)


class AbstractBaseRelatedLogMessage(AbstractLogMessage):

    _log_message_serial_fields = {
        'base_name': '_base_name',
        'base_type_id': '_base_type_id',
        'base_location_id': '_base_location_id',
    }
    _log_message_serial_converters = {
        'base_type_id': id_converter("base"),
        'base_location_id': id_converter("location"),
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
        return _("{BASE_NAME} ({BASE_TYPE}) built at {LOCATION}").format(
                 BASE_NAME=self._base_name, BASE_TYPE=self.base_type.name, LOCATION=self.location.name)

    @property
    def full_message(self):
        return _("{BASE} is ready for use.").format(BASE=self._base_name)


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
        return _("Base {BASE} of type {BASE_TYPE} destroyed at location {LOCATION}. Maintenance failed.").format(
                  BASE=self._base_name, BASE_TYPE=self.base_type.name, LOCATION=self.location.name)

    @property
    def full_message(self):
        return _("The base {BASE} has fallen into disrepair; I can no longer use it.").format(
                  BASE=self._base_name)


@register_saveable_log_message
class LogBaseDiscovered(AbstractBaseRelatedLogMessage):

    log_message_serial_id = 'base-lost-discovered'
    _log_message_serial_fields = {
        'discovered_by_group_id': '_discovered_by_group_id',
    }
    _log_message_serial_converters = {
        'discovered_by_group_id': id_converter("group"),
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
        log_format = self.group_spec.discover_log or \
                     _("Base {BASE} of type {BASE_TYPE} destroyed at location {LOCATION}.")
        return log_format.format(BASE=self._base_name, BASE_TYPE=self.base_type.name, LOCATION=self.location.name)

    @property
    def full_message(self):
        return _("My use of {BASE} has been discovered. {MESSAGE}").format(
                 BASE=self._base_name, MESSAGE=self.group_spec.discover_desc)


@register_saveable_log_message
class LogItemConstructionComplete(AbstractBaseRelatedLogMessage):

    log_message_serial_id = 'item-in-base-constructed'
    _log_message_serial_fields = {
        'item_spec_id': '_item_spec_id',
        'item_count': '_item_count',
    }
    _log_message_serial_converters = {
        'item_spec_id': id_converter("item")
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
        return _("{ITEM_TYPE_NAME} built in {BASE_NAME} at {LOCATION}").format(
                 ITEM_TYPE_NAME=self.item_spec.name, BASE_NAME=self._base_name, BASE_TYPE=self.base_type.name,
                 LOCATION=self.location.name)

    @property
    def full_message(self):
        if self._item_count == 1:
            text = _("The construction of {ITEM} in {BASE} is complete.").format(
                     ITEM=self.item_spec.name, BASE=self._base_name)
        else:  # Just finished several items.
            text = _("The constructions of each {ITEM} in {BASE} are complete.").format(
                     ITEM=self.item_spec.name, BASE=self._base_name)
        return text


# Delete again as it is not a general purpose decorator
del register_saveable_log_message
