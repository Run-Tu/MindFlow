"""Exercise the public wrapper through real HTTP with a local fake API."""

import asyncio
import os
import unittest
from unittest.mock import patch

from aiohttp import web
from aiohttp.test_utils import TestServer

from mindflow.llm import LLM
from mindflow.llm.models.minimax import MiniMax


class MiniMaxRequestTests(unittest.TestCase):
    """Capture serialized requests without provider credentials or inference."""

    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.requests = []
        app = web.Application()
        app.router.add_post("/{path:.*}", self.respond)
        self.server = TestServer(app)
        self.loop.run_until_complete(self.server.start_server())
        self.base_url = str(self.server.make_url("/v1"))
        self.environment = patch.dict(os.environ, {}, clear=True)
        self.environment.start()

    def tearDown(self):
        self.environment.stop()
        self.loop.run_until_complete(self.server.close())
        self.loop.close()
        asyncio.set_event_loop(None)

    async def respond(self, request):
        """Return an SSE fixture after recording the received JSON body."""
        self.requests.append((request.path, await request.json()))
        return web.Response(
            content_type="text/event-stream",
            text='data: {"choices":[{"delta":{"content":"answer"}}]}\n\n'
                 'data: [DONE]\n\n',
        )

    async def consume(self, chunks):
        """Consume the public streaming result on the test event loop."""
        return "".join([chunk async for chunk in chunks])

    def test_default_request_for_each_region_and_response_mode(self):
        """Use Flash by default and keep each region's existing endpoint."""
        for region, endpoint in MiniMax.base_urls.items():
            for stream in (False, True):
                with self.subTest(region=region, stream=stream):
                    llm = LLM(provider="minimax", api_key="test-key", region=region)
                    self.assertEqual(llm.llm.endpoint, endpoint + "/chat/completions")
                    llm.llm.endpoint = self.base_url + "/chat/completions"
                    result = llm.chat("hello", stream=stream)
                    if stream:
                        result = self.loop.run_until_complete(self.consume(result))
                    self.assertEqual(result, "answer")
                    path, payload = self.requests[-1]
                    self.assertEqual(path, "/v1/chat/completions")
                    self.assertEqual(payload, {
                        "model": "MiniMax-M3.1-Flash",
                        "messages": [
                            {"role": "system", "content": ""},
                            {"role": "user", "content": "hello"},
                        ],
                        "max_tokens": 1400,
                        "stream": True,
                    })

    def test_explicit_and_saved_models_reach_transport(self):
        """Never silently replace an explicitly configured model ID."""
        for model in ("MiniMax-M3.1-Flash", "MiniMax-M3", "MiniMax-M2.7", "custom-model"):
            for saved in (False, True):
                with self.subTest(model=model, saved=saved):
                    environment = {
                        "LLM_PROVIDER": "minimax",
                        "MINIMAX_API_KEY": "test-key",
                        "MINIMAX_MODEL": model if saved else "MiniMax-M3",
                        "MINIMAX_BASE_URL": self.base_url + "/",
                    }
                    with patch.dict(os.environ, environment, clear=True):
                        llm = LLM() if saved else LLM(model=model)
                    self.assertEqual(llm.chat("hello"), "answer")
                    self.assertEqual(self.requests[-1][1]["model"], model)

    def test_custom_endpoint_preserves_multimodal_and_tool_history(self):
        """Retain structured messages and omit unsupported request options."""
        history = [
            {"role": "assistant", "content": None, "reasoning_details": [{"text": "saved"}],
             "tool_calls": [{"id": "call_1", "type": "function",
                             "function": {"name": "lookup", "arguments": "{}"}}]},
            {"role": "tool", "tool_call_id": "call_1", "content": "result"},
        ]
        message = {"role": "user", "content": [
            {"type": "text", "text": "describe"},
            {"type": "image_url", "image_url": {"url": "https://example.invalid/image.png"}},
        ]}
        llm = LLM(provider="minimax", api_key="test-key", model="custom-model",
                  endpoint=str(self.server.make_url("/custom")), region="custom",
                  system="Keep history", messages=list(history))
        self.assertEqual(llm.chat(message, lmc=True), "answer")
        path, payload = self.requests[-1]
        self.assertEqual(path, "/custom")
        self.assertEqual(payload["model"], "custom-model")
        self.assertEqual(payload["messages"], [
            {"role": "system", "content": "Keep history"}, *history, message,
        ])
        self.assertEqual(llm.messages, [
            *history, message, {"role": "assistant", "content": "answer"},
        ])
        for unsupported in ("thinking", "reasoning_effort", "reasoning_split", "service_tier"):
            self.assertNotIn(unsupported, payload)


if __name__ == "__main__":
    unittest.main()
