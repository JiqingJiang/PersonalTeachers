# PersonalTeachers 关键词系统设计

## 📖 文档概述

**为什么需要这个文档？**
- 明确60个关键词的分类逻辑和权重策略
- 为AI生成语录提供主题框架
- 确保人生智慧的全面覆盖

**适合谁阅读？**
- 自己（配置权重时参考）
- 未来扩展关键词时

---

## 🎯 设计哲学

### 核心理念

> **人生的智慧，可以从四个维度来审视：生存、关系、成长、终极**

### 为什么是这四个象限？

1. **第一象限：生存与根基**
   - 这是人生的**基础**
   - 没有1（健康），后面再多0也没有意义
   - 对应马斯洛需求层次的**生理和安全需求**

2. **第二象限：关系与情感**
   - 这是人生的**温度**
   - 人是社会性动物，关系决定幸福感
   - 对应马斯洛需求层次的**归属和爱的需求**

3. **第三象限：成长与认知**
   - 这是人生的**高度**
   - 认知升级是跨越阶层的唯一途径
   - 对应马斯洛需求层次的**尊重和自我实现**

4. **第四象限：终极与哲思**
   - 这是人生的**深度**
   - 思考死亡、自由、意义等终极问题
   - 对应马斯洛需求层次的**超越需求**

### 为什么是60个关键词？

- **15 × 4 = 60**：每个象限15个，结构对称
- **覆盖全面**：每个维度都有足够的细分主题
- **数量适中**：60个不至于太多导致重复，也不至于太少有遗漏
- **便于权重**：用户可以针对每个关键词设置权重

---

## 📊 四象限关键词体系

### 🟢 第一象限：生存与根基 (The Foundation)

**象限属性**：刚需、物理、客观、底层逻辑
**对应视角**：【底层】普通百姓、生物学视角
**核心问题**：我如何活下去？

#### 关键词列表（15个）

| 序号 | 关键词 | 英文 | 类别 | 默认权重 | 说明 |
|------|--------|------|------|----------|------|
| 1 | 健康 | Health | physical | 2.0 | 所有的0前面那个1 |
| 2 | 金钱 | Money | resource | 1.5 | 资源交换的媒介，生存的底气 |
| 3 | 时间 | Time | resource | 1.8 | 唯一不可再生的资源，最为公平 |
| 4 | 睡眠 | Sleep | physical | 1.5 | 系统的重启与修复机制 |
| 5 | 房子 | Housing | resource | 1.0 | 物理空间的庇护，中国社会的特殊图腾 |
| 6 | 欲望 | Desire | psychological | 1.2 | 驱动力的源头，也是痛苦的根源 |
| 7 | 性 | Sex | physical | 1.0 | 繁衍本能与亲密关系的物理连接 |
| 8 | 衰老 | Aging | biological | 1.3 | 熵增的必然过程 |
| 9 | 风险 | Risk | uncertainty | 1.4 | 不确定性的量化，跃迁的代价 |
| 10 | 安全感 | Security | psychological | 1.6 | 对确定性的渴望 |
| 11 | 债务 | Debt | financial | 1.0 | 透支未来以换取现在的杠杆 |
| 12 | 食物 | Food | physical | 1.0 | 能量输入 |
| 13 | 贫穷 | Poverty | economic | 1.5 | 稀缺心态的根源，限制带宽的枷锁 |
| 14 | 生存 | Survival | fundamental | 1.8 | 一切文明的前提 |
| 15 | 资产 | Assets | financial | 1.2 | 睡后能产生价值的东西（复利的基础） |

**优先级排序**（按重要性）：
1. 健康（2.0） - 最高权重
2. 时间（1.8）
3. 生存（1.8）
4. 安全感（1.6）
5. 金钱（1.5）
6. 贫穷（1.5）

---

### 🔵 第二象限：关系与情感 (The Connection)

**象限属性**：感性、连接、波动、社会属性
**对应视角**：【情感】重建期的你、社会学视角
**核心问题**：我与他人的关系如何？

#### 关键词列表（15个）

