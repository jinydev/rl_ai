---
layout: docs
title: "APPENDIX D - 정책 경사법 증명"
---

# APPENDIX D

# 정책 경사법 증명 (Policy Gradient Theorem Proof)

**그림 D-0** 미분과 적분 기호가 빼곡한 칠판 앞에서 엄밀한 정책 경사 정리를 수학적으로 증명하는 이호진 교수님과 꼼꼼히 노트를 기록하는 도로시, 호기심 가득한 지니와 토토
![정책 경사법 증명 인트로](./img/02_policy_gradient_proof_chalkboard.jpg)

---

> **도로시와 토토의 비유로 이해하기**:
> 칠판 가득 적분 기호(∫)와 정책 경사(∇) 수식이 적혀 있습니다. 직관적인 감각으로만 이해했던 13장의 **정책 경사 정리(Policy Gradient Theorem)**와 **베이스라인(Baseline)의 분산 감소 원리**를 이호진 교수님과 함께 한 줄 한 줄 수학적으로 완벽하게 증명해 봅니다. 환경의 복잡한 전이 확률을 전혀 몰라도(Model-Free) 최적 정책을 찾을 수 있는 '강화학습의 기적'이 수식 속에서 아름답게 펼쳐집니다!

13장에서 다룬 정책 경사법의 핵심 정리 두 가지를 엄밀하게 유도해 보겠습니다.

---

## D.1 정책 경사 정리 도출

13.1절에서 에이전트의 목표 함수를 궤적 $\tau$ 의 누적 보상 기댓값인 $J(\theta) = \mathbb{E}_{\tau \sim \pi_\theta}[G(\tau)]$ 로 정의했을 때, 파라미터 $\theta$ 에 대한 목적 함수의 기울기는 다음과 같이 표현된다고 배웠습니다.

$$
\nabla_\theta J(\theta) = \mathbb{E}_{\tau \sim \pi_\theta} \left[ \sum_{t=0}^T G(\tau) \cdot \nabla_\theta \log \pi_\theta(A_t \mid S_t) \right]
$$

[식 13.1] 정책 경사 정리 (Policy Gradient Theorem)

이제 [식 13.1]이 어떻게 유도되는지 한 단계씩 확인해 보겠습니다.

### 1단계: 기댓값 전개와 미분 기호의 이동

먼저 기호를 정리합니다.
- 정책 매개변수: $\theta$
- 상태와 행동의 궤적: $\tau = (S_0, A_0, S_1, A_1, \dots, S_T, A_T)$
- 정책 $\pi_\theta$ 를 따를 때 궤적 $\tau$ 가 발생할 확률: $\Pr(\tau \mid \theta)$
- 궤적 전체에서 얻은 총 수익: $G(\tau)$

목적 함수 $J(\theta)$ 의 정의에 따라 기울기 $\nabla_\theta J(\theta)$ 를 수식으로 전개합니다.

$$
\begin{aligned}
\nabla_\theta J(\theta) &= \nabla_\theta \mathbb{E}_{\tau \sim \pi_\theta} [G(\tau)] \\
&= \nabla_\theta \sum_\tau \Pr(\tau \mid \theta) \cdot G(\tau) \quad (\text{기댓값의 수학적 정의}) \\
&= \sum_\tau \nabla_\theta (\Pr(\tau \mid \theta) \cdot G(\tau)) \quad (\text{선형 연산인 미분 기호 } \nabla_\theta \text{를 합 } \sum \text{ 안으로 이동}) \\
&= \sum_\tau \{ G(\tau) \cdot \nabla_\theta \Pr(\tau \mid \theta) + \Pr(\tau \mid \theta) \cdot \nabla_\theta G(\tau) \} \quad (\text{곱의 미분법 적용})
\end{aligned}
$$

[식 D.1] 기댓값 정의와 곱의 미분법

