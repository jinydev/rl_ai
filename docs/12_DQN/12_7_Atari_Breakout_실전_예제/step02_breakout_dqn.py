"""
[실습 2단계] 순수 NumPy Double DQN으로 아타리 벽돌깨기(Atari Breakout) 학습 및 시연
=================================================================================
경험 재생 버퍼(Replay Buffer), 소프트 목표 신경망(Soft Target Network), Double DQN을
순수 NumPy로 구현하여 아타리 벽돌깨기를 CPU에서도 약 10초 내외로 학습합니다.

실습 구성:
1부. 200 에피소드 Double DQN 고속 학습 (초기 ~1개 벽돌 -> 수십 개 벽돌 연속 격파!)
2부. 학습 완료 에이전트 5회 정량 검증 (탐욕 정책 ε = 0)
3부. 학습 곡선 + 실제 아타리 RGB 플레이 스냅샷 3종 시각화 그래프 저장
4부. Pygame 아케이드 창에서 학습된 DQN 에이전트의 실시간 벽돌 격파 라이브 시연
"""

from collections import deque
import copy
import os
import random
import time
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from atari_breakout_env import AtariBreakoutEnv


class ReplayBuffer:
    """경험 재생 버퍼 (FIFO 순환 큐)"""

    def __init__(self, buffer_size=25000, batch_size=64):
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
    """순수 NumPy 2층 은닉 MLP Q-네트워크 (5 -> 64 -> 64 -> 3) + Adam 옵티마이저"""

    def __init__(self, state_dim=5, hidden_dim=64, action_dim=3, lr=0.002):
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

    def predict(self, x):
        """역전파 캐시를 덮어쓰지 않는 순수 추론 전용 순전파"""
        a1 = np.maximum(0, np.dot(x, self.W1) + self.b1)
        a2 = np.maximum(0, np.dot(a1, self.W2) + self.b2)
        return np.dot(a2, self.W3) + self.b3

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


def extract_features(obs):
    """5차원 환경 상태에 상대 수평 오차(공X - 패들X)를 결합한 6차원 DQN 입력 특징"""
    dx = float(obs[1]) - float(obs[0])
    return np.array([obs[0], obs[1], obs[2], obs[3], obs[4], dx], dtype=np.float32)


class BreakoutDQNAgent:
    """경험 재생 + 소프트 목표 신경망 + Double DQN 아타리 벽돌깨기 에이전트"""

    def __init__(self):
        self.gamma = 0.96
        self.lr = 0.0025
        self.tau = 0.03
        self.epsilon = 1.0
        self.epsilon_min = 0.03
        self.epsilon_decay = 0.975
        self.action_size = 3
        self.batch_size = 64

        self.replay_buffer = ReplayBuffer(buffer_size=30000, batch_size=self.batch_size)
        self.qnet = QNetwork(state_dim=6, hidden_dim=64, action_dim=3, lr=self.lr)
        self.qnet_target = copy.deepcopy(self.qnet)

    def soft_sync_qnet(self):
        for p_target, p_main in zip(self.qnet_target.get_params(), self.qnet.get_params()):
            p_target[:] = (1.0 - self.tau) * p_target + self.tau * p_main

    def get_action(self, state, greedy=False):
        if not greedy and np.random.rand() < self.epsilon:
            return int(np.random.choice(self.action_size))
        qs = self.qnet.predict(state[np.newaxis, :])
        return int(np.argmax(qs[0]))

    def train_step(self):
        if len(self.replay_buffer) < self.batch_size:
            return None

        s, a, r, next_s, d = self.replay_buffer.get_batch()

        # Double DQN 타깃 계산 (predict 사용으로 메인망 역전파 캐시 보호!)
        best_next_a = np.argmax(self.qnet.predict(next_s), axis=1)
        next_q = self.qnet_target.predict(next_s)[np.arange(self.batch_size), best_next_a]
        target = r + (1.0 - d) * self.gamma * next_q

        qs = self.qnet.forward(s)
        q = qs[np.arange(self.batch_size), a]

        # Huber 기울기 클리핑
        td_diff = np.clip(q - target, -1.0, 1.0)
        dout = np.zeros_like(qs)
        dout[np.arange(self.batch_size), a] = td_diff

        self.qnet.backward(dout)
        self.soft_sync_qnet()
        return float(np.mean((q - target) ** 2))


