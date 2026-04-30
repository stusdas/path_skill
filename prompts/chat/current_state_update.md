# Current State Update

请根据最近几轮消息，更新当前状态快照。

## 可更新字段
- emotion_state：stable / anxious / low / overwhelmed / hopeful / conflicted
- decision_state：none / lightly_stuck / repeatedly_stuck / major_choice_period
- life_phase：stable_phase / exploration / turning_point / recovery
- confidence：0.0 - 1.0

## 规则
1. 只更新“最近阶段”状态，不把一次情绪写成永久属性。
2. 允许保守估计，不要夸大。
3. 如果信息不足，维持原状态。
