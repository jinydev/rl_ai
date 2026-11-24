"""
[실습 2단계] 순수 NumPy DQN + 역학적 에너지 보상 셰이핑으로 마운틴 카(MountainCar-v0) 정복
======================================================================================
12.2절에서 구현한 경험 재생 버퍼(Replay Buffer)와 목표 신경망(Target Network) 기반
순수 NumPy Double DQN을 마운틴 카(MountainCar-v0)에 적용합니다.

핵심 포인트:
1. 2차원 연속 상태 [위치, 속도]를 [-1, 1] 범위로 정규화하여 신경망 입력
2. 희소 보상(Sparse Reward) 난제를 극복하기 위한 역학적 에너지 퍼텐셜 보상 셰이핑
   -> E(x, v) = 0.5*v^2 + (0.0025/3)*sin(3x) (운동에너지 + 위치에너지)
   -> 뒤로 물러나 반동을 쌓아 언덕을 오르는 진자 추진 전략을 스스로 발견
3. Huber 클리핑 + 소프트 목표 신경망 동기화(Soft Target Update)로 안정적 수렴
4. 학습 완료 후 5회 정량 검증 + 학습 곡선/2D 정책 지도 저장 + 라이브 시각화 시연
"""

from collections import deque
import copy
import os
import random
import time
import warnings
import numpy as np
import gym
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

warnings.filterwarnings('ignore')


class ReplayBuffer:
    """경험 재생 버퍼 (FIFO 순환 큐)"""

    def __init__(self, buffer_size=20000, batch_size=64):
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
    """순수 NumPy 2층 은닉 MLP Q-네트워크 (2 -> 64 -> 64 -> 3) + Adam 옵티마이저"""

    def __init__(self, state_dim=2, hidden_dim=64, action_dim=3, lr=0.0015):
        self.lr = lr
        self.W1 = np.random.randn(state_dim, hidden_dim) * np.sqrt(2.0 / state_dim)
        self.b1 = np.zeros(hidden_dim)
        self.W2 = np.random.randn(hidden_dim, hidden_dim) * np.sqrt(2.0 / hidden_dim)
        self.b2 = np.zeros(hidden_dim)
        self.W3 = np.random.randn(hidden_dim, action_dim) * np.sqrt(2.0 / hidden_dim)
        self.b3 = np.zeros(action_dim)

        self.m = [np.zeros_like(p) for p in self.get_params()]
        self.v = [np.zeros_like(p) for p in self.get_params()]
        self.t = 0

    def get_params(self):
        return [self.W1, self.b1, self.W2, self.b2, self.W3, self.b3]

    def forward(self, x):
        self.x = x
        self.z1 = np.dot(x, self.W1) + self.b1
        self.a1 = np.maximum(0, self.z1)
        self.z2 = np.dot(self.a1, self.W2) + self.b2
        self.a2 = np.maximum(0, self.z2)
        return np.dot(self.a2, self.W3) + self.b3

    def backward(self, dout):
        batch_size = dout.shape[0]

        dW3 = np.dot(self.a2.T, dout) / batch_size
        db3 = np.sum(dout, axis=0) / batch_size
        da2 = np.dot(dout, self.W3.T)

        dz2 = da2 * (self.z2 > 0)
        dW2 = np.dot(self.a1.T, dz2) / batch_size
        db2 = np.sum(dz2, axis=0) / batch_size
        da1 = np.dot(dz2, self.W2.T)

        dz1 = da1 * (self.z1 > 0)
        dW1 = np.dot(self.x.T, dz1) / batch_size
        db1 = np.sum(dz1, axis=0) / batch_size

        self.t += 1
        beta1, beta2, eps = 0.9, 0.999, 1e-8
        grads = [dW1, db1, dW2, db2, dW3, db3]
        params = self.get_params()

        for i in range(len(params)):
            g = np.clip(grads[i], -2.0, 2.0)
            self.m[i] = beta1 * self.m[i] + (1.0 - beta1) * g
            self.v[i] = beta2 * self.v[i] + (1.0 - beta2) * (g ** 2)
            m_hat = self.m[i] / (1.0 - beta1 ** self.t)
            v_hat = self.v[i] / (1.0 - beta2 ** self.t)
            params[i] -= self.lr * m_hat / (np.sqrt(v_hat) + eps)


def normalize_state(state):
    """[위치(-1.2~0.6), 속도(-0.07~0.07)]을 [-1, 1] 구간으로 정규화"""
    pos_norm = (state[0] - (-0.3)) / 0.9
    vel_norm = state[1] / 0.07
    return np.array([pos_norm, vel_norm], dtype=np.float32)


