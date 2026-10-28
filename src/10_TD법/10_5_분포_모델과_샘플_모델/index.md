---
layout: docs
title: "10.5 분포 모델과 샘플 모델: 에이전트의 초경량화"
---

# 10.5 분포 모델과 샘플 모델: 에이전트의 초경량화

![10.5 분포 모델과 샘플 모델](./10_5_분포_모델과_샘플_모델.png)

![모델 비교 인트로](./img/jiny_ch10_5_models.png)
**그림 10-5-1** 칠판에 그려진 이론적 확률 분포(분포 모델)와 토토가 통에 넣고 굴린 주사위 실증 표본들(샘플 모델)의 관계를 분석해 주는 지니와 도로시

![분포 모델 vs 샘플 모델 비교도](./img/02_dist_vs_sample_model_concept.jpg)
**그림 10-5-2** 모든 상태마다 거대한 행동 확률 원판 *π*(*a*|*s*)을 유지해야 하는 분포 모델(왼쪽)과, 동전 튕기기(*ε*)와 최고 점수 블록 직접 선택(*argmax*)만으로 초경량 실행과 메모리 절약을 달성하는 샘플 모델(오른쪽)의 차이를 설명하는 이호진 교수님과 도로시

강화학습에서 '모델'이라는 단어는 환경뿐만 아니라 에이전트의 내부 구조를 설명할 때도 매우 중요하게 쓰입니다. 에이전트가 상태별 확률 분포를 일일이 기억하고 관리하는 **분포 모델(Distribution Model)**에서 벗어나, 행동을 직접 즉석에서 추출하는 **샘플 모델(Sample Model)**로 전환함으로써 코드를 극적으로 단순화하고 딥러닝(DQN)으로 나아가는 징검다리를 놓아봅시다!

---

## 10.5.1 강화학습에서의 두 가지 '모델' 개념

'모델(Model)'이라는 용어는 문맥에 따라 두 가지 층위에서 사용됩니다:

