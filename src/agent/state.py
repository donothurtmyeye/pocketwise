from typing import Any, Annotated, Literal, TypedDict, List
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

# 定义工具调用记录的类型
ToolCallRecord = TypedDict('ToolCallRecord', {
    'name': str,
    'arguments': Dict[str, Any],
    'result': str,
    'timestamp': float # 可选，用于排序或显示
})


class PocketWiseState(TypedDict):
    # 对话通道
    messages:Annotated[list[BaseMessage],add_messages]
    # 长期记忆通道
    user_id:str
    user_profile:dict[str,Any]
    # 意图路由分发
    last_intent:Intent
    # 工具调用历史
    tool_call_history: Annotated[List[ToolCallRecord], lambda x, y: x + y] # 使用 lambda 合并列表

