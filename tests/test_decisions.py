import json
import unittest
import httpx
from tokenlab import TokenLabClient


class DecisionsTest(unittest.TestCase):
    def test_native_request_result_error_and_timeout(self):
        requests = []
        answer = {"model": "jev-1.13", "answers": {"refund": {"type": "noul", "noul": 0.8}}, "usage": {"input_tokens": 20, "output_tokens": 3}}
        status = 200

        def handle(request):
            requests.append(request)
            if status == 0:
                raise httpx.ReadTimeout("test timeout", request=request)
            return httpx.Response(status, json=answer if status == 200 else {"error": {"code": "invalid_request"}})

        with TokenLabClient(api_key="sk-test") as client:
            client._client.close()
            client._client = httpx.Client(transport=httpx.MockTransport(handle))
            body = {"model": "jev-1.13", "state": {"ticket": "Refund requested"}, "questions": {"refund": {"type": "noul", "instructions": "Is a refund requested?"}}}
            self.assertEqual(client.evaluate_decisions(body), answer)
            self.assertEqual(str(requests[0].url), "https://api.tokenlab.sh/v1/systemone")
            self.assertEqual(requests[0].headers["Authorization"], "Bearer sk-test")
            self.assertEqual(json.loads(requests[0].content), body)
            status = 400
            with self.assertRaisesRegex(RuntimeError, "invalid_request"):
                client.evaluate_decisions(body)
            status = 0
            with self.assertRaises(httpx.ReadTimeout):
                client.evaluate_decisions(body)
            self.assertEqual(len(requests), 3)
