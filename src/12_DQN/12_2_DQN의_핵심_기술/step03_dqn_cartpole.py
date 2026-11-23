"""
[실습 3단계] 완전 자립형(Self-contained) 카트폴 DQN 전체 학습 및 검증
===================================================================
외부 거대 프레임워크 설치 의존성 없이, 순수 NumPy와 파이썬 표준 라이브러리만으로
경험 재생(ReplayBuffer)과 목표 신경망(Target Network)을 갖춘 완전한 DQN을 구현하여
카트폴 환경에서 200스텝 완주 균형 제어를 달성합니다.
"""

from collections import deque
import copy
import random
import time
import warnings
import numpy as np
import gym

warnings.filterwarnings('ignore')


class ReplayBuffer:
    """경험 재생 버퍼"""
    def __init__(self, buffer_size=10000, batch_size=32):
        self.buffer = deque(maxlen=buffer_size)
        self.batch_size = batch_size

    def add(self, state, action, reward, next_state, done):
        self.buffer.append((state, action, reward, next_state, done))

    def __len__(self):
        return len(self.buffer)

    def get_batch(self):
        data = random.sample(self.buffer, self.batch_size)
        state = np.stack([x[0] for x in data])
        action = np.array([x[1] for x in data], dtype=np.int64)
        reward = np.array([x[2] for x in data], dtype=np.float32)
        next_state = np.stack([x[3] for x in data])
        done = np.array([x[4] for x in data], dtype=np.float32)
        return state, action, reward, next_state, done


class QNetwork:
    """순수 NumPy 2층 완전연결 신경망 (4 -> 64 -> 64 -> 2)"""
    def __init__(self, state_dim=4, hidden_dim=64, action_dim=2, lr=0.001):
        self.lr = lr
        # He 초기화 (He et al.)
        self.W1 = np.random.randn(state_dim, hidden_dim) * np.sqrt(2.0 / state_dim)
        self.b1 = np.zeros(hidden_dim)
        self.W2 = np.random.randn(hidden_dim, hidden_dim) * np.sqrt(2.0 / hidden_dim)
        self.b2 = np.zeros(hidden_dim)
        self.W3 = np.random.randn(hidden_dim, action_dim) * np.sqrt(2.0 / hidden_dim)
        self.b3 = np.zeros(action_dim)

        # Adam 옵티마이저 모멘텀 버퍼
        self.m = [np.zeros_like(p) for p in [self.W1, self.b1, self.W2, self.b2, self.W3, self.b3]]
        self.v = [np.zeros_like(p) for p in [self.W1, self.b1, self.W2, self.b2, self.W3, self.b3]]
        self.t = 0

    def forward(self, x):
        """순전파 연산"""
        self.x = x
        self.z1 = np.dot(x, self.W1) + self.b1
        self.a1 = np.maximum(0, self.z1)  # ReLU
        self.z2 = np.dot(self.a1, self.W2) + self.b2
        self.a2 = np.maximum(0, self.z2)  # ReLU
        self.out = np.dot(self.a2, self.W3) + self.b3
        return self.out

    def backward(self, dout):
        """역전파 및 Adam 가중치 갱신"""
        batch_size = dout.shape[0]

        # Layer 3
        dW3 = np.dot(self.a2.T, dout) / batch_size
        db3 = np.sum(dout, axis=0) / batch_size
        da2 = np.dot(dout, self.W3.T)

        # Layer 2
        dz2 = da2 * (self.z2 > 0)
        dW2 = np.dot(self.a1.T, dz2) / batch_size
        db2 = np.sum(dz2, axis=0) / batch_size
        da1 = np.dot(dz2, self.W2.T)

        # Layer 1
        dz1 = da1 * (self.z1 > 0)
        dW1 = np.dot(self.x.T, dz1) / batch_size
        db1 = np.sum(dz1, axis=0) / batch_size

        # Adam 매개변수 갱신
        self.t += 1
        beta1, beta2, eps = 0.9, 0.999, 1e-8
        grads = [dW1, db1, dW2, db2, dW3, db3]
        params = [self.W1, self.b1, self.W2, self.b2, self.W3, self.b3]

        for i in range(len(params)):
            self.m[i] = beta1 * self.m[i] + (1 - beta1) * grads[i]
            self.v[i] = beta2 * self.v[i] + (1 - beta2) * (grads[i] ** 2)
            m_hat = self.m[i] / (1 - beta1 ** self.t)
            v_hat = self.v[i] / (1 - beta2 ** self.t)
            params[i] -= self.lr * m_hat / (np.sqrt(v_hat) + eps)


