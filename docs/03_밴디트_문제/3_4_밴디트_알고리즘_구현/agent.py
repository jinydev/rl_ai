import numpy as np

class Agent:
    """
    ε-탐욕(epsilon-greedy) 정책을 사용하여 다중 슬롯머신 문제를 해결하는 강화학습 에이전트 클래스
    """
    def __init__(self, epsilon, action_size=10):
        """
        에이전트 초기화 (기억 장치 설정)
        :param epsilon: 무작위 탐색 확률 (예: 0.1 이면 10% 확률로 무작위 탐색)
        :param action_size: 선택 가능한 슬롯머신(행동)의 총 대수 (기본값: 10)
        """
        self.epsilon = epsilon           # 무작위 행동 확률 (탐색 확률)
        self.Qs = np.zeros(action_size)  # 각 슬롯머신의 가치 추정치 배열 (초기값: 모두 0.0)
        self.ns = np.zeros(action_size)  # 각 슬롯머신의 누적 플레이 횟수 배열 (초기값: 모두 0)

    def update(self, action, reward):
        """
        플레이 경험(행동과 보상)을 바탕으로 가치 추정치를 증분 방식으로 갱신 (학습)
        :param action: 플레이한 슬롯머신 번호 (인덱스)
        :param reward: 슬롯머신으로부터 획득한 보상 (1 또는 0)
        """
        self.ns[action] += 1  # 해당 슬롯머신의 플레이 횟수 1 증가
        # 증분 가치 갱신 공식: Q(a) <- Q(a) + (1 / N(a)) * (R - Q(a))
        self.Qs[action] += (reward - self.Qs[action]) / self.ns[action]

    def get_action(self):
        """
        ε-탐욕(epsilon-greedy) 정책에 따라 다음으로 플레이할 슬롯머신(행동) 선택
        :return: 선택된 슬롯머신 인덱스 (0 ~ action_size-1)
        """
        # 1. ε의 확률로 무작위 탐색 (Exploration): 새로운 기회를 위해 임의의 머신 선택
        if np.random.rand() < self.epsilon:
            return np.random.randint(0, len(self.Qs))
        
        # 2. (1 - ε)의 확률로 탐욕적 활용 (Exploitation): 현재까지 가장 가치 추정치가 높은 머신 선택
        return np.argmax(self.Qs)

if __name__ == "__main__":
    from bandit1 import Bandit

    print("=== Agent 클래스 동작 테스트 ===")
    bandit = Bandit()
    agent = Agent(epsilon=0.1, action_size=10)

    print(f"설정된 탐색률 ε: {agent.epsilon}")
    print(f"초기 가치 추정치 Qs: {agent.Qs}")
    print(f"초기 플레이 횟수 ns: {agent.ns.astype(int)}")
    print("-" * 60)

    # 10회 플레이 테스트
    for step in range(1, 11):
        action = agent.get_action()   # 1. 행동 선택 (ε-탐욕 정책)
        reward = bandit.play(action)  # 2. 보상 획득 (슬롯머신 플레이)
        agent.update(action, reward)  # 3. 경험 학습 (증분 갱신)
        print(f"스텝 {step:2d} | 선택 머신: #{action} | 보상: {reward} | 현재 최고 가치 머신: #{np.argmax(agent.Qs)}")

    print("-" * 60)
    print("10회 플레이 후 가치 추정치 Qs:", np.round(agent.Qs, 3))
    print("10회 플레이 후 플레이 횟수 ns:", agent.ns.astype(int))
