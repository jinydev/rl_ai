"""
[실습 5단계] 카트폴(CartPole) 강화학습 에이전트 학습 및 200스텝 균형 유지 시연
===========================================================================
실습 4단계의 무작위(Random) 에이전트는 10~20스텝 만에 쓰러졌지만,
Q-러닝(Q-Learning)으로 상태별 행동 가치를 학습하면 200스텝 만점 동안
막대가 쓰러지지 않고 완벽하게 균형을 유지하는 모습을 직접 확인할 수 있습니다.
"""

import time
import warnings
import numpy as np
import gym

warnings.filterwarnings('ignore')


class DiscretizedQLearningAgent:
    """연속 상태 공간(4차원)을 구간(Bin)으로 나누어 Q-테이블을 학습하는 에이전트"""

    def __init__(self, n_bins=(3, 3, 8, 12), action_size=2,
                 alpha=0.2, gamma=0.99,
                 epsilon=1.0, epsilon_min=0.01, epsilon_decay=0.985):
        self.action_size = action_size
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay

        # 카트폴 4차원 상태 [위치, 속도, 막대 각도, 막대 각속도]의 구간 경계 설정
        self.bins = [
            np.linspace(-2.4, 2.4, n_bins[0] - 1),
            np.linspace(-2.5, 2.5, n_bins[1] - 1),
            np.linspace(-0.21, 0.21, n_bins[2] - 1),
            np.linspace(-2.5, 2.5, n_bins[3] - 1),
        ]
        self.q_table = np.zeros(n_bins + (action_size,), dtype=np.float64)

    def discretize(self, state):
        """연속 실수 상태 벡터를 Q-테이블 인덱스 튜플로 변환"""
        return tuple(int(np.digitize(state[i], self.bins[i])) for i in range(len(self.bins)))

    def get_action(self, state, greedy=False):
        """ε-탐욕 정책 또는 순수 탐욕 정책(greedy=True)으로 행동 선택"""
        if not greedy and np.random.rand() < self.epsilon:
            return int(np.random.choice(self.action_size))
        s_idx = self.discretize(state)
        return int(np.argmax(self.q_table[s_idx]))

    def update(self, state, action, reward, next_state, terminated):
        """벨만 최적 방정식 기반 Q-테이블 TD 갱신"""
        s_idx = self.discretize(state)
        next_s_idx = self.discretize(next_state)

        next_max_q = 0.0 if terminated else float(np.max(self.q_table[next_s_idx]))
        td_target = reward + self.gamma * next_max_q
        td_error = td_target - self.q_table[s_idx][action]
        self.q_table[s_idx][action] += self.alpha * td_error

    def decay_epsilon(self):
        """에피소드 종료 시 탐색률(ε) 점진적 감소"""
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)


def train_agent(episodes=350, seed=42):
    """헤드리스(비렌더링) 고속 학습 루프: 에피소드별 보상 추이 출력"""
    np.random.seed(seed)
    env = gym.make('CartPole-v0')
    agent = DiscretizedQLearningAgent()

    reward_history = []
    start_time = time.time()

    print("=" * 68)
    print(" [실습 5단계 - 1부] 카트폴 Q-러닝 에이전트 고속 학습 시작")
    print("=" * 68)
    print(f"{'에피소드':^10} | {'현재 점수':^10} | {'최근 25회 평균':^14} | {'탐색률(ε)':^10} | {'학습 상태'}")
    print("-" * 68)

    for ep in range(1, episodes + 1):
        state = env.reset(seed=seed + ep)[0]
        done = False
        total_reward = 0.0

        while not done:
            action = agent.get_action(state)
            next_state, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated

            # 200스텝을 채우지 못하고 쓰러졌을 때 페널티를 주어 균형 유지 가속
            learn_reward = -10.0 if terminated else reward
            agent.update(state, action, learn_reward, next_state, terminated)

            state = next_state
            total_reward += reward

        agent.decay_epsilon()
        reward_history.append(total_reward)

        if ep == 1 or ep % 50 == 0 or ep == episodes:
            recent_avg = float(np.mean(reward_history[-25:]))
            if recent_avg >= 195.0:
                stage = "★ 200스텝 마스터 달성!"
            elif recent_avg >= 100.0:
                stage = "균형 유지 학습 중..."
            else:
                stage = "초기 탐색 단계"
            print(f"{ep:4d}/{episodes:<4d} | {total_reward:8.1f} 점 | {recent_avg:12.1f} 점 | {agent.epsilon:8.3f}  | {stage}")

    env.close()
    elapsed = time.time() - start_time
    print("-" * 68)
    print(f"[*] 학습 완료! (소요 시간: {elapsed:.2f}초, 최종 25회 평균: {np.mean(reward_history[-25:]):.1f}점 / 200점)")
    print("=" * 68)
    return agent


