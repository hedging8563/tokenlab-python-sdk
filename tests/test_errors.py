import unittest

import httpx

import tokenlab
from tokenlab import TokenLabClient, TokenLabError


def make_client(handler):
    client = TokenLabClient(api_key="sk-test")
    client._client.close()
    client._client = httpx.Client(transport=httpx.MockTransport(handler))
    return client


class TokenLabErrorTest(unittest.TestCase):
    def test_exported_and_runtime_error_subclass(self):
        self.assertIs(tokenlab.TokenLabError, TokenLabError)
        self.assertIn("TokenLabError", tokenlab.__all__)
        self.assertTrue(issubclass(TokenLabError, RuntimeError))

    def test_json_error_body_with_retry_after(self):
        calls = []
        body = {"error": {"code": "rate_limited", "type": "rate_limit_error", "message": "Too many requests"}}

        def handle(request):
            calls.append(request)
            return httpx.Response(429, json=body, headers={"x-request-id": "req_123", "Retry-After": "7"})

        with make_client(handle) as client:
            with self.assertRaises(TokenLabError) as ctx:
                client.list_models()
        err = ctx.exception
        self.assertIsInstance(err, RuntimeError)
        self.assertEqual(err.status_code, 429)
        self.assertEqual(err.code, "rate_limited")
        self.assertEqual(err.type, "rate_limit_error")
        self.assertEqual(err.message, "Too many requests")
        self.assertEqual(err.request_id, "req_123")
        self.assertEqual(err.retry_after, 7.0)
        self.assertTrue(str(err).startswith("TokenLab request failed:"))
        self.assertIn("rate_limited", str(err))
        self.assertIsInstance(err.__cause__, httpx.HTTPStatusError)
        self.assertEqual(len(calls), 1)  # no automatic retry

    def test_json_error_body_without_retry_after(self):
        def handle(request):
            return httpx.Response(400, json={"error": {"code": "invalid_request", "message": "model is required"}})

        with make_client(handle) as client:
            with self.assertRaises(TokenLabError) as ctx:
                client.create_response({})
        err = ctx.exception
        self.assertEqual(err.status_code, 400)
        self.assertEqual(err.code, "invalid_request")
        self.assertIsNone(err.type)
        self.assertEqual(err.message, "model is required")
        self.assertIsNone(err.request_id)
        self.assertIsNone(err.retry_after)

    def test_non_json_error_body(self):
        def handle(request):
            return httpx.Response(502, text="Bad Gateway", headers={"x-request-id": "req_502", "retry-after": "30"})

        with make_client(handle) as client:
            with self.assertRaises(TokenLabError) as ctx:
                client.get_models_json()
        err = ctx.exception
        self.assertEqual(err.status_code, 502)
        self.assertIsNone(err.code)
        self.assertIsNone(err.type)
        self.assertEqual(err.message, "Bad Gateway")
        self.assertEqual(err.request_id, "req_502")
        self.assertEqual(err.retry_after, 30.0)
        self.assertEqual(str(err), "TokenLab request failed: Bad Gateway")

    def test_non_json_error_body_without_retry_after(self):
        def handle(request):
            return httpx.Response(500, text="")

        with make_client(handle) as client:
            with self.assertRaises(TokenLabError) as ctx:
                client.get_pricing_json()
        err = ctx.exception
        self.assertEqual(err.status_code, 500)
        self.assertEqual(err.message, "")
        self.assertIsNone(err.retry_after)
        self.assertTrue(str(err).startswith("TokenLab request failed:"))

    def test_unparseable_retry_after_is_none(self):
        def handle(request):
            return httpx.Response(503, json={"error": {"message": "busy"}}, headers={"Retry-After": "Wed, 21 Oct 2026 07:28:00 GMT"})

        with make_client(handle) as client:
            with self.assertRaises(TokenLabError) as ctx:
                client.list_pricing()
        self.assertIsNone(ctx.exception.retry_after)
        self.assertEqual(ctx.exception.message, "busy")

    def test_success_still_returns_json(self):
        def handle(request):
            return httpx.Response(200, json={"data": []})

        with make_client(handle) as client:
            self.assertEqual(client.list_models(), {"data": []})


if __name__ == "__main__":
    unittest.main()
