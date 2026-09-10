import numpy as np
from bandit1 import Bandit

# =====================================================================
# 10대 슬롯머신 전체 가치 추정 확장 실습
# =====================================================================

# 1. 10대 슬롯머신 환경 객체 생성
bandit = Bandit()

# 2. 10대 슬롯머신의 가치 추정치(Qs)와 플레이 횟수(ns)를 0으로 초기화
Qs = np.zeros(10)  # 각 슬롯머신의 가치 추정치 배열 (초기값: 모두 0.0)
ns = np.zeros(10)  # 각 슬롯머신을 플레이한 횟수 기록 배열 (초기값: 모두 0)

print("10대 슬롯머신의 실제 숨겨진 승률:")
for i, rate in enumerate(bandit.rates):
    print(f"머신 #{i}: {rate:.3f}", end=" | ")
print("\n" + "=" * 65)

# 3. 10번 동안 무작위로 슬롯머신을 골라 플레이하고 가치 추정치(Qs) 갱신
for n in range(1, 11):
    # 0번부터 9번까지의 슬롯머신 중 하나를 무작위로 선택 (탐색 행동)
    action = np.random.randint(0, 10)
    
    # 선택한 슬롯머신의 레버를 당겨 보상(1 또는 0) 획득
    reward = bandit.play(action)
    
    # 해당 슬롯머신의 플레이 횟수 1 증가
    ns[action] += 1
    
    # 증분 가치 갱신 공식 적용: Q(a) <- Q(a) + (1 / N(a)) * (R - Q(a))
    Qs[action] += (reward - Qs[action]) / ns[action]
    
    print(f"시행 {n:2d}회 | 선택 머신: #{action} | 획득 보상: {reward} | 누적 횟수 ns[{action}]: {int(ns[action])}")
    print(f" -> 현재 Qs 추정치: {np.round(Qs, 2)}")
    print("-" * 65)

print("\n[최종 결과]")
print("각 머신별 플레이 횟수 ns:", ns.astype(int))
print("각 머신별 추정 가치   Qs:", np.round(Qs, 3))
