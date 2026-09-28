# ch07/dp.py
"""
반복적 정책 평가 (Iterative Policy Evaluation) - 2개 딕셔너리 방식
교재: 07.2 동적 프로그래밍과 정책 평가
"""

def policy_eval_100_steps():
    print("=" * 60)
    print("실습 1: 2개 딕셔너리 방식 - 100회 고정 반복 갱신")
    print("=" * 60)

    # 1. 상태 가치 초깃값 설정 (V_0 = 0)
    V = {'L1': 0.0, 'L2': 0.0}
    new_V = V.copy()  # 계산 오염을 방지하기 위한 독립된 복사본

    print(f"초깃값: V = {V}\n")

    for k in range(1, 101):
        # 결정적 벨만 갱신식: V_{k+1}(s) = sum_a pi(a|s) * { r(s,a,s') + gamma * V_k(s') }
        # 상태 L1 갱신: 왼쪽(0.5, r=-1, s'=L1) + 오른쪽(0.5, r=+1, s'=L2)
        new_V['L1'] = 0.5 * (-1 + 0.9 * V['L1']) + 0.5 * (1 + 0.9 * V['L2'])

        # 상태 L2 갱신: 왼쪽(0.5, r=0, s'=L1) + 오른쪽(0.5, r=-1, s'=L2)
        new_V['L2'] = 0.5 * (0 + 0.9 * V['L1']) + 0.5 * (-1 + 0.9 * V['L2'])

        # 읽기용 딕셔너리에 새 가치 덮어쓰기 (다음 반복 준비)
        V = new_V.copy()

        # 주요 갱신 시점 출력
        if k in [1, 2, 3, 5, 10, 20, 50, 100]:
            print(f"[{k:3d}회 갱신] L1: {V['L1']:10.6f}, L2: {V['L2']:10.6f}")

    print("\n100회 갱신 완료!")
    print(f"최종 추정치: {V}")
    print(f"이론상 참값: [-2.25, -2.75]\n")


def policy_eval_with_threshold():
    print("=" * 60)
    print("실습 2: 2개 딕셔너리 방식 - 임곗값(threshold = 0.0001) 자동 중단")
    print("=" * 60)

    V = {'L1': 0.0, 'L2': 0.0}
    new_V = V.copy()

    threshold = 0.0001
    cnt = 0  # 갱신 횟수 기록

    while True:
        # L1 및 L2 가치 갱신
        new_V['L1'] = 0.5 * (-1 + 0.9 * V['L1']) + 0.5 * (1 + 0.9 * V['L2'])
        new_V['L2'] = 0.5 * (0 + 0.9 * V['L1']) + 0.5 * (-1 + 0.9 * V['L2'])

        # 갱신된 양의 최댓값 (delta) 측정
        delta = abs(new_V['L1'] - V['L1'])
        delta = max(delta, abs(new_V['L2'] - V['L2']))

        # 이전 가치를 새 가치로 교체
        V = new_V.copy()
        cnt += 1

        if cnt % 10 == 0:
            print(f"[갱신 {cnt:2d}회차] delta: {delta:.6f} | L1: {V['L1']:.5f}, L2: {V['L2']:.5f}")

        # 수렴 판정: 변화량이 임곗값보다 작아지면 갱신 중단
        if delta < threshold:
            print("-" * 60)
            print(f"수렴 완료! (임곗값 {threshold} 미만 도달)")
            print(f"총 갱신 횟수: {cnt}회")
            print(f"최종 가치 함수: L1 = {V['L1']:.6f}, L2 = {V['L2']:.6f}")
            print(f"참값 오차: L1 오차 = {abs(V['L1'] - (-2.25)):.6e}, L2 오차 = {abs(V['L2'] - (-2.75)):.6e}")
            print("=" * 60)
            break


if __name__ == '__main__':
    policy_eval_100_steps()
    policy_eval_with_threshold()
