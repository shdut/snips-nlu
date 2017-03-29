from duckling import core
from enum import Enum

from utils import LimitedSizeDict, classproperty

core.load()


class BuiltInEntity(Enum):
    DATETIME = {"label": "snips/datetime", "duckling_dim": "time"}
    DURATION = {"label": "snips/duration", "duckling_dim": "duration"}
    NUMBER = {"label": "snips/number", "duckling_dim": "number"}

    @property
    def label(self):
        return self.value["label"]

    @property
    def duckling_dim(self):
        return self.value["duckling_dim"]

    @classproperty
    @classmethod
    def built_in_entity_by_label(cls):
        try:
            return cls._built_in_entity_by_label
        except AttributeError:
            cls._built_in_entity_by_label = dict()
            for ent in cls:
                cls._built_in_entity_by_label[ent.label] = ent
        return cls._built_in_entity_by_label

    @classmethod
    def from_label(cls, label, default=None):
        try:
            ent = cls.built_in_entity_by_label[label]
        except KeyError:
            if default is None:
                raise KeyError("Unknown entity '%s'" % label)
            else:
                return default
        return ent

    @classproperty
    @classmethod
    def built_in_entity_by_duckling_dim(cls):
        try:
            return cls._built_in_entity_by_duckling_dim
        except AttributeError:
            cls._built_in_entity_by_duckling_dim = dict()
            for ent in cls:
                cls._built_in_entity_by_duckling_dim[ent.duckling_dim] = ent
        return cls._built_in_entity_by_duckling_dim

    @classmethod
    def from_duckling_dim(cls, duckling_dim, default=None):
        try:
            ent = cls.built_in_entity_by_duckling_dim[duckling_dim]
        except KeyError:
            if default is None:
                raise KeyError("Unknown duckling dim '%s'" % duckling_dim)
            else:
                return default
        return ent


def scope_to_dims(scope):
    return [entity.duckling_dim for entity in scope]


_DUCKLING_CACHE = LimitedSizeDict(size_limit=1000)


def get_built_in_entities(text, language, scope=None):
    global _DUCKLING_CACHE
    if scope is None:
        dims = core.get_dims(language)
    else:
        dims = scope_to_dims(scope)

    if (text, language) not in _DUCKLING_CACHE:
        parse = core.parse(language, text)
        _DUCKLING_CACHE[(text, language)] = parse
    else:
        parse = _DUCKLING_CACHE[(text, language)]

    parsed_entities = []
    for ent in parse:
        if ent["dim"] in dims:
            parsed_entity = {
                "match_range": (ent["start"], ent["end"]),
                "value": ent["body"],
                "entity": BuiltInEntity.from_duckling_dim(ent["dim"])
            }
            parsed_entities.append(parsed_entity)
    return parsed_entities
