---
layout: docs
title: "11.2 선형 회귀: 데이터로부터 패턴을 배우는 첫걸음"
---

# 11.2 선형 회귀: 데이터로부터 패턴을 배우는 첫걸음

머신러닝의 주춧돌이자 수많은 인공지능 예측의 뿌리가 되는 **선형 회귀(Linear Regression)** 이론을 공부합니다. 

![선형 회귀 인트로](./img/jiny_ch11_2_linear_regression.png)
**그림 11-2-1** 칠판 위에 흩뿌려진 빨간색 경험 데이터 점들을 관통하는 완벽한 예측 직선을 요술 지팡이로 그려보이는 지니와 도로시

---

연속적인 데이터 점들의 분포를 가장 정확하게 설명해 주는 1차 함수 직선 수식(*y* = *Wx* + *b*)의 **평균 제곱 오차(MSE)** 손실을 정의하고, 경사 하강법(Gradient Descent)을 통해 최적의 파라미터를 찾아가는 과정을 깊이 있게 배워봅시다!

![선형 회귀와 MSE 최적화](./img/02_linear_regression_fitting_flow.jpg)
**그림 11-2-2** 흩어진 100개의 관측 데이터 점들의 중심을 관통하는 최적의 직선 *y* = *Wx* + *b*를 정렬하는 도로시와, 평균 제곱 오차(MSE) 손실이 0에 가깝게 감소하는 과정을 기록하는 지니, 그리고 경사 하강법에 의한 가중치/편향 갱신 원리를 설명하는 이호진 교수님



---

## 11.2.1 머신러닝의 본질과 토이 데이터셋

전통적인 프로그래밍에서는 사람이 직접 규칙(알고리즘)을 작성하여 컴퓨터에 입력했습니다. 

![전통적인 프로그래밍과 머신러닝의 차이](./img/ch11_2_01_traditional_programming_rules.png)

---

하지만 **머신러닝(Machine Learning)**은 접근 방식이 정반대입니다:
- 사람은 모델의 기본 뼈대(함수)만 세워두고,
- 컴퓨터가 수집된 **데이터(Data)**를 스스로 관찰하며 가중치를 조절해 최적의 규칙을 찾아냅니다.

![데이터로부터 스스로 규칙을 학습하는 머신러닝](./img/ch11_2_02_machine_learning_learning_from_data.png)

---

### 실험용 토이 데이터셋(Toy Dataset) 생성

간단한 1차원 선형 관계에 노이즈가 섞인 100개의 데이터셋을 넘파이로 만들어 봅시다:

```python
import numpy as np

np.random.seed(0) # 결과 재현을 위한 난수 시드 고정
x = np.random.rand(100, 1)                      # 0~1 사이의 100개 입력 데이터
y = 5 + 2 * x + np.random.rand(100, 1)          # 기울기 2, 절편 5에 노이즈를 더한 참값
```

---



![그림 11-5](./img/fig_8_5.jpg)
**그림 11-2-3** 노이즈가 포함된 100개의 2차원 토이 데이터셋 산점도

참된 수식은 대략 *y* = 2*x* + 5.5 부근입니다. 



---



우리는 이 정답 수식을 모른다고 가정하고, 오직 점들의 좌표 (*x*, *y*)만을 컴퓨터에 건네주어 최적의 직선을 스스로 찾아내도록 만들어야 합니다.

![노이즈가 섞인 2차원 산점도 데이터의 수수께끼](./img/ch11_2_03_noisy_scatter_data_mystery.png)

---

## 11.2.2 선형 회귀와 손실 함수(MSE)의 수학적 원리

입력 *x*로부터 실수 출력 *y*를 예측하는 문제를 **회귀(Regression)**라고 부릅니다. 

![연속적인 수치를 예측하는 회귀의 개념](./img/ch11_2_04_regression_concept_continuous_prediction.png)

---

이때 가장 단순한 가설로 **직선 모델**을 세우는 것이 **선형 회귀(Linear Regression)**입니다:

> ***y* = *W* · *x* + *b***

- ***W* (가중치, Weight)**: 직선의 기울기를 결정합니다.
- ***b* (편향, Bias)**: 직선의 *y*절편(위아래 높낮이)을 결정합니다.

![직선의 기울기와 절편을 결정하는 가중치와 편향](./img/ch11_2_05_linear_equation_slope_intercept.png)

---

![그림 11-6](./img/fig_8_6.jpg)
**그림 11-2-4** 실제 데이터 점들과 예측 직선 사이의 수직 거리 차이인 잔차(Residual)

---

### 모델의 성적표: 평균 제곱 오차 (MSE: Mean Squared Error)

어떤 직선이 데이터에 "가장 잘 들어맞는가"를 수치로 평가하려면 오차를 측정해야 합니다.

