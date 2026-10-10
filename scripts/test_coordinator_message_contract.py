"""Offline checks for the explicit read receipt contract."""
import unittest
from coordinator_message_contract import validate_ack, validate_ack_result


class AckTests(unittest.TestCase):
    def setUp(self):
        self.request = {'method': 'message.ack', 'body': {'cursor': '42'}}
        self.result = {'actor': 'nuiak', 'read_cursor': '42', 'state': 'read', 'work_accepted': False}

    def test_valid_read_is_not_work_acceptance(self):
        validate_ack(self.request)
        self.assertEqual(validate_ack_result(self.request, self.result), self.result)

    def test_invalid_cursors(self):
        for value in [42, True, None, '-1', '01', '4.2', ' 42', '9223372036854775808']:
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate_ack({'method': 'message.ack', 'body': {'cursor': value}})

    def test_identity_cannot_be_supplied(self):
        for key in ['actor', 'request_id', 'grant']:
            with self.subTest(key=key), self.assertRaises(ValueError):
                validate_ack({'method': 'message.ack', 'body': {'cursor': '42', key: 'x'}})

    def test_invalid_envelopes(self):
        for request in [None, {}, {'method': 'job.start', 'body': {'cursor': '42'}},
                        {'method': 'message.ack', 'body': []}, {**self.request, 'actor': 'x'}]:
            with self.subTest(request=request), self.assertRaises(ValueError):
                validate_ack(request)

    def test_work_acceptance_and_missing_fields_reject(self):
        for result in [None, {}, {**self.result, 'work_accepted': True},
                       {**self.result, 'work_accepted': 0}, {**self.result, 'state': 'accepted'},
                       {**self.result, 'actor': ''}, {**self.result, 'read_cursor': '41'}]:
            with self.subTest(result=result), self.assertRaises(ValueError):
                validate_ack_result(self.request, result)

    def test_server_cursor_can_already_be_later(self):
        validate_ack_result(self.request, {**self.result, 'read_cursor': '43'})


if __name__ == '__main__':
    unittest.main()