여기서 두 번째 항인 $\nabla_\theta G(\tau)$ 에 주목합시다. 궤적 $\tau$ 가 주어졌을 때 총 수익 $G(\tau)$ 는 환경에서 실제로 수집된 보상들의 합($R_1 + \gamma R_2 + \dots$)일 뿐이므로, 정책 파라미터 $\theta$ 에 의해 값이 변하지 않는 상수입니다. 따라서 **$\nabla_\theta G(\tau) = 0$** 이 되어 두 번째 항은 완전히 사라집니다!

$$
\nabla_\theta J(\theta) = \sum_\tau G(\tau) \cdot \nabla_\theta \Pr(\tau \mid \theta)
$$

---

### 2단계: 로그-기울기 트릭 (Log-Derivative Trick)

위 식을 에이전트가 샘플링으로 추정할 수 있는 기댓값 형태($\mathbb{E}_{\tau \sim \pi_\theta}[ \cdot ]$)로 되돌리려면 식 안에 $\Pr(\tau \mid \theta)$ 가 곱해져 있어야 합니다. 이를 위해 분자와 분모에 $\Pr(\tau \mid \theta)$ 를 동시에 곱해 줍니다.

$$
\sum_\tau G(\tau) \cdot \nabla_\theta \Pr(\tau \mid \theta) = \sum_\tau G(\tau) \cdot \Pr(\tau \mid \theta) \cdot \left[ \frac{\nabla_\theta \Pr(\tau \mid \theta)}{\Pr(\tau \mid \theta)} \right]
$$

여기서 고등학교 미적분의 **로그 도함수(Logarithmic Derivative)** 공식을 떠올려 봅니다.

