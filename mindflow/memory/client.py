from chromadb import HttpClient, AsyncHttpClient

import logging
logging.disable(logging.CRITICAL + 1)

Memory: HttpClient = HttpClient
AsyncMemory: AsyncHttpClient = AsyncHttpClient

# can't believe HttpClient and AsyncHttpClient are functions, not classes
# class Memory(HttpClient):
#     def __init__(self, host: str = None, port: int = None, telemetry: bool = False):
#         self.client = HttpClient(host=host or "localhost", 
#                                  port=port or 8000, 
#                                  settings=Settings(anonymized_telemetry=telemetry))

# class AsyncMemory(AsyncHttpClient):
#     def __init__(self, host: str = None, port: int = None, telemetry: bool = False):
#         super().__init__(host=host or "localhost", 
#                          port=port or 8000, 
#                          settings=Settings(anonymized_telemetry=telemetry))
