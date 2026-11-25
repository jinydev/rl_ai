---
layout: docs
title: "16.2 신뢰 구역 정책 최적화 (TRPO): 단조 개선 보장과 켤레 기울기법"
---

# 16.2 신뢰 구역 정책 최적화 (TRPO): 단조 개선 보장과 켤레 기울기법

![16.2 신뢰 구역 정책 최적화 TRPO](./17_2_신뢰_구역_정책_최적화_TRPO.png)
**그림 16-2** 정책 확률분포의 폭풍우 속에서도 안전한 KL 발산 신뢰 영역($D_{\text{KL}}(\pi_{\text{old}} \parallel \pi) \le \delta$) 보호막 안에서 평온하게 최적 성능을 찾아가는 도로시와 지니

---

> **도로시와 토토의 비유로 이해하기**:
> 거친 폭풍이 몰아치는 절벽 위에서 줄타기 연습을 할 때, 떨어지지 않는 가장 확실한 방법은 몸 주위에 반경 1미터짜리 '투명한 마법 방어막(신뢰 구역, Trust Region)'을 치는 것입니다!
> 방어막 안에서는 아무리 발을 뻗고 몸을 틀어도 절벽 밖으로 튕겨 나갈 염려가 전혀 없습니다. TRPO는 이전 정책($\pi_{\text{old}}$)을 중심으로 확률분포의 차이(KL 발산)가 $\delta$보다 작아야 한다는 엄격한 방어막을 쳐서, 정책이 매 스텝 단 0.1%도 나빠지지 않고 무조건 이전보다 나아지게(Monotonic Improvement) 만드는 수학적 마법입니다!

---

## 16.2.1 대체 목적 함수 (Surrogate Objective)의 유도

새로운 정책 $\pi$의 성능 $J(\pi)$와 이전 정책 $\pi_{\text{old}}$의 성능 $J(\pi_{\text{old}})$ 사이에는 다음과 같은 엄밀한 등식이 성립합니다 (Kakade & Langford, 2002):

$$
J(\pi) = J(\pi_{\text{old}}) + \mathbb{E}_{\tau \sim \pi} \left[ \sum_{t=0}^\infty \gamma^t A^{\pi_{\text{old}}}(S_t, A_t) \right]
$$

[식 16.6] 정책 성능의 상대적 분해

하지만 이 식에서 기댓값은 **새로운 정책 $\pi$에 의해 방문되는 상태 분포 $d^\pi(s)$**를 따라야 합니다. 아직 새 정책 $\pi$를 굴려보지도 않았는데 $d^\pi$를 알 수는 없습니다!
존 슐만(John Schulman, 2015)은 $d^\pi$ 대신 이미 데이터를 수집해 둔 **이전 정책의 상태 분포 $d^{\pi_{\text{old}}}$를 대신 사용하는 근사 목적 함수**, 즉 **대체 목적 함수(Surrogate Objective $L_{\pi_{\text{old}}}(\pi)$)**를 정의했습니다:

$$
L_{\pi_{\text{old}}}(\pi) = J(\pi_{\text{old}}) + \sum_s d^{\pi_{\text{old}}}(s) \sum_a \pi(a \mid s) A^{\pi_{\text{old}}}(s, a)
$$

여기에 중요도 샘플링(Importance Sampling)을 적용하면, 이전 정책 $\pi_{\text{old}}$로 수집한 샘플들만으로 기댓값을 표현할 수 있습니다:

$$
L_{\pi_{\text{old}}}(\pi) = \mathbb{E}_{s \sim d^{\pi_{\text{old}}}, a \sim \pi_{\text{old}}} \left[ \frac{\pi(a \mid s)}{\pi_{\text{old}}(a \mid s)} A^{\pi_{\text{old}}}(s, a) \right]
$$

[식 16.7] 대체 목적 함수 (Surrogate Objective)

---

## 16.2.2 단조 개선 보장 정리 (Monotonic Improvement Guarantee)

그렇다면 $d^\pi$ 대신 $d^{\pi_{\text{old}}}$를 썼을 때 발생하는 오차는 얼마나 될까요? 슐만 연구진은 두 정책 간의 **최대 KL 발산(Maximum KL Divergence)**을 이용하여 실제 성능 $J(\pi)$의 엄밀한 하한선을 유도했습니다:

