from bandit1 import Bandit

# 10대 슬롯머신 환경 객체 생성
bandit = Bandit()

# 0번째 슬롯머신을 3회 연속으로 플레이 테스트
for i in range(3):
    print(bandit.play(0))
