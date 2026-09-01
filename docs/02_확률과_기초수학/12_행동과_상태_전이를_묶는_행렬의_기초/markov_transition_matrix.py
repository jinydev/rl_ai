# markov_transition_matrix.py
# 마르코프 체인 상태 전이 행렬 시뮬레이터

import numpy as np

def main():
    # 1. 오늘 날씨 상태 확률분포 벡터 x0 (맑음 60%, 비 40%)
    x0 = np.array([0.6, 0.4])

    # 2. 상태 전이 확률 행렬 P
    # 행 0: 오늘 맑음 -> [내일 맑음 0.7, 내일 비 0.3]
    # 행 1: 오늘 비     -> [내일 맑음 0.4, 내일 비 0.6]
    P = np.array([
        [0.7, 0.3],
        [0.4, 0.6]
    ])

    print("=== 마르코프 체인 상태 전이 계산 ===")
    print("오늘 날씨 분포 (x0):", x0)

    # 1일 후 내일 날씨 x1 = x0 @ P
    x1 = np.dot(x0, P)
    print(f"1일 후 날씨 분포 (x1): 맑음 {x1[0]:.4f}, 비 {x1[1]:.4f}")

    # 2일 후 모레 날씨 x2 = x1 @ P = x0 @ P^2
    x2 = np.dot(x1, P)
    print(f"2일 후 날씨 분포 (x2): 맑음 {x2[0]:.4f}, 비 {x2[1]:.4f}")

    # 10일 후 장기 정상 상태 분포 x10
    x_current = x0.copy()
    for day in range(1, 11):
        x_current = np.dot(x_current, P)

    print(f"\n10일 후 수렴 분포 (x10): 맑음 {x_current[0]:.4f}, 비 {x_current[1]:.4f}")
    print(f"이론적 정상 분포 (4/7, 3/7): 맑음 {4/7:.4f}, 비 {3/7:.4f}")

if __name__ == "__main__":
    main()
