from model import llm_chat, llm_plan
from state import PocketWiseState, Intent
from tools import (
    view_user_profile,
    edit_user_profile,
    log_notable_expense,
    view_recent_expenses,
    detect_impulse_buying,
    log_plan,
    view_plan,
    update_plan,
    delete_plan,
)
from prompts import get_intent_prompt, get_chatbot_prompt, get_plan_prompt, get_guidance_map
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage, BaseMessage
from langchain.agents import create_agent
from typing import List, Dict, Any
import database as db


class GraphConstants:
    """图配置常量"""
    MAX_MESSAGES = 20
    PLAN_AGENT_THREAD_ID = "plan_agent"
    DEFAULT_INTENT = "unknown"

    # 节点名称常量
    NODE_LOAD_CONTEXT = "load_context"
    NODE_RECOGNIZE_INTENT = "recognize_intent"
    NODE_TRUNCATE_HISTORY = "truncate_message_history"
    NODE_CHATBOT = "chatbot"
    NODE_EXECUTE_PLAN = "execute_plan"
    NODE_TOOLS = "tools"

class ContextManager:
    """上下文管理器"""
    def __init__(self, db_module):
        self.db = db_module

    @staticmethod
    def load_user_context(state: PocketWiseState) -> Dict[str, Any]:
        """导入长期记忆"""
        user_id = state["user_id"]
        profile = db.get_user_profile(user_id)
        return {"user_profile": profile}

    @staticmethod
    def truncate_message_history(state: PocketWiseState, max_messages: int = GraphConstants.MAX_MESSAGES) -> Dict[str, Any]:
        """控制对话上下文"""
        messages: List[BaseMessage] = state["messages"]
        # 无需截断
        if len(messages) <= max_messages:
            return {"messages": messages}
        truncated = messages[-max_messages:]
        return {"messages": truncated}

class IntentRecognizer:
    """意图识别器"""

    def __init__(self, llm_model):
        self.llm = llm_model

    @staticmethod
    def _last_human_text(messages: List[BaseMessage]) -> str:
        """提取最后一条用户消息"""
        for m in reversed(messages):
            if isinstance(m, HumanMessage):
                return str(m.content or "").strip()
        return ""

    def _llm_recognize_intent(self, message: str) -> str:
        """使用LLM识别意图"""
        system_prompt = get_intent_prompt()
        try:
            resp = self.llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=message)
            ])
            return str(resp.content).strip()
        except Exception:
            return GraphConstants.DEFAULT_INTENT

    def recognize_intent(self, state: PocketWiseState) -> Dict[str, Any]:
        """意图识别主方法"""
        text = self._last_human_text(state["messages"])
        intent = self._llm_recognize_intent(text)

        if intent not in Intent.__args__:
            intent = GraphConstants.DEFAULT_INTENT

        return {"last_intent": intent}


class ChatbotService:
    """聊天机器人服务"""

    def __init__(self, llm_model, available_tools: List):
        self.llm = llm_model
        self.available_tools = available_tools

    def _get_extra_guidance(self, intent: str) -> str:
        """根据意图获取额外指导"""
        intent_guidance_map = get_guidance_map()
        return intent_guidance_map.get(intent, intent_guidance_map[GraphConstants.DEFAULT_INTENT])

    def _prepare_system_message(self, user_id: str, profile: Dict[str, Any], extra_guidance: str) -> str:
        """准备系统消息"""
        return get_chatbot_prompt(user_id, profile, extra_guidance)

    def _bind_tools(self):
        """绑定工具到LLM"""
        return self.llm.bind_tools(self.available_tools)

    def generate_response(self, state: PocketWiseState) -> Dict[str, Any]:
        """生成聊天响应"""
        user_id = state["user_id"]
        profile = state.get("user_profile", {})
        last_intent = state.get("last_intent", GraphConstants.DEFAULT_INTENT)

        extra_guidance = self._get_extra_guidance(last_intent)
        sys_msg = self._prepare_system_message(user_id, profile, extra_guidance)

        llm_with_tools = self._bind_tools()
        messages = [SystemMessage(content=sys_msg)] + state["messages"]

        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}
    

class FlowController:
    """流程控制器"""

    @staticmethod
    def should_continue(state: PocketWiseState) -> str:
        """判断是否继续处理"""
        last_message = state["messages"][-1]
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return GraphConstants.NODE_TOOLS
        return END


class PlanExecutor:
    """计划执行器"""

    def __init__(self, plan_agent):
        self.plan_agent = plan_agent


    def execute_plan(self, state: PocketWiseState) -> Dict[str, Any]:
        """执行计划生成"""
        config = {"configurable": {"thread_id": GraphConstants.PLAN_AGENT_THREAD_ID}}
        response = self.plan_agent.invoke({"messages": state["messages"]}, config=config)
        return {"messages": [response["messages"][-1].content]}