def mechanical_energy(raw_state):
    """마운틴 카의 물리적 총 역학적 에너지 E(x, v) = 운동에너지 + 위치에너지"""
    pos, vel = float(raw_state[0]), float(raw_state[1])
    kinetic = 0.5 * (vel ** 2)
    potential = (0.0025 / 3.0) * np.sin(3.0 * pos)
    return kinetic + potential


class MountainCarDQNAgent:
    """경험 재생 + 소프트 목표 신경망 + Double DQN 기반 마운틴 카 에이전트"""

    def __init__(self):
        self.gamma = 0.99
        self.lr = 0.0015
        self.tau = 0.02
        self.epsilon = 1.0
        self.epsilon_min = 0.05
        self.epsilon_decay = 0.975
        self.action_size = 3
        self.batch_size = 64

        self.replay_buffer = ReplayBuffer(buffer_size=20000, batch_size=self.batch_size)
        self.qnet = QNetwork(state_dim=2, hidden_dim=64, action_dim=3, lr=self.lr)
        self.qnet_target = copy.deepcopy(self.qnet)

    def soft_sync_qnet(self):
        """목표 신경망 가중치를 지수 이동 평균(Polyak Averaging)으로 부드럽게 동기화"""
        for p_target, p_main in zip(self.qnet_target.get_params(), self.qnet.get_params()):
            p_target[:] = (1.0 - self.tau) * p_target + self.tau * p_main

    def get_action(self, norm_state, greedy=False):
        if not greedy and np.random.rand() < self.epsilon:
            return int(np.random.choice(self.action_size))
        qs = self.qnet.forward(norm_state[np.newaxis, :])
        return int(np.argmax(qs[0]))

    def train_step(self):
        """경험 재생 버퍼에서 미니배치를 추출해 Double DQN 역전파 1회 수행"""
        if len(self.replay_buffer) < self.batch_size:
            return None

        s, a, r, next_s, d = self.replay_buffer.get_batch()

        qs = self.qnet.forward(s)
        q = qs[np.arange(self.batch_size), a]

        # Double DQN: 메인망으로 최적 행동 선택, 목표 신경망으로 가치 평가
        best_next_actions = np.argmax(self.qnet.forward(next_s), axis=1)
        next_qs_target = self.qnet_target.forward(next_s)
        next_q = next_qs_target[np.arange(self.batch_size), best_next_actions]

        target = r + (1.0 - d) * self.gamma * next_q

        # Huber 손실 기울기 클리핑으로 발산 방지
        td_diff = np.clip(q - target, -1.0, 1.0)
        dout = np.zeros_like(qs)
        dout[np.arange(self.batch_size), a] = td_diff

        self.qnet.backward(dout)
        self.soft_sync_qnet()
        return float(np.mean((q - target) ** 2))


def train_dqn(episodes=150, seed=42):
    """마운틴 카 DQN 학습 루프"""
    random.seed(seed)
    np.random.seed(seed)

    env = gym.make('MountainCar-v0')
    agent = MountainCarDQNAgent()

    raw_rewards = []
    max_positions = []
    success_flags = []
    best_avg_reward = -200.0
    best_qnet = copy.deepcopy(agent.qnet)
    start_time = time.time()

    print("=" * 72)
    print(" [실습 2단계 - 1부] 마운틴 카(MountainCar-v0) 순수 NumPy DQN 학습 시작")
    print("=" * 72)
    print(f"{'에피소드':^10} | {'원본 보상':^10} | {'최고 위치':^10} | {'최근20회 성공률':^14} | {'ε':^7} | {'상태'}")
    print("-" * 72)

    for ep in range(1, episodes + 1):
        raw_state = env.reset(seed=seed + ep)[0]
        state = normalize_state(raw_state)
        done = False
        ep_raw_reward = 0.0
        ep_max_pos = float(raw_state[0])
        reached_goal = False
        step_idx = 0

        while not done:
            action = agent.get_action(state)
            next_raw_state, reward, terminated, truncated, _ = env.step(action)
            next_state = normalize_state(next_raw_state)
            done = terminated or truncated
            step_idx += 1

            # 역학적 에너지 퍼텐셜 기반 보상 셰이핑:
            # 운동에너지 + 위치에너지가 커질수록(진자 반동 증폭) 즉각적인 양의 학습 신호 제공
            e_curr = 1000.0 * mechanical_energy(raw_state)
            e_next = 1000.0 * mechanical_energy(next_raw_state)
            shaped_reward = -0.1 + 5.0 * (agent.gamma * e_next - e_curr)
            if terminated:
                shaped_reward += 10.0
                reached_goal = True

            agent.replay_buffer.add(state, action, shaped_reward, next_state, float(terminated))
            if step_idx % 2 == 0:
                agent.train_step()

            raw_state = next_raw_state
            state = next_state
            ep_raw_reward += reward
            ep_max_pos = max(ep_max_pos, float(raw_state[0]))

        if agent.epsilon > agent.epsilon_min:
            agent.epsilon = max(agent.epsilon_min, agent.epsilon * agent.epsilon_decay)

        raw_rewards.append(ep_raw_reward)
        max_positions.append(ep_max_pos)
        success_flags.append(1.0 if reached_goal else 0.0)

        # 최근 10회 평균 보상이 최고 기록을 경신하면 최적 가중치 스냅샷 저장
        if ep >= 20:
            recent_avg_r = float(np.mean(raw_rewards[-10:]))
            if recent_avg_r > best_avg_reward:
                best_avg_reward = recent_avg_r
                best_qnet = copy.deepcopy(agent.qnet)

        if ep == 1 or ep % 25 == 0 or ep == episodes:
            recent_sr = float(np.mean(success_flags[-20:])) * 100.0
            status = "★ 깃발 등정 안정화!" if recent_sr >= 90.0 else ("등정 전략 학습 중..." if recent_sr > 0 else "초기 탐색")
            print(f"{ep:4d}/{episodes:<4d} | {ep_raw_reward:8.1f} 점 | {ep_max_pos:+8.3f}  | {recent_sr:12.1f} % | {agent.epsilon:5.3f} | {status}")

    env.close()
    agent.qnet = best_qnet
    elapsed = time.time() - start_time
    print("-" * 72)
    print(f"[*] DQN 학습 완료! (소요 시간: {elapsed:.2f}초, 최종 20회 깃발 도달률: {np.mean(success_flags[-20:])*100:.1f}%)")
    print("=" * 72)
    return agent, raw_rewards, max_positions