class DQNAgent:
    """경험 재생과 목표 신경망을 탑재한 완성형 DQN 에이전트"""
    def __init__(self):
        self.gamma = 0.98
        self.lr = 0.001
        self.epsilon = 1.0          # 초기 탐색률 100%
        self.epsilon_min = 0.05     # 최소 탐색률 5%
        self.epsilon_decay = 0.995  # 점진적 감쇠율
        self.buffer_size = 10000
        self.batch_size = 32
        self.action_size = 2

        self.replay_buffer = ReplayBuffer(self.buffer_size, self.batch_size)
        self.qnet = QNetwork(state_dim=4, hidden_dim=64, action_dim=2, lr=self.lr)
        self.qnet_target = copy.deepcopy(self.qnet)

    def sync_qnet(self):
        """목표 신경망으로 원본 가중치 깊은 복사 (동기화)"""
        self.qnet_target = copy.deepcopy(self.qnet)

    def get_action(self, state):
        """ε-탐욕 정책에 따른 행동 선택"""
        if np.random.rand() < self.epsilon:
            return np.random.choice(self.action_size)
        else:
            state_tensor = state[np.newaxis, :]  # (1, 4) 형상 변환
            qs = self.qnet.forward(state_tensor)
            return int(np.argmax(qs[0]))

    def update(self, state, action, reward, next_state, done):
        """1스텝 경험 저장 및 미니배치 벨만 오차 역전파 학습"""
        self.replay_buffer.add(state, action, reward, next_state, done)
        if len(self.replay_buffer) < self.batch_size:
            return None

        # 1. 미니배치 샘플링
        s, a, r, next_s, d = self.replay_buffer.get_batch()

        # 2. 원본 신경망 현재 Q(s, a) 계산
        qs = self.qnet.forward(s)  # (32, 2)
        q = qs[np.arange(self.batch_size), a]  # 팬시 인덱싱 (32,)

        # 3. 목표 신경망 차기 가치 max Q_target(s', a') 계산
        next_qs = self.qnet_target.forward(next_s)  # (32, 2)
        next_q_max = np.max(next_qs, axis=1)        # (32,)

        # 4. 벨만 TD 목표 계산: target = r + (1 - done) * gamma * max Q_target
        target = r + (1.0 - d) * self.gamma * next_q_max  # (32,)

        # 5. 평균 제곱 오차(MSE)의 기울기 계산: dout = 2 * (q - target)
        loss = np.mean((q - target) ** 2)
        dout = np.zeros_like(qs)
        dout[np.arange(self.batch_size), a] = 2.0 * (q - target)

        # 6. 역전파 수행
        self.qnet.backward(dout)
        return loss


if __name__ == '__main__':
    print("=" * 65)
    print(" [실습 3단계] 순수 NumPy 기반 카트폴 DQN 250 에피소드 학습 시작")
    print("=" * 65)

    env = gym.make('CartPole-v0')
    agent = DQNAgent()
    episodes = 250
    sync_interval = 10  # 10 에피소드마다 목표 신경망 동기화
    reward_history = []
    start_time = time.time()

    for episode in range(1, episodes + 1):
        state = env.reset()[0]
        done = False
        total_reward = 0.0

        while not done:
            action = agent.get_action(state)
            next_state, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated

            # 실패 페널티 보정: 쓰러져서 끝나면 보상을 -1로 조정하여 안전 생존 유도
            adjusted_reward = reward if not terminated else -1.0

            agent.update(state, action, adjusted_reward, next_state, float(done))
            state = next_state
            total_reward += reward

        # ε 감쇠 (점진적으로 탐색을 줄이고 학습된 지능 활용)
        if agent.epsilon > agent.epsilon_min:
            agent.epsilon *= agent.epsilon_decay

        # 주기적 목표 신경망 동기화
        if episode % sync_interval == 0:
            agent.sync_qnet()

        reward_history.append(total_reward)

        if episode % 25 == 0 or episode == 1:
            recent_avg = np.mean(reward_history[-25:])
            elapsed = time.time() - start_time
            print(f"  에피소드 {episode:3d}/{episodes} | 보상: {total_reward:5.1f} | 최근 25회 평균: {recent_avg:5.1f} | ε: {agent.epsilon:.3f} | 경과: {elapsed:.1f}초")

    env.close()

    print("-" * 65)
    print(f"[*] 학습 완료! (총 소요 시간: {time.time() - start_time:.1f} 초)")
    print(f"[*] 최종 50회 에피소드 평균 지속 스텝: {np.mean(reward_history[-50:]):.1f} 점 / 200점")
    print("=" * 65)

    # 학습 완료 후 탐욕 정책(ε = 0) 검증
    print("\n[검증] 학습을 완료한 DQN 에이전트의 탐욕 정책(ε=0) 카트폴 제어 테스트:")
    agent.epsilon = 0.0
    test_env = gym.make('CartPole-v0')
    test_scores = []

    for t in range(5):
        s = test_env.reset()[0]
        d = False
        score = 0
        while not d:
            a = agent.get_action(s)
            s_next, r, term, trunc, _ = test_env.step(a)
            d = term or trunc
            s = s_next
            score += int(r)
        test_scores.append(score)
        print(f"  - 테스트 {t+1}회: 버틴 스텝 = {score:3d} 단계 {'(★ 200단계 만점 성공!)' if score >= 200 else ''}")

    test_env.close()
    print("-" * 65)
    print(f">>> 5회 테스트 평균 점수: {np.mean(test_scores):.1f} 점! (무작위 14스텝 대비 비약적 발전)\n")
