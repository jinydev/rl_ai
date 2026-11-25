---
layout: docs
title: "15.3 정책 그래디언트 정리와 로그 미분 트릭"
---

# 15.3 정책 그래디언트 정리와 로그 미분 트릭

**그림 15-3** 미지의 환경 전이 확률 수식을 마법의 지팡이로 톡 건드려 반짝이는 별가루로 소거시키고 순수한 점수 함수만을 칠판에 남기는 호진 교수님과 도로시, 지니
![정책 그래디언트 정리와 로그 미분 트릭](./15_3_정책_그래디언트_정리와_로그_미분_트릭.png)

---

> **호진 교수님의 칠판 강의**:
> "우리가 강화학습을 할 때 가장 곤란한 점은 '우리가 취한 행동이 다음 상태를 어떻게 바꿀지'를 완벽히 나타내는 환경의 전이 확률 $P(s'|s, a)$를 사전에 알 수 없다는(Model-free) 것입니다. 그렇다면 목적 함수 $J(\theta)$를 미분할 때 이 미지의 환경 확률도 미분해야 할까요?
> 놀랍게도 **로그 미분 트릭(Log-Derivative Trick)**을 사용하면, 환경의 복잡한 물리 법칙이 미분식에서 마법처럼 완전히 소거됩니다! 오직 에이전트가 통제할 수 있는 정책 신경망의 로그 확률 미분값(점수 함수)만 남게 되는 것이죠. 이것이 바로 강화학습 역사상 가장 아름다운 정리라 불리는 **정책 그래디언트 정리(Policy Gradient Theorem)**입니다."

---

### 1. Model-free 환경에서의 미분 난제

목적 함수 $J(\theta)$의 정의를 다시 살펴보겠습니다:

$$J(\theta) = \mathbb{E}_{\tau \sim \pi_\theta} [R(\tau)] = \int P(\tau; \theta) R(\tau) d\tau$$

여기서 궤적 $\tau = (s_0, a_0, s_1, a_1, \dots, s_T)$가 발생할 결합 확률 $P(\tau; \theta)$는 다음과 같이 전개됩니다:

$$P(\tau; \theta) = \rho_0(s_0) \prod_{t=0}^{T-1} \pi_\theta(a_t \mid s_t) P(s_{t+1} \mid s_t, a_t)$$

* $\rho_0(s_0)$: 초기 상태 분포
* $\pi_\theta(a_t|s_t)$: 우리가 설계한 신경망 정책
* $P(s_{t+1}|s_t, a_t)$: **환경의 전이 확률 (알지 못함 / Model-free)**

목적 함수를 $\theta$에 대해 미분하면:

$$\nabla_\theta J(\theta) = \nabla_\theta \int P(\tau; \theta) R(\tau) d\tau = \int \nabla_\theta P(\tau; \theta) R(\tau) d\tau$$

문제는 $\nabla_\theta P(\tau; \theta)$는 더 이상 확률 분포가 아니기 때문에 기댓값 형태($\mathbb{E}[\cdot]$)로 표현할 수 없어, 몬테카를로 샘플링을 통한 수치적 근사가 불가능하다는 점입니다.

---

### 2. 로그 미분 트릭 (Log-Derivative Trick / Likelihood Ratio Identity)

이 난제를 극복하기 위해 미적분학의 기본적인 합성함수 미분법을 활용합니다:

