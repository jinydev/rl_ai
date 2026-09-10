# monty_hall_and_binomial.py
# 몬티 홀 딜레마 및 독립시행 시뮬레이터

import random
import math

def monty_hall_simulation(trials=100000):
    stay_wins = 0
    switch_wins = 0
    random.seed(42)
    
    for _ in range(trials):
        # 3개의 문 중 무작위로 1곳에 자동차(1), 나머지 2곳에 염소(0) 배치
        doors = [0, 1, 2]
        car_door = random.randint(0, 2)
        player_choice = random.randint(0, 2)
        
        # 사회자는 플레이어가 선택하지 않았고, 자동차도 없는 꽝 문을 열어 공개
        possible_host_doors = [d for d in doors if d != player_choice and d != car_door]
        host_door = random.choice(possible_host_doors)
        
        # 선택을 바꿀 경우 남은 문
        switch_choice = [d for d in doors if d != player_choice and d != host_door][0]
        
        # 승리 카운팅
        if player_choice == car_door:
            stay_wins += 1
        if switch_choice == car_door:
            switch_wins += 1
            
    print(f"=== 몬티 홀 시뮬레이션 ({trials:,}회 시행) ===")
    print(f"1. 처음 선택 유지 시 승률: {stay_wins / trials * 100:.2f}% (이론값 33.33%)")
    print(f"2. 다른 문으로 변경 시 승률: {switch_wins / trials * 100:.2f}% (이론값 66.67%)")

def main():
    monty_hall_simulation()

    # 독립시행 양궁 계산
    n, r, p = 5, 2, 0.8
    binomial_prob = math.comb(n, r) * (p ** r) * ((1 - p) ** (n - r))
    print(f"\n양궁 5발 중 2발 명중 확률 (n=5, r=2, p=0.8): {binomial_prob * 100:.2f}%")

if __name__ == "__main__":
    main()
