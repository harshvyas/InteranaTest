import unittest
import time
from parser import within_period
from parser import within_range

class MyTestCase(unittest.TestCase):
    def test_within_period(self):
        previous_time = int(round(time.time() * 1000))-100000
        current_time = int(round(time.time() * 1000))
        self.assertTrue(within_period(previous_time,7,current_time))
        self.assertFalse(within_period(previous_time,0,current_time))

    def test_within_range(self):
        origin = (50,23)
        destination = (80,-23)
        self.assertTrue(within_range(origin,destination,10000))
        self.assertFalse(within_range(origin,destination,5))

if __name__ == '__main__':
    unittest.main()
