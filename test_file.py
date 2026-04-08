import unittest
import json
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from basic_http import handle_roll_dice


class TestAPI(unittest.TestCase):

    PROBS = [0.1, 0.2, 0.3, 0.1, 0.2, 0.1]

    def _req(self, body_dict):
        body = json.dumps(body_dict)
        return f"GET /roll_dice HTTP/1.1\r\nHost: localhost\r\n\r\n{body}"

    def test_valid_returns_200(self):
        status, resp = handle_roll_dice(self._req({"probabilities": self.PROBS, "number_of_random": 10}))
        self.assertEqual(status, 200)
        self.assertEqual(resp["status"], "success")

    def test_valid_correct_count(self):
        status, resp = handle_roll_dice(self._req({"probabilities": self.PROBS, "number_of_random": 10}))
        self.assertEqual(len(resp["dices"]), 10)

    def test_valid_echoes_probabilities(self):
        status, resp = handle_roll_dice(self._req({"probabilities": self.PROBS, "number_of_random": 5}))
        self.assertEqual(resp["probabilities"], self.PROBS)

    def test_dice_values_in_range(self):
        status, resp = handle_roll_dice(self._req({"probabilities": self.PROBS, "number_of_random": 500}))
        for d in resp["dices"]:
            self.assertIn(d, range(1, 7))

    def test_malformed_json_returns_400(self):
        req = "GET /roll_dice HTTP/1.1\r\n\r\n{not: valid json}"
        status, resp = handle_roll_dice(req)
        self.assertEqual(status, 400)
        self.assertIn("JSON", resp["message"])

    def test_empty_body_returns_400(self):
        status, resp = handle_roll_dice("GET /roll_dice HTTP/1.1\r\n\r\n")
        self.assertEqual(status, 400)

    def test_missing_probabilities_returns_400(self):
        status, resp = handle_roll_dice(self._req({"number_of_random": 5}))
        self.assertEqual(status, 400)
        self.assertIn("probabilities", resp["message"])

    def test_wrong_sum_returns_400(self):
        status, resp = handle_roll_dice(self._req({"probabilities": [0.2]*6, "number_of_random": 5}))
        self.assertEqual(status, 400)

    def test_negative_prob_returns_400(self):
        status, resp = handle_roll_dice(self._req({"probabilities": [0.3, 0.2, 0.3, 0.1, 0.2, -0.1], "number_of_random": 5}))
        self.assertEqual(status, 400)

    def test_wrong_length_returns_400(self):
        status, resp = handle_roll_dice(self._req({"probabilities": [0.5, 0.5], "number_of_random": 5}))
        self.assertEqual(status, 400)

    def test_negative_number_of_random_returns_400(self):
        status, resp = handle_roll_dice(self._req({"probabilities": self.PROBS, "number_of_random": -1}))
        self.assertEqual(status, 400)

    def test_zero_number_of_random_returns_400(self):
        status, resp = handle_roll_dice(self._req({"probabilities": self.PROBS, "number_of_random": 0}))
        self.assertEqual(status, 400)


if __name__ == "__main__":
    unittest.main(verbosity=2)