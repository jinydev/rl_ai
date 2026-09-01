# perm_comb_calculator.py
# 파이썬으로 구현하는 순열과 조합 계산기

import itertools
import math

def main():
    items = ['A', 'B', 'C', 'D']
    n = len(items)
    r = 2

    # 1. math 모듈을 사용한 총 경우의 수 계산
    perm_count = math.perm(n, r)  # 4P2 = 12
    comb_count = math.comb(n, r)  # 4C2 = 6

    print(f"4개 중 2개를 순서 있게 나열하는 순열(4P2) 개수: {perm_count}")
    print(f"4개 중 2개를 순서 없이 뽑는 조합(4C2) 개수: {comb_count}")

    # 2. itertools 모듈을 사용한 실제 요소 묶음 목록 생성
    perm_list = list(itertools.permutations(items, r))
    comb_list = list(itertools.combinations(items, r))

    print("\n[순열 목록 (순서 있음)]:", perm_list)
    print("[조합 목록 (순서 없음)]:", comb_list)

if __name__ == "__main__":
    main()
