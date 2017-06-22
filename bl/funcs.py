"""This module is meant to help in creating an abstraction on
conditional evaluation. It's especially handy in turning complex business
logic into small digestable/testable chunks
"""
from collections import defaultdict


_EVENT_HANDLERS = defaultdict(list)


def ON(event_name, func):
    _EVENT_HANDLERS[event_name].append(func)


def FIRE_EVENT(event_name, *args, **kwargs):
    event_handlers = _EVENT_HANDLERS[event_name]
    for eh in event_handlers:
        eh(*args, **kwargs)


class Condition(object):
    EQUALS = "=="
    NOT_EQUALS = "!="

    def __init__(self, operator, lhs, rhs):
        self.operator = operator
        self.lhs = lhs
        self.rhs = rhs

    def __or__(self, other_condition):
        return OR(self, other_condition)

    def __and__(self, other_condition):
        return AND(self, other_condition)

    def evaluate(self, *args, **kwargs):
        raise NotImplemented()


class Action(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def run(self, *args, **kwargs):
        raise NotImplemented()


class ConditionGroup(object):
    AND = "AND"
    OR = "OR"

    def __init__(self, operator="AND", *args):
        self.operator=operator
        self.conditions = args

    def __or__(self, other_condition):
        return OR(self, other_condition)

    def __and__(self, other_condition):
        return AND(self, other_condition)

    def evaluate(self, *args, **kwargs):
        for condition in self.conditions:
            result = condition.evaluate(*args, **kwargs)
            if self.operator == ConditionGroup.AND:
                if not result:
                    return False
            if self.operator == ConditionGroup.OR:
                if result:
                    return True
        if self.operator == ConditionGroup.AND:
            return True
        if self.operator == ConditionGroup.OR:
            return False
        raise NotImplemented()


def AND(*args):
    return ConditionGroup("AND", *args)


def OR(*args):
    return ConditionGroup("OR", *args)


def IF_THEN_ELSE(evaluable, actions, else_actions):
    def func(*args, **kwargs):
        to_run = actions if evaluable.evaluate(*args, **kwargs) else else_actions
        for action in to_run:
            action.run(*args, **kwargs)
    return func


def IF_THEN(evaluable, actions):
    return IF_THEN_ELSE(evaluable, actions, [])


def IF_NOT_THEN(evaluable, actions):
    return IF_THEN_ELSE(evaluable, [], actions)