def evaluate_agent(agent, n_tests=5, seed=1000):
    """학습된 에이전트 성능 정량 검증 (ε = 0, 순수 탐욕 정책)"""
    env = gym.make('CartPole-v0')
    scores = []
    print("\n" + "=" * 68)
    print(" [실습 5단계 - 2부] 학습 완료 에이전트 정량 검증 (탐욕 정책 ε=0)")
    print("=" * 68)

    for i in range(1, n_tests + 1):
        state = env.reset(seed=seed + i)[0]
        done = False
        score = 0
        while not done:
            action = agent.get_action(state, greedy=True)
            next_state, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
            state = next_state
            score += int(reward)
        scores.append(score)
        badge = "★ 200스텝 만점 완주!" if score >= 200 else "미달"
        print(f"  - 검증 테스트 {i}/{n_tests}: 버틴 스텝 = {score:3d} 스텝 ({badge})")

    env.close()
    print("-" * 68)
    print(f"[*] {n_tests}회 검증 평균 점수: {np.mean(scores):.1f} 점 / 200.0 점")
    print("=" * 68)
    return scores


def render_demo(agent, seed=2025):
    """학습된 에이전트의 실시간 카트폴 200스텝 균형 유지 시연 (화면 출력)"""
    print("\n" + "=" * 68)
    print(" [실습 5단계 - 3부] 학습된 에이전트 라이브 시각화 시연 (200스텝 도전)")
    print("=" * 68)
    print(f"{'스텝':^6} | {'선택 행동':^10} | {'카트 위치':^12} | {'막대 각도':^12} | {'상태'}")
    print("-" * 68)

    env = gym.make('CartPole-v0', render_mode='human')
    state = env.reset(seed=seed)[0]
    done = False
    step_count = 0
    total_reward = 0.0
    max_abs_angle = 0.0

    while not done:
        env.render()
        action = agent.get_action(state, greedy=True)
        action_name = "0 (← 좌측)" if action == 0 else "1 (→ 우측)"

        next_state, reward, terminated, truncated, _ = env.step(action)
        step_count += 1
        total_reward += reward
        done = terminated or truncated

        cart_x = next_state[0]
        pole_deg = np.degrees(next_state[2])
        max_abs_angle = max(max_abs_angle, abs(pole_deg))

        if step_count == 1 or step_count % 20 == 0 or done:
            if not done:
                status = "안정적 균형 유지"
            elif truncated:
                status = "★ 성공 (200스텝 만점 완주!)"
            else:
                status = "실패 (전도)"
            print(f"{step_count:^6} | {action_name:^10} | {cart_x:^+10.3f} m | {pole_deg:^+10.2f}° | {status}")

        # 학생들이 균형 제어를 눈으로 관찰할 수 있도록 프레임 간격 조절
        time.sleep(0.02)
        state = next_state

    print("-" * 68)
    print("[*] 라이브 시연 종료 요약:")
    print(f"  - 총 버틴 스텝 수   : {step_count} 스텝 (최대 200스텝)")
    print(f"  - 총 획득 누적 보상 : {total_reward:.1f} 점 / 200.0 점")
    print(f"  - 주행 중 최대 기울기: ±{max_abs_angle:.2f}° (허용 한계 ±12.00° 이내 안정 제어)")
    print(f"  - 종료 사유         : {'200스텝 완주 성공 (Truncated)' if truncated else '막대 전도 (Terminated)'}")
    print("=" * 68)

    print("\n[안내] 200스텝 완주 장면을 확인하세요. 2초 후 창이 자동으로 닫힙니다...")
    time.sleep(2)
    env.close()


if __name__ == '__main__':
    trained_agent = train_agent(episodes=350, seed=42)
    evaluate_agent(trained_agent, n_tests=5, seed=1000)
    render_demo(trained_agent, seed=2025)
