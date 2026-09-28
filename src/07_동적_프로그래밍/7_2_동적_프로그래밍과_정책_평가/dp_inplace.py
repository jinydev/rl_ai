# ch07/dp_inplace.py
"""
반복적 정책 평가 (Iterative Policy Evaluation) - 덮어쓰기(In-place) 방식
교재: 07.2 동적 프로그래밍과 정책 평가
"""

def policy_eval_inplace():
    print("=" * 60)
    print("실습 3: 덮어쓰기(In-place) 방식 - 1개 딕셔너리 즉시 갱신")
    print("=" * 60)

    # 1개의 딕셔너리만 선언하여 즉시 덮어쓰기
    V = {'L1': 0.0, 'L2': 0.0}
    threshold = 0.0001
    cnt = 0

    print(f"초깃값: V = {V}\n")

    while True:
        # 1. 상태 L1 갱신 (새 가치를 임시 변수 t에 계산 후 즉시 V['L1']에 덮어씀)
        t = 0.5 * (-1 + 0.9 * V['L1']) + 0.5 * (1 + 0.9 * V['L2'])
        delta = abs(t - V['L1'])
        V['L1'] = t

        # 2. 상태 L2 갱신 (방금 갱신된 새로운 V['L1']의 최신 값을 '즉시' 활용!)
        t = 0.5 * (0 + 0.9 * V['L1']) + 0.5 * (-1 + 0.9 * V['L2'])
        delta = max(delta, abs(t - V['L2']))
        V['L2'] = t

        cnt += 1

        if cnt % 10 == 0:
            print(f"[갱신 {cnt:2d}회차] delta: {delta:.6f} | L1: {V['L1']:.5f}, L2: {V['L2']:.5f}")

        # 수렴 판정
        if delta < threshold:
            print("-" * 60)
            print(f"수렴 완료! (임곗값 {threshold} 미만 도달)")
            print(f"총 갱신 횟수: {cnt}회")
            print(f"최종 가치 함수: L1 = {V['L1']:.6f}, L2 = {V['L2']:.6f}")
            print(f"참값 오차: L1 오차 = {abs(V['L1'] - (-2.25)):.6e}, L2 오차 = {abs(V['L2'] - (-2.75)):.6e}")
            print("=" * 60)
            print("\n💡 성능 비교 요약:")
            print("- 기존 2개 딕셔너리 방식: 76회 갱신")
            print(f"- 새로운 덮어쓰기(In-place) 방식: {cnt}회 갱신 (약 21% 연산 속도 향상!)")
            print("=" * 60)
            break


if __name__ == '__main__':
    policy_eval_inplace()
