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
    # 从 user_id 获取用户状态、阶段计划与历史支出
    user_state = db.get_user_profile(user_id)
    active_plans = db.get_active_plans(user_id) or []
    stage_plan = db.get_stage_plan(user_id) or {}
    recent_expenses = db.get_recent_expenses(user_id) or []

    budget = user_state.get("monthly_budget", 0)
    personality = user_state.get("personality_tags", [])

    reasons = []
    is_impulse = False

    # 1) 阶段性计划参考：若存在活跃计划且本次消费可能影响目标达成，则提醒
    plan_reasons = []
    for plan in active_plans:
        # 只对储蓄/消费节制类计划做简单判断
        plan_type = plan.get("plan_type", "").lower() if plan else ""
        stages_amount = plan.get("stages_amount")
        if plan_type in ("储蓄", "saving", "消费节制", "节省") and stages_amount:
            plan_reasons.append(f"存在阶段计划（每阶段目标 {stages_amount}），本次消费可能影响计划进度。")
    if plan_reasons:
        reasons.extend(plan_reasons)

    # 2) 简单判定算法（多条件打分）
    score = 0
    # a) 相对于月预算比例
    if budget > 0:
        ratio = amount / budget
        if ratio >= 0.1:
            score += 2
            reasons.append(f"金额占月预算的 {ratio:.1%}（阈值 10%）")
        elif ratio >= 0.05:
            score += 1
            reasons.append(f"金额占月预算的 {ratio:.1%}（较高）")

    # b) 相对于最近消费均值
    avg_recent = 0
    if recent_expenses:
        try:
            avg_recent = sum(e.get("amount", 0) for e in recent_expenses) / len(recent_expenses)
        except Exception:
            avg_recent = 0
    if avg_recent > 0:
        if amount > avg_recent * 3:
            score += 2
            reasons.append(f"消费远高于近期平均（{avg_recent:.2f}），超过 3 倍")
        elif amount > avg_recent * 1.5:
            score += 1
            reasons.append(f"消费高于近期平均（{avg_recent:.2f}）")

    # c) 描述关键词触发
    impulse_keywords = ["盲盒", "限时", "促销", "折扣", "不需要", "冲动", "买买买"]
    if any(k in (description or "").lower() for k in impulse_keywords):
        score += 2
        reasons.append("商品描述包含冲动消费触发词")

    # d) 用户自我标签
    if any("impuls" in t.lower() or "冲动" in t for t in personality):
        score += 1
        reasons.append("用户档案包含“容易冲动”相关标签")

    # e) 当月已花费与剩余额度（基于最近记录的近似当月支出）
    from datetime import datetime
    now = datetime.now()
    month = now.month
    year = now.year
    month_spent = 0
    for e in recent_expenses:
        t = e.get("timestamp", "")
        if t:
            time = t.split("T")[0]
            t_year = time.split("-")[0]
            t_month = time.split("-")[1]
        if t_year == year and t_month == month:
            month_spent += float(e.get("amount", 0))
    
    remaining = max(0, budget - month_spent) if budget else None
    if remaining is not None:
        if remaining <= 0:
            score += 2
            reasons.append("本月预算已接近或超支")
        elif amount > remaining:
            score += 2
            reasons.append(f"本次消费超过本月剩余额度（剩余 {remaining:.2f}）")
        elif amount > remaining * 0.5:
            score += 1
            reasons.append(f"本次消费占本月剩余额度较高（剩余 {remaining:.2f}）")

    # 判定阈值：score >=3 认定为冲动消费；2 为可疑；否则非冲动
    if score >= 3:
        is_impulse = True
    elif score == 2:
        # 可疑，需要用户确认
        is_impulse = False
        reasons.append("判定为可疑消费，建议二次确认")
    else:
        is_impulse = False

    # 找到与本次描述相似的历史消费例子（简单文本包含匹配）
    category = []
    for e in recent_expenses:
        if category and category.lower() in (e.get("category", "") or "").lower():
            category.append(e)

    # 组装提醒信息（包含阶段计划、活跃计划与历史记录摘要）
    remind = {
        "active_plans": active_plans,
        "stage_plan": stage_plan,
        "recent_expenses_sample": recent_expenses[:5],
        "similar_past_expenses": category[:5],
        "monthly_budget": budget,
        "month_spent_estimate": month_spent,
        "month_remaining_estimate": remaining,
    }

    recommendation = "无特别建议。"
    if is_impulse:
        recommendation = "该消费可能为冲动消费，建议考虑推迟购买、设置等待期或采用预算外决定流程。"
    elif score == 2:
        recommendation = "该消费可疑，建议二次确认或缩小购买金额。"
    else:
        recommendation = "看起来是理性消费，可记录入账以便后续分析。"

    return {
        "is_impulse": is_impulse,
        "score": score,
        "reason": "; ".join(reasons) if reasons else "看起来是一笔在合理范围内的理性消费。",
        "remind": remind,
        "recommendation": recommendation
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

