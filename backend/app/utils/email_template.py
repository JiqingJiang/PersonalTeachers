"""邮件模板渲染"""

from datetime import datetime
from pathlib import Path

from app.config import get_settings


def render_daily_quote_email(quotes: list[dict], date_str: str | None = None) -> str:
    """将语录列表渲染为邮件 HTML"""
    if date_str is None:
        date_str = datetime.now().strftime("%Y年%m月%d日")

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

    return html


def _fallback_template() -> str:
    return """<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="utf-8"><title>今日人生导师智慧</title>
<style>
body{font-family:sans-serif;background:#f5f5f5;padding:20px;margin:0}
.container{max-width:600px;margin:0 auto;background:#fff;border-radius:10px;box-shadow:0 4px 15px rgba(0,0,0,0.1)}
.header{background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;padding:30px;text-align:center}
.header h1{margin:0;font-size:28px}
.header p{margin:10px 0 0;font-size:14px;opacity:0.9}
.content{padding:30px}
.quote-card{margin-bottom:20px;padding:20px;background:#f8f9fa;border-left:4px solid #667eea;border-radius:6px}
.quote-meta{font-size:12px;color:#6c757d;margin-bottom:10px}
.quote-content{font-size:15px;line-height:1.7;color:#212529}
.distribution{background:#f8f9fa;padding:20px;text-align:center;border-radius:6px;margin-top:30px}
.distribution p{margin:0;font-size:14px;color:#6c757d}
.footer{text-align:center;padding:20px;font-size:12px;color:#6c757d;background:#f8f9fa}
</style></head><body>
<div class="container">
<div class="header"><h1>📚 今日人生导师智慧</h1><p>{{date_str}}</p></div>
<div class="content">{{quotes_html}}
<div class="distribution"><p>🎯 本日主题分布</p><p style="margin-top:10px">{{distribution_html}}</p></div>
</div>
<div class="footer"><p>— Powered by PersonalTeachers —</p></div>
</div></body></html>"""
