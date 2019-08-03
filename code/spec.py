#file: spec.py
#Copyright (C) 2005,2006,2007,2008 Evil Mr Henry, Phil Bordelon, Brian Reid,
#                        and FunnyMan3595
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

#This file contains class to handle basic functionality of Spec's

import inspect


UNSET = object()


class InvalidDataEntryError(RuntimeError):
    pass


def promote_to_list(value):
    if not isinstance(value, list):
        return [value]
    return value


def validate_must_be_list(value):
    if type(value) != list:  # pragma: no cover
        raise TypeError("Must be list, got type %s (value: %s)" % (type(value), repr(value)))


class SpecDataField(object):

    def __init__(self, field_name, data_field_name=None, mandatory=None, converter=None, validator=None,
                 default_value=UNSET):
        self.field_name = field_name
        self.data_field_name = data_field_name if data_field_name is not None else field_name
        self.mandatory = mandatory
        self.default_value = default_value
        if self.mandatory is None:
            self.mandatory = True if default_value is UNSET else False
        self.converter = converter
        self.validator = validator
        assert self.mandatory or default_value is not UNSET, "%s (field: %s) must either be mandatory or have a " \
                                                             "default_value" % (self.__class__.__name__, field_name)
        assert not converter or not validator, "%s (field: %s) at can most have one of converter or validator" % \
                                               (self.__class__.__name__, field_name)

    def parse_data_field(self, raw_data_set, data_reference):
        try:
            value = raw_data_set[self.data_field_name]
        except KeyError:
            if self.mandatory:  # pragma: no cover
                raise InvalidDataEntryError("Missing mandatory data field %s (field name: %s) for %s" % (
                    self.data_field_name, self.field_name, data_reference))
            if callable(self.default_value):
                return self.default_value()
            return self.default_value

        if self.validator:
            self.validator(value)
        if self.converter:
            value = self.converter(value)
        return value


def spec_field_effect(mandatory=True):
    return SpecDataField('effect_data', data_field_name='effect', mandatory=mandatory, validator=list,
                         default_value=list)


class GenericSpec(object):

    spec_data_fields = None

    def __init__(self, id):
        self.id = id
        assert self.__class__.spec_data_fields is not None, "Class %s is missing spec_data_field" % \
                                                            self.__class__.__name__

    @classmethod
    def create_from_data_file(cls, data_id, spec_data):
        named_fields = {
            f.field_name: f.parse_data_field(spec_data, data_id)
            for f in cls.spec_data_fields
        }
        named_fields['id'] = data_id
        # Use reflection to call the constructor with the arguments
        # properly aligned
        arg_desc = inspect.getargspec(cls.__init__)
        args = [named_fields[name] for name in arg_desc.args[1:]]
        return cls(*args)

