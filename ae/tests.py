import unittest

from . import funcs
from .funcs import IF, IF_NOT, AND, OR, Evaluable, Action, CmpEvaluable, RUN


class CmpCondition(CmpEvaluable):
    pass


class Equals(CmpCondition):
    def __init__(self, lhs, rhs):
        return super(Equals, self).__init__("==", lhs, rhs)


class DifferentThan(CmpCondition):
    def __init__(self, lhs, rhs):
        return super(DifferentThan, self).__init__("!=", lhs, rhs)


class AlwayTrueCondition(Evaluable):
    def __call__(self, *args, **kwargs):
        return True


class IncrementCounterAction(Action):
    def __init__(self, counter=0):
        self.counter = counter

    def __call__(self):
        self.counter += 1


class TestFuncs(unittest.TestCase):
    def test_simple_evaluation(self):
        equals = Equals(1, 1)
        self.assertTrue(equals())
        not_equals = CmpCondition("!=", 1, 1)
        self.assertFalse(not_equals())

    def test_evaluate_base_evaluable(self):
        with self.assertRaises(Exception):
            e = Evaluable()
            e()

    def test_and_logic(self):
        condition = AND(
            CmpCondition("==", 100, 100),
            CmpCondition("==", "a", "a"),
            CmpCondition("!=", 100, 101),
            CmpCondition("!=", "a", "b"),
        )
        self.assertTrue(condition())

    def test_shorthand_and_logic(self):
        condition_a = CmpCondition("==", "", "")
        condition_b = CmpCondition("==", 42, 42)
        condition_c = (condition_a & condition_b)
        self.assertTrue(condition_c())
        self.assertTrue((condition_a | condition_b)())
        self.assertTrue((condition_a & condition_b)())

    def test_shorthand_or_logic(self):
        condition_a = CmpCondition("==", "", "")
        condition_b = CmpCondition("==", "", 42)
        condition = condition_a | condition_b
        self.assertTrue(condition())
        self.assertFalse((condition_a & condition_b)())

    def test_or_logic(self):
        condition_a = OR(
            CmpCondition("==", 1, 1),
            CmpCondition("==", 1, 2),
        )
        condition_b = OR(
            CmpCondition("==", 1, 2),
            CmpCondition("==", 1, 1),
        )
        self.assertTrue(condition_a())
        self.assertTrue(condition_b())

    def test_combined_logic(self):
        nested_conditions = OR(
            CmpCondition("==", 1, "a"),
            CmpCondition("==", 1, 1),
        )
        conditions = AND(
            nested_conditions,
            CmpCondition("==", "a", "a"),
            CmpCondition("==", 1, 1),
        )
        self.assertTrue(conditions())

    def test_if_then(self):
        counter_action = IncrementCounterAction()
        condition = CmpCondition("==", 1, 1)
        function = IF(condition, (counter_action,))
        function()
        self.assertEquals(counter_action.counter, 1)

    def test_if_not_then(self):
        counter_action = IncrementCounterAction()
        condition = CmpCondition("==", "abc", "xyz")
        function = IF_NOT(condition, (counter_action,))
        function()
        self.assertEquals(counter_action.counter, 1)

    def test_if_then_else(self):
        counter_action = IncrementCounterAction()
        condition = CmpCondition("==", "abc", "xyz")
        then_actions = (
            counter_action,
            counter_action,
        )
        else_actions = (
            counter_action,
            counter_action,
            counter_action,
        )
        IF(condition, then_actions, else_actions)()
        self.assertEquals(3, counter_action.counter)

    def test_event_handlers(self):
        self.test_value = 0
        def handler():
            self.test_value += 1
        funcs.ON("test", handler)
        funcs.ON("test", handler)
        funcs.FIRE_EVENT("test")
        self.assertEquals(2, self.test_value)

    def test_unit_integration(self):
        condition_a = CmpCondition("==", "abc", "abc") # True
        condition_b = CmpCondition("==", 12345, 12345) # True
        condition_c = CmpCondition("==", "abc", 12345) # False
        condition_d = OR( 
            condition_c,
            AND(condition_a, condition_b,),
        ) # False OR (True AND TRUE)
        counter_action = IncrementCounterAction()
        actions = (
            counter_action,
            counter_action,
        )
        funcs.ON("test_event", IF(condition_d, actions))
        funcs.FIRE_EVENT("test_event")
        self.assertEquals(counter_action.counter, 2)


class Subject(object):
    def __init__(self, identifier):
        self.identifier = identifier
        self.counter = 0


class User(object):
    def __init__(self, username):
        self.username = username


class EvaluationContext(object):
    def __init__(self, subject, user):
        self.subject = subject
        self.user = user


def dec_subject_counter(eval_context):
    eval_context.subject.counter -= 1


def inc_subject_counter(eval_context):
    eval_context.subject.counter += 1


def user_has_username(username):
    def decorator(eval_context):
        return eval_context.user.username == username
    return decorator


def subject_has_count(counter):
    def decorator(eval_context):
        return eval_context.subject.counter == counter
    return decorator


class TestExtended(unittest.TestCase):
    def setUp(self):
        self.user_1 = User("user_1")
        self.user_2 = User("user_2")
        self.subject_1 = Subject("subject_1")
        self.subject_2 = Subject("subject_2")

    def test_integration(self):
        context = EvaluationContext(self.subject_1, self.user_1)
        e = IF(subject_has_count(0), (inc_subject_counter,))(context)
        self.assertEqual(1, self.subject_1.counter)

    def test_another_integration(self):
        context = EvaluationContext(self.subject_2, User("admin"))
        is_admin_user = user_has_username("admin")
        has_0_counter = subject_has_count(0)
        RUN(context, 
            IF(OR(is_admin_user, has_0_counter), (inc_subject_counter,)),
            IF(is_admin_user, (dec_subject_counter,)),
            IF(is_admin_user, (inc_subject_counter,)),
        )
        self.assertEqual(0, self.subject_1.counter)
        self.assertEqual(1, self.subject_2.counter)