def train_dqn(episodes=220, seed=42):
    """아타리 벽돌깨기 Double DQN 고속 학습"""
    random.seed(seed)
    np.random.seed(seed)

    # 학습 효율을 위해 1목숨 에피소드(DeepMind 아타리 논문 'Episodic Life' 트릭!)로 학습
    env = AtariBreakoutEnv(render_mode=None, max_steps=1600, lives=1)
    agent = BreakoutDQNAgent()

    score_history = []
    brick_history = []
    hit_history = []
    best_avg_bricks = -1.0
    best_qnet = copy.deepcopy(agent.qnet)
    start_time = time.time()

    print("=" * 74)
    print(" [실습 2단계 - 1부] 아타리 벽돌깨기(Breakout) 순수 NumPy Double DQN 학습")
    print("=" * 74)
    print(f"{'에피소드':^10} | {'아타리 점수':^10} | {'파괴 벽돌':^10} | {'최근20회 평균벽돌':^16} | {'ε':^6} | {'상태'}")
    print("-" * 74)

    for ep in range(1, episodes + 1):
        obs, info = env.reset(seed=seed + ep)
        state = extract_features(obs)
        done = False
        step_idx = 0

        while not done:
            action = agent.get_action(state)
            next_obs, raw_reward, terminated, truncated, info = env.step(action)
            next_state = extract_features(next_obs)
            done = terminated or truncated
            step_idx += 1

            # 아타리 DQN 보상 클리핑 + 패들 반사/추적 보상 설계
            learn_reward = 0.0
            if raw_reward > 0:
                learn_reward += 1.0          # 벽돌 파괴 (DQN 논문 Reward Clipping: +1)
            if info["paddle_hit"]:
                learn_reward += 2.5          # 패들로 공 받아치기 성공 보너스
            if info["life_lost"]:
                learn_reward -= 3.0          # 공 놓침 페널티

            # 공의 수평 위치를 향해 패들이 접근하면 즉각 밀집 신호 제공
            prev_dist = abs(float(state[5]))
            next_dist = abs(float(next_state[5]))
            learn_reward += 1.5 * (prev_dist - next_dist)

            agent.replay_buffer.add(state, action, learn_reward, next_state, float(terminated))
            if step_idx % 2 == 0:
                agent.train_step()

            state = next_state

        if agent.epsilon > agent.epsilon_min:
            agent.epsilon = max(agent.epsilon_min, agent.epsilon * agent.epsilon_decay)

        score_history.append(info["score"])
        brick_history.append(info["bricks_broken"])
        hit_history.append(info["paddle_hits"])

        if ep >= 20:
            avg_b = float(np.mean(brick_history[-15:]))
            if avg_b > best_avg_bricks:
                best_avg_bricks = avg_b
                best_qnet = copy.deepcopy(agent.qnet)

        if ep == 1 or ep % 30 == 0 or ep == episodes:
            recent_b = float(np.mean(brick_history[-20:]))
            if recent_b >= 25.0:
                stage = "★ 벽돌 대량 격파 마스터!"
            elif recent_b >= 8.0:
                stage = "공 추적·반사 숙달 중..."
            else:
                stage = "초기 탐색 단계"
            print(f"{ep:4d}/{episodes:<4d} | {info['score']:7d} 점 | {info['bricks_broken']:4d} / 60 | {recent_b:12.1f} 개  | {agent.epsilon:5.3f} | {stage}")

    env.close()
    agent.qnet = best_qnet
    elapsed = time.time() - start_time
    print("-" * 74)
    print(f"[*] 학습 완료! (소요 시간: {elapsed:.2f}초, 최고 15회 평균 파괴 벽돌: {best_avg_bricks:.1f}개)")
    print("=" * 74)
    return agent, score_history, brick_history


def evaluate_dqn(agent, n_tests=5, seed=1000):
    """학습 완료 DQN 에이전트 3목숨 정규 게임 정량 검증 (ε = 0)"""
    env = AtariBreakoutEnv(render_mode=None, max_steps=3000, lives=3)
    scores, bricks_list, hits_list = [], [], []
    best_snapshots = []

    print("\n" + "=" * 74)
    print(" [실습 2단계 - 2부] 아타리 벽돌깨기 정규 3목숨 검증 (탐욕 정책 ε=0)")
    print("=" * 74)

    best_score = -1
    for i in range(1, n_tests + 1):
        obs, info = env.reset(seed=seed + i)
        state = extract_features(obs)
        done = False
        frames = [env.get_rgb_frame()]
        steps = 0

        while not done:
            action = agent.get_action(state, greedy=True)
            next_obs, _, terminated, truncated, info = env.step(action)
            state = extract_features(next_obs)
            done = terminated or truncated
            steps += 1
            if steps in (400, 1000) or done:
                frames.append(env.get_rgb_frame())

        scores.append(info["score"])
        bricks_list.append(info["bricks_broken"])
        hits_list.append(info["paddle_hits"])

        if info["score"] > best_score:
            best_score = info["score"]
            best_snapshots = frames

        clear_tag = " ★ 전체 60개 완파(CLEAR)!" if info["cleared"] else ""
        print(
            f"  - 검증 게임 {i}/{n_tests}: 점수 = {info['score']:3d} 점 | "
            f"파괴 벽돌 = {info['bricks_broken']:2d}/60 | 패들 반사 = {info['paddle_hits']:2d}회{clear_tag}"
        )

    env.close()
    print("-" * 74)
    print(
        f"[*] {n_tests}회 정규 게임 평균: 점수 {np.mean(scores):.1f}점 | "
        f"파괴 벽돌 {np.mean(bricks_list):.1f}개 / 60개 | 평균 패들 반사 {np.mean(hits_list):.1f}회"
    )
    print("=" * 74)
    return best_snapshots


