from typing import Any, Annotated, Literal, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

Intent = Literal[
    "log_expense",  # 记录一笔消费
    "consult",  # 咨询某次消费/是否值得
    "generate_plan",  # 制定计划
    "update_plan",  # 更新计划
    "delete_plan",  # 删除计划
    "review_plan",  #查看计划
    "review_profile",  # 复盘/画像/概览
    "edit_profile",  # 修改画像字段
    "unknown"
]
class PocketWiseState(TypedDict):
    # 对话通道
    messages:Annotated[list[BaseMessage],add_messages]
    # 长期记忆通道
    user_id:str
    user_profile:dict[str,Any]
    # 意图路由分发
    last_intent:Intent