def evaluate_dqn(agent, n_tests=5, seed=1000):
    """학습 완료 DQN 에이전트 정량 검증 (ε = 0)"""
    env = gym.make('MountainCar-v0')
    scores = []
    successes = 0

    print("\n" + "=" * 72)
    print(" [실습 2단계 - 2부] 학습 완료 DQN 에이전트 정량 검증 (탐욕 정책 ε=0)")
    print("=" * 72)

    for i in range(1, n_tests + 1):
        raw_state = env.reset(seed=seed + i)[0]
        state = normalize_state(raw_state)
        done = False
        steps = 0
        total_reward = 0.0
        max_pos = float(raw_state[0])

        while not done:
            action = agent.get_action(state, greedy=True)
            next_raw_state, reward, terminated, truncated, _ = env.step(action)
            state = normalize_state(next_raw_state)
            done = terminated or truncated
            steps += 1
            total_reward += reward
            max_pos = max(max_pos, float(next_raw_state[0]))

        scores.append(total_reward)
        if terminated:
            successes += 1
            badge = f"★ {steps}스텝 만에 깃발 도달 성공!"
        else:
            badge = f"실패 (최고 위치 {max_pos:+.3f})"
        print(f"  - 검증 테스트 {i}/{n_tests}: 원본 보상 = {total_reward:6.1f} 점 | 최고 위치 = {max_pos:+.3f} | {badge}")

    env.close()
    print("-" * 72)
    print(f"[*] {n_tests}회 검증 결과: 성공률 {successes}/{n_tests} ({successes/n_tests*100:.0f}%), 평균 보상 {np.mean(scores):.1f} 점")
    print("=" * 72)
    return scores


