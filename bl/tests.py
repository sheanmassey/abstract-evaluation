import unittest

from . import funcs


class DemoCmpCondition(funcs.Condition):
    def evaluate(self):
        if self.operator == funcs.Condition.EQUALS:
            return self.lhs == self.rhs
        if self.operator == funcs.Condition.NOT_EQUALS:
            return self.lhs != self.rhs
        raise NotImplemented("unknown cmp operator")


class DemoIncrementCounterAction(funcs.Action):
    def __init__(self, counter=0):
        self.counter = counter
    def run(self):
        self.counter += 1


class TestFuncs(unittest.TestCase):
    def test_simple_evaluation(self):
        equals = DemoCmpCondition("==", 1, 1)
        self.assertTrue(equals.evaluate())
        not_equals = DemoCmpCondition("!=", 1, 1)
        self.assertFalse(not_equals.evaluate())

    def test_and_logic(self):
        condition = funcs.AND(
            DemoCmpCondition("==", 100, 100),
            DemoCmpCondition("==", "a", "a"),
            DemoCmpCondition("!=", 100, 101),
            DemoCmpCondition("!=", "a", "b"),
        )
        self.assertTrue(condition.evaluate())

    def test_shorthand_and_logic(self):
        condition_a = DemoCmpCondition("==", "", "")
        condition_b = DemoCmpCondition("==", 42, 42)
        condition_c = (condition_a & condition_b)
        self.assertTrue(condition_c.evaluate())
        self.assertTrue((condition_a | condition_b).evaluate())
        self.assertTrue((condition_a & condition_b).evaluate())

    def test_shorthand_or_logic(self):
        condition_a = DemoCmpCondition("==", "", "")
        condition_b = DemoCmpCondition("==", "", 42)
        condition = condition_a | condition_b
        self.assertTrue(condition.evaluate())
        self.assertFalse((condition_a & condition_b).evaluate())

    def test_or_logic(self):
        condition_a = funcs.OR(
            DemoCmpCondition("==", 1, 1),
            DemoCmpCondition("==", 1, 2),
        )
        condition_b = funcs.OR(
            DemoCmpCondition("==", 1, 2),
            DemoCmpCondition("==", 1, 1),
        )
        self.assertTrue(condition_a.evaluate())
        self.assertTrue(condition_b.evaluate())

    def test_combined_logic(self):
        nested_conditions = funcs.OR(
            DemoCmpCondition("==", 1, "a"),
            DemoCmpCondition("==", 1, 1),
        )
        conditions = funcs.AND(
            nested_conditions,
            DemoCmpCondition("==", "a", "a"),
            DemoCmpCondition("==", 1, 1),
        )
        self.assertTrue(conditions.evaluate())

    def test_if_then(self):
        counter_action = DemoIncrementCounterAction()
        condition = DemoCmpCondition("==", 1, 1)
        function = funcs.IF_THEN(condition, (counter_action,))
        function()
        self.assertEquals(counter_action.counter, 1)

    def test_if_not_then(self):
        counter_action = DemoIncrementCounterAction()
        condition = DemoCmpCondition("==", "abc", "xyz")
        function = funcs.IF_NOT_THEN(condition, (counter_action,))
        function()
        self.assertEquals(counter_action.counter, 1)

    def test_if_then_else(self):
        counter_action = DemoIncrementCounterAction()
        condition = DemoCmpCondition("==", "abc", "xyz")
        then_actions = (
            counter_action,
            counter_action,
        )
        else_actions = (
            counter_action,
            counter_action,
            counter_action,
        )
        funcs.IF_THEN_ELSE(condition, then_actions, else_actions)()
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
        condition_a = DemoCmpCondition("==", "abc", "abc") # True
        condition_b = DemoCmpCondition("==", 12345, 12345) # True
        condition_c = DemoCmpCondition("==", "abc", 12345) # False
        condition_d = funcs.OR( 
            condition_c,
            funcs.AND(condition_a, condition_b,),
        ) # False OR (True AND TRUE)
        counter_action = DemoIncrementCounterAction()
        actions = (
            counter_action,
            counter_action,
        )
        funcs.ON("test_event", funcs.IF_THEN(condition_d, actions))
        funcs.FIRE_EVENT("test_event")
        self.assertEquals(counter_action.counter, 2)