### 1) 환경(Environment)의 관점
- **환경의 분포 모델**:
  동적 계획법(DP)처럼 상태 전이 확률 행렬 *p*(*s*&#39; | *s*, *a*)과 보상 함수 *r*(*s*, *a*, *s*&#39;)의 **완전한 확률 분포 표**를 에이전트가 손에 쥐고 있는 경우입니다.
- **환경의 샘플 모델**:
  몬테카를로법(MC)이나 시간차 학습(TD)처럼 내부 확률은 전혀 모르지만, 행동을 집어넣으면 다음 상태와 보상을 툭 뱉어내는 **시뮬레이터(`env.step(action)`)**를 가진 경우입니다.

---

### 2) 에이전트(Agent)의 관점
에이전트가 자신의 정책(행동을 선택하는 규칙)을 컴퓨터 메모리에 표현하는 방식에도 똑같이 두 가지가 존재합니다:
- **에이전트의 분포 모델**:
  모든 상태 *s*마다 "위로 갈 확률 70%, 아래로 갈 확률 10%, 좌 10%, 우 10%"와 같은 **명시적인 확률 분포 딕셔너리(`self.pi[state]`, `self.b[state]`)를 메모리에 할당하여 유지**하는 방식입니다.
- **에이전트의 샘플 모델**:
  확률 분포 딕셔너리 자체를 아예 만들지 않습니다! 오직 **"행동을 하나 뽑아달라"는 요청이 들어오는 그 순간, 즉석에서 난수를 발생시켜 행동 하나를 샘플링하거나 최댓값(*argmax*)을 계산해 반환**하는 초경량 방식입니다.

---

## 10.5.2 무작위 에이전트로 비교하는 구현 차이

가장 단순한 무작위 에이전트(Random Agent)를 두 가지 방식으로 비교해 보면 차이가 확연히 드러납니다.

### 1) 분포 모델 방식
```python
from collections import defaultdict
import numpy as np

class RandomAgentDistribution:
    def __init__(self):
        # 모든 상태마다 4개 행동의 확률 분포를 명시적으로 저장
        random_actions = {0: 0.25, 1: 0.25, 2: 0.25, 3: 0.25}
        self.pi = defaultdict(lambda: random_actions)

    def get_action(self, state):
        # 1. 상태에 해당하는 확률 분포를 메모리에서 꺼냄
        action_probs = self.pi[state]
        actions = list(action_probs.keys())
        probs = list(action_probs.values())
        # 2. 확률 분포 p에 따라 가중 샘플링
        return np.random.choice(actions, p=probs)
```
- 모든 상태가 방문될 때마다 딕셔너리에 4개의 float 키-값 쌍이 누적됩니다.
- 상태 공간이 수만 개, 수억 개로 커지면 메모리 낭비가 극심해집니다.

### 2) 샘플 모델 방식
```python
import numpy as np

class RandomAgentSample:
    def get_action(self, state):
        # 확률 분포 딕셔너리 없이 4개 행동 중 하나를 즉석 난수 추출!
        return np.random.choice(4)
```
- 클래스 초기화(`__init__`)조차 필요 없습니다!
- 메모리 사용량이 완벽한 0에 수렴하며 속도도 훨씬 빠릅니다.

---

## 10.5.3 Q-러닝의 단계적 다이어트: 분포 모델에서 샘플 모델로

10.4절에서 우리가 구현했던 `QLearningAgent`는 전형적인 분포 모델이었습니다:
- 대상 정책 딕셔너리 `self.pi` 유지
- 행동 정책 딕셔너리 `self.b` 유지
- 매 스텝마다 `greedy_probs()`를 호출하여 두 딕셔너리를 일일이 업데이트

이 무거운 코드를 두 단계에 걸쳐 가볍게 깎아내 봅시다.

---

### Step 1: 불필요한 `self.pi` 삭제와 `self.b`의 지연 평가

```python
class QLearningAgentStep1:
    def __init__(self):
        self.gamma = 0.9
        self.alpha = 0.8
        self.epsilon = 0.1
        self.action_size = 4
        # self.pi 삭제! (Q 테이블만 있으면 언제든 argmax로 최적 행동을 찾을 수 있으므로 불필요)
        self.b = defaultdict(lambda: {0: 0.25, 1: 0.25, 2: 0.25, 3: 0.25})
        self.Q = defaultdict(lambda: 0)

    def get_action(self, state):
        # 행동을 결정해야 하는 순간에만 Q를 바탕으로 ε-탐욕 확률을 생성
        self.b[state] = greedy_probs(self.Q, state, self.epsilon)
        action_probs = self.b[state]
        actions = list(action_probs.keys())
        probs = list(action_probs.values())
        return np.random.choice(actions, p=probs)

    def update(self, state, action, reward, next_state, done):
        if done:
            next_q_max = 0
        else:
            next_qs = [self.Q[next_state, a] for a in range(self.action_size)]
            next_q_max = max(next_qs)

        target = reward + self.gamma * next_q_max
        self.Q[state, action] += (target - self.Q[state, action]) * self.alpha
        # update() 안에서 정책 딕셔너리를 일일이 갱신하던 부하를 제거!
```

---

### Step 2: 완벽한 샘플 모델 Q-러닝 (`q_learning_simple.py`)

이제 마지막으로 남아있던 행동 정책 딕셔너리 `self.b`마저 완전히 없애버립시다!

<div align="right"><b>ch06/q_learning_simple.py</b></div>

```python
import numpy as np
from collections import defaultdict

class QLearningAgentSimple:
    def __init__(self):
        self.gamma = 0.9
        self.alpha = 0.8
        self.epsilon = 0.1
        self.action_size = 4
        self.Q = defaultdict(lambda: 0) # 오직 Q 테이블 하나만 유지!

    def get_action(self, state):
        # ❶ ε의 확률로 무작위 탐험 (동전 튕기기!)
        if np.random.rand() < self.epsilon:
            return np.random.choice(self.action_size)
        # ❷ 1 - ε의 확률로 최적 탐욕 행동 선택 (최고 점수 argmax!)
        else:
            qs = [self.Q[state, a] for a in range(self.action_size)]
            return np.argmax(qs)

    def update(self, state, action, reward, next_state, done):
        if done:
            next_q_max = 0
        else:
            next_qs = [self.Q[next_state, a] for a in range(self.action_size)]
            next_q_max = max(next_qs)

        target = reward + self.gamma * next_q_max
        self.Q[state, action] += (target - self.Q[state, action]) * self.alpha
```

#### 코드 핵심 분석:
- **딕셔너리 정책의 완전한 소멸**:
  에이전트가 들고 있는 메모리는 오직 `self.Q` 하나뿐입니다. `self.pi`도 없고 `self.b`도 없습니다.
- **`get_action(self, state)`의 눈부신 단순함**:
  - `if np.random.rand() < self.epsilon:` 
    0부터 1 사이의 난수를 뽑아 *ε*(0.1)보다 작으면 4가지 행동 중 하나를 무작위로 고릅니다.
  - `else: return np.argmax(qs)`
    그렇지 않으면 현재 상태의 Q값들 중 가장 큰 값을 가진 행동 번호를 곧바로 반환합니다.
- 복잡한 딕셔너리 조회, 확률 리스트 추출, `greedy_probs()` 유틸리티 함수 호출이 전부 사라졌습니다!

---

## 10.5.4 딥러닝과 DQN으로 이어지는 결정적 연결고리

이 샘플 모델 구현은 단순한 코드 줄이기 테크닉이 아닙니다. **다음 장(11장 신경망과 Q-러닝)과 12장(DQN)**으로 넘어가기 위한 절대적인 필수 관문입니다!

1. **연속 상태 공간(Continuous State Space)의 등장**:
   - 그리드 월드에서는 칸 수가 12개뿐이라 상태마다 딕셔너리를 만들 수 있었습니다.
   - 하지만 자율주행차(위치, 속도, 각도)나 아타리 비디오게임(수십만 픽셀 화면)처럼 상태가 연속적인 실수 벡터일 경우, **상태의 가짓수가 무한대**가 됩니다!
   - 상태마다 확률 분포를 저장하는 '분포 모델' 방식은 컴퓨터 메모리가 폭발하여 단 1초도 버틸 수 없습니다.
2. **신경망(Neural Network)과의 완벽한 융합**:
   - 11장부터는 테이블 형태의 `self.Q` 대신, 상태 벡터를 입력받아 각 행동의 Q값을 출력하는 **신경망 모델 `Q_network(state)`**를 사용할 것입니다.
   - 신경망을 통과시켜 나온 출력 벡터에서 `np.argmax()`를 취하는 구조는 방금 우리가 완성한 **샘플 모델의 `get_action()` 구조와 100% 동일**합니다!

이로써 우리는 기초적인 테이블형 강화학습의 모든 거추장스러운 껍질을 벗겨내고, 딥 강화학습(Deep RL)의 바다로 뛰어들 준비를 완벽하게 마쳤습니다!
