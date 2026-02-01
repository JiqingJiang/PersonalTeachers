"""
未来自己动态生成模块

根据用户当前状态，动态生成"未来的自己"的人设
"""
from typing import Dict, Optional
from datetime import datetime, timedelta
from pathlib import Path
import yaml

from app.models.database import Mentor, MentorCategory


class FutureSelfGenerator:
    """未来自己生成器"""

    def __init__(self):
        # 加载用户配置
        self._user_config = self._load_user_config()

    def _load_user_config(self) -> dict:
        """加载用户配置"""
        config_path = Path(__file__).parent.parent.parent / "data" / "config.yaml"

        import yaml
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def generate_future_self_mentor(
        self,
        years_ahead: int
    ) -> Mentor:
        """
        生成未来自己的导师人设

        Args:
            years_ahead: 未来年数（3/5/10/20/60）

        Returns:
            导师对象
        """
        user = self._user_config.get('user', {})
        current_state = self._user_config.get('user', {}).get('current_state', {})

        current_age = user.get('age', 26)
        future_age = current_age + years_ahead

        # 根据年数生成不同的人设
        if years_ahead <= 3:
            # 3年后的你 - 短期目标达成后的反思
            name = f"{years_ahead}年后的你"
            personality = "温暖理解，刚刚经历过，感同身受"
            background = self._generate_short_term_background(current_state)
            keywords = ["选择", "改变", "成长", "回顾", "建议"]

        elif years_ahead <= 5:
            # 5年后的你 - 中期规划的检验
            name = f"{years_ahead}年后的你"
            personality = "更加成熟，经历过更多，有更多智慧"
            background = self._generate_medium_term_background(current_state)
            keywords = ["成长", "选择", "后悔", "改变", "建议"]

        elif years_ahead <= 10:
            # 10年后的你 - 长期人生视角
            name = f"{years_ahead}年后的你"
            personality = "更加从容，看透很多事，与自己和解"
            background = self._generate_long_term_background(current_state)
            keywords = ["人生", "意义", "选择", "成长", "和解"]

        elif years_ahead <= 20:
            # 20年后的你 - 跨代际的智慧
            name = f"{years_ahead}年后的你"
            personality = "经历过人生大半，有深度的人生智慧"
            background = self._generate_cross_generational_background(current_state)
            keywords = ["人生", "意义", "时间", "珍惜", "智慧"]

        else:
            # 临终前的你 - 终局视角
            name = "临终前的你"
            personality = "从终点看起点，一切都是过程，唯有爱和真实重要"
            background = self._generate_end_of_life_background(current_state)
            keywords = ["人生", "意义", "后悔", "爱", "放下"]

        return Mentor(
            id=f"future_self_{years_ahead}",
            name=name,
            category=MentorCategory.FUTURE_SELF,
            age_range=(future_age, future_age),
            field="人生智慧",
            perspective="emotional",
            keywords=keywords,
            personality=personality,
            tone="温暖、亲切、充满人生智慧",
            background=background,
            template_type="future_self",
            years_ahead=years_ahead
        )

    def _generate_short_term_background(self, current_state: dict) -> str:
        """生成短期未来背景"""
        status = current_state.get('status', '探索中')
        confusion = current_state.get('confusion', '')

        return f"""3年后的你，刚刚经历过你现在正在经历的困惑。

那时候的你回头看，会发现现在的{status}其实是一个必经阶段。关于{confusion}的困惑，你已经有了一些答案，但也有了新的问题。

你变得更加从容，对自己有了更深的理解。"""

    def _generate_medium_term_background(self, current_state: dict) -> str:
        """生成中期未来背景"""
        return """5年后的你，已经跨过了你现在认为的大坎。

那些让你焦虑的，在5年的时间尺度下都变得渺小了。你经历了工作、生活的各种变化，学会了在不确定性中寻找确定。

你开始明白，人生不是一场短跑，而是一场马拉松。"""

    def _generate_long_term_background(self, current_state: dict) -> str:
        """生成长期未来背景"""
        return """10年后的你，已经经历了人生的很多阶段。

你可能换了几次工作，甚至换了跑道。你经历了得失，经历了聚散。那些你现在认为的大事，在10年的维度下都变得可以理解。

你与自己达成了某种和解，不再强求完美，而是接受真实的自己。"""

    def _generate_cross_generational_background(self, current_state: dict) -> str:
        """生成跨代际未来背景"""
        return """20年后的你，已经经历了人生的大半。

你可能已经送走了父母，孩子已经长大。你开始理解生命的轮回和传承。那些你年轻时执着的东西，现在看来都变得淡然。

你从终点看起点，能给现在的自己最真诚的建议。"""

    def _generate_end_of_life_background(self, current_state: dict) -> str:
        """生成终局未来背景"""
        return """临终前的你，回顾整个人生。

在死亡面前，所有的名利、地位、成就都变得无足轻重。你真正在乎的是什么？你最后悔的是什么？你最感恩的是什么？

从终极视角看，你现在认为重要的事情，真的是最重要的吗？"""

    def update_future_self_by_current_state(
        self,
        current_status: str,
        current_confusion: str,
        current_expectation: str
    ) -> Dict[str, str]:
        """
        根据当前状态更新未来自己的人设

        Args:
            current_status: 当前状态
            current_confusion: 当前困惑
            current_expectation: 期望方向

        Returns:
            更新后的状态描述
        """
        # 更新配置文件
        config_path = Path(__file__).parent.parent.parent / "data" / "config.yaml"

        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        config['user']['current_state'] = {
            'status': current_status,
            'confusion': current_confusion,
            'expectation': current_expectation
        }

        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, allow_unicode=True)

        # 重新加载配置
        self._user_config = config

        return config['user']['current_state']


# 全局单例
_generator: Optional[FutureSelfGenerator] = None


def get_future_self_generator() -> FutureSelfGenerator:
    """获取未来自己生成器单例"""
    global _generator
    if _generator is None:
        _generator = FutureSelfGenerator()
    return _generator
