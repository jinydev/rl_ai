from bandit1 import Bandit

# 1. 10대 슬롯머신 환경 객체 생성 및 0번 머신 가치 추정치(Q) 초기화
bandit = Bandit()
Q = 0  # 0번째 슬롯머신의 초기 가치 추정치

print(f"0번째 슬롯머신의 숨겨진 실제 승률: {bandit.rates[0]:.4f}")
print("=" * 45)
print("회차 | 보상(Reward) | 갱신된 가치 추정치(Q)")
print("-" * 45)

# 2. 0번째 슬롯머신을 10번 플레이하며 증분 방식으로 Q값 갱신
for n in range(1, 11):  # n = 1, 2, ..., 10
    reward = bandit.play(0)  # 0번째 슬롯머신 플레이
    Q += (reward - Q) / n  # 증분 가치 갱신 공식 적용
    print(f" {n:2d}회 |     {reward}        |       {Q:.4f}")

print("=" * 45)
print(f"최종 추정 가치 Q: {Q:.4f} (실제 승률: {bandit.rates[0]:.4f})")