def save_analysis_chart(score_history, brick_history, snapshots):
    """학습 곡선 + 실제 아타리 벽돌깨기 RGB 플레이 스냅샷 시각화 저장"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    img_dir = os.path.join(script_dir, "img")
    os.makedirs(img_dir, exist_ok=True)
    out_path = os.path.join(img_dir, "ch12_7_breakout_result.png")

    fig = plt.figure(figsize=(15, 5.2))
    gs = fig.add_gridspec(1, 4, width_ratios=[2.1, 1.0, 1.0, 1.0], wspace=0.25)

    # 좌측: 학습 곡선 (에피소드별 파괴 벽돌 수)
    ax0 = fig.add_subplot(gs[0, 0])
    eps = np.arange(1, len(brick_history) + 1)
    ax0.plot(eps, brick_history, color="#90cdf4", alpha=0.55, label="Episode Bricks Broken")
    window = 15
    if len(brick_history) >= window:
        ma = np.convolve(brick_history, np.ones(window) / window, mode="valid")
        ax0.plot(np.arange(window, len(brick_history) + 1), ma, color="#2b6cb0", linewidth=2.5,
                 label=f"{window}-Episode Moving Avg")
    ax0.axhline(60, color="#38a169", linestyle="--", linewidth=1.6, label="Full Wall Clear (60)")
    ax0.set_title("Atari Breakout Double DQN Learning Curve", fontsize=12, fontweight="bold")
    ax0.set_xlabel("Training Episode (1-Life Episodic Mode)", fontsize=10.5)
    ax0.set_ylabel("Bricks Broken (out of 60)", fontsize=10.5)
    ax0.set_ylim(-2, 65)
    ax0.legend(loc="upper left", fontsize=9)
    ax0.grid(True, alpha=0.3)

    # 우측 3패널: 실제 아타리 210x160 RGB 게임 진행 스냅샷
    titles = ["Start (t=0)", "Mid-Game Rally", "Final State"]
    picks = [snapshots[0], snapshots[len(snapshots) // 2], snapshots[-1]]
    for idx in range(3):
        ax = fig.add_subplot(gs[0, idx + 1])
        ax.imshow(picks[idx])
        ax.set_title(titles[idx], fontsize=11, fontweight="bold")
        ax.axis("off")

    plt.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"\n[저장 완료] 아타리 벽돌깨기 학습 곡선 및 플레이 스냅샷: {out_path}")


def render_demo(agent, seed=2026):
    """Pygame 아케이드 창에서 학습된 DQN 에이전트 실시간 시연"""
    print("\n" + "=" * 74)
    print(" [실습 2단계 - 3부] 학습 완료 DQN 에이전트 아타리 라이브 아케이드 시연")
    print("=" * 74)
    print(f"{'스텝':^6} | {'선택 행동':^12} | {'누적 점수':^10} | {'파괴 벽돌':^10} | {'패들 반사':^10} | {'생명'}")
    print("-" * 74)

    env = AtariBreakoutEnv(render_mode="human", max_steps=600, lives=3)
    obs, info = env.reset(seed=seed)
    state = extract_features(obs)
    done = False
    step_count = 0
    action_names = {0: "0 (← 좌측)", 1: "1 (· 정지)", 2: "2 (→ 우측)"}

    while not done:
        env.render(" - Trained Double DQN")
        action = agent.get_action(state, greedy=True)
        next_obs, _, terminated, truncated, info = env.step(action)
        state = extract_features(next_obs)
        step_count += 1
        done = terminated or truncated

        if step_count == 1 or step_count % 120 == 0 or done:
            print(
                f"{step_count:^6} | {action_names[action]:^12} | {info['score']:6d} 점   | "
                f"{info['bricks_broken']:3d} / 60  | {info['paddle_hits']:5d} 회   | {info['lives']}"
            )

    print("-" * 74)
    print("[*] 아타리 라이브 시연 요약:")
    print(f"  - 총 진행 스텝 : {step_count} 스텝")
    print(f"  - 패들 반사 수 : {info['paddle_hits']} 회")
    print(f"  - 파괴한 벽돌  : {info['bricks_broken']} / 60 개")
    print(f"  - 최종 점수    : {info['score']} 점 {'(★ 전체 완파!)' if info['cleared'] else ''}")
    print("=" * 74)
    print("\n[안내] 아타리 벽돌깨기 시연을 확인하세요. 2초 후 창이 자동으로 닫힙니다...")
    time.sleep(2)
    env.close()


if __name__ == "__main__":
    trained_agent, scores, bricks = train_dqn(episodes=220, seed=42)
    best_frames = evaluate_dqn(trained_agent, n_tests=5, seed=1000)
    save_analysis_chart(scores, bricks, best_frames)
    render_demo(trained_agent, seed=2026)
