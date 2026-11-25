---
layout: docs
title: "16.1 정책 개선의 불안정성과 보수적 정책 개선: 스텝 크기 딜레마와 자연 정책 경사"
---

# 16.1 정책 개선의 불안정성과 보수적 정책 개선: 스텝 크기 딜레마와 자연 정책 경사

![16.1 정책 개선의 불안정성과 보수적 정책 개선](./17_1_정책_개선의_불안정성과_보수적_정책_개선.png)
**그림 16-1** 과도한 한 걸음으로 디딤돌이 무너져 내리는 정책 붕괴의 위험과, 보수적이고 안전한 스텝 크기($\alpha$)를 설정하는 지니의 신중한 가이드

---

> **도로시와 토토의 비유로 이해하기**:
> 지도 학습(Supervised Learning)에서는 한 번 틀린 문제를 만나 가중치가 조금 삐끗해도, 고정된 문제집 데이터셋이 그대로 남아있으므로 다음 배치에서 다시 오답 노트를 보며 만회할 수 있습니다.
> 하지만 강화학습에서는 도로시가 모험하며 밟는 땅(상태 분포 $d^\pi(s)$) 자체가 도로시의 현재 실력(정책 $\pi$)에 의해 결정됩니다! 만약 욕심을 부려 너무 큰 보폭으로 가중치를 바꾸었다가 나쁜 정책이 되면, 도로시는 절벽 밑으로 떨어져 버리고, 거기서 수집되는 경험 데이터는 전부 절벽 밑의 쓸모없는 조약돌뿐이라 영영 원래 길로 돌아오지 못합니다. 이것이 바로 강화학습에서 스텝 크기가 생명인 이유입니다.

---

## 16.1.1 정책 붕괴(Policy Collapse)의 수학적 원인

일반적인 1차 경사 상승법(First-Order Gradient Ascent)은 다음과 같이 파라미터를 갱신합니다:

$$
\theta_{\text{new}} \leftarrow \theta_{\text{old}} + \alpha \nabla_\theta J(\theta_{\text{old}})
$$

[식 16.1] 표준 정책 경사 파라미터 갱신

여기서 파라미터 공간에서의 유클리드 거리 $\|\theta_{\text{new}} - \theta_{\text{old}}\|$가 작다고 해서, **실제 행동 확률분포의 차이(Distributional Difference)**도 반드시 작을까요? **절대 그렇지 않습니다!**

### 1) 파라미터 공간 vs 확률분포 공간의 불일치
- 신경망은 고도로 비선형적(Non-linear)입니다.
- 가중치 $\theta$가 아주 미세하게 $0.001$만 바뀌어도, 출력층의 Softmax 함수를 통과하면서 특정 상태에서의 행동 확률이 $99\%$에서 $1\%$로 곤두박질칠 수 있습니다.
- 반대로 가중치가 $10.0$만큼 크게 변해도 확률분포는 거의 변하지 않을 수도 있습니다.
- 따라서 **파라미터 공간의 유클리드 거리($\Delta \theta$)를 기준으로 학습률을 제어하는 것은 확률분포의 변화를 전혀 보장하지 못합니다.**

### 2) 데이터 수집 분포의 파괴적 순환
$$
\text{나쁜 갱신}(\Delta \theta \text{ 과대}) \;\longrightarrow\; \text{파괴된 정책 } \pi_{\text{new}} \;\longrightarrow\; \text{질 낮은 탐색 데이터 } \tau \sim \pi_{\text{new}} \;\longrightarrow\; \text{완전한 학습 불능 (Collapse)}
$$

---

## 16.1.2 보수적 정책 개선 (Conservative Policy Iteration, CPI)

카크마데와 랭포드(Kakade & Langford, 2002)는 정책의 변화를 안전하게 제한하면서 매 스텝 성능이 단조 증가(Monotonic Improvement)함을 보장하는 **보수적 정책 개선(CPI)** 이론을 발표했습니다:

새로운 탐욕 정책 $\pi'$를 곧바로 전면 채택하는 대신, 이전 정책 $\pi_{\text{old}}$와 소량 혼합(Mixture)하는 것입니다:

$$
\pi_{\text{new}}(a \mid s) = (1 - \alpha) \pi_{\text{old}}(a \mid s) + \alpha \pi'(a \mid s) \quad (\alpha \in [0, 1])
$$

[식 16.2] CPI의 정책 혼합 업데이트

이 방식을 사용하면 성능 개선의 하한선(Lower Bound)을 수학적으로 유도할 수 있습니다:

$$
J(\pi_{\text{new}}) \ge J(\pi_{\text{old}}) + \frac{\alpha}{1-\gamma} \left( \mathbb{E}_{s \sim d^{\pi_{\text{old}}}, a \sim \pi'} [A^{\pi_{\text{old}}}(s, a)] - \frac{2\alpha \gamma \epsilon}{(1-\gamma)(1-\alpha\gamma)} \right)
$$

[식 16.3] CPI의 단조 개선 하한 정리 ($\epsilon = \max_s |\mathbb{E}_a [A(s, a)]|$)

이 하한선은 $\alpha$를 충분히 작게 유지한다면, **새 정책의 기대 수익이 이전 정책보다 절대로 떨어지지 않음($J(\pi_{\text{new}}) \ge J(\pi_{\text{old}})$)**을 최초로 증명한 역사적 정리입니다!

---

## 16.1.3 자연 정책 경사 (Natural Policy Gradient, NPG)

샴 카크마데(Sham Kakade, 2001)는 파라미터 공간의 단순 유클리드 기하학 대신, **확률분포 공간의 리만 기하학(Riemannian Manifold)**을 고려하는 **자연 정책 경사(Natural Policy Gradient)**를 제안했습니다:

$$
\Delta \theta = F^{-1} \nabla_\theta J(\theta)
$$

[식 16.4] 자연 정책 경사의 파라미터 갱신

여기서 **$F$는 피셔 정보 행렬(Fisher Information Matrix, FIM)**입니다:

$$
F(\theta) = \mathbb{E}_{s \sim d^\pi, a \sim \pi_\theta} \left[ \nabla_\theta \log \pi_\theta(a \mid s) \, \nabla_\theta \log \pi_\theta(a \mid s)^T \right]
$$

[식 16.5] 피셔 정보 행렬의 정의

- 피셔 정보 행렬은 확률분포 공간에서의 곡률(Curvature)과 거리를 측정하는 척도입니다.
- 가중치가 조금만 바뀌어도 확률분포가 급변하는 민감한 축에 대해서는 보폭을 자동으로 줄여주고, 확률분포가 둔감한 축에 대해서는 보폭을 넓혀주어 **항상 일정한 확률분포 거리($D_{\text{KL}}$)를 유지하며 갱신**합니다.

하지만 현대 심층 신경망에서는 파라미터 수 $N$이 수만~수백만 개에 달하므로, $N \times N$ 크기의 거대한 피셔 행렬 $F$의 역행렬($F^{-1}$)을 직접 구하는 것은 연산량 $\mathcal{O}(N^3)$과 메모리 면에서 불가능했습니다. 
이 거대한 계산 장벽을 극복하기 위해 등장한 것이 바로 다음 절에서 배울 **TRPO (Trust Region Policy Optimization)**입니다!
