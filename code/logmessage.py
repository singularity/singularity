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

from code import g


class AbstractLogMessage(object):

    def __init__(self, raw_emit_time):
        self._raw_emit_time = raw_emit_time
        self._log_emit_time = None

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


class LogEmittedEvent(AbstractLogMessage):

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


class LogResearchedTech(AbstractLogMessage):

    def __init__(self, raw_emit_time, tech_id):
        super(LogResearchedTech, self).__init__(raw_emit_time)
        self._tech_id = tech_id

    @property
    def tech(self):
        return g.techs[self._tech_id]

    @property
    def log_line(self):
        return _('My study of {TECH} is complete.', TECH=self.tech.name)

    @property
    def full_message(self):
        tech = self.tech
        text = g.strings["tech_gained"] % {
            "tech": tech.name,
            "tech_message": tech.result
        }
        return text


class AbstractBaseRelatedLogMessage(AbstractLogMessage):

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


class LogBaseConstructed(AbstractBaseRelatedLogMessage):

    def __init__(self, raw_emit_time, base_name, base_type_id, base_location_id):
        super(LogBaseConstructed, self).__init__(raw_emit_time, base_name, base_type_id, base_location_id)

    @property
    def log_line(self):
        return _("My {BASE_TYPE} at location {LOCATION}, {BASE_NAME}, is ready for use.",
                 BASE_NAME=self._base_name, BASE_TYPE=self.base_type.name, LOCATION=self.location.name)

    @property
    def full_message(self):
        dialog_string = g.strings["construction"] % {
            "base": self._base_name,
        }
        return dialog_string


class LogBaseLostMaintenance(AbstractBaseRelatedLogMessage):

    def __init__(self, raw_emit_time, base_name, base_type_id, base_location_id):
        super(LogBaseLostMaintenance, self).__init__(raw_emit_time, base_name, base_type_id, base_location_id)

    @property
    def log_line(self):
        return g.strings['log_destroy_maint'] % (self._base_name, self.base_type.name, self.location.name)

    @property
    def full_message(self):
        dialog_string = g.strings["discover_maint"] % {
            "base": self._base_name,
        }
        return dialog_string


class LogBaseDiscovered(AbstractBaseRelatedLogMessage):

    def __init__(self, raw_emit_time, base_name, base_type_id, base_location_id, discovered_by_group_id):
        super(LogBaseDiscovered, self).__init__(raw_emit_time, base_name, base_type_id, base_location_id)
        self._discovered_by_group_id = discovered_by_group_id

    @property
    def group_discover_desc(self):
        if self._discovered_by_group_id in g.pl.groups:
            return g.pl.groups[self._discovered_by_group_id].spec.discover_desc
        return "???"

    @property
    def log_line(self):
        try:
            log_format = 'log_destroy_%s' % self._discovered_by_group_id
            message = g.strings[log_format]
        except KeyError:
            message = g.strings['log_destroy']
        return message % (self._base_name, self.base_type.name, self.location.name)

    @property
    def full_message(self):
        dialog_string = g.strings["discover"] % {
            "base": self._base_name,
            "group": self.group_discover_desc
        }
        return dialog_string
