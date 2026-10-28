---
layout: docs
title: "10.3 오프-정책 SARSA: 중요도 샘플링 기반 제어"
---

# 10.3 오프-정책 SARSA: 중요도 샘플링 기반 제어

![10.3 오프-정책 SARSA](./10_3_오프-정책_SARSA.png)

![오프-정책 SARSA 인트로](./img/jiny_ch10_3_off_policy_sarsa.png)
**그림 10-3-1** 탐험 지도(Behavior Policy)와 학습 목표 책(Target Policy)의 확률 변동 비를 대수적으로 유도해 칠판에 필기해주는 지니와 도로시

![오프-정책 SARSA 개념도](./img/02_off_policy_sarsa_concept.jpg)
**그림 10-3-2** 도로시가 행동 정책 *b*(*a*|*s*)의 나침반을 들고 모험을 떠나는 동안, 지니가 1-스텝 중요도 가중치 *ρ*를 계산하여 이호진 교수님의 목표 정책 *π* 갱신식에 보정해 주는 오프-정책 SARSA 협업 메커니즘

탐험 전용 정책(행동 정책)과 최적화 대상 정책(대상 정책)을 분리하여 학습하는 **오프-정책(Off-policy) SARSA** 알고리즘을 공부합니다. 9장에서 배운 중요도 샘플링(Importance Sampling)을 시간차(TD) 학습에 결합할 때, 왜 몬테카를로법에 비해 분산 폭발이 극적으로 줄어드는지, 그리고 여전히 남는 한계는 무엇인지 명쾌하게 파헤쳐 봅시다!

---

## 10.3.1 오프-정책 시간차 제어의 수학적 원리

10.2절의 온-정책(On-policy) SARSA에서는 하나의 정책으로 행동 선택과 가치 학습을 동시에 처리했습니다. 이로 인해 최적의 길을 찾아가는 과정에서도 강제로 *ε*(10%)의 무작위 탐험을 감수해야 했고, 그 결과 에이전트는 폭탄을 지나치게 두려워하며 멀리 돌아가는 보수적인 정책을 학습했습니다.

이 타협을 깨고 **"충분히 대담하게 탐험하면서도, 궁극적으로 도달할 대상 정책은 완벽한 100% 최적 탐욕 정책으로 학습할 수 없을까?"**라는 질문에서 출발하는 것이 바로 **오프-정책(Off-policy)**입니다.

오프-정책에서는 두 개의 분리된 정책을 운용합니다:
1. **행동 정책(Behavior Policy, *b*)**: 실제로 환경과 몸으로 부딪치며 데이터를 수집하는 정책입니다. 다양한 경로를 개척하기 위해 *ε*-탐욕 정책을 사용합니다.
2. **대상 정책(Target Policy, *π*)**: 우리가 궁극적으로 완성하고자 하는 이상적인 정책입니다. 100% 탐욕적(Greedy)으로 최적 가치만을 추구합니다.

---

### 1) 백업 다이어그램과 샘플링 정책의 차이

기존 온-정책 SARSA의 갱신식을 다시 상기해 봅시다:

> ### ***Q*<sub>*π*</sub>(*S*<sub>*t*</sub>, *A*<sub>*t*</sub>) ← *Q*<sub>*π*</sub>(*S*<sub>*t*</sub>, *A*<sub>*t*</sub>) + *α* · [*R*<sub>*t*</sub> + *γQ*<sub>*π*</sub>(*S*<sub>*t*+1</sub>, *A*<sub>*t*+1</sub>) - *Q*<sub>*π*</sub>(*S*<sub>*t*</sub>, *A*<sub>*t*</sub>)]** &nbsp;&nbsp;&nbsp;&nbsp; *(식 10.13)*

