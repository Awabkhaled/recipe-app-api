"""
a simple test
"""
from django.test import SimpleTestCase
from . import calc

class calcTest(SimpleTestCase):
    """
    test calc methos
    """
    def test_plus(self):
        element1=5
        element2=5
        res=calc.plus(element1,element2)
        self.assertEqual(res,10)