import unittest

from last.server import parse_message

class TestParseMessage(unittest.TestCase):

    def test_200(self):
        self.assertEqual(parse_message({'action': 'presence', 'time':1.1}),{'response':200})

    def test_no_time(self):
        self.assertEqual(parse_message({'action': 'presence'}), {'response': 400, 'error':'Bad Request'})

    def test_no_action(self):
        self.assertEqual(parse_message({"time":1.1}), {'response': 400, 'error':'Bad Request'})

    def test_action_not_presence(self):
        self.assertEqual(parse_message({'action': 'message',"time":1.1}), {'response': 400, 'error':'Bad Request'})


if __name__ == '__main__':
    unittest.main()