| 序号 | 关键词 | 英文 | 类别 | 默认权重 | 说明 |
|------|--------|------|------|----------|------|
| 16 | 爱 | Love | emotion | 1.8 | 最高的能量频率，也是最大的软肋 |
| 17 | 父母 | Parents | family | 1.5 | 生命的来处，需要和解的对象 |
| 18 | 伴侣 | Partner | intimate | 1.6 | 价值合伙人，人生最大的投资选择 |
| 19 | 孤独 | Loneliness | emotion | 1.4 | 强者的常态，内省的最佳时刻 |
| 20 | 信任 | Trust | social | 1.3 | 协作成本最低的契约 |
| 21 | 遗憾 | Regret | emotion | 1.2 | 决策偏差带来的后效情绪 |
| 22 | 嫉妒 | Jealousy | emotion | 1.0 | 意识到自己匮乏的信号 |
| 23 | 面子 | Face | social | 1.1 | 他人眼中的投影，往往束缚自我 |
| 24 | 归属感 | Belonging | psychological | 1.5 | 群体性动物的本能需求 |
| 25 | 告别 | Farewell | emotion | 1.3 | 断舍离，成长的必修课 |
| 26 | 尊重 | Respect | social | 1.2 | 心理地位的确认 |
| 27 | 情绪 | Emotion | psychological | 1.6 | 大脑对环境的生化反应，需被管理而非压抑 |
| 28 | 原谅 | Forgiveness | emotion | 1.4 | 放过自己，停止内耗的手段 |
| 29 | 朋友 | Friends | social | 1.3 | 阶段性的同行者 |
| 30 | 孩子 | Children | family | 1.5 | 基因的延续，责任的具象化 |

**优先级排序**（按重要性）：
1. 爱（1.8） - 最高权重
2. 伴侣（1.6）
3. 情绪（1.6）
4. 父母（1.5）
5. 归属感（1.5）
6. 孩子（1.5）

---

### 🟡 第三象限：成长与认知 (The Growth)

**象限属性**：进取、迭代、理性、工具属性
**对应视角**：【顶层】马斯克、第一性原理、INTJ视角
**核心问题**：我如何变得更好？

#### 关键词列表（15个）

| 序号 | 关键词 | 英文 | 类别 | 默认权重 | 说明 |
|------|--------|------|------|----------|------|
| 31 | 选择 | Choice | decision | 2.0 | 决定命运的关键节点，大于努力 |
| 32 | 认知 | Cognition | mental | 1.8 | 人与人之间唯一的本质壁垒 |
| 33 | 习惯 | Habit | behavioral | 1.6 | 自动化的行为模式，复利的载体 |
| 34 | 复利 | Compounding | mathematical | 1.7 | 世界第八大奇迹，长期主义的核心 |
| 35 | 专注 | Focus | attention | 1.8 | 注意力的聚焦，稀缺的生产力 |
| 36 | 学习 | Learning | growth | 1.6 | 系统升级的唯一途径 |
| 37 | 失败 | Failure | experience | 1.4 | 排除错误路径的数据反馈 |
| 38 | 逻辑 | Logic | thinking | 1.5 | 思考的骨架，祛除迷雾的工具 |
| 39 | 改变 | Change | transformation | 1.7 | 违背人性的舒适区，但却是进化的必须 |
| 40 | 耐心 | Patience | virtue | 1.6 | 等待临界点到来的能力 |
| 41 | 焦虑 | Anxiety | emotion | 1.5 | 能力与野心不匹配时的状态 |
| 42 | 竞争 | Competition | game | 1.3 | 资源有限环境下的必然博弈 |
| 43 | 天赋 | Talent | potential | 1.2 | 初始属性点，需被挖掘 |
| 44 | 执行 | Execution | action | 1.8 | 将想法变为现实的桥梁 |
| 45 | 阶层 | Class | social | 1.4 | 社会资源的分配层级 |

**优先级排序**（按重要性）：
1. 选择（2.0） - 最高权重
2. 认知（1.8）
3. 专注（1.8）
4. 执行（1.8）
5. 复利（1.7）
6. 改变（1.7）

---

### 🟣 第四象限：终极与哲思 (The Ultimate)

**象限属性**：抽象、宏大、精神、终局思维
**对应视角**：【顶层】老子、乔布斯、哲学视角
**核心问题**：这一切的意义是什么？

#### 关键词列表（15个）

