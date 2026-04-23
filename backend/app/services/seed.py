"""种子数据：首次启动时导入系统数据"""

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models import database as db_module
from app.models import (
    User, Keyword, Mentor, AIModel, UserKeywordPref,
)


async def seed_system_data():
    """导入系统种子数据（幂等，已存在则跳过）"""
    if db_module.async_session is None:
        return

    async with db_module.async_session() as db:
        # 1. 创建管理员
        await _seed_admin(db)
        # 2. 导入关键词
        await _seed_keywords(db)
        # 3. 导入导师
        await _seed_mentors(db)
        # 4. 导入预设 AI 模型
        await _seed_ai_models(db)

        await db.commit()


async def _seed_admin(db: AsyncSession):
    """创建管理员账号"""
    settings = get_settings()
    if not settings.ADMIN_EMAIL or not settings.ADMIN_PASSWORD:
        logger.info("未配置管理员账号，跳过")
        return

    result = await db.execute(select(User).where(User.is_admin == True))
    if result.scalar_one_or_none():
        return  # 已有管理员

    from app.utils.security import hash_password
    admin = User(
        email=settings.ADMIN_EMAIL,
        password_hash=hash_password(settings.ADMIN_PASSWORD),
        nickname="管理员",
        is_admin=True,
    )
    db.add(admin)
    logger.info(f"创建管理员账号: {settings.ADMIN_EMAIL}")


async def _seed_keywords(db: AsyncSession):
    """从 keywords.yaml 导入60个系统关键词"""
    result = await db.execute(select(Keyword).where(Keyword.is_system == True))
    if result.scalars().first():
        return  # 已导入

    settings = get_settings()
    keywords_file = settings.DATA_DIR / "keywords.yaml"
    if not keywords_file.exists():
        logger.warning(f"关键词文件不存在: {keywords_file}")
        return

    import yaml
    with open(keywords_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    quadrant_map = {
        "quadrant_1_foundation": 1,
        "quadrant_2_connection": 2,
        "quadrant_3_growth": 3,
        "quadrant_4_ultimate": 4,
    }

    count = 0
    for quadrant_key, quadrant_num in quadrant_map.items():
        kw_list = data.get("keywords", {}).get(quadrant_key, [])
        for kw in kw_list:
            keyword = Keyword(
                name=kw["name"],
                english=kw.get("english"),
                quadrant=quadrant_num,
                category=kw.get("category"),
                description=kw.get("description"),
                default_weight=kw.get("default_weight", 1.0),
                related_keywords=kw.get("related_keywords"),
                preferred_mentor_types=kw.get("mentors_preferred"),
                is_system=True,
            )
            db.add(keyword)
            count += 1

    logger.info(f"导入 {count} 个系统关键词")


async def _seed_mentors(db: AsyncSession):
    """从 mentors.yaml 导入系统导师"""
    result = await db.execute(select(Mentor).where(Mentor.is_system == True))
    if result.scalars().first():
        return  # 已导入

    settings = get_settings()
    mentors_file = settings.DATA_DIR / "mentors.yaml"
    if not mentors_file.exists():
        logger.warning(f"导师文件不存在: {mentors_file}")
        return

    import yaml
    with open(mentors_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    count = 0
    for category_name, mentor_list in data.get("mentors", {}).items():
        if not isinstance(mentor_list, list):
            continue
        for m in mentor_list:
            mentor = Mentor(
                external_id=m.get("id"),
                name=m["name"],
                category=category_name,
                age_range=m.get("age_range"),
                field=m.get("field"),
                perspective=m.get("perspective"),
                keywords=m.get("keywords"),
                personality=m.get("personality"),
                tone=m.get("tone"),
                background=m.get("background"),
                era=m.get("era"),
                achievements=m.get("achievements"),
                peak_age=m.get("peak_age"),
                peak_stage=m.get("peak_stage"),
                peak_description=m.get("peak_description"),
                years_ahead=m.get("years_ahead"),
                representative_quotes=m.get("representative_quotes"),
                is_system=True,
            )
            db.add(mentor)
            count += 1

    logger.info(f"导入 {count} 个系统导师")


async def _seed_ai_models(db: AsyncSession):
    """创建预设 AI 模型配置"""
    result = await db.execute(select(AIModel))
    if result.scalars().first():
        return  # 已有配置

    presets = [
        AIModel(
            name="DeepSeek",
            provider="deepseek",
            base_url="https://api.deepseek.com",
            api_key="",
            model_id="deepseek-chat",
            priority=1,
            is_active=False,
            max_tokens=300,
            temperature=0.7,
        ),
        AIModel(
            name="智谱GLM",
            provider="zhipu",
            base_url="https://open.bigmodel.cn/api/paas/v4",
            api_key="",
            model_id="glm-4-flash",
            priority=2,
            is_active=False,
            max_tokens=300,
            temperature=0.7,
        ),
    ]
    for preset in presets:
        db.add(preset)

    logger.info("创建预设 AI 模型配置（需在管理后台填写 API Key）")
