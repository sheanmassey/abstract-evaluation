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


class Evaluable(object):
    """
    """
    def __or__(self, other_condition):
        return OR(self, other_condition)

    def __and__(self, other_condition):
        return AND(self, other_condition)

    def __call__(self, *args, **kwargs):
        """implement in children classes and have it return a bool
        """
        raise NotImplemented()


class CmpEvaluable(Evaluable):
    EQUALS = "=="
    NOT_EQUALS = "!="

    def __init__(self, operator, lhs, rhs):
        self.operator = operator
        self.lhs = lhs
        self.rhs = rhs

    def __call__(self, *args, **kwargs):
        if self.operator == CmpEvaluable.EQUALS:
            return self.lhs == self.rhs
        if self.operator == CmpEvaluable.NOT_EQUALS:
            return self.lhs != self.rhs
        raise NotImplemented("unknown cmp operator")


class Action(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __call__(self, *args, **kwargs):
        raise NotImplemented()


class EvaluableGroup(Evaluable):
    AND = "AND"
    OR = "OR"

    def __init__(self, operator="AND", *args):
        self.operator=operator
        self.conditions = args

    def __call__(self, *args, **kwargs):
        for condition in self.conditions:
            result = condition(*args, **kwargs)
            if self.operator == EvaluableGroup.AND:
                if not result:
                    return False
            if self.operator == EvaluableGroup.OR:
                if result:
                    return True
        if self.operator == EvaluableGroup.AND:
            return True
        if self.operator == EvaluableGroup.OR:
            return False
        raise NotImplemented()


def AND(*args):
    return EvaluableGroup("AND", *args)


def OR(*args):
    return EvaluableGroup("OR", *args)


def IF(evaluable, then_actions=None, else_actions=None):
    """
    """
    def func(*args, **kwargs):
        actions = then_actions if evaluable(*args, **kwargs) else else_actions
        if not actions:
            return
        for action in actions:
            action(*args, **kwargs)
    return func


def IF_NOT(evaluable, then_actions):
    return IF(evaluable, [], then_actions)


def RUN(context, *funcs):
    for func in funcs:
        func(context)