$$
\frac{d}{dx} [ \log f(x) ] = \frac{f'(x)}{f(x)}
$$

다변수 벡터 미분(기울기 $\nabla$)에서도 동일한 규칙이 성립합니다.

$$
\nabla_\theta \log \Pr(\tau \mid \theta) = \frac{\nabla_\theta \Pr(\tau \mid \theta)}{\Pr(\tau \mid \theta)}
$$

따라서 분수 항을 로그 도함수로 바꿔치기할 수 있습니다.

$$
\begin{aligned}
\nabla_\theta J(\theta) &= \sum_\tau \Pr(\tau \mid \theta) \cdot \{ G(\tau) \cdot \nabla_\theta \log \Pr(\tau \mid \theta) \} \\
&= \mathbb{E}_{\tau \sim \pi_\theta} [ G(\tau) \cdot \nabla_\theta \log \Pr(\tau \mid \theta) ]
\end{aligned}
$$

[식 D.2] 로그-기울기 트릭을 통한 기댓값 복원

이처럼 미분 항을 '로그의 미분'으로 전환하여 기댓값 안으로 자연스럽게 집어넣는 기법을 **로그-기울기 트릭(Log-Gradient Trick)** 또는 **로그-도함수 트릭(Log-Derivative Trick)**이라 부르며, 현대 머신러닝과 강화학습에서 가장 광범위하게 애용되는 기법입니다.

---

### 3단계: 환경 전이 확률의 소거 (강화학습의 기적)

이제 궤적 확률 $\Pr(\tau \mid \theta)$ 의 내부를 분해해 봅니다.
시작 상태 $S_0$ 부터 종료 시점 $T$ 까지 일어나는 모든 상태 전이와 에이전트의 행동 선택 확률을 곱하면 다음과 같습니다.

$$
\begin{aligned}
\Pr(\tau \mid \theta) &= p(S_0) \cdot \pi_\theta(A_0 \mid S_0) \cdot p(S_1 \mid S_0, A_0) \dots \pi_\theta(A_T \mid S_T) \cdot p(S_{T+1} \mid S_T, A_T) \\
&= p(S_0) \cdot \prod_{t=0}^T [ \pi_\theta(A_t \mid S_t) \cdot p(S_{t+1} \mid S_t, A_t) ]
\end{aligned}
$$

여기서 $p(S_0)$ 은 환경의 초기 상태 분포이고, $p(S_{t+1} \mid S_t, A_t)$ 는 상태 $S_t$ 에서 행동 $A_t$ 를 취했을 때 다음 상태 $S_{t+1}$ 로 전이될 환경의 물리 법칙(전이 확률)입니다.

양변에 자연로그($\log$)를 취하면 곱셈이 덧셈으로 분해됩니다.

$$
\log \Pr(\tau \mid \theta) = \log p(S_0) + \sum_{t=0}^T \log p(S_{t+1} \mid S_t, A_t) + \sum_{t=0}^T \log \pi_\theta(A_t \mid S_t)
$$

이제 양변을 정책 파라미터 $\theta$ 에 대해 미분($\nabla_\theta$)해 봅시다!

$$
\nabla_\theta \log \Pr(\tau \mid \theta) = \nabla_\theta \log p(S_0) + \nabla_\theta \sum_{t=0}^T \log p(S_{t+1} \mid S_t, A_t) + \nabla_\theta \sum_{t=0}^T \log \pi_\theta(A_t \mid S_t)
$$

놀랍게도, 환경의 초기 상태 확률 $p(S_0)$ 과 환경의 물리적 전이 확률 $p(S_{t+1} \mid S_t, A_t)$ 는 **에이전트의 정책 가중치 $\theta$ 와 아무런 관련이 없습니다.** 따라서 $\theta$ 에 대해 편미분하면 정확하게 **0**이 되어 완전히 소거됩니다!

$$
\nabla_\theta \log p(S_0) = 0, \quad \nabla_\theta \log p(S_{t+1} \mid S_t, A_t) = 0
$$

남는 항은 오직 에이전트의 정책 신경망에 관한 항뿐입니다.

$$
\nabla_\theta \log \Pr(\tau \mid \theta) = \sum_{t=0}^T \nabla_\theta \log \pi_\theta(A_t \mid S_t)
$$

[식 D.3] 궤적 로그 기울기의 정책 분해

이 결과를 [식 D.2]에 대입하면 우리가 원하는 최종 형태가 도출됩니다!

$$
\nabla_\theta J(\theta) = \mathbb{E}_{\tau \sim \pi_\theta} \left[ \sum_{t=0}^T G(\tau) \cdot \nabla_\theta \log \pi_\theta(A_t \mid S_t) \right]
$$

[식 D.4] 최종 정책 경사 수식

> [!NOTE]
> **왜 이것이 강화학습의 기적인가?**  
> 현실 세계(자율주행, 로봇 제어, 주식 시장 등)에서 환경의 전이 확률 $p(S_{t+1} \mid S_t, A_t)$ 는 계산하기 불가능할 정도로 복잡합니다. 하지만 정책 경사 정리 덕분에 환경의 전이 모델을 전혀 몰라도(Model-Free), 에이전트가 직접 샘플링한 행동 로그 확률의 기울기 $\nabla_\theta \log \pi_\theta(A_t \mid S_t)$ 에 관측된 보상 $G(\tau)$ 만 곱해 주면 목표 함수를 정확하게 극대화하는 파라미터 업데이트 방향을 구할 수 있습니다.

---

## D.2 베이스라인(Baseline)의 분산 감소 원리 증명

13.3절에서는 학습의 분산을 획기적으로 낮추기 위해 총 수익 $G_t$ 에서 임의의 상태 기준 함수 $b(S_t)$ 를 차감한 형태를 소개했습니다.

$$
\nabla_\theta J(\theta) = \mathbb{E}_{\tau \sim \pi_\theta} \left[ \sum_{t=0}^T (G_t - b(S_t)) \cdot \nabla_\theta \log \pi_\theta(A_t \mid S_t) \right]
$$

[식 13.4] 베이스라인이 적용된 정책 경사

여기서 $b(S_t)$ 를 빼도 수식의 기댓값이 일절 왜곡되지 않는(Unbiased) 이유를 수학적으로 증명해 보겠습니다.

### 1단계: 임의의 확률 분포에서 스코어 함수의 기댓값은 0

먼저 머신러닝의 기초 정리 하나를 증명합니다.  
매개변수 $\theta$ 를 가지는 임의의 이산 확률 분포 $P_\theta(x)$ 에 대해 다음 등식이 성립합니다.

$$
\mathbb{E}_{x \sim P_\theta} [ \nabla_\theta \log P_\theta(x) ] = 0
$$

[정리] 로그 확률 도함수의 기댓값은 항상 0

**증명:**  
확률의 기본 공리에 의해 모든 가능한 사건 $x$ 에 대한 확률의 합은 항상 1입니다.

$$
\sum_x P_\theta(x) = 1
$$

이 등식의 양변을 $\theta$ 에 대해 미분합니다. 상수 1을 미분하면 0이 됩니다.

$$
\nabla_\theta \sum_x P_\theta(x) = \nabla_\theta 1 = 0
$$

합 기호($\sum$)와 미분 연산자($\nabla_\theta$)의 순서를 바꾸고, 다시 한번 '로그-기울기 트릭'을 적용합니다.

$$
\begin{aligned}
0 &= \sum_x \nabla_\theta P_\theta(x) \\
&= \sum_x P_\theta(x) \cdot \left[ \frac{\nabla_\theta P_\theta(x)}{P_\theta(x)} \right] \\
&= \sum_x P_\theta(x) \cdot \nabla_\theta \log P_\theta(x) \\
&= \mathbb{E}_{x \sim P_\theta} [ \nabla_\theta \log P_\theta(x) ]
\end{aligned}
$$

증명이 완료되었습니다! 즉, **어떤 확률 분포이든 간에 '로그 확률의 기울기(Score function)'의 기댓값은 항상 수학적으로 정확히 0**입니다.

---

### 2단계: 강화학습 정책 분포에 적용

이 일반 정리를 강화학습의 특정 시점 상태 $S_t$ 에서의 행동 정책 $\pi_\theta( \cdot \mid S_t)$ 에 대입합니다.  
$x$ 대신 행동 $A_t$ 를, $P_\theta(x)$ 대신 $\pi_\theta(A_t \mid S_t)$ 를 넣으면 다음을 얻습니다.

$$
\mathbb{E}_{A_t \sim \pi_\theta} [ \nabla_\theta \log \pi_\theta(A_t \mid S_t) ] = 0
$$

[식 D.5] 정책 스코어 함수의 기댓값

이제 여기에 상태 $S_t$ 에만 의존하는 임의의 스칼라 함수 $b(S_t)$ 를 곱해 봅니다.  
기댓값 연산 $\mathbb{E}_{A_t \sim \pi_\theta}$ 는 행동 $A_t$ 에 대한 평균이므로, $A_t$ 와 전혀 무관한 $b(S_t)$ 는 기댓값 바깥으로 자유롭게 빠져나올 수 있습니다!

$$
\begin{aligned}
\mathbb{E}_{A_t \sim \pi_\theta} [ b(S_t) \cdot \nabla_\theta \log \pi_\theta(A_t \mid S_t) ] &= b(S_t) \cdot \mathbb{E}_{A_t \sim \pi_\theta} [ \nabla_\theta \log \pi_\theta(A_t \mid S_t) ] \\
&= b(S_t) \cdot 0 \\
&= 0
\end{aligned}
$$

[식 D.6] 베이스라인 항의 소거

> [!CAUTION]
> **주의: 왜 수익 *G*<sub>*t*</sub>는 기댓값 밖으로 빠져나올 수 없는가?**  
> 수익 $G_t = R_{t+1} + \gamma R_{t+2} + \dots$ 는 상태 $S_t$ 에서 에이전트가 어떤 행동 $A_t$ 를 선택했느냐에 따라 값이 극적으로 달라집니다! 즉, $G_t$ 는 $A_t$ 에 강하게 의존하는 확률 변수이므로 $\mathbb{E}[G_t \cdot \nabla_\theta \log \pi_\theta(A_t \mid S_t)] \ne 0$ 이며 결코 0이 되지 않습니다. 반면 베이스라인 $b(S_t)$ 는 행동 $A_t$ 를 결정하기 이전의 상태 평가 기준선(예: 가치 함수 $V(S_t)$)이므로 $A_t$ 와 독립적입니다.

---

### 3단계: 전체 궤적에 대한 확장

[식 D.6]은 모든 시점 $t = 0, 1, \dots, T$ 에서 각각 독립적으로 성립합니다. 따라서 전체 궤적 $\tau$ 에 대한 기댓값으로 합산해도 여전히 0입니다.

$$
\mathbb{E}_{\tau \sim \pi_\theta} \left[ \sum_{t=0}^T b(S_t) \cdot \nabla_\theta \log \pi_\theta(A_t \mid S_t) \right] = 0
$$

따라서 원래의 정책 경사 [식 13.1]에서 0을 빼는 것은 수학적으로 등식을 완벽히 보존합니다.

$$
\begin{aligned}
\nabla_\theta J(\theta) &= \mathbb{E}_{\tau \sim \pi_\theta} \left[ \sum_{t=0}^T G_t \cdot \nabla_\theta \log \pi_\theta(A_t \mid S_t) \right] - \mathbb{E}_{\tau \sim \pi_\theta} \left[ \sum_{t=0}^T b(S_t) \cdot \nabla_\theta \log \pi_\theta(A_t \mid S_t) \right] \\
&= \mathbb{E}_{\tau \sim \pi_\theta} \left[ \sum_{t=0}^T (G_t - b(S_t)) \cdot \nabla_\theta \log \pi_\theta(A_t \mid S_t) \right]
\end{aligned}
$$

이로써 [식 13.4]의 베이스라인 항 차감이 증명되었습니다!

```
                                  [수학적 증명 요약도]
                   
       1. 기댓값 전개        ∇_θ J(θ) = Σ_τ ∇_θ [ Pr(τ|θ) G(τ) ]
                                    ↓ (∇_θ G(τ) = 0)
       2. 로그 트릭          ∇_θ J(θ) = E [ G(τ) · ∇_θ log Pr(τ|θ) ]
                                    ↓ (환경 전이 확률 ∇_θ log p = 0 소거)
       3. 정책 경사 정리     ∇_θ J(θ) = E [ Σ_t G_t · ∇_θ log π_θ(A_t|S_t) ]
                                    ↓ (E [ b(S_t) · ∇_θ log π_θ ] = 0)
       4. 베이스라인 감산    ∇_θ J(θ) = E [ Σ_t (G_t - b(S_t)) · ∇_θ log π_θ(A_t|S_t) ]
                                      ▶ 평균은 보존(Unbiased), 분산만 감소(Variance Reduction)!
```

---

## 🎯 부록 D 핵심 정리

| 증명 단계 | 핵심 수학적 원리 | 직관적 의미 |
| :--- | :--- | :--- |
| **로그-기울기 트릭** | $\nabla f = f \cdot \nabla \log f$ | 미분 기호가 확률 밀도 안으로 들어가 기댓값 표기 복원 |
| **환경 모델 소거** | $\nabla_\theta \log p(S_{t+1} \mid S_t, A_t) = 0$ | 환경의 물리 법칙을 몰라도 정책 최적화 가능 (Model-Free) |
| **스코어 함수 0** | $\mathbb{E}_{a \sim \pi} [ \nabla \log \pi(a \mid s) ] = 0$ | 확률 총합이 1이므로 기울기의 가중 평균은 항상 0 |
| **베이스라인 무편향성** | $\mathbb{E} [ b(s) \nabla \log \pi ] = 0$ | 행동에 무관한 기준선을 빼도 기대 경사는 왜곡 없이 분산만 축소 |

이제 독자 여러분은 13장에서 배운 정책 경사법, REINFORCE 알고리즘, 그리고 액터-크리틱(Actor-Critic)의 어드밴티지 계산식이 왜 수학적으로 흠결 없는 완벽한 토대 위에 서 있는지 명확하게 이해하셨습니다!
