"""
[실습 2단계] 순수 NumPy Double DQN으로 아타리 팩맨(Atari Pac-Man) 학습 및 시연
=================================================================================
경험 재생 버퍼(Replay Buffer), 소프트 목표 신경망(Soft Target Network), Double DQN을
순수 NumPy로 구현하여 아타리 팩맨을 CPU에서도 수십 초 내외로 학습합니다.

실습 구성:
1부. 220 에피소드 Double DQN 고속 학습 (초기 방황 -> 유령 회피 + 쿠키 완식 + 파워 포식!)
2부. 학습 완료 에이전트 5회 정규 3목숨 검증 (탐욕 정책 ε = 0)
3부. 학습 곡선 + 실제 아타리 210x160 RGB 플레이 스냅샷 3종 시각화 그래프 저장
4부. Pygame 아케이드 창에서 학습된 DQN 에이전트의 실시간 팩맨 라이브 시연
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

from atari_pacman_env import AtariPacmanEnv


class ReplayBuffer:
    """경험 재생 버퍼 (FIFO 순환 큐)"""

    def __init__(self, buffer_size=30000, batch_size=64):
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
    """순수 NumPy 2층 은닉 MLP Q-네트워크 (18 -> 64 -> 64 -> 4) + Adam 옵티마이저"""

    def __init__(self, state_dim=18, hidden_dim=64, action_dim=4, lr=0.0025):
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


class PacmanDQNAgent:
    """경험 재생 + 소프트 목표 신경망 + Double DQN 아타리 팩맨 에이전트"""

    def __init__(self, state_dim=18, action_size=4):
        self.gamma = 0.95
        self.lr = 0.0025
        self.tau = 0.03
        self.epsilon = 1.0
        self.epsilon_min = 0.03
        self.epsilon_decay = 0.975
        self.action_size = action_size
        self.batch_size = 64

        self.replay_buffer = ReplayBuffer(buffer_size=30000, batch_size=self.batch_size)
        self.qnet = QNetwork(state_dim=state_dim, hidden_dim=64, action_dim=action_size, lr=self.lr)
        self.qnet_target = copy.deepcopy(self.qnet)

    def soft_sync_qnet(self):
        for p_target, p_main in zip(self.qnet_target.get_params(), self.qnet.get_params()):
            p_target[:] = (1.0 - self.tau) * p_target + self.tau * p_main

    def get_action(self, state, greedy=False):
        if not greedy and np.random.rand() < self.epsilon:
            return int(np.random.choice(self.action_size))
        qs = self.qnet.predict(state[np.newaxis, :])[0]
        return int(np.argmax(qs))

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
    """아타리 팩맨 Double DQN 고속 학습"""
    random.seed(seed)
    np.random.seed(seed)

    # 학습 효율을 위해 1목숨 에피소드(DeepMind 아타리 논문 'Episodic Life' 트릭!)로 학습
    env = AtariPacmanEnv(render_mode=None, max_steps=350, lives=1)
    agent = PacmanDQNAgent(state_dim=env.observation_space.shape[0], action_size=env.action_space.n)

    score_history = []
    pellet_history = []
    ghost_history = []
    best_avg_pellets = -1.0
    best_qnet = copy.deepcopy(agent.qnet)
    start_time = time.time()

    print("=" * 78)
    print(" [실습 2단계 - 1부] 아타리 팩맨(Pac-Man) 순수 NumPy Double DQN 학습")
    print("=" * 78)
    print(f"{'에피소드':^10} | {'아타리 점수':^10} | {'먹은 쿠키':^10} | {'최근20회 평균쿠키':^16} | {'ε':^6} | {'상태'}")
    print("-" * 78)

    for ep in range(1, episodes + 1):
        state, info = env.reset(seed=seed + ep)
        done = False
        step_idx = 0

        while not done:
            action = agent.get_action(state)
            next_state, raw_reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated
            step_idx += 1

            # 아타리 DQN 보상 클리핑 + 생존/탐색 보상 설계
            learn_reward = -0.04  # 불필요한 배회 억제 시간 페널티
            if info["pellet_eaten_now"]:
                learn_reward += 1.0      # 쿠키 섭취 (Reward Clipping: +1)
            if info["power_eaten_now"]:
                learn_reward += 0.8      # 파워 쿠키 추가 보너스
            if info["ghost_eaten_now"]:
                learn_reward += 3.0      # 파워 모드 유령 포식 대보너스!
            if info["cleared"]:
                learn_reward += 5.0      # 스테이지 완식 클리어 보너스!
            if info["wall_hit"]:
                learn_reward -= 0.4      # 벽 충돌 페널티
            if info["life_lost"]:
                learn_reward -= 4.0      # 유령 충돌(사망) 페널티

            # 즉각적인 방향 감각 밀집 신호 (쿠키 접근, 활성 유령 회피, 겁먹은 유령 추적)
            if not info["wall_hit"] and not info["life_lost"]:
                learn_reward += 0.15 * float(state[4 + action])
                learn_reward -= 0.35 * float(state[8 + action])
                learn_reward += 0.25 * float(state[12 + action])

            agent.replay_buffer.add(state, action, learn_reward, next_state, float(terminated))
            if step_idx % 2 == 0:
                agent.train_step()

            state = next_state

        if agent.epsilon > agent.epsilon_min:
            agent.epsilon = max(agent.epsilon_min, agent.epsilon * agent.epsilon_decay)

        score_history.append(info["score"])
        pellet_history.append(info["pellets_eaten"])
        ghost_history.append(info["ghosts_eaten"])

        if ep >= 20:
            avg_p = float(np.mean(pellet_history[-15:]))
            if avg_p > best_avg_pellets:
                best_avg_pellets = avg_p
                best_qnet = copy.deepcopy(agent.qnet)

        if ep == 1 or ep % 30 == 0 or ep == episodes:
            recent_p = float(np.mean(pellet_history[-20:]))
            if recent_p >= 50.0:
                stage = "★ 미로 완식·유령 사냥 마스터!"
            elif recent_p >= 28.0:
                stage = "유령 회피·쿠키 탐색 숙달 중..."
            else:
                stage = "초기 탐색 단계"
            print(
                f"{ep:4d}/{episodes:<4d} | {info['score']:7d} 점 | "
                f"{info['pellets_eaten']:4d} / {info['total_pellets']} | "
                f"{recent_p:12.1f} 개  | {agent.epsilon:5.3f} | {stage}"
            )

    env.close()
    agent.qnet = best_qnet
    elapsed = time.time() - start_time
    print("-" * 78)
    print(f"[*] 학습 완료! (소요 시간: {elapsed:.2f}초, 최고 15회 평균 먹은 쿠키: {best_avg_pellets:.1f}/{env.total_pellets}개)")
    print("=" * 78)
    return agent, score_history, pellet_history


def evaluate_dqn(agent, n_tests=5, seed=1000):
    """학습 완료 DQN 에이전트 정규 3목숨 게임 정량 검증 (ε = 0)"""
    env = AtariPacmanEnv(render_mode=None, max_steps=600, lives=3)
    scores, pellets_list, ghosts_list = [], [], []
    best_snapshots = []

    print("\n" + "=" * 78)
    print(" [실습 2단계 - 2부] 아타리 팩맨 정규 3목숨 검증 (탐욕 정책 ε=0)")
    print("=" * 78)

    best_score = -1
    for i in range(1, n_tests + 1):
        state, info = env.reset(seed=seed + i)
        done = False
        frames = [env.get_rgb_frame()]
        steps = 0

        while not done:
            action = agent.get_action(state, greedy=True)
            next_state, _, terminated, truncated, info = env.step(action)
            state = next_state
            done = terminated or truncated
            steps += 1
            if steps in (45, 95) or info["ghost_eaten_now"] or done:
                frames.append(env.get_rgb_frame())

        scores.append(info["score"])
        pellets_list.append(info["pellets_eaten"])
        ghosts_list.append(info["ghosts_eaten"])

        if info["score"] > best_score:
            best_score = info["score"]
            best_snapshots = frames

        clear_tag = f" ★ 전체 {info['total_pellets']}개 완식(CLEAR)!" if info["cleared"] else ""
        print(
            f"  - 검증 게임 {i}/{n_tests}: 점수 = {info['score']:4d} 점 | "
            f"먹은 쿠키 = {info['pellets_eaten']:2d}/{info['total_pellets']} | "
            f"포식 유령 = {info['ghosts_eaten']}마리 | 남은 생명 = {info['lives']}{clear_tag}"
        )

    env.close()
    print("-" * 78)
    print(
        f"[*] {n_tests}회 정규 게임 평균: 점수 {np.mean(scores):.1f}점 | "
        f"먹은 쿠키 {np.mean(pellets_list):.1f}개 / {env.total_pellets}개 | "
        f"평균 유령 포식 {np.mean(ghosts_list):.1f}마리"
    )
    print("=" * 78)
    return best_snapshots


def save_analysis_chart(score_history, pellet_history, snapshots):
    """학습 곡선 + 실제 아타리 팩맨 RGB 플레이 스냅샷 시각화 저장"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    img_dir = os.path.join(script_dir, "img")
    os.makedirs(img_dir, exist_ok=True)
    out_path = os.path.join(img_dir, "ch12_8_pacman_result.png")

    fig = plt.figure(figsize=(15, 5.2))
    gs = fig.add_gridspec(1, 4, width_ratios=[2.1, 1.0, 1.0, 1.0], wspace=0.25)

    # 좌측: 학습 곡선 (에피소드별 먹은 쿠키 수)
    ax0 = fig.add_subplot(gs[0, 0])
    eps = np.arange(1, len(pellet_history) + 1)
    ax0.plot(eps, pellet_history, color="#fbd38d", alpha=0.65, label="Episode Pellets Eaten")
    window = 15
    if len(pellet_history) >= window:
        ma = np.convolve(pellet_history, np.ones(window) / window, mode="valid")
        ax0.plot(
            np.arange(window, len(pellet_history) + 1),
            ma,
            color="#dd6b20",
            linewidth=2.5,
            label=f"{window}-Episode Moving Avg",
        )
    ax0.axhline(70, color="#38a169", linestyle="--", linewidth=1.6, label="Full Maze Clear (70)")
    ax0.set_title("Atari Pac-Man Double DQN Learning Curve", fontsize=12, fontweight="bold")
    ax0.set_xlabel("Training Episode (1-Life Episodic Mode)", fontsize=10.5)
    ax0.set_ylabel("Pellets Eaten (out of 70)", fontsize=10.5)
    ax0.set_ylim(-2, 75)
    ax0.legend(loc="upper left", fontsize=9)
    ax0.grid(True, alpha=0.3)

    # 우측 3패널: 실제 아타리 210x160 RGB 게임 진행 스냅샷
    titles = ["Start (t=0)", "Mid-Game Chase & Power", "Final State"]
    picks = [snapshots[0], snapshots[len(snapshots) // 2], snapshots[-1]]
    for idx in range(3):
        ax = fig.add_subplot(gs[0, idx + 1])
        ax.imshow(picks[idx])
        ax.set_title(titles[idx], fontsize=11, fontweight="bold")
        ax.axis("off")

    plt.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"\n[저장 완료] 아타리 팩맨 학습 곡선 및 플레이 스냅샷: {out_path}")


def render_demo(agent, seed=2026):
    """Pygame 아케이드 창에서 학습된 DQN 에이전트 실시간 시연"""
    print("\n" + "=" * 78)
    print(" [실습 2단계 - 3부] 학습 완료 DQN 에이전트 아타리 팩맨 라이브 아케이드 시연")
    print("=" * 78)
    print(f"{'스텝':^6} | {'선택 행동':^12} | {'누적 점수':^10} | {'먹은 쿠키':^10} | {'포식 유령':^10} | {'생명'}")
    print("-" * 78)

    env = AtariPacmanEnv(render_mode="human", max_steps=260, lives=3)
    state, info = env.reset(seed=seed)
    done = False
    step_count = 0
    action_names = {0: "0 (↑ 위)", 1: "1 (↓ 아래)", 2: "2 (← 좌측)", 3: "3 (→ 우측)"}

    while not done:
        env.render(" - Trained Double DQN")
        action = agent.get_action(state, greedy=True)
        next_state, _, terminated, truncated, info = env.step(action)
        state = next_state
        step_count += 1
        done = terminated or truncated

        if step_count == 1 or step_count % 35 == 0 or info["ghost_eaten_now"] or info["life_lost"] or done:
            tag = ""
            if info["ghost_eaten_now"]:
                tag = " [파워 포식! +200]"
            elif info["life_lost"]:
                tag = " [생명 손실]"
            elif info["cleared"]:
                tag = " ★ CLEAR!"
            print(
                f"{step_count:^6} | {action_names[action]:^12} | {info['score']:6d} 점   | "
                f"{info['pellets_eaten']:3d} / {info['total_pellets']}  | {info['ghosts_eaten']:5d} 마리  | "
                f"{info['lives']}{tag}"
            )

    print("-" * 78)
    print("[*] 아타리 팩맨 라이브 시연 요약:")
    print(f"  - 총 진행 스텝 : {step_count} 스텝")
    print(f"  - 먹은 쿠키 수 : {info['pellets_eaten']} / {info['total_pellets']} 개")
    print(f"  - 포식한 유령  : {info['ghosts_eaten']} 마리")
    print(f"  - 최종 점수    : {info['score']} 점 {'(★ 전체 완식 CLEAR!)' if info['cleared'] else ''}")
    print("=" * 78)
    print("\n[안내] 아타리 팩맨 시연을 확인하세요. 2초 후 창이 자동으로 닫힙니다...")
    time.sleep(2)
    env.close()


if __name__ == "__main__":
    trained_agent, scores, pellets = train_dqn(episodes=220, seed=42)
    best_frames = evaluate_dqn(trained_agent, n_tests=5, seed=1000)
    save_analysis_chart(scores, pellets, best_frames)
    render_demo(trained_agent, seed=2026)
