"""邮件模板渲染"""

from datetime import datetime
from pathlib import Path

from app.config import get_settings


def render_daily_quote_email(
    quotes: list[dict],
    date_str: str | None = None,
    user_nickname: str | None = None,
) -> str:
    """将语录列表渲染为邮件 HTML"""
    if date_str is None:
        date_str = datetime.now().strftime("%Y年%m月%d日")

    # 个性化问候语
    greeting = f"你好，{user_nickname}" if user_nickname else "你好"

    # 构建每条语录的 HTML
    quotes_html_parts = []
    for i, q in enumerate(quotes, 1):
        quotes_html_parts.append(f"""
            <div class="quote-card">
                <div class="quote-meta">
                    #{i} · {q.get('keyword', '')} — {q.get('mentor_name', '')}
                </div>
                <div class="quote-content">{q.get('content', '')}</div>
            </div>
        """)

    quotes_html = "\n".join(quotes_html_parts)

    # 构建主题分布
    quadrant_names = {1: "🏠生存", 2: "❤️情感", 3: "🌱成长", 4: "🌌哲思"}
    quadrant_counts: dict[int, int] = {1: 0, 2: 0, 3: 0, 4: 0}
    # 简单统计：用关键词的第一个字符判断象限（实际应从数据库查询）
    for q in quotes:
        cat = q.get("mentor_category", "")
        # 简单分配
        quadrant_counts[3] += 1  # 默认归为成长

    distribution_html = " · ".join(
        f"{name} {count}条"
        for qid, name in quadrant_names.items()
        if (count := quadrant_counts[qid]) > 0
    )

    # 读取模板
    settings = get_settings()
    template_path = settings.TEMPLATE_DIR / "daily_quote.html"

    if template_path.exists():
        template = template_path.read_text(encoding="utf-8")
    else:
        # 内联备用模板
        template = _fallback_template()

    # 简单字符串替换
    html = template.replace("{{date_str}}", date_str)
    html = html.replace("{{quotes_html}}", quotes_html)
    html = html.replace("{{distribution_html}}", distribution_html)
    html = html.replace("{{greeting}}", greeting)

    return html


def _fallback_template() -> str:
    return """<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="utf-8"><title>今日人生导师智慧</title>
<style>
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#F8F4EE;padding:20px;margin:0}
.container{max-width:580px;margin:0 auto;background:#fff;border-radius:12px;box-shadow:0 2px 20px rgba(45,43,38,0.06);overflow:hidden}
.header{background:linear-gradient(135deg,#E8A838,#D4763C,#B8533A);padding:36px 32px;text-align:center}
.header h1{margin:0;font-family:Georgia,serif;font-size:24px;color:#fff;letter-spacing:2px}
.header p{margin:10px 0 0;font-size:12px;color:rgba(255,255,255,0.85)}
.content{padding:32px}
.quote-card{margin-bottom:18px;padding:22px 22px 22px 26px;background:#FFFDF8;border-left:4px solid #E8A838;border-radius:0 8px 8px 0}
.quote-meta{font-size:12px;color:#A08860;margin-bottom:10px;font-weight:600}
.quote-content{font-size:15px;line-height:1.9;color:#2D2B26}
.distribution{padding:18px 0;border-top:1px solid #EDE8DF;text-align:center;margin-top:28px}
.distribution p{margin:0;font-size:13px;color:#7A756A}
.footer{text-align:center;padding:20px 32px;font-size:12px;color:#B5AFA3;background:#FAF7F2}
</style></head><body>
<div class="container">
<div class="header"><h1>今日人生导师智慧</h1><p>{{date_str}}</p></div>
<div class="content">
<p style="font-size:17px;color:#2D2B26;font-weight:500;">{{greeting}}</p>
{{quotes_html}}
<div class="distribution"><p style="font-size:11px;color:#B5AFA3;letter-spacing:2px;margin-bottom:6px;">本日主题分布</p><p>{{distribution_html}}</p></div>
</div>
<div class="footer"><p>PersonalTeachers — 每日人生智慧推送</p></div>
</div></body></html>"""
