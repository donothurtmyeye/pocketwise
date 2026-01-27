from langchain_openai import ChatOpenAI
from env_utils import QWEN_API_KEY,QWEN_BASE_URL
llm_chat = ChatOpenAI(
    model="qwen-flash-2025-07-28",
    temperature=0.3,
    api_key=QWEN_API_KEY,
    base_url=QWEN_BASE_URL
)
llm_plan = ChatOpenAI(
    model="qwen-flash-2025-07-28",
    temperature=0.7,
    api_key=QWEN_API_KEY,
    base_url=QWEN_BASE_URL
)