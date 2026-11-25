---
layout: docs
title: "15.6 정리"
---

# 15.6 정리

**그림 15-6** 정책 기반 에이전트와 REINFORCE 알고리즘 과정을 마스터하고 황금빛 졸업 수료증을 들고 환하게 웃는 도로시와 호진 교수님, 지니, 토토
![정리](./15_6_정리.png)

---

### 1. 15장 핵심 개념 요약

이번 15장에서는 가치 기반의 한계를 극복하고 정책 자체를 파라미터화하여 직접 최적화하는 **정책 기반 강화학습(Policy-based Reinforcement Learning)**의 기본 원리와 수학적 유도, 그리고 **REINFORCE** 알고리즘의 파이토치 실전 구현을 완성했습니다.

| 핵심 주제 | 핵심 내용 및 수식 |
| :--- | :--- |
| **패러다임 전환** | 가치 함수 $Q(s,a)$의 간접적 $\arg\max$ 선택 대신, 상태 $s$에서 행동 확률 $\pi_\theta(a \mid s)$를 직접 출력 |
| **행동 공간 확장** | 이산 행동(소프트맥스)뿐 아니라 무한한 연속 행동(가우시안 평균/분산)을 직관적으로 제어 가능 |
| **목적 함수와 최적화** | 기대 누적 보상 $J(\theta) = \mathbb{E}_{\tau \sim \pi_\theta}[R(\tau)]$를 최대화하는 경사상승법 $\theta \leftarrow \theta + \alpha \nabla_\theta J(\theta)$ |
| **로그 미분 트릭** | $\nabla_\theta P(\tau;\theta) = P(\tau;\theta) \nabla_\theta \log P(\tau;\theta)$를 통해 미지의 환경 역학 $P(s' \mid s, a)$를 미분식에서 완벽히 소거 |
| **점수 함수 (Score Function)** | $\nabla_\theta \log \pi_\theta(a_t \mid s_t)$ — 행동 확률을 높이기 위한 정책 파라미터의 감도 벡터 |
| **정책 그래디언트 정리** | $\nabla_\theta J(\theta) = \mathbb{E}_{\tau \sim \pi_\theta} \left[ \sum_{t=0}^{T-1} \nabla_\theta \log \pi_\theta(a_t \mid s_t) G_t \right]$ |
| **REINFORCE 알고리즘** | 몬테카를로 방식으로 에피소드 종료 후 실제 반환값 $G_t$를 측정하여 정책 신경망을 갱신하는 기법 |
| **고분산 극복과 진화** | 몬테카를로 반환값의 높은 분산을 완화하기 위한 반환값 정규화 및 상태 가치 베이스라인 $V(s)$ 도입 |

---

### 2. 필수 수식 총정리

1. **정책 목적 함수**:
   $$J(\theta) = \mathbb{E}_{\tau \sim \pi_\theta}[R(\tau)] = \int P(\tau; \theta) R(\tau) d\tau$$

2. **로그 미분 트릭(Likelihood Ratio Identity)**:
   $$\nabla_\theta P(\tau; \theta) = P(\tau; \theta) \nabla_\theta \log P(\tau; \theta)$$

3. **정책 그래디언트 정리**:
   $$\nabla_\theta J(\theta) = \mathbb{E}_{\tau \sim \pi_\theta} \left[ \sum_{t=0}^{T-1} \nabla_\theta \log \pi_\theta(a_t \mid s_t) G_t \right]$$

4. **베이스라인 차감 형태**:
   $$\nabla_\theta J(\theta) = \mathbb{E}_{\tau \sim \pi_\theta} \left[ \sum_{t=0}^{T-1} \nabla_\theta \log \pi_\theta(a_t \mid s_t) (G_t - b(s_t)) \right] \quad (\text{단, } \mathbb{E}[\nabla_\theta \log \pi_\theta \cdot b(s)] = 0)$$

5. **PyTorch 파라미터 갱신 손실(Surrogate Loss)**:
   $$\mathcal{L}(\theta) = - \sum_{t=0}^{T-1} \log \pi_\theta(a_t \mid s_t) \cdot \hat{G}_t$$

---

### 3. 학습 퀴즈 (Quiz)

#### Q1. 정책 기반 에이전트(Policy-based Agent)에 대한 설명 중 가장 거리가 먼 것은?
1. 가치 함수를 경유하지 않고 상태에서 최적의 행동 확률 분포를 직접 출력하도록 모델링한다.
2. 소프트맥스나 가우시안 정규분포 함수를 매개변수화하여 확률적 정책을 직접 표현할 수 있다.
3. 연속적인 행동 공간(Continuous Action Space)을 가지는 환경에는 원리적으로 적용할 수 없다.
4. 일반적으로 기대 보상 목적 함수의 그래디언트를 구하여 경사상승법(Gradient Ascent)으로 파라미터를 갱신한다.

> **정답**: **3번**  
> **해설**: 정책 기반 에이전트는 연속적인 행동 공간에서 가장 강력한 위력을 발휘합니다. 가우시안 분포의 평균과 분산을 신경망 출력으로 지정함으로써 무한한 실수 행동 공간에서도 자연스럽게 샘플링 제어를 수행할 수 있습니다.

---

#### Q2. REINFORCE 알고리즘의 특징과 한계점에 대한 설명으로 가장 올바른 것은?
1. 에피소드가 끝나기 전에 매 스텝 즉각적으로 시간차(TD) 오차를 이용하여 가중치를 갱신한다.
2. 몬테카를로(Monte-Carlo) 방식으로 실제 에피소드 끝까지의 반환값을 사용하므로 그래디언트 추정의 분산(Variance)이 매우 크다.
3. 타깃 네트워크와 경험 리플레이 버퍼를 필수적으로 사용하여 오프폴리시(Off-policy)로 학습한다.
4. 상태 전이 확률(Transition Probability)을 완벽히 알고 있어야만 목적 함수의 기울기를 계산할 수 있는 Model-based 방식이다.

> **정답**: **2번**  
> **해설**: REINFORCE는 몬테카를로(MC) 정책 그래디언트 방식이므로 에피소드가 완전히 종료된 후 실제 누적 반환값 $G_t$를 사용합니다. 이로 인해 편향(Bias)은 없으나 반환값의 분산(Variance)이 매우 커서 수렴 속도가 느리고 학습이 불안정할 수 있습니다.

---

### 4. 다음 단계: 16장 액터-크리틱(Actor-Critic)으로의 도약

REINFORCE 알고리즘은 정책 그래디언트의 기본 원리를 우아하게 실현했지만, **"에피소드가 끝날 때까지 기다려야 하는 몬테카를로 방식의 한계"**와 **"에피소드 전체의 확률적 사건이 누적되어 발생하는 극단적인 고분산"**이라는 큰 장벽을 안고 있습니다.

이를 해결하기 위해 16장에서는:
* **정책을 담당하는 액터(Actor)**와
* **가치를 평가하고 베이스라인을 제공하는 크리틱(Critic)**이

환상의 듀엣으로 결합하여, 매 스텝마다 실시간으로 시간차(TD) 오차를 기반으로 분산을 극적으로 낮추며 학습하는 **액터-크리틱(Actor-Critic, A2C, A3C)** 아키텍처로 나아갑니다!