$$
J(\pi) \ge L_{\pi_{\text{old}}}(\pi) - C \cdot D_{\text{KL}}^{\max}(\pi_{\text{old}}, \pi)
$$

$$
\text{where } C = \frac{4\epsilon \gamma}{(1-\gamma)^2}, \quad \epsilon = \max_{s, a} |A^{\pi_{\text{old}}}(s, a)|
$$

[식 16.8] TRPO 단조 개선 정리 (Monotonic Improvement Bound)

이 수식은 기계학습의 EM(Expectation-Maximization) 알고리즘처럼, **우변의 하한선(Lower Bound)을 극대화하면 실제 성능 $J(\pi)$는 절대로 떨어지지 않고 단조 증가함을 수학적으로 증명**합니다!

---

## 16.2.3 TRPO의 제약 조건 최적화 문제 정의

이론적으로는 페널티 계수 $C$를 목적 함수에 빼주는 비제약 최적화(Unconstrained Optimization)가 가능하지만, 이론적 $C$ 값은 너무 거대하여 스텝 크기가 지나치게 보수적으로 위축됩니다.
따라서 TRPO는 페널티 항 대신 **명시적인 신뢰 영역 제약 조건(Hard Trust Region Constraint)**으로 문제를 재구성합니다:

$$
\max_\theta \mathbb{E}_{s, a \sim \pi_{\theta_{\text{old}}}} \left[ \frac{\pi_\theta(a \mid s)}{\pi_{\theta_{\text{old}}}(a \mid s)} A^{\pi_{\theta_{\text{old}}}}(s, a) \right]
$$
$$
\text{subject to } \bar{D}_{\text{KL}}(\theta_{\text{old}}, \theta) = \mathbb{E}_{s \sim d^{\pi_{\theta_{\text{old}}}}} \left[ D_{\text{KL}}\left(\pi_{\theta_{\text{old}}}(\cdot \mid s) \parallel \pi_\theta(\cdot \mid s)\right) \right] \le \delta
$$

[식 16.9] TRPO의 핵심 최적화 공식 ($\delta$는 통상 $0.01$)

---

## 16.2.4 테일러 전개와 켤레 기울기법 (Conjugate Gradient)

이 비선형 제약 조건 문제를 풀기 위해 테일러 급수 근사(Taylor Expansion)를 적용합니다:
1. **목적 함수**: 1차 선형 근사 $\rightarrow$ $L(\theta) \approx g^T (\theta - \theta_{\text{old}})$ (여기서 $g = \nabla_\theta L$)
2. **KL 제약 조건**: 2차 곡률 근사 $\rightarrow$ $\bar{D}_{\text{KL}} \approx \frac{1}{2} (\theta - \theta_{\text{old}})^T H (\theta - \theta_{\text{old}})$ (여기서 $H$는 피셔 정보 행렬 $F$)

라그랑주 승수법(Lagrange Multipliers)을 풀면 최적 갱신 벡터는 다음과 같은 해석적 해를 갖습니다:

$$
\theta_{\text{new}} = \theta_{\text{old}} + \sqrt{\frac{2\delta}{g^T H^{-1} g}} H^{-1} g
$$

[식 16.10] TRPO의 최적 스텝 벡터

### 켤레 기울기법(Conjugate Gradient)과 라인 서치(Line Search)
- 거대한 행렬 $H^{-1}$을 직접 구하지 않고, 선형 연립방정식 $H x = g$를 풀기 위해 **켤레 기울기법(Conjugate Gradient)**을 사용하여 몇 번의 행렬-벡터 곱($H v$)만으로 방향 $x \approx H^{-1}g$를 고속 근사합니다.
- 마지막으로 테일러 2차 근사 오차로 인해 제약 조건을 위반하지 않도록 **백트래킹 라인 서치(Backtracking Line Search)**를 수행하여 실제로 $L(\theta)$가 개선되고 $D_{\text{KL}} \le \delta$를 만족하는지 검증 후 파라미터를 확정합니다.

TRPO는 이론적으로 완벽에 가까운 안정성을 보여주었지만, **Hessian-벡터 곱, 켤레 기울기법, 라인 서치라는 복잡하고 무거운 연산 체계** 때문에 실전 적용이 까다로웠습니다. 이를 1차 최적화로 혁신한 것이 바로 **PPO**입니다!
