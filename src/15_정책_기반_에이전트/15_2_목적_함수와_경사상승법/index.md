---
layout: docs
title: "15.2 목적 함수와 경사상승법"
---

# 15.2 목적 함수와 경사상승법

**그림 15-2** 기대 보상이 가장 높은 봉우리의 황금 깃발을 향해 경사상승법 황금 지팡이를 짚고 힘차게 언덕을 오르는 도로시와 토토, 그리고 등고선 지도를 든 지니
![목적 함수와 경사상승법](./15_2_목적_함수와_경사상승법.png)

---

> **도로시의 탐험 일기**:
> "일반적인 딥러닝 공부를 할 때는 오차(Loss)를 줄여야 하니까 언덕 아래로 내려가는 '경사하강법'을 썼어요. 그런데 강화학습은 모험에서 보물(보상)을 최대한 많이 모으는 게임이잖아요? 그러니 아래로 내려갈 게 아니라 가장 보상이 높은 봉우리를 향해 위로 올라가야 해요! 이것이 바로 파라미터를 보상이 커지는 방향으로 끌어올리는 **경사상승법(Gradient Ascent)**이랍니다!"

---

### 1. 궤적(Trajectory)과 총 보상

에이전트가 상태 $s_0$에서 시작하여 정책 $\pi_\theta$에 따라 행동을 선택하고 환경이 다음 상태를 돌려주는 상호작용의 전체 기록을 **궤적(Trajectory, $\tau$)**이라고 부릅니다:

$$\tau = (s_0, a_0, s_1, a_1, s_2, a_2, \dots, s_T)$$

에피소드 동안 궤적 $\tau$를 따라 얻게 되는 전체 할인 누적 보상(Return) $R(\tau)$는 다음과 같이 정의됩니다:

$$R(\tau) = \sum_{t=0}^{T} \gamma^t r(s_t, a_t)$$

여기서 $\gamma \in [0, 1]$는 미래 보상에 대한 할인율(Discount Factor)이며, $\gamma = 1$일 경우 무할인 유한 에피소드의 단순 총합 보상이 됩니다.

---

### 2. 정책의 목적 함수 (Objective Function, $J(\theta)$)

정책 신경망의 파라미터가 $\theta$로 고정되어 있을 때, 특정 궤적 $\tau$가 발생할 확률은 $P(\tau; \theta)$로 결정됩니다.

정책 기반 강화학습의 궁극적인 목표는 **파라미터 $\theta$를 가진 정책 $\pi_\theta$를 따랐을 때 얻게 되는 기대 누적 보상(Expected Cumulative Return)을 최대화**하는 것입니다. 이를 목적 함수 $J(\theta)$로 정의합니다:

$$J(\theta) = \mathbb{E}_{\tau \sim \pi_\theta} [R(\tau)] = \int P(\tau; \theta) R(\tau) d\tau$$

(이산 상태-행동 공간의 경우 적분 기호 $\int$ 대신 가능한 모든 궤적에 대한 합 $\sum_\tau$으로 표현됩니다.)

* $P(\tau; \theta)$: 정책 $\pi_\theta$ 하에서 궤적 $\tau$가 생성될 확률.
* $R(\tau)$: 해당 궤적에서 얻은 누적 보상의 총합.
* $J(\theta)$: 정책 $\pi_\theta$의 종합 성적표(기댓값).

---

### 3. 경사하강법 vs 경사상승법

지도학습(Supervised Learning)이나 일반적인 딥러닝에서는 예측값과 정답 사이의 손실(Loss, $\mathcal{L}$)을 최소화하는 것이 목적이므로 손실 함수의 그래디언트 **반대 방향**으로 파라미터를 갱신하는 **경사하강법(Gradient Descent)**을 사용합니다:

$$\theta \leftarrow \theta - \alpha \nabla_\theta \mathcal{L}(\theta) \quad (\text{Loss 최소화})$$

반면, 강화학습에서는 목적 함수 $J(\theta)$가 '손실'이 아니라 '누적 보상'이므로, 보상을 **최대화**하기 위해 그래디언트의 **양의 방향**으로 파라미터를 갱신하는 **경사상승법(Gradient Ascent)**을 적용해야 합니다:

$$\theta \leftarrow \theta + \alpha \nabla_\theta J(\theta) \quad (\text{Return 최대화})$$

* $\alpha > 0$: 학습률 (Learning Rate)
* $\nabla_\theta J(\theta)$: 파라미터 공간에서 기대 보상이 가장 가파르게 증가하는 방향 벡터 (정책 그래디언트 / Policy Gradient)

```
[경사하강법 vs 경사상승법의 파라미터 갱신]

1. 경사하강법 (Gradient Descent) : 골짜기 밑바닥으로 하강!
   θ ───(-α∇L)───> [ 오차 최소점(골짜기) 도달 ]

2. 경사상승법 (Gradient Ascent) : 산봉우리 정상으로 상승!
   θ ───(+α∇J)───> [ 보상 최대점(산봉우리) 등극 ]
```

> [!TIP]
> **파이토치(PyTorch) 옵티마이저와의 연동 팁**:
> PyTorch의 모든 옵티마이저(`optim.Adam`, `optim.SGD` 등)는 기본적으로 손실을 '최소화'하는 경사하강법으로 구현되어 있습니다. 따라서 실전 코드에서는 목적 함수에 마이너스 부호를 붙인 가짜 손실 함수(Surrogate Loss)를 정의하여 역전파를 수행합니다:
> 
> $$\mathcal{L}_{\text{policy}}(\theta) = - J(\theta)$$
> 
> 이렇게 하면 `optimizer.zero_grad()`, `loss.backward()`, `optimizer.step()`을 호출했을 때 내부적으로 경사하강법이 동작하면서 실제로는 $J(\theta)$가 최대화되는 경사상승법의 효과를 완벽하게 누릴 수 있습니다!

---

### 4. 정책 파라미터 공간에서의 탐색 메커니즘

경사상승법을 통한 정책 최적화는 다음과 같은 고유한 특성을 가집니다:

1. **연속적이고 매끄러운 정책 변화**:
   - 가치 기반 기법처럼 $\arg\max$의 문턱 효과(Thresholding)에 의해 행동이 급변하지 않고, 매 에폭마다 파라미터가 미세하게 갱신되면서 행동 확률 분포가 부드럽게 시프트됩니다.
2. **국소 최적점(Local Optima) 주의**:
   - 목적 함수 $J(\theta)$는 일반적으로 비볼록(Non-convex) 함수이므로 전역 최적점(Global Optimum)이 아닌 지역 최적점에 갇힐 위험이 존재합니다. 이를 방지하기 위해 엔트로피 정규화(Entropy Regularization)나 다양한 탐색 기법을 병행합니다.
3. **가장 큰 난제: $\nabla_\theta J(\theta)$는 어떻게 계산하는가?**:
   - $J(\theta) = \int P(\tau; \theta) R(\tau) d\tau$에서 확률 $P(\tau; \theta)$ 내부에는 우리가 알지 못하는 환경의 물리적 전이 확률 $P(s_{t+1}|s_t, a_t)$가 곱해져 있습니다.
   - 환경의 법칙을 모르는 Model-free 강화학습에서 과연 이 적분식의 미분을 어떻게 구해낼 수 있을까요?

이 놀라운 수학적 해법이 바로 다음 절에서 다룰 **정책 그래디언트 정리(Policy Gradient Theorem)**와 **로그 미분 트릭**입니다.
