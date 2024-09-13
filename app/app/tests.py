"""
a simple test
"""
from django.test import SimpleTestCase
from . import calc


class calcTest(SimpleTestCase):
    """test calc method"""

    def test_plus(self):
        element1 = 5
        element2 = 5
        res = calc.plus(element1, element2)
        self.assertEqual(res, 10)

    def test_sub(self):
        element1 = 10
        element2 = 2
        res = calc.sub(element1, element2)
        self.assertEqual(res, 8)