$$\frac{d}{dx} \log f(x) = \frac{f'(x)}{f(x)} \iff f'(x) = f(x) \frac{d}{dx} \log f(x)$$

이를 다변수 벡터 함수 $P(\tau; \theta)$에 적용하면 다음과 같은 항등식을 얻습니다:

$$\nabla_\theta P(\tau; \theta) = P(\tau; \theta) \frac{\nabla_\theta P(\tau; \theta)}{P(\tau; \theta)} = P(\tau; \theta) \nabla_\theta \log P(\tau; \theta)$$

이를 원래의 그래디언트 식에 대입하면 놀라운 변화가 일어납니다:

$$\nabla_\theta J(\theta) = \int \nabla_\theta P(\tau; \theta) R(\tau) d\tau = \int P(\tau; \theta) \left[ \nabla_\theta \log P(\tau; \theta) R(\tau) \right] d\tau$$

다시 $P(\tau; \theta)$가 식의 맨 앞에 곱해졌으므로, 적분식을 **기댓값(Expectation) 형태**로 완벽하게 되돌릴 수 있습니다!

$$\nabla_\theta J(\theta) = \mathbb{E}_{\tau \sim \pi_\theta} \left[ \nabla_\theta \log P(\tau; \theta) R(\tau) \right]$$

---

### 3. 환경 전이 역학의 기적적 소거 (Cancellation of Dynamics)

이제 $\log P(\tau; \theta)$의 미분을 구해보겠습니다. 곱의 로그는 합의 로그로 분해됩니다:

$$\log P(\tau; \theta) = \log \rho_0(s_0) + \sum_{t=0}^{T-1} \log \pi_\theta(a_t \mid s_t) + \sum_{t=0}^{T-1} \log P(s_{t+1} \mid s_t, a_t)$$

양변을 $\theta$에 대해 그래디언트를 취하면:
* $\nabla_\theta \log \rho_0(s_0) = 0$ (초기 상태 분포는 $\theta$와 무관)
* $\nabla_\theta \log P(s_{t+1}|s_t, a_t) = 0$ (**환경의 물리적 전이 확률은 $\theta$와 완전히 무관!**)

따라서 우리가 알지 못했던 복잡한 환경 역학 항이 미분 과정에서 **완전히 $0$으로 소거**됩니다!

$$\nabla_\theta \log P(\tau; \theta) = \sum_{t=0}^{T-1} \nabla_\theta \log \pi_\theta(a_t \mid s_t)$$

---

### 4. 점수 함수(Score Function)와 정책 그래디언트 정리

미적분학 및 통계학에서 확률 밀도 함수의 로그 미분을 **점수 함수(Score Function)**라고 부릅니다:

$$\text{Score Function} = \nabla_\theta \log \pi_\theta(a_t \mid s_t)$$

여기에 인과성(Causality) 원리(과거의 행동은 미래의 보상에만 영향을 미치고, 과거의 보상에는 영향을 미칠 수 없음)를 적용하면, 전체 보상 $R(\tau)$ 대신 시점 $t$ 이후의 할인 누적 반환값 $G_t$를 대입할 수 있습니다:

$$G_t = \sum_{k=t}^{T} \gamma^{k-t} r_k$$

최종적으로 도출되는 **정책 그래디언트 정리(Policy Gradient Theorem)**의 핵심 공식은 다음과 같습니다:

$$\nabla_\theta J(\theta) = \mathbb{E}_{\tau \sim \pi_\theta} \left[ \sum_{t=0}^{T-1} \nabla_\theta \log \pi_\theta(a_t \mid s_t) \cdot G_t \right]$$

```
[정책 그래디언트 정리의 직관적 해석]

∇_θ J(θ) = E [ (선택한 행동의 로그 확률 변화율) × (그 행동 이후 얻은 실제 성과 G_t) ]
               └───────── 점수 함수 ────────┘     └────── 가중치(보상) ──────┘
```

* **$G_t > 0$ (보상이 우수함)**: 그 행동 $a_t$의 로그 확률 $\log \pi_\theta(a_t|s_t)$를 증가시키는 방향으로 $\theta$를 갱신합니다.
* **$G_t < 0$ (보상이 나쁨)**: 그 행동의 선택 확률을 감소시키는 방향으로 $\theta$를 갱신합니다.

환경의 전이 모델을 전혀 몰라도, 에이전트가 실제로 에피소드를 주행하며 수집한 샘플 데이터만으로 기대 보상을 최대화하는 파라미터 업데이트 방향을 정확하게 계산할 수 있게 된 것입니다!
