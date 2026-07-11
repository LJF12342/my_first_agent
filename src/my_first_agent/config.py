"""配置管理 — 通过 .env 文件和环境变量加载配置。"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置，优先读取环境变量，支持 .env 文件。

    配置项说明：
    - DEEPSEEK_API_KEY: DeepSeek API 密钥
    - DEEPSEEK_MODEL:   模型名称 (deepseek-chat / deepseek-reasoner)
    - DEEPSEEK_BASE_URL: API 地址
    - SEARCH_MAX_RESULTS: 每次搜索返回的最大结果数
    """

    deepseek_api_key: str = ""
    deepseek_model: str = "deepseek-chat"
    deepseek_base_url: str = "https://api.deepseek.com/v1"
    search_max_results: int = 5

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @property
    def llm_kwargs(self) -> dict:
        """返回传递给 ChatOpenAI 的参数。"""
        return {
            "model": self.deepseek_model,
            "api_key": self.deepseek_api_key,
            "base_url": self.deepseek_base_url,
            "temperature": 0.3,
        }


settings = Settings()