![데이터에 가장 잘 들어맞는 직선의 적합도 평가](./img/ch11_2_06_evaluating_model_fitness.png)

---

 실제 정답 *y*<sub>*i*</sub>와 모델의 예측값 (*Wx*<sub>*i*</sub> + *b*) 사이의 거리를 **잔차(Residual)**라고 합니다.

![실제값과 모델 예측값 사이의 수직 거리인 잔차](./img/ch11_2_07_residual_vertical_distance.png)

---

이 잔차들을 제곱하여 평균을 낸 것이 **평균 제곱 오차(MSE)** 손실 함수입니다:

> ***L* = (1 / *N*) · ∑<sub>*i*=1</sub><sup>*N*</sup> (*W* · *x*<sub>*i*</sub> + *b* - *y*<sub>*i*</sub>)<sup>2</sup>** &nbsp;&nbsp;&nbsp;&nbsp; *(식 11.3: 평균 제곱 오차, MSE)*

![잔차의 제곱 면적으로 계산하는 평균 제곱 오차](./img/ch11_2_08_mse_loss_formula_squared_boxes.png)

---

#### 💡 왜 잔차를 제곱(Square)해서 더할까요?
1. **부호 상쇄 방지**: 오차가 +3인 점과 -3인 점을 단순 합산하면 오차가 0이 되어 완벽한 모델로 착각하는 치명적인 오류를 막습니다.
2. **큰 오차에 대한 강력한 페널티**: 오차가 2배 커지면 손실은 4배로 폭발하므로, 극단적으로 빗나간 이상치를 강력하게 교정합니다.
3. **부드러운 미분 가능성**: 절댓값 함수와 달리 2차 포물선 형태이므로 모든 지점에서 매끄러운 미분(기울기)이 보장되어 경사 하강법에 가장 이상적입니다.

![오차를 제곱하는 세 가지 수학적 이유](./img/ch11_2_09_why_square_three_reasons.png)



---

우리의 목표는 이 손실 함수 $L$ 을 최소화하는 최적의 가중치 $W^*$ 와 편향 $b^*$ 를 경사 하강법으로 찾아내는 것입니다.

![손실 함수를 최소화하는 최적화 목표](./img/ch11_2_10_optimization_goal_minimizing_loss.png)

---

## 11.2.3 배치 행렬 연산과 차원 형상(Shape)

100개의 데이터를 `for`문으로 하나씩 계산하면 속도가 매우 느립니다. 

![느린 반복문과 빠른 배치 행렬 연산의 비교](./img/ch11_2_11_slow_loop_vs_fast_batch.png)

---

딥러닝에서는 **행렬 곱(Matrix Multiplication)**을 이용해 100개의 데이터를 한 방에 일괄 처리(Batch Processing)합니다.

![그림 11-8](./img/fig_8_8.jpg)
**그림 11-2-5** 행렬 곱 연산에서의 차원 형상 변환 (*N* × *D*) × (*D* × 1) = (*N* × 1)

---

- 데이터 행렬 **x**: (100, 1) 형상 (100개의 행, 1개의 특성)
- 가중치 행렬 **W**: (1, 1) 형상
- 편향 벡터 **b**: (1,) 형상 (브로드캐스팅에 의해 100개의 행에 자동으로 더해짐)

이 행렬 곱 `F.matmul(x, W) + b` 한 줄로 100개 데이터의 예측값 벡터 `y_pred` (100, 1)이 즉시 계산됩니다.

![행렬 곱과 브로드캐스팅을 통한 일괄 연산 파이프라인](./img/ch11_2_12_matrix_multiplication_batch_pipeline.png)

---

## 11.2.4 DeZero로 구현하는 선형 회귀

이제 DeZero 프레임워크를 사용하여 데이터 생성부터 경사 하강 학습까지 전체 파이프라인을 완성해 봅시다.

![DeZero로 구축하는 선형 회귀 학습 파이프라인](./img/ch11_2_13_dezero_linear_regression_pipeline.png)

---

<div align="right"><b>ch07/dezero3.py</b></div>

