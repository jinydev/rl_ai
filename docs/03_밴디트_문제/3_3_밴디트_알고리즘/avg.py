import numpy as np

def run_average_simulation():
    print("==================================================")
    # [방식 1] 나이브한 표본 평균 계산 (메모리 및 계산량이 계속 늘어나는 방식)
    print("[방식 1] 전체 보상을 보관하여 평균 계산 (Naive sample mean)")
    print("==================================================")
    np.random.seed(0)  # 시드 고정
    rewards = []
    for n in range(1, 11):  # 10번 플레이
        reward = np.random.rand()  # 보상 시뮬레이션
        rewards.append(reward)
        Q = sum(rewards) / n
        print(f"시도 {n:2d}회차 | 방금 얻은 보상: {reward:.6f} | 추정 가치 Q: {Q:.6f}")

    print("\n==================================================")
    # [방식 2] 증분 구현 (메모리와 계산량이 늘지 않고 직전 추정치와 횟수만으로 계산)
    print("[방식 2] 증분 구현으로 평균 계산 (Incremental implementation)")
    print("==================================================")
    np.random.seed(0)  # 시드 고정 (동일한 난수 흐름 보장)
    Q = 0.0
    for n in range(1, 11):  # 10번 플레이
        reward = np.random.rand()  # 보상 시뮬레이션
        Q = Q + (reward - Q) / n  # 식 1.5 적용
        print(f"시도 {n:2d}회차 | 방금 얻은 보상: {reward:.6f} | 추정 가치 Q: {Q:.6f}")

    print("\n※ 시드를 똑같이 고정했기 때문에 방식 1과 방식 2의 결과는 소수점 아래까지 완전히 일치합니다.")

if __name__ == "__main__":
    run_average_simulation()