| 序号 | 关键词 | 英文 | 类别 | 默认权重 | 说明 |
|------|--------|------|------|----------|------|
| 46 | 自由 | Freedom | ultimate | 2.0 | 选择权的极致，不仅仅是财富自由 |
| 47 | 意义 | Meaning | existential | 1.8 | 对抗虚无的武器，主观赋予的价值 |
| 48 | 死亡 | Death | ultimate | 1.7 | 终点，赋予生命以紧迫感 |
| 49 | 命运 | Destiny | metaphysical | 1.5 | 概率与因果的集合体 |
| 50 | 真理 | Truth | epistemological | 1.6 | 客观世界的底层代码 |
| 51 | 自我 | Self | identity | 1.8 | 剥离社会角色后剩下的那个核心 |
| 52 | 遗忘 | Forgetting | memory | 1.2 | 大脑的垃圾清理机制 |
| 53 | 权力 | Power | social | 1.3 | 支配资源的能量 |
| 54 | 公平 | Fairness | moral | 1.1 | 理想状态，现实中往往不存在 |
| 55 | 无常 | Impermanence | philosophical | 1.4 | 世界变化的唯一永恒 |
| 56 | 创造 | Creation | expression | 1.6 | 接近神性的行为 |
| 57 | 责任 | Responsibility | moral | 1.5 | 成年人的标志，权力的对等物 |
| 58 | 和解 | Reconciliation | emotional | 1.4 | 与过去、与不完美、与世界达成一致 |
| 59 | 信仰 | Belief | spiritual | 1.5 | 在看不见时依然选择相信 |
| 60 | 因果 | Causality | philosophical | 1.6 | 种瓜得瓜，所有行为的果 |

**优先级排序**（按重要性）：
1. 自由（2.0） - 最高权重
2. 自我（1.8）
3. 意义（1.8）
4. 死亡（1.7）
5. 真理（1.6）
6. 创造（1.6）
7. 因果（1.6）

---

## 🎲 关键词权重系统

### 权重的作用

**为什么需要权重？**
- ✅ **个性化**：不同人生阶段关注点不同
- ✅ **动态调整**：可以随时间变化调整权重
- ✅ **聚焦深度**：高频接触高权重关键词，深入思考

**权重如何工作？**
```python
# 权重影响关键词被选中的概率
P(keyword) = weight(keyword) / sum(all_weights)

# 示例：
# 如果"健康"权重=2.0，"金钱"权重=1.0
# 则"健康"被选中的概率是"金钱"的2倍
```

### 权重设置建议

#### 按人生阶段

**20-25岁（初入职场）**：
```yaml
优先提升：
  - 选择: 2.5      # 职业方向、人生道路
  - 学习: 2.0
  - 执行: 2.0
  - 焦虑: 2.0      # 这个年纪容易焦虑

保持关注：
  - 健康: 1.5      # 打基础的好时候
  - 习惯: 1.8
  - 认知: 1.8
```

**25-30岁（职业上升期）**：
```yaml
优先提升：
  - 选择: 2.5      # 换工作、结婚等关键选择
  - 伴侣: 2.0
  - 金钱: 1.8
  - 专注: 2.0

保持关注：
  - 健康: 1.5
  - 复利: 1.8
  - 执行: 1.8
```

**30-40岁（中年压力期）**：
```yaml
优先提升：
  - 健康: 2.5      # 身体开始报警
  - 情绪: 2.0      # 中年危机
  - 选择: 2.0
  - 伴侣: 2.0
  - 孩子: 1.8

保持关注：
  - 时间: 2.0      # 最稀缺的资源
  - 金钱: 1.8
  - 焦虑: 1.8
```

**40-50岁（人生下半场）**：
```yaml
优先提升：
  - 健康: 3.0      # 必须重视了
  - 自我: 2.0      # 寻找真正的自己
  - 意义: 2.0
  - 自由: 2.0

保持关注：
  - 时间: 2.0
  - 改变: 1.8
  - 和解: 1.8
```

#### 按当前困境

**财务紧张时**：
```yaml
  - 金钱: 3.0
  - 贫穷: 2.5
  - 资产: 2.0
  - 负债: 2.0
```

**感情困惑时**：
```yaml
  - 伴侣: 3.0
  - 爱: 2.5
  - 情绪: 2.0
  - 孤独: 2.0
```

**职业迷茫时**：
```yaml
  - 选择: 3.0
  - 认知: 2.0
  - 焦虑: 2.0
  - 竞争: 1.8
```

**健康问题时**：
```yaml
  - 健康: 3.0
  - 睡眠: 2.5
  - 食物: 2.0
  - 情绪: 2.0
```