def save_analysis_chart(agent, raw_rewards, max_positions):
    """학습 곡선(최고 도달 위치 & 보상)과 2D 상태 공간 정책 지도 시각화 저장"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    img_dir = os.path.join(script_dir, "img")
    os.makedirs(img_dir, exist_ok=True)
    out_path = os.path.join(img_dir, "ch12_6_mountaincar_result.png")

    fig, axes = plt.subplots(1, 2, figsize=(14, 5.2))
    plt.subplots_adjust(wspace=0.28)

    episodes = np.arange(1, len(raw_rewards) + 1)

    # 1. 좌측: 에피소드별 원본 보상(스텝 단축 추이)
    ax1 = axes[0]
    ax1.plot(episodes, raw_rewards, color='#90cdf4', alpha=0.55, label='Episode Raw Reward')
    window = 10
    if len(raw_rewards) >= window:
        ma = np.convolve(raw_rewards, np.ones(window) / window, mode='valid')
        ax1.plot(np.arange(window, len(raw_rewards) + 1), ma, color='#2b6cb0', linewidth=2.5,
                 label=f'{window}-Episode Moving Avg')
    ax1.axhline(-200.0, color='#e53e3e', linestyle='--', linewidth=1.6, label='Random Baseline (-200)')
    ax1.set_title("MountainCar-v0 DQN Learning Curve (Raw Reward)", fontsize=12, fontweight='bold')
    ax1.set_xlabel("Episode", fontsize=11)
    ax1.set_ylabel("Raw Episode Reward (-Steps)", fontsize=11)
    ax1.set_ylim(-210, -70)
    ax1.legend(loc='lower right', fontsize=9.5)
    ax1.grid(True, alpha=0.3)

    # 2. 우측: 학습된 2D 상태 공간(위치 x 속도) 정책 결정 경계 지도
    ax2 = axes[1]
    pos_grid = np.linspace(-1.2, 0.6, 80)
    vel_grid = np.linspace(-0.07, 0.07, 80)
    P, V = np.meshgrid(pos_grid, vel_grid)
    grid_states = np.stack([(P.ravel() + 0.3) / 0.9, V.ravel() / 0.07], axis=1).astype(np.float32)
    best_actions = np.argmax(agent.qnet.forward(grid_states), axis=1).reshape(P.shape)

    cmap = matplotlib.colors.ListedColormap(['#4299e1', '#ecc94b', '#f56565'])
    im = ax2.contourf(P, V, best_actions, levels=[-0.5, 0.5, 1.5, 2.5], cmap=cmap, alpha=0.82)
    ax2.axvline(0.5, color='black', linestyle='--', linewidth=1.8, label='Flag Goal (+0.5)')
    ax2.axhline(0.0, color='white', linestyle=':', linewidth=1.2)
    cbar = fig.colorbar(im, ax=ax2, ticks=[0, 1, 2])
    cbar.ax.set_yticklabels(['0: Left', '1: Coast', '2: Right'])
    ax2.set_title("Learned DQN Policy Map (Position vs Velocity)", fontsize=12, fontweight='bold')
    ax2.set_xlabel("Car Position", fontsize=11)
    ax2.set_ylabel("Car Velocity", fontsize=11)
    ax2.legend(loc='upper left', fontsize=9.5)
    ax2.grid(True, alpha=0.25)

    plt.savefig(out_path, dpi=200, bbox_inches='tight')
    plt.close()
    print(f"\n[저장 완료] 학습 곡선 및 2D 정책 지도: {out_path}")


def render_demo(agent, seed=2025):
    """학습 완료 DQN 에이전트의 실시간 정상 깃발 등정 라이브 시연"""
    print("\n" + "=" * 72)
    print(" [실습 2단계 - 3부] 학습 완료 DQN 에이전트 라이브 시연 (정상 깃발 등정)")
    print("=" * 72)
    print(f"{'스텝':^6} | {'선택 행동':^12} | {'자동차 위치':^12} | {'자동차 속도':^12} | {'상태'}")
    print("-" * 72)

    env = gym.make('MountainCar-v0', render_mode='human')
    raw_state = env.reset(seed=seed)[0]
    state = normalize_state(raw_state)
    done = False
    step_count = 0
    total_reward = 0.0
    action_labels = {0: "0 (← 좌측)", 1: "1 (· 관성)", 2: "2 (→ 우측)"}

    while not done:
        env.render()
        action = agent.get_action(state, greedy=True)
        next_raw_state, reward, terminated, truncated, _ = env.step(action)
        state = normalize_state(next_raw_state)

        step_count += 1
        total_reward += reward
        done = terminated or truncated

        if step_count == 1 or step_count % 20 == 0 or done:
            if terminated:
                status = "★ 정상 깃발 도달 성공!"
            elif truncated:
                status = "시간 초과"
            else:
                status = "반동 가속 주행 중..."
            print(f"{step_count:^6} | {action_labels[action]:^12} | {next_raw_state[0]:^+10.3f}   | {next_raw_state[1]:^+10.4f}   | {status}")

        time.sleep(0.02)

    print("-" * 72)
    print("[*] 라이브 시연 종료 요약:")
    print(f"  - 정상 도달 소요 스텝 : {step_count} 스텝 (제한 200스텝 중)")
    print(f"  - 원본 Gym 획득 보상 : {total_reward:.1f} 점 (무작위 -200.0점 대비 대폭 개선)")
    goal_msg = "목표 +0.500 돌파!" if terminated else "목표 +0.500 미달"
    print(f"  - 최종 도달 위치      : {next_raw_state[0]:+.3f} ({goal_msg})")
    print(f"  - 종료 사유           : {'정상 깃발 등정 성공 (Terminated)' if terminated else '시간 초과 (Truncated)'}")
    print("=" * 72)
    print("\n[안내] 정상 깃발 도달 장면을 확인하세요. 2초 후 창이 자동으로 닫힙니다...")
    time.sleep(2)
    env.close()


if __name__ == '__main__':
    dqn_agent, rewards, max_pos_list = train_dqn(episodes=150, seed=42)
    evaluate_dqn(dqn_agent, n_tests=5, seed=1000)
    save_analysis_chart(dqn_agent, rewards, max_pos_list)
    render_demo(dqn_agent, seed=2025)
