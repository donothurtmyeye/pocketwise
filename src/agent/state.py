from typing import Any, Annotated, Literal, TypedDict, List, Dict
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
# 定义一个合并 tool_call_history 的函数
def merge_tool_histories(left: List[ToolCallRecord], right: List[ToolCallRecord]) -> List[ToolCallRecord]:
    # 如果左侧没有历史（例如，初始化时），则使用右侧
    if left is None:
        left = []
    # 如果右侧没有历史（例如，某次迭代未调用工具），则使用左侧
    if right is None:
        right = []
    return left + right

class PocketWiseState(TypedDict):
    # 对话通道
    messages:Annotated[list[BaseMessage],add_messages]
    # 长期记忆通道
    user_id:str
    user_profile:dict[str,Any]
    # 意图路由分发
    last_intent:Intent
    # 工具调用历史
    tool_call_history: Annotated[List[ToolCallRecord], merge_tool_histories]