---

## 🔗 关键词与导师的匹配

### 匹配原则

1. **领域相关性**：导师的领域与关键词相关
2. **经历相关性**：导师有该关键词相关的经历
3. **视角互补性**：不同象限的关键词配对不同的导师视角

### 匹配示例

```yaml
# 健康关键词 - 适合的导师
健康:
  - 心理医生      # 专业视角
  - 养生专家      # 传统视角
  - 运动员        # 实践视角
  - 普通老人      # 底层视角

# 金钱关键词 - 适合的导师
金钱:
  - 巴菲特        # 投资大师
  - 普通打工者    # 底层视角
  - 经济学家      # 理论视角
  - 房产中介      # 实践视角

# 自由关键词 - 适合的导师
自由:
  - 老子          # 哲学视角
  - 斯多葛哲学家  # 心理自由
  - 数字游民      # 现代自由
  - 未来自己      # 时间自由
```

---

## 📐 关键词的数据结构

### YAML定义格式

```yaml
keywords:
  # 第一象限：生存与根基
  quadrant_1_foundation:
    - name: "健康"
      english: "Health"
      category: "physical"
      default_weight: 2.0
      description: "所有的0前面那个1"
      mentors_preferred:
        - "心理医生"
        - "养生专家"
        - "生物学家"
      related_keywords:
        - "睡眠"
        - "食物"
        - "衰老"

    # ... 共15个

  # 第二象限：关系与情感
  quadrant_2_connection:
    - name: "爱"
      english: "Love"
      category: "emotion"
      default_weight: 1.8
      description: "最高的能量频率，也是最大的软肋"
      mentors_preferred:
        - "诗人"
        - "心理学家"
        - "智者"
      related_keywords:
        - "伴侣"
        - "父母"
        - "情绪"

    # ... 共15个

  # 第三象限：成长与认知
  quadrant_3_growth:
    - name: "选择"
      english: "Choice"
      category: "decision"
      default_weight: 2.0
      description: "决定命运的关键节点，大于努力"
      mentors_preferred:
        - "企业家"
        - "哲学家"
        - "决策专家"
      related_keywords:
        - "风险"
        - "改变"
        - "认知"

    # ... 共15个

  # 第四象限：终极与哲思
  quadrant_4_ultimate:
    - name: "自由"
      english: "Freedom"
      category: "ultimate"
      default_weight: 2.0
      description: "选择权的极致，不仅仅是财富自由"
      mentors_preferred:
        - "哲学家"
        - "斯多葛学者"
        - "隐士"
      related_keywords:
        - "自我"
        - "意义"
        - "权力"

    # ... 共15个
```

### Python数据类

```python
from dataclasses import dataclass
from enum import Enum

class KeywordCategory(Enum):
    PHYSICAL = "physical"          # 生理
    PSYCHOLOGICAL = "psychological"  # 心理
    EMOTION = "emotion"           # 情感
    SOCIAL = "social"             # 社会
    FINANCIAL = "financial"       # 财务
    ECONOMIC = "economic"         # 经济
    DECISION = "decision"         # 决策
    MENTAL = "mental"             # 精神
    BEHAVIORAL = "behavioral"     # 行为
    MATHEMATICAL = "mathematical" # 数学
    GROWTH = "growth"             # 成长
    THINKING = "thinking"         # 思考
    ATTENTION = "attention"       # 注意
    ACTION = "action"             # 行动
    EXPERIENCE = "experience"     # 经验
    TRANSFORMATION = "transformation"  # 转变
    VIRTUE = "virtue"             # 美德
    GAME = "game"                 # 博弈
    POTENTIAL = "potential"       # 潜力
    ULTIMATE = "ultimate"         # 终极
    EXISTENTIAL = "existential"   # 存在
    METAPHYSICAL = "metaphysical" # 形而上
    EPISTEMOLOGICAL = "epistemological"  # 认识
    IDENTITY = "identity"         # 身份
    MEMORY = "memory"             # 记忆
    MORAL = "moral"              # 道德
    PHILOSOPHICAL = "philosophical"  # 哲学
    EXPRESSION = "expression"     # 表达
    SPIRITUAL = "spiritual"       # 精神

@dataclass
class Keyword:
    name: str                    # 中文名称
    english: str                 # 英文名称
    category: KeywordCategory    # 类别
    default_weight: float        # 默认权重
    description: str             # 描述
    mentors_preferred: list[str] # 适合的导师类型
    related_keywords: list[str]  # 相关关键词
    quadrant: int                # 所属象限 (1-4)
```

