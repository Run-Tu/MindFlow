from .samba import SambaNova


def available() -> set:
    return {"MiniMax-M3", "MiniMax-M2.7"}


class MiniMax(SambaNova):
    available_models = available()
    default_model = "MiniMax-M3"
    base_urls = {
        "global_en": "https://api.minimax.io/v1",
        "cn_zh": "https://api.minimaxi.com/v1",
    }

    def __init__(self,
                 api_key: str,
                 model="MiniMax-M3",
                 messages=None,
                 system="You are a helpful assistant.",
                 remember=False,
                 limit=30,
                 region="global_en",
                 base_url=None,
                 endpoint=None):
        if endpoint is None:
            base_url = base_url or self.base_urls.get(region)
            if base_url is None:
                raise ValueError(f"Unsupported MiniMax region: {region}")
            endpoint = f"{base_url.rstrip('/')}/chat/completions"

        self.region = region
        self.base_url = base_url or endpoint.rsplit("/chat/completions", 1)[0]
        super().__init__(api_key=api_key,
                         model=model,
                         messages=messages,
                         system=system,
                         remember=remember,
                         limit=limit,
                         endpoint=endpoint)