![SARSA 백업 다이어그램](./img/fig_7_8.jpg)
**그림 10-3-3** SARSA의 백업 다이어그램. 현재 상태-행동 쌍 (S<sub>t</sub>, A<sub>t</sub>)에서 보상 R<sub>t</sub>와 다음 상태 S<sub>t+1</sub>을 환경 전이 확률 p(s'|s, a)로 얻은 뒤, 다음 행동 A<sub>t+1</sub>을 특정 정책으로부터 샘플링합니다.

[그림 10-3-3]에서 주목할 지점은 다음 상태 *S*<sub>*t*+1</sub>에서 선택되는 다음 행동 ***A*<sub>*t*+1</sub>**입니다:
- 만약 *A*<sub>*t*+1</sub>이 대상 정책 *π*로부터 선택된다면 (*A*<sub>*t*+1</sub> ~ *π*), TD 타깃 [*R*<sub>*t*</sub> + *γQ*<sub>*π*</sub>(*S*<sub>*t*+1</sub>, *A*<sub>*t*+1</sub>)]은 정책 *π*를 따를 때의 참된 기댓값을 편향 없이 나타냅니다.
- 하지만 오프-정책에서는 에이전트가 현실에서 움직이는 정책이 **행동 정책 *b***이므로, 실제로 관측되는 다음 행동은 ***A*<sub>*t*+1</sub> ~ *b***로부터 샘플링됩니다!

서로 다른 확률 분포(*b*)에서 뽑아낸 행동을 가지고 우리가 원하는 목표 분포(*π*)의 가치를 그대로 갱신해 버리면 심각한 수학적 왜곡(편향)이 발생합니다. 이 분포의 차이를 보정해 주는 마법의 도구가 바로 **중요도 샘플링(Importance Sampling)**입니다.

---

### 2) 1-스텝 중요도 샘플링 가중치 *ρ*

9.5절에서 배운 중요도 샘플링의 원리를 적용하여 가중치 *ρ*(로)를 정의합니다:

> ### ***ρ* = *π*(*A*<sub>*t*+1</sub> | *S*<sub>*t*+1</sub>) / *b*(*A*<sub>*t*+1</sub> | *S*<sub>*t*+1</sub>)** &nbsp;&nbsp;&nbsp;&nbsp; *(식 10.14: 1-스텝 중요도 가중치)*

이 가중치 *ρ*는 **"행동 정책 *b*가 다음 행동 *A*<sub>*t*+1</sub>을 선택할 확률 대비, 우리가 목표로 하는 정책 *π*가 그 행동을 선택했을 확률의 비율"**을 의미합니다.

이 가중치 *ρ*를 TD 목표에 곱해주면 다음과 같은 **오프-정책 SARSA 갱신식**이 도출됩니다:

> ### ***Q*<sub>*π*</sub>(*S*<sub>*t*</sub>, *A*<sub>*t*</sub>) ← *Q*<sub>*π*</sub>(*S*<sub>*t*</sub>, *A*<sub>*t*</sub>) + *α* · [*ρ* · (*R*<sub>*t*</sub> + *γQ*<sub>*π*</sub>(*S*<sub>*t*+1</sub>, *A*<sub>*t*+1</sub>)) - *Q*<sub>*π*</sub>(*S*<sub>*t*</sub>, *A*<sub>*t*</sub>)]** &nbsp;&nbsp;&nbsp;&nbsp; *(식 10.15: 오프-정책 SARSA)*

---

### 3) MC 중요도 샘플링 vs TD 중요도 샘플링의 결정적 차이

여기서 시간차(TD) 학습의 위대한 장점이 다시 한번 드러납니다:
- **몬테카를로(MC)법의 중요도 가중치**:
  에피소드가 끝날 때까지 발생한 수십~수백 번의 모든 행동에 대한 비율을 **모조리 곱한 누적 곱**이었습니다:
  > *ρ*<sub>*t*:*T*</sub> = *ρ*<sub>*t*</sub> · *ρ*<sub>*t*+1</sub> · *ρ*<sub>*t*+2</sub> &hellip; *ρ*<sub>*T*-1</sub>
  
  작은 오차들이 수백 번 곱해지면서 가중치가 0으로 소멸하거나 수천만으로 폭발하는 **극심한 분산 폭발(Variance Explosion)**이 발생했습니다.
- **시간차(TD)법의 중요도 가중치**:
  단 1걸음 이동한 뒤 곧바로 다음 가치를 빌려와 부트스트랩하므로, **오직 1단계의 확률 비율 *ρ* = *π*(*A*<sub>*t*+1</sub> | *S*<sub>*t*+1</sub>) / *b*(*A*<sub>*t*+1</sub> | *S*<sub>*t*+1</sub>) 단 하나만 곱해집니다!**
  따라서 MC법에 비해 분산이 상상할 수 없을 만큼 극적으로 안정화됩니다.

---

## 10.3.2 오프-정책 SARSA 에이전트 구현

이제 오프-정책 SARSA를 코드로 구현해 봅시다.

<div align="right"><b>ch06/sarsa_off_policy.py</b></div>

```python
from collections import defaultdict, deque
import numpy as np
from common.utils import greedy_probs

class SarsaOffPolicyAgent:
    def __init__(self):
        self.gamma = 0.9
        self.alpha = 0.8
        self.epsilon = 0.1
        self.action_size = 4

        random_actions = {0: 0.25, 1: 0.25, 2: 0.25, 3: 0.25}
        self.pi = defaultdict(lambda: random_actions) # ❶ 목표 정책 π: 최적 탐욕 정책 (epsilon=0)
        self.b = defaultdict(lambda: random_actions)  # ❷ 행동 정책 b: 활발한 탐험 정책 (epsilon=0.1)
        self.Q = defaultdict(lambda: 0)
        self.memory = deque(maxlen=2)

    def get_action(self, state):
        # ❸ 실제 필드에서의 행동은 반드시 행동 정책 b로부터 샘플링!
        action_probs = self.b[state]
        actions = list(action_probs.keys())
        probs = list(action_probs.values())
        return np.random.choice(actions, p=probs)

    def reset(self):
        self.memory.clear()

    def update(self, state, action, reward, done):
        self.memory.append((state, action, reward, done))
        if len(self.memory) < 2:
            return

        state, action, reward, done = self.memory[0]
        next_state, next_action, _, _ = self.memory[1]

        if done:
            next_q = 0
            rho = 1.0 # 종단 상태에서는 추가 행동이 없으므로 보정 불필요
        else:
            next_q = self.Q[next_state, next_action]
            # ❹ 1-스텝 중요도 가중치 rho 계산: pi(A_{t+1}|S_{t+1}) / b(A_{t+1}|S_{t+1})
            rho = self.pi[next_state][next_action] / self.b[next_state][next_action]

        # ❺ 식 (10.15)에 따라 rho를 가중한 TD 목표로 Q 갱신
        target = rho * (reward + self.gamma * next_q)
        self.Q[state, action] += (target - self.Q[state, action]) * self.alpha

        # ❻ 두 정책을 각각 서로 다른 기준으로 개선!
        self.pi[state] = greedy_probs(self.Q, state, epsilon=0)      # π는 100% 완전 탐욕 정책
        self.b[state] = greedy_probs(self.Q, state, self.epsilon)   # b는 ε-탐욕 탐험 정책
```

#### 코드 핵심 분석:
- **❶, ❷ `self.pi`와 `self.b` 분리**:
  `self.pi`는 100% 탐욕적(`epsilon=0`)으로 개선되어 최적의 길을 추구하고, `self.b`는 `self.epsilon=0.1`의 무작위 탐색을 유지하여 미지의 영역을 정찰합니다.
- **❸ `get_action`**:
  에이전트가 현실 그리드 월드에서 움직일 때는 오직 탐색 정책인 `self.b`에 따라 행동합니다.
- **❹ `rho = self.pi[next_state][next_action] / self.b[next_state][next_action]`**:
  다음 상태에서 에이전트가 우연히 탐색 행동을 골랐을 때와 탐욕 행동을 골랐을 때의 확률 차이를 정확히 계산합니다.
- **❺ `target = rho * (reward + self.gamma * next_q)`**:
  중요도 비율 *ρ*를 TD 목표에 곱하여 대상 정책 *π* 관점에서의 올바른 기댓값으로 환산합니다.

---

## 10.3.3 오프-정책 SARSA의 치명적 약점과 Q-러닝으로의 도약

오프-정책 SARSA 에이전트를 훈련시킨 후 얻은 결과를 살펴봅시다.

![그림 10-9](./img/fig_7_9.jpg)
**그림 10-3-4** 오프-정책 SARSA로 얻은 그리드 월드 제어 결과. 온-정책 SARSA에 비해 다소 불안정하고 수렴 속도가 느린 양상을 보입니다.

### 왜 오프-정책 SARSA는 불안정할까?

[그림 10-3-4]를 보면 온-정책 SARSA에 비해 화살표 방향이 흔들리고 완벽한 최적 정책에 깔끔하게 도달하지 못하는 현상을 볼 수 있습니다. 그 이유는 바로 **식 (10.15)의 중요도 가중치 *ρ*** 때문입니다:

1. ***ρ* = 0 이 되는 치명적인 낭비**:
   - 대상 정책 *π*는 100% 탐욕 정책(`epsilon=0`)이므로, 최선의 행동 하나에만 확률 1.0을 주고 나머지 행동에는 확률 **0.0**을 줍니다.
   - 반면 행동 정책 *b*는 탐색을 위해 가끔 비탐욕적인 엉뚱한 행동을 선택합니다.
   - 이때 *b*가 탐색 행동을 선택하면, *π*(*A*<sub>*t*+1</sub> | *S*<sub>*t*+1</sub>)은 **0**이 되어버립니다!
   - 그 결과 ***ρ* = 0**이 되고, TD 목표는 0이 되어 **에이전트가 방금 얻은 즉각 보상 *R*<sub>*t*</sub>마저 0으로 지워진 채 *Q* 값이 0을 향해 곤두박질치는 심각한 왜곡**이 발생합니다!
2. **높은 가중치 변동성**:
   - 탐욕 행동을 선택했을 때는 *ρ*가 1보다 훨씬 커지고, 비탐욕 행동을 선택하면 0으로 뚝 떨어져서 TD 타깃의 진폭이 너무 큽니다.

> [!IMPORTANT]
> **질문: "그렇다면 중요도 샘플링 비 *ρ*를 곱하지 않고도, 행동 정책 *b*가 수집한 데이터로부터 대상 정책 *π*의 최적 가치를 깔끔하게 뽑아낼 수 있는 방법은 없을까요?"**
> 
> 정답은 **"있습니다!"** 바로 다음 절(10.4절)에서 다룰 강화학습 역사상 가장 위대한 알고리즘, **Q-러닝(Q-Learning)**이 그 해답을 제공합니다!
