from langchain_openai import ChatOpenAI
from env_utils import QWEN_API_KEY,QWEN_BASE_URL
llm_chat = ChatOpenAI(
    model="qwen-flash",
    temperature=0.25,
    api_key=QWEN_API_KEY,
    base_url=QWEN_BASE_URL
)
llm_plan = ChatOpenAI(
    model="qwen-flash",
    temperature=0.7,
    api_key=QWEN_API_KEY,
    base_url=QWEN_BASE_URL
)