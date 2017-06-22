import unittest

from . import funcs


class TestFuncs(unittest.TestCase):
    def test_simple_evaluation(self):
        equals = funcs.DemoEqualsCondition("==", 1, 1)
        self.assertTrue(equals.evaluate())
        not_equals = funcs.DemoEqualsCondition("!=", 1, 1)
        self.assertFalse(not_equals.evaluate())

    def test_and_logic(self):
        condition = funcs.AND(
            funcs.DemoEqualsCondition("==", 100, 100),
            funcs.DemoEqualsCondition("==", "a", "a"),
            funcs.DemoEqualsCondition("!=", 100, 101),
            funcs.DemoEqualsCondition("!=", "a", "b"),
        )
        self.assertTrue(condition.evaluate())

    def test_shorthand_and_logic(self):
        condition_a = funcs.DemoEqualsCondition("==", "", "")
        condition_b = funcs.DemoEqualsCondition("==", 42, 42)
        condition_c = (condition_a & condition_b)
        self.assertTrue(condition_c.evaluate())
        self.assertTrue((condition_a | condition_b).evaluate())
        self.assertTrue((condition_a & condition_b).evaluate())

    def test_shorthand_or_logic(self):
        condition_a = funcs.DemoEqualsCondition("==", "", "")
        condition_b = funcs.DemoEqualsCondition("==", "", 42)
        condition = condition_a | condition_b
        self.assertTrue(condition.evaluate())
        self.assertFalse((condition_a & condition_b).evaluate())

    def test_or_logic(self):
        condition_a = funcs.OR(
            funcs.DemoEqualsCondition("==", 1, 1),
            funcs.DemoEqualsCondition("==", 1, 2),
        )
        condition_b = funcs.OR(
            funcs.DemoEqualsCondition("==", 1, 2),
            funcs.DemoEqualsCondition("==", 1, 1),
        )
        self.assertTrue(condition_a.evaluate())
        self.assertTrue(condition_b.evaluate())

    def test_combined_logic(self):
        nested_conditions = funcs.OR(
            funcs.DemoEqualsCondition("==", 1, "a"),
            funcs.DemoEqualsCondition("==", 1, 1),
        )
        conditions = funcs.AND(
            nested_conditions,
            funcs.DemoEqualsCondition("==", "a", "a"),
            funcs.DemoEqualsCondition("==", 1, 1),
        )
        self.assertTrue(conditions.evaluate())

    def test_if_then(self):
        counter_action = funcs.DemoIncrementCounterAction()
        condition = funcs.DemoEqualsCondition("==", 1, 1)
        function = funcs.IF_THEN(condition, (counter_action,))
        function()
        self.assertEquals(counter_action.counter, 1)

    def test_if_not_then(self):
        counter_action = funcs.DemoIncrementCounterAction()
        condition = funcs.DemoEqualsCondition("==", "abc", "xyz")
        function = funcs.IF_NOT_THEN(condition, (counter_action,))
        function()
        self.assertEquals(counter_action.counter, 1)

    def test_if_then_else(self):
        counter_action = funcs.DemoIncrementCounterAction()
        condition = funcs.DemoEqualsCondition("==", "abc", "xyz")
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
        condition_a = funcs.DemoEqualsCondition("==", "abc", "abc") # True
        condition_b = funcs.DemoEqualsCondition("==", 12345, 12345) # True
        condition_c = funcs.DemoEqualsCondition("==", "abc", 12345) # False
        condition_d = funcs.OR( 
            condition_c,
            funcs.AND(condition_a, condition_b,),
        ) # False OR (True AND TRUE)
        counter_action = funcs.DemoIncrementCounterAction()
        actions = (
            counter_action,
            counter_action,
        )
        funcs.ON("test_event", funcs.IF_THEN(condition_d, actions))
        funcs.FIRE_EVENT("test_event")
        self.assertEquals(counter_action.counter, 2)

