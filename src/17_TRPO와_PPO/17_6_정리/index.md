---
layout: docs
title: "16.6 정리 및 요약: 신뢰 구역에서 PPO 클리핑까지"
---

# 16.6 정리 및 요약: 신뢰 구역에서 PPO 클리핑까지

![16.6 정리 및 요약](./17_6_정리.png)
**그림 16-6** 'PPO Master' 훈장을 수여받은 도로시와 축하의 박수를 보내는 이호진 교수님, 그리고 학사모를 쓴 지니와 토토

---

## 16.6.1 16장에서 배운 핵심 원리 총정리

1. **정책 붕괴(Policy Collapse)와 스텝 크기 딜레마**:
   - 강화학습에서는 정책 $\pi_\theta$ 자체가 데이터를 수집하는 탐색기이므로, 한 번의 과도한 가중치 갱신이 정책을 파괴하면 회복이 불가능합니다.
   - 파라미터 유클리드 공간($\|\Delta \theta\|$)과 실제 행동 확률분포 공간($D_{\text{KL}}$) 간의 불일치를 극복해야 합니다.

2. **CPI와 자연 정책 경사(NPG)**:
   - **CPI**: 정책 혼합 업데이트를 통해 단조 개선 하한 정리 증명.
   - **NPG**: 피셔 정보 행렬 $F(\theta)$를 도입하여 확률분포 공간의 곡률을 보정한 갱신($\Delta \theta = F^{-1} g$) 실현.

3. **TRPO (Trust Region Policy Optimization)**:
   - 이전 정책과의 평균 KL 발산을 임계치 $\delta$ 이하로 제한하는 **명시적 신뢰 구역 제약 조건(Hard Trust Region Constraint)** 도입.
   - 테일러 2차 전개, 켤레 기울기법(Conjugate Gradient), 백트래킹 라인 서치를 통해 단조 개선을 공학적으로 구현.

4. **PPO (Proximal Policy Optimization)**:
   - 복잡한 2차 최적화 대신, 확률 비율 $r_t(\theta) = \frac{\pi_\theta(a|s)}{\pi_{\theta_{\text{old}}}(a|s)}$를 **$[1-\epsilon, 1+\epsilon]$ 구간으로 클리핑하는 1차 목적 함수(PPO-Clip)** 제안.
   - $\min$ 연산을 통해 비관적 하한선(Pessimistic Bound)을 형성하여 정책의 돌발적 폭주를 방지.
   - **GAE(Generalized Advantage Estimation)**를 통해 편향과 분산의 이상적 균형 확보.

---

## 16.6.2 핵심 공식 요약표

| 알고리즘 | 목적 함수 및 핵심 공식 | 제약 조건 및 특징 |
| :--- | :--- | :--- |
| **TRPO** | $\max_\theta \mathbb{E} \left[ \frac{\pi_\theta(a \mid s)}{\pi_{\theta_{\text{old}}}(a \mid s)} A(s, a) \right]$ | **제약**: $\mathbb{E}[D_{\text{KL}}(\pi_{\text{old}} \parallel \pi)] \le \delta$<br>2차 피셔 행렬, 켤레 기울기법 |
| **PPO-Clip** | $\max_\theta \hat{\mathbb{E}}_t \left[ \min\left( r_t(\theta)\hat{A}_t, \; \text{clip}(r_t(\theta), 1-\epsilon, 1+\epsilon)\hat{A}_t \right) \right]$ | **제약 없음 (비관적 클리핑)**<br>표준 Adam 1차 최적화 가능 |
| **GAE** | $\hat{A}_t^{\text{GAE}(\gamma, \lambda)} = \sum_{l=0}^\infty (\gamma \lambda)^l \delta_{t+l}^V$ | $\lambda=0$ (1스텝 TD) $\sim \lambda=1$ (MC) 보간 |

---

## 16.6.3 확인 퀴즈 (Quiz)

**Q1. TRPO에서 2차 최적화를 위해 피셔 정보 행렬(Fisher Information Matrix)의 역행렬을 계산해야 할 때, 계산 복잡도 $\mathcal{O}(N^3)$의 직접 계산을 피하기 위해 사용하는 수치해석 기법은 무엇인가요?**
- **정답**: **켤레 기울기법 (Conjugate Gradient Method)**
- **해설**: 피셔 행렬을 메모리에 통째로 올리거나 역행렬을 직접 구하지 않고, 몇 번의 행렬-벡터 곱($Hv$) 연산만으로 선형 연립방정식 $Hx = g$의 근사해를 빠르게 찾아냅니다.

**Q2. PPO-Clip 목적 함수에서 $\min(r_t \hat{A}_t, \text{clip}(r_t, 1-\epsilon, 1+\epsilon)\hat{A}_t)$ 수식이 어드밴티지 $\hat{A}_t > 0$일 때 수행하는 역할은 무엇인가요?**
- **정답**: 확률 비율 $r_t(\theta)$가 $1+\epsilon$보다 커질 경우 기울기를 0으로 만들어, **정책이 한 번에 너무 큰 폭으로 개선되는 것을 제한(클리핑)**합니다.

---

## 16.6.4 다음 장(Chapter 17)으로의 도약

이제 우리는 심층 강화학습의 최강자 PPO를 완전히 손에 넣었습니다! 그렇다면 이 강력한 알고리즘은 게임과 로봇에만 쓰일까요?
**놀랍게도 2022년 전 세계를 뒤흔든 생성형 AI 혁명(ChatGPT, GPT-4, Claude)의 심장부에 바로 이 PPO가 자리 잡고 있습니다.**

다음 17장에서는 대형언어모델(LLM)이 인간의 윤리와 지시를 완벽히 따르도록 훈련시키는 핵심 기술인 **RLHF(인간 피드백 기반 강화학습)**와 보상 모델링(Reward Modeling), 그리고 최근 각광받는 **DPO(Direct Preference Optimization)** 및 **GRPO(Group Relative Policy Optimization)**의 최첨단 정렬 세계로 나아갑니다!
