from typing import Dict
from langchain_core.tools import tool
import database as db

# 初始化数据库
db.init_db()

@tool
def view_user_profile(user_id: str) -> Dict:
    """
    获取当前用户的档案，包括收入、预算、现有存款和性格标签。
    用于了解用户的财务基准情况。
    :param user_id: 用户 ID。
    """
    return db.get_user_profile(user_id)


@tool
def edit_user_profile(user_id: str, updates: Dict):
    """
    更新用户档案中的特定字段。
    :param user_id: 用户 ID。
    :param updates: 要更新的字段字典（例如：{"monthly_budget": 5000}）。
    """
    new_profile = db.update_user_profile(user_id, updates)
    return f"档案已成功更新。当前状态：{new_profile}"


@tool
def log_notable_expense(user_id: str, description: str, amount: float, category: str,
                        context: str):
    """
    记录一笔值得追踪或分析的支出。
    :param user_id: 用户 ID。
    :param description: 购买了什么。
    :param amount: 花费金额。
    :param category: 支出类别（例如：'餐饮'、'娱乐'）。
    :param context: 购买原因或当时的情境（例如：'心情不好'、'打折促销'）。
    """
    db.add_expense(user_id, description, amount, category, context)
    return f"已记录支出：{description}，花费 ${amount}。"


@tool
def view_recent_expenses(user_id: str):
    """
    查看用户最近5笔支出。
    :param user_id: 用户 ID。
    :return: 最近5笔支出列表。
    """
    return db.get_recent_expenses(user_id)


@tool
def detect_impulse_buying(user_id: str, description: str, amount: float):
    """
    基于用户当前状态，分析某笔消费是否可能属于冲动消费。
    :param user_id: 用户 ID。
    :param description: 商品描述。
    :param amount: 消费金额。
    :return: dict:{'is_impulse': bool, 'reason': str}
    """
    # 从 user_id 获取用户状态和阶段计划
    user_state = db.get_user_profile(user_id)
    remind = db.get_stage_plan(user_id)

    budget = user_state.get("monthly_budget", 0)
    personality = user_state.get("personality_tags", [])
    reasons = []
    is_impulse = False

    if budget > 0 and amount > (budget * 0.1):
        reasons.append(f"金额 (${amount}) 超过月预算 (${budget}) 的 10%。")
        is_impulse = True

    impulse_keywords = ["盲盒", "限时", "促销", "折扣", "不需要"]
    if any(k in description.lower() for k in impulse_keywords):
        reasons.append("商品描述包含冲动消费触发词。")
        is_impulse = True

    if "impulsive" in [t.lower() for t in personality]:
        reasons.append("用户自我标识为容易冲动。")

    return {
        "is_impulse": is_impulse,
        "reason": "; ".join(reasons) if reasons else "看起来是一笔在合理范围内的理性消费。",
        "remind": remind if remind else None
    }


@tool
def log_plan(user_id: str, plan_type: str, content: str, start_date: str,
             goal_amount: float = None, stages_amount: float = None):
    """
    记录用户的财务计划或目标。
    :param user_id: 用户ID。
    :param plan_type: 计划类型（例如：'储蓄'、'消费节制'）。
    :param content: 计划具体内容。
    :param start_date: 开始日期（ISO 格式字符串）。
    :param goal_amount: 目标金额（如适用）。
    :param stages_amount: 阶段划分金额。
    """
    db.add_plan(user_id, plan_type, content, start_date, goal_amount, stages_amount)
    return f"计划已保存：{content}"


@tool
def view_plan(user_id: str):
    """
    查看用户计划
    :param user_id: 用户ID。
    :return:
    """
    return db.get_active_plans(user_id)


@tool
def update_plan(plan_id: int, user_id: str, plan_type: str = None, content: str = None,
                start_date: str = None, goal_amount: float = None, stages_amount: float = None, status: str = None):
    """
    更新用户计划
    :param plan_id: 计划ID。
    :param user_id: 用户ID。
    :param plan_type: 计划类型。
    :param content: 计划内容。
    :param start_date: 开始日期。
    :param goal_amount: 目标金额。
    :param stages_amount: 阶段划分金额。
    :param status: 计划状态。
    """
    return db.update_plan(plan_id, user_id, plan_type, content, start_date, goal_amount, stages_amount, status)

@tool
def delete_plan(plan_id: int, user_id: str):
    """
    删除用户计划
    :param plan_id: 计划ID。
    :param user_id: 用户ID。
    """
    return db.delete_plan(plan_id, user_id)

