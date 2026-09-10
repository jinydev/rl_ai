# points_and_combination.py
# 상금 분배 문제와 조합 확률 계산기

import math

def main():
    # 1. 상금 분배 문제 (도로시 2승 vs 토토 1승, 3승 선승제)
    total_prize = 800000  # 총 상금 80만원
    p_dorothy_win = 0.5 + (0.5 * 0.5)  # 1/2 + 1/4 = 0.75
    p_toto_win = 0.5 * 0.5             # 1/4 = 0.25

    dorothy_share = int(total_prize * p_dorothy_win)
    toto_share = int(total_prize * p_toto_win)

    print("=== 1. 상금 분배 문제 계산 결과 ===")
    print(f"도로시 우승 확률: {p_dorothy_win * 100:.1f}% -> 배분 상금: {dorothy_share:,}원")
    print(f"토토 우승 확률: {p_toto_win * 100:.1f}% -> 배분 상금: {toto_share:,}원")

    # 2. 조합을 이용한 구슬 주머니 확률 계산 (흰 공 3, 검은 공 5 중 3개 추출)
    total_combinations = math.comb(8, 3)                # 8C3 = 56
    target_combinations = math.comb(3, 1) * math.comb(5, 2)  # 3C1 * 5C2 = 3 * 10 = 30
    prob_balls = target_combinations / total_combinations

    print("\n=== 2. 조합 활용 구슬 추출 확률 ===")
    print(f"전체 경우의 수 (8C3): {total_combinations}가지")
    print(f"흰 공 1개, 검은 공 2개 경우의 수 (3C1 * 5C2): {target_combinations}가지")
    print(f"최종 추출 확률: {prob_balls:.5f} ({prob_balls * 100:.2f}%)")

if __name__ == "__main__":
    main()
