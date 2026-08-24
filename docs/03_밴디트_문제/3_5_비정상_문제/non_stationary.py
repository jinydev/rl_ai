import numpy as np
import matplotlib.pyplot as plt

class NonStatBandit:
    def __init__(self, arms=10):
        self.arms = arms
        self.rates = np.random.rand(arms)

    def play(self, arm):
        rate = self.rates[arm]
        self.rates += 0.1 * np.random.randn(self.arms)  # 플레이 시마다 노이즈 추가(비정상 문제)
        if rate > np.random.rand():
            return 1
        else:
            return 0

class Agent:
    def __init__(self, epsilon, action_size=10):
        self.epsilon = epsilon
        self.Qs = np.zeros(action_size)
        self.ns = np.zeros(action_size)

    def update(self, action, reward):
        self.ns[action] += 1
        self.Qs[action] += (reward - self.Qs[action]) / self.ns[action]

    def get_action(self):
        if np.random.rand() < self.epsilon:
            return np.random.randint(0, len(self.Qs))
        return np.argmax(self.Qs)

class AlphaAgent:
    def __init__(self, epsilon, alpha, actions=10):
        self.epsilon = epsilon
        self.Qs = np.zeros(actions)
        self.alpha = alpha  # 고정값 α

    def update(self, action, reward):
        # α로 갱신
        self.Qs[action] += (reward - self.Qs[action]) * self.alpha

    def get_action(self):
        if np.random.rand() < self.epsilon:
            return np.random.randint(0, len(self.Qs))
        return np.argmax(self.Qs)

if __name__ == "__main__":
    runs = 200
    steps = 1000
    epsilon = 0.1
    alpha = 0.8
    
    print("비정상 문제 시뮬레이션을 시작합니다 (200회 반복)...")
    
    np.random.seed(0)
    all_rates_sample = np.zeros((runs, steps))
    all_rates_alpha = np.zeros((runs, steps))
    
    for run in range(runs):
        # 1. 표본 평균 에이전트 실행
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
        
        # 2. 고정값 α 에이전트 실행
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
    
    print("시뮬레이션 완료. 그래프를 표시합니다.")
    
    # 결과 그래프
    plt.figure(figsize=(8, 5))
    plt.plot(avg_s, label='sample average')
    plt.plot(avg_a, label='alpha const update (α=0.8)')
    plt.xlabel('Steps')
    plt.ylabel('Average Rates')
    plt.title('Sample Average vs Constant Alpha Update in Non-Stationary Bandit')
    plt.legend()
    plt.grid(True)
    plt.show()