---

## 🎲 关键词选择算法

### 轮盘赌算法

```python
import random

def select_keywords(
    count: int,
    weights: dict[str, float],
    ensure_diversity: bool = True
) -> list[str]:
    """
    根据权重选择关键词

    算法：
    1. 计算每个关键词的选中概率
    2. 使用轮盘赌算法选择
    3. 如果需要多样性，确保每个象限至少1个

    返回：选中的关键词列表
    """
    # 1. 计算总权重
    total_weight = sum(weights.values())

    # 2. 归一化权重
    normalized_weights = {
        kw: weight / total_weight
        for kw, weight in weights.items()
    }

    # 3. 轮盘赌选择
    selected = []
    for _ in range(count):
        rand = random.random()
        cumulative = 0.0
        for keyword, prob in normalized_weights.items():
            cumulative += prob
            if rand <= cumulative:
                selected.append(keyword)
                break

    # 4. 确保多样性（可选）
    if ensure_diversity:
        selected = ensure_quadrant_diversity(selected, weights)

    return selected

def ensure_quadrant_diversity(
    selected: list[str],
    weights: dict[str, float]
) -> list[str]:
    """
    确保每个象限至少有1个关键词
    """
    # 按象限分组
    by_quadrant = {1: [], 2: [], 3: [], 4: []}
    for kw in selected:
        quadrant = get_keyword_quadrant(kw)
        by_quadrant[quadrant].append(kw)

    # 补充缺失的象限
    for quadrant, keywords in by_quadrant.items():
        if not keywords:
            # 从该象限选择权重最高的
            candidates = get_keywords_by_quadrant(quadrant)
            best = max(candidates, key=lambda x: weights.get(x, 0))
            selected.append(best)

    return selected
```

---

## 📈 关键词的统计分析

### 覆盖度统计

```python
{
    "total_keywords": 60,
    "by_quadrant": {
        "quadrant_1_foundation": 15,
        "quadrant_2_connection": 15,
        "quadrant_3_growth": 15,
        "quadrant_4_ultimate": 15
    },
    "by_category": {
        "physical": 4,
        "emotion": 6,
        "decision": 3,
        # ...
    }
}
```

### 使用频率统计

```python
{
    "健康": {
        "total_generated": 45,
        "last_generated": "2026-01-17",
        "avg_quality_score": 4.2,
        "favorite_mentor": "mentor_030"  # 彭凯平
    },
    # ...
}
```

---

## 🔄 关键词的持续优化

### 定期评估（每月）

- [ ] 哪些关键词生成的语录质量高？
- [ ] 哪些关键词需要更多的导师支持？
- [ ] 是否有新的关键词需要添加？

### 动态调整权重

**根据人生阶段调整**：
```yaml
# 20多岁时
phase_20s:
  选择: 2.5
  学习: 2.0
  焦虑: 2.0

# 30多岁时
phase_30s:
  健康: 2.5
  情绪: 2.0
  伴侣: 2.0

# 40多岁时
phase_40s:
  健康: 3.0
  自我: 2.0
  意义: 2.0
```

**根据当前困境调整**：
```yaml
# 当前困境
current_challenge:
  type: "career"  # career/relationship/health/financial
  boosted_keywords:
    - 选择
    - 焦虑
    - 竞争
```

---

## 📚 关键词的参考资料

### 书籍推荐

**第一象限：生存与根基**
- 《睡眠革命》 - 关于睡眠
- 《贫穷的本质》 - 关于贫穷
- 《金钱心理学》 - 关于金钱

**第二象限：关系与情感**
- 《亲密关系》 - 关于爱
- 《非暴力沟通》 - 关于关系
- 《被讨厌的勇气》 - 关于自我

**第三象限：成长与认知**
- 《原则》 - 关于选择
- 《思考，快与慢》 - 关于认知
- 《习惯的力量》 - 关于习惯

**第四象限：终极与哲思**
- 《沉思录》 - 关于哲思
- 《活出意义来》 - 关于意义
- 《有限与无限的游戏》 - 关于终极

---

**文档版本**：v1.0
**最后更新**：2026-01-17
