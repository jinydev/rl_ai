# law_of_large_numbers.py
# 대수의 법칙 동전 던지기 시뮬레이터

import random

def simulate_law_of_large_numbers(trials_list):
    print("=== 대수의 법칙 동전 던지기 시뮬레이션 ===")
    random.seed(42)  # 재현성을 위한 시드 고정
    
    for n in trials_list:
        heads_count = 0
        for _ in range(n):
            # 1: 앞면, 0: 뒷면
            if random.randint(0, 1) == 1:
                heads_count += 1
                
        relative_frequency = heads_count / n
        error = abs(relative_frequency - 0.5)
        print(f"시행 횟수 N = {n:7,d} | 앞면 횟수 = {heads_count:7,d} | "
              f"상대도수 = {relative_frequency:.5f} | 오차 = {error:.5f}")

def main():
    # 시행 횟수를 10회부터 1,000,000회까지 기하급수적으로 증가
    trials = [10, 50, 100, 500, 1000, 10000, 100000, 1000000]
    simulate_law_of_large_numbers(trials)

if __name__ == "__main__":
    main()
