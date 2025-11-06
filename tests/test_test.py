import unittest
 
class Calculator():
    def add_num(self, a, b):
        return a + b
 
class MyTest(unittest.TestCase):
    def test_hello_world(self):
        myCal = Calculator()
        self.assertEqual(myCal.add_num(1, 2), 3)
 
if __name__ == '__main__':
  unittest.main()