```python
import numpy as np
from dezero import Variable
import dezero.functions as F

# 1. 토이 데이터셋 생성
np.random.seed(0)
x = np.random.rand(100, 1)
y = 5 + 2 * x + np.random.rand(100, 1)

# 2. 학습할 매개변수 W와 b를 Variable로 선언 (초깃값 0.0)
W = Variable(np.zeros((1, 1)))
b = Variable(np.zeros(1))

# 3. 선형 모델 예측 함수 정의
def predict(x):
    return F.matmul(x, W) + b

# 4. 평균 제곱 오차(MSE) 손실 함수 정의
def mean_squared_error(y_true, y_pred):
    diff = y_true - y_pred
    return F.sum(diff ** 2) / len(diff)

# 5. 경사 하강법 학습 루프
lr = 0.1          # 학습률
iters = 100       # 에포크 횟수

for i in range(iters):
    # 순전파: 예측값 및 손실 계산
    y_pred = predict(x)
    loss = mean_squared_error(y, y_pred)

    # 역전파 전 기울기 초기화
    W.cleargrad()
    b.cleargrad()

    # 역전파: dLoss/dW와 dLoss/db 자동 계산
    loss.backward()

    # 파라미터 경사 하강 갱신
    W.data -= lr * W.grad.data
    b.data -= lr * b.grad.data

    if i % 10 == 0:
        print(f"에포크 {i:02d} | 손실(MSE): {loss.data:.4f}")

print("=" * 30)
print("최종 학습된 W:", W.data)
print("최종 학습된 b:", b.data)
```

---

**학습 진행 로그**:

```text
에포크 00 | 손실(MSE): 42.2963
에포크 10 | 손실(MSE): 0.2492
에포크 20 | 손실(MSE): 0.1008
에포크 30 | 손실(MSE): 0.0946
에포크 40 | 손실(MSE): 0.0903
에포크 50 | 손실(MSE): 0.0869
에포크 60 | 손실(MSE): 0.0844
에포크 70 | 손실(MSE): 0.0825
에포크 80 | 손실(MSE): 0.0810
에포크 90 | 손실(MSE): 0.0799
==============================
최종 학습된 W: [[2.11807369]]
최종 학습된 b: [5.46608905]
```



---



![그림 11-9](./img/fig_8_9.jpg)
**그림 11-2-6** 100회 경사 하강 갱신 후 도출된 최종 예측 직선 *y* = 2.118*x* + 5.466. 노이즈 낀 데이터 점들의 중심을 자로 잰 듯 완벽하게 관통합니다.

---

초기 손실 42.29에서 단 10회 만에 0.24로 급락하며 최종적으로 **0.0799**까지 수렴했습니다. 
도출된 가중치 **$W = 2.118$** 과 편향 **$b = 5.466$** 은 우리가 처음에 노이즈를 섞어 만든 참 모델(기울기 2.0, 절편 5.5)과 거의 완벽하게 일치합니다!

![손실이 수렴하고 최적 직선을 찾아낸 기쁨](./img/ch11_2_14_perfect_convergence_celebration.png)

---

## 11.2.5 선형 회귀에서 강화학습으로 이어지는 실마리

선형 회귀에서 배운 이 단순한 루프는 **딥 강화학습(DQN)**의 학습 메커니즘과 본질적으로 같습니다:

![선형 회귀에서 딥 강화학습으로 이어지는 실마리](./img/ch11_2_15_linear_regression_to_rl_bridge.png)

---



1. **상태 입력**: 환경의 상태 *S*가 입력 *x*로 주어집니다.

![강화학습 1단계: 환경의 상태 입력](./img/ch11_2_16_rl_step1_state_input.png)

---



2. **Q 예측**: 신경망 모델이 각 행동의 Q값을 예측합니다 (`Q_pred = predict(state)`).

![강화학습 2단계: 신경망의 행동 가치 Q 예측](./img/ch11_2_17_rl_step2_q_prediction.png)



---



3. **TD 타깃 정답**: 환경에서 받은 즉각 보상과 다음 상태 최댓값으로 정답 레이블을 만듭니다 (`target = R + γ max Q(S', a')`).



![강화학습 3단계: 벨만 방정식을 통한 TD 타깃 정답 생성](./img/ch11_2_18_rl_step3_td_target_creation.png)

---



4. **MSE 손실 역전파**: 예측 Q값과 타깃 사이의 MSE 손실을 구하고 `loss.backward()`로 신경망 가중치를 업데이트합니다!

![강화학습 4단계: MSE 손실 역전파를 통한 신경망 파라미터 갱신](./img/ch11_2_19_rl_step4_mse_loss_backprop.png)

---



하지만 현실 세계의 복잡한 물리 법칙과 게임 전략은 직선 하나만으로는 결코 표현할 수 없습니다. 

![복잡한 곡선 데이터를 표현하지 못하는 단일 직선의 한계](./img/ch11_2_20_limitation_single_straight_line.png)



---

곡선과 꺾은선, 복잡한 비선형 관계를 자유자재로 그려내기 위해, 다음 절에서는 **활성화 함수(Activation Function)**를 탑재한 진짜 **인공신경망(Neural Network)**으로 진화해 봅시다!

![비선형 활성화 함수를 통한 다층 신경망으로의 진화](./img/ch11_2_21_evolution_to_nonlinear_neural_nets.png)
