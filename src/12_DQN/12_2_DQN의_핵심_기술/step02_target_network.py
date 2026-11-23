"""
[실습 2단계] 목표 신경망(Target Network) 및 핵심 텐서 연산 검증
============================================================
1. deepcopy()를 통한 쌍둥이 신경망 가중치 동기화 (id 메모리 주소 비교)
2. 팬시 인덱싱 qs[np.arange(batch_size), action] 연산 검증
3. (1 - done) 마스킹을 통한 TD 목표(Target) 계산 메커니즘 검증
"""

import copy
import numpy as np


class SimpleQNet:
    """원리 검증용 2층 MLP Q-네트워크 가중치 컨테이너"""
    def __init__(self, state_dim=4, hidden_dim=8, action_dim=2):
        self.w1 = np.random.randn(state_dim, hidden_dim) * 0.1
        self.b1 = np.zeros(hidden_dim)
        self.w2 = np.random.randn(hidden_dim, action_dim) * 0.1
        self.b2 = np.zeros(action_dim)

    def forward(self, x):
        """순전파: ReLU 활성화 함수 적용"""
        h = np.maximum(0, np.dot(x, self.w1) + self.b1)
        qs = np.dot(h, self.w2) + self.b2
        return qs


if __name__ == '__main__':
    print("=" * 65)
    print(" [실습 2단계] 목표 신경망(Target Network) 핵심 메커니즘 검증")
    print("=" * 65)

    # -------------------------------------------------------------
    # 1. 쌍둥이 신경망 생성 및 copy.deepcopy() 검증
    # -------------------------------------------------------------
    print("\n[검증 1] 원본 신경망(qnet)과 목표 신경망(qnet_target) 분리 및 동기화")
    print("-" * 65)

    qnet = SimpleQNet(state_dim=4, hidden_dim=8, action_dim=2)
    qnet_target = copy.deepcopy(qnet)  # 깊은 복사 (완전한 독립 복제)
    qnet_shallow = copy.copy(qnet)      # 얕은 복사 (위험: 주소 공유)

    print(f"  * 원본 qnet.w1         메모리 ID: {id(qnet.w1)}")
    print(f"  * 깊은 복사 target.w1  메모리 ID: {id(qnet_target.w1)} -> 독립된 메모리 공간! (안전)")
    print(f"  * 얕은 복사 shallow.w1 메모리 ID: {id(qnet_shallow.w1)} -> 원본과 동일한 주소! (위험 버그)")

    # 원본 가중치를 수정했을 때 deepcopy는 영향받지 않음을 증명
    qnet.w1 += 10.0
    diff_target = np.max(np.abs(qnet.w1 - qnet_target.w1))
    diff_shallow = np.max(np.abs(qnet.w1 - qnet_shallow.w1))

    print(f"  >>> qnet 가중치 갱신 후 target과의 최대 오차 : {diff_target:.4f} (target은 얼려져 불변)")
    print(f"  >>> qnet 가중치 갱신 후 shallow와의 최대 오차: {diff_shallow:.4f} (얕은 복사는 함께 오염됨)")

    # -------------------------------------------------------------
    # 2. 팬시 인덱싱 qs[np.arange(batch_size), action] 검증
    # -------------------------------------------------------------
    print("\n" + "-" * 65)
    print("[검증 2] 팬시 인덱싱 qs[np.arange(batch_size), action] 추출 연산")
    print("-" * 65)

    batch_size = 5
    # 모의 예측 Q값 행렬 (5개 샘플 x 2개 행동 [Q(s, 0), Q(s, 1)])
    mock_qs = np.array([
        [0.12, 0.85],  # 샘플 0: 행동 1 선택
        [0.91, 0.23],  # 샘플 1: 행동 0 선택
        [0.45, 0.78],  # 샘플 2: 행동 1 선택
        [0.63, 0.31],  # 샘플 3: 행동 0 선택
        [0.29, 0.94],  # 샘플 4: 행동 1 선택
    ])
    mock_actions = np.array([1, 0, 1, 0, 1])

    # 넘파이 팬시 인덱싱으로 실제 선택된 행동의 Q값만 추출
    selected_q = mock_qs[np.arange(batch_size), mock_actions]

    print(f"  * 신경망 예측 Q값 전체 행렬 (qs, shape {mock_qs.shape}):\n{mock_qs}")
    print(f"  * 에이전트가 수행한 행동 벡터 (action): {mock_actions}")
    print(f"  * 팬시 인덱싱으로 추출된 Q(s, a) (shape {selected_q.shape}): {selected_q}")
    print("  >>> 샘플별로 선택된 열의 값 [0.85, 0.91, 0.78, 0.63, 0.94]이 정확히 1차원으로 추출됨!")

    # -------------------------------------------------------------
    # 3. (1 - done) 마스킹과 벨만 TD 목표 계산 검증
    # -------------------------------------------------------------
    print("\n" + "-" * 65)
    print("[검증 3] (1 - done) 마스킹을 통한 벨만 TD 목표(Target) 연산")
    print("-" * 65)

    gamma = 0.98
    rewards = np.array([1.0, 1.0, 1.0, 1.0, 1.0])
    dones = np.array([0, 0, 1, 0, 1])  # 2번, 4번 샘플은 종료(done=1)

    # 목표 신경망의 차기 상태 Q값 최댓값
    mock_next_qs = np.array([
        [0.50, 0.80],  # max = 0.80
        [0.40, 0.60],  # max = 0.60
        [0.95, 0.70],  # max = 0.95 (하지만 종료 상태!)
        [0.30, 0.85],  # max = 0.85
        [0.88, 0.45],  # max = 0.88 (하지만 종료 상태!)
    ])
    next_q_max = mock_next_qs.max(axis=1)

    # TD 목표 계산 공식: target = R + (1 - done) * gamma * max Q_target
    td_targets = rewards + (1 - dones) * gamma * next_q_max

    for i in range(batch_size):
        done_str = "종료(Terminated) -> 미래 가치 0 차단!" if dones[i] == 1 else "진행 중 -> 부트스트랩 미래 가치 반영"
        print(f"  샘플 {i}: 보상 {rewards[i]:.1f} + (1 - {dones[i]}) * {gamma} * {next_q_max[i]:.2f} = {td_targets[i]:.4f} ({done_str})")

    print("=" * 65)
    print(">>> 목표 신경망 및 텐서 연산 3대 핵심 메커니즘 검증 성공!\n")
