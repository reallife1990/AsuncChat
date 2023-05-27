import unittest
import time
from last.client import create_message, process_ans

class Test(unittest.TestCase):

    def test_create_message(self):
        test = create_message()
        self.assertEqual(test, {'action': 'presence',
                                'time': time.time(),
                                'user': 'test'})

    def test_process_ans_200(self):
        test = process_ans({'response':200})
        self.assertEqual(test,'200 : OK')

    def test_process_ans_400(self):
        test = process_ans({'response': 400, 'error':'Bad request'})
        self.assertEqual(test,'400 : Bad request')

    def test_no_response(self):
        self.assertRaises(ValueError, process_ans, {'error': 'Bad Request'})

if __name__ == '__main__':
    unittest.main()