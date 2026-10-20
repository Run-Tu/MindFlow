import asyncio
import os
import unittest
from unittest.mock import patch

from mindflow.llm import LLM
from mindflow.llm.models.minimax import MiniMax, available


class MiniMaxProviderTests(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        self.loop.close()
        asyncio.set_event_loop(None)

    def test_models_and_regional_endpoints(self):
        self.assertEqual(available(), {"MiniMax-M3.1-Flash", "MiniMax-M3"})
        self.assertEqual(MiniMax(api_key="test-key").model, "MiniMax-M3.1-Flash")

        global_client = MiniMax(api_key="test-key", model="MiniMax-M3")
        cn_client = MiniMax(
            api_key="test-key",
            model="MiniMax-M2.7",
            region="cn_zh",
        )

        self.assertEqual(
            global_client.endpoint,
            "https://api.minimax.io/v1/chat/completions",
        )
        self.assertEqual(
            cn_client.endpoint,
            "https://api.minimaxi.com/v1/chat/completions",
        )
        self.assertEqual(cn_client.model, "MiniMax-M2.7")

    def test_public_wrapper_accepts_explicit_configuration(self):
        with patch.dict(os.environ, {}, clear=True):
            llm = LLM(
                provider="MiniMax",
                api_key="test-key",
                model="MiniMax-M2.7",
                region="cn_zh",
            )

        self.assertIsInstance(llm.llm, MiniMax)
        self.assertEqual(llm.llm.model, "MiniMax-M2.7")
        self.assertEqual(
            llm.llm.endpoint,
            "https://api.minimaxi.com/v1/chat/completions",
        )

    def test_public_wrapper_reads_environment_configuration(self):
        environment = {
            "LLM_PROVIDER": "minimax",
            "MINIMAX_API_KEY": "test-key",
            "MINIMAX_MODEL": "MiniMax-M3",
            "MINIMAX_REGION": "global_en",
        }
        with patch.dict(os.environ, environment, clear=True):
            llm = LLM()

        self.assertEqual(llm.provider, "minimax")
        self.assertEqual(llm.llm.model, "MiniMax-M3")
        self.assertEqual(
            llm.llm.endpoint,
            "https://api.minimax.io/v1/chat/completions",
        )

    def test_unknown_region_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unsupported MiniMax region"):
            MiniMax(api_key="test-key", region="unknown")


if __name__ == "__main__":
    unittest.main()