class ToolExecutor:
    """工具执行器"""

    def __init__(self, tool_registry: Dict[str, Any]):
        self.tool_registry = tool_registry

    def execute_tool(self, state: PocketWiseState) -> Dict[str, Any]:
        """执行工具调用"""
        user_id = state["user_id"]
        last_message = state["messages"][-1]

        if not (hasattr(last_message, 'tool_calls') and last_message.tool_calls):
            return {}

        tool_call = last_message.tool_calls[0]
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]

        full_args = {"user_id": user_id, **tool_args}

        if tool_name not in self.tool_registry:
            result = "未知工具"
        else:
            try:
                result = self.tool_registry[tool_name].invoke(full_args)
            except Exception as e:
                result = f"工具执行出错: {str(e)}"

        return {"messages": [ToolMessage(content=str(result), tool_call_id=tool_call["id"])]}


class Router:
    """路由器"""

    @staticmethod
    def route_by_intent(state: PocketWiseState) -> str:
        """根据意图路由"""
        if state["last_intent"] == "generate_plan" or state["last_intent"] == "update_plan" or state["last_intent"] == "delete_plan":
            return GraphConstants.NODE_EXECUTE_PLAN
        
        return GraphConstants.NODE_CHATBOT

def build_graph(checkpointer):
    """构建对话图"""

    # 创建服务实例（依赖注入）
    context_manager = ContextManager(db)
    intent_recognizer = IntentRecognizer(llm_chat)

    available_tools = [
        view_user_profile,
        edit_user_profile,
        log_notable_expense,
        view_recent_expenses,
        detect_impulse_buying,
        view_plan
    ]
    chatbot_service = ChatbotService(llm_chat, available_tools)

    # 创建计划生成agent
    plan_agent_prompt = get_plan_prompt()
    plan_agent = create_agent(llm_plan, system_prompt=plan_agent_prompt, tools=[view_user_profile, log_plan, view_plan, update_plan, delete_plan], checkpointer=checkpointer)
    plan_executor = PlanExecutor(plan_agent)

    # 工具注册表
    tool_registry = {
        "view_user_profile": view_user_profile,
        "edit_user_profile": edit_user_profile,
        "log_notable_expense": log_notable_expense,
        "view_recent_expenses": view_recent_expenses,
        "detect_impulse_buying": detect_impulse_buying,
        "view_plan": view_plan
    }
    tool_executor = ToolExecutor(tool_registry)

    graph_builder = StateGraph(PocketWiseState)

    graph_builder.add_node(GraphConstants.NODE_LOAD_CONTEXT, context_manager.load_user_context)
    graph_builder.add_node(GraphConstants.NODE_RECOGNIZE_INTENT, intent_recognizer.recognize_intent)
    graph_builder.add_node(GraphConstants.NODE_TRUNCATE_HISTORY,
                          lambda s: context_manager.truncate_message_history(s, GraphConstants.MAX_MESSAGES))

    graph_builder.add_node(GraphConstants.NODE_CHATBOT, chatbot_service.generate_response)
    graph_builder.add_node(GraphConstants.NODE_EXECUTE_PLAN, plan_executor.execute_plan)
    graph_builder.add_node(GraphConstants.NODE_TOOLS, tool_executor.execute_tool)

    # 编排
    graph_builder.add_edge(START, GraphConstants.NODE_LOAD_CONTEXT)
    graph_builder.add_edge(GraphConstants.NODE_LOAD_CONTEXT, GraphConstants.NODE_RECOGNIZE_INTENT)
    graph_builder.add_edge(GraphConstants.NODE_RECOGNIZE_INTENT, GraphConstants.NODE_TRUNCATE_HISTORY)

    graph_builder.add_conditional_edges(GraphConstants.NODE_TRUNCATE_HISTORY,
                                        Router.route_by_intent,
                                        {
                                            GraphConstants.NODE_EXECUTE_PLAN: GraphConstants.NODE_EXECUTE_PLAN,
                                            GraphConstants.NODE_CHATBOT: GraphConstants.NODE_CHATBOT
                                        }
                                        )
    graph_builder.add_edge(GraphConstants.NODE_EXECUTE_PLAN, END)
    graph_builder.add_conditional_edges(GraphConstants.NODE_CHATBOT, FlowController.should_continue, [GraphConstants.NODE_TOOLS, END])
    graph_builder.add_edge(GraphConstants.NODE_TOOLS, GraphConstants.NODE_CHATBOT)

    return graph_builder.compile(checkpointer=checkpointer)

