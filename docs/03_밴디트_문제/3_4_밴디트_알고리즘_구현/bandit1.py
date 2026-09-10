import numpy as np

class Bandit:
    def __init__(self, arms=10):  # arms = 슬롯머신 대수 (매직 메서드: 객체 생성 시 자동 호출)
        self.rates = np.random.rand(arms)  # 슬롯머신 각각의 승률 설정(무작위)

    def play(self, arm):  # arm번째 슬롯머신 플레이 메서드
        rate = self.rates[arm]
        if rate > np.random.rand():
            return 1  # 승리: 코인 1개 획득
        else:
            return 0  # 패배: 코인 0개 (꽝)

if __name__ == "__main__":
    bandit = Bandit()
    print("10대 슬롯머신의 무작위 실제 승률:", np.round(bandit.rates, 3))
    
    print("\n0번째 슬롯머신 3회 플레이 테스트:")
    for i in range(3):
        print(f"{i+1}번째 시도 보상:", bandit.play(0))
