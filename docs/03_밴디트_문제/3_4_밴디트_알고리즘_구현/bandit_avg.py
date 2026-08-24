import numpy as np
import matplotlib.pyplot as plt
from bandit import Bandit, Agent

def run_simulation(epsilon, runs=200, steps=1000):
    all_rates = np.zeros((runs, steps))
    for run in range(runs):
        bandit = Bandit()
        agent = Agent(epsilon)
        total_reward = 0
        rates = []
        for step in range(steps):
            action = agent.get_action()
            reward = bandit.play(action)
            agent.update(action, reward)
            total_reward += reward
            rates.append(total_reward / (step + 1))
        all_rates[run] = rates
    return np.average(all_rates, axis=0)

if __name__ == "__main__":
    runs = 200
    steps = 1000
    
    print("실험을 시작합니다 (실행 시간이 다소 걸릴 수 있습니다)...")
    
    # 1. ε = 0.1 에 대한 200번 평균 승률 구하기
    print("ε = 0.1 시뮬레이션 중...")
    avg_rates = run_simulation(0.1, runs, steps)
    
    plt.figure(figsize=(6, 4))
    plt.ylabel('Rates')
    plt.xlabel('Steps')
    plt.title('단계별 승률 (200번 실험 후 평균)')
    plt.plot(avg_rates)
    plt.show()

    # 2. 다양한 ε 값 비교 (0.01 vs 0.1 vs 0.3)
    print("다양한 ε 값 비교 시뮬레이션 중...")
    epsilons = [0.01, 0.1, 0.3]
    plt.figure(figsize=(8, 5))
    
    for eps in epsilons:
        print(f"ε = {eps} 진행 중...")
        rates = run_simulation(eps, runs, steps)
        plt.plot(rates, label=f"ε = {eps}")
        
    plt.ylabel('Rates')
    plt.xlabel('Steps')
    plt.title('ε-탐욕 정책의 ε값을 바꾼 결과 비교')
    plt.legend()
    plt.show()
