import platform
import numpy as np
import matplotlib.pyplot as plt

# ==========================================
# 0. 운영체제별 한글 폰트 설정 (깨짐 방지)
# ==========================================
os_name = platform.system()
if os_name == "Darwin":  # Mac OS
    plt.rc("font", family="AppleGothic")
elif os_name == "Windows":  # Windows OS
    plt.rc("font", family="Malgun Gothic")
else:  # Linux (Colab, Ubuntu 등)
    plt.rc("font", family="NanumGothic")

# 마이너스 부호(-) 깨짐 방지
plt.rcParams["axes.unicode_minus"] = False


class NonStatBandit:
    """
    비정상(Non-stationary) 슬롯머신 환경
    - 머신의 당첨 확률이 고정되지 않고, 플레이할 때마다 평균 0, 표준편차 0.1의 노이즈가 더해져 계속 변합니다.
    """
    def __init__(self, arms=10):
        self.arms = arms
        self.rates = np.random.rand(arms)  # 초기 10개 슬롯머신 승률 (0.0 ~ 1.0)

    def play(self, arm):
        rate = self.rates[arm]
        # 플레이할 때마다 모든 슬롯머신의 승률에 무작위 노이즈를 추가 (비정상 문제의 핵심)
        self.rates += 0.1 * np.random.randn(self.arms)
        if rate > np.random.rand():
            return 1
        else:
            return 0


class Agent:
    """
    기존 표본 평균(Sample Average) 방식의 에이전트
    - 과거의 모든 보상을 동일한 가중치(1/n)로 평균냅니다.
    """
    def __init__(self, epsilon, action_size=10):
        self.epsilon = epsilon
        self.Qs = np.zeros(action_size)
        self.ns = np.zeros(action_size)

    def update(self, action, reward):
        self.ns[action] += 1
        # 표본 평균 갱신: Q_n = Q_{n-1} + (1/n) * (R_n - Q_{n-1})
        self.Qs[action] += (reward - self.Qs[action]) / self.ns[action]

    def get_action(self):
        if np.random.rand() < self.epsilon:
            return np.random.randint(0, len(self.Qs))
        return np.argmax(self.Qs)


class AlphaAgent:
    """
    고정 학습률 α(Constant Alpha) 방식의 에이전트 (지수 이동 평균, EMA)
    - 과거의 보상 가중치를 기하급수적으로 감소시키고, 최신 보상에 더 큰 가중치를 부여합니다.
    """
    def __init__(self, epsilon, alpha, actions=10):
        self.epsilon = epsilon
        self.Qs = np.zeros(actions)
        self.alpha = alpha  # 고정 학습률 α (0 < α < 1)

    def update(self, action, reward):
        # 고정값 α 갱신: Q_n = Q_{n-1} + α * (R_n - Q_{n-1})
        self.Qs[action] += (reward - self.Qs[action]) * self.alpha

    def get_action(self):
        if np.random.rand() < self.epsilon:
            return np.random.randint(0, len(self.Qs))
        return np.argmax(self.Qs)


if __name__ == "__main__":
    runs = 200        # 독립적인 반복 실험 횟수 (몬테카를로 평균)
    steps = 1000      # 1회 실험당 레버를 당기는 단계 수
    epsilon = 0.1     # 탐색 확률 (10%)
    alpha = 0.8       # 고정 학습률 (최신 정보 80% 반영)
    
    print("비정상 밴디트 문제 시뮬레이션을 시작합니다 (200회 반복 평균)...")
    
    np.random.seed(0)
    all_rates_sample = np.zeros((runs, steps))
    all_rates_alpha = np.zeros((runs, steps))
    
    for run in range(runs):
        # 1. 표본 평균 에이전트 실행 (과거를 잊지 못하는 에이전트)
        bandit_s = NonStatBandit()
        agent_s = Agent(epsilon)
        total_reward_s = 0
        rates_s = []
        for step in range(steps):
            action = agent_s.get_action()
            reward = bandit_s.play(action)
            agent_s.update(action, reward)
            total_reward_s += reward
            rates_s.append(total_reward_s / (step + 1))
        all_rates_sample[run] = rates_s
        
        # 2. 고정값 α 에이전트 실행 (최신 트렌드에 빠르게 적응하는 에이전트)
        bandit_a = NonStatBandit()
        agent_a = AlphaAgent(epsilon, alpha)
        total_reward_a = 0
        rates_a = []
        for step in range(steps):
            action = agent_a.get_action()
            reward = bandit_a.play(action)
            agent_a.update(action, reward)
            total_reward_a += reward
            rates_a.append(total_reward_a / (step + 1))
        all_rates_alpha[run] = rates_a
        
    avg_s = np.average(all_rates_sample, axis=0)
    avg_a = np.average(all_rates_alpha, axis=0)
    
    print("시뮬레이션 완료. 그래프를 화면에 출력합니다.")
    
    # 결과 그래프 시각화
    plt.figure(figsize=(9, 5.5))
    plt.plot(avg_s, label='표본 평균 (Sample Average: 1/n)', color='#3498db', linewidth=1.8)
    plt.plot(avg_a, label='고정값 α 갱신 (Alpha Const: α=0.8)', color='#e67e22', linewidth=2.0)
    plt.xlabel('학습 단계 (Steps)', fontsize=12)
    plt.ylabel('평균 승률 (Average Rates)', fontsize=12)
    plt.title('비정상 밴디트 문제: 표본 평균 vs 고정값 α 갱신 성능 비교', fontsize=14, pad=12)
    plt.legend(fontsize=11)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.show()
