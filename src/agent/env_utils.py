import os
from dotenv import load_dotenv

load_dotenv(override=True)
QWEN_API_KEY = os.getenv("DASHSCOPE_API_KEY")
QWEN_BASE_URL = os.getenv("BASE_URL")
