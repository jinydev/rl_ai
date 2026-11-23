"""
[Step 03] env.step(action) 상태 전이 및 5-튜플 반환값 검사 스크립트

이 스크립트는 에이전트가 선택한 행동을 환경에 전달하여 1스텝 물리 시뮬레이션을 수행하고,
반환되는 5가지 정보(next_state, reward, terminated, truncated, info)의 이론적 의미를 확인합니다.
"""

import sys

try:
    import gymnasium as gym
except ImportError:
    import gym

def main():
    print("=" * 70)
    print(" 3단계: env.step(action) 1스텝 전이 및 5대 반환값 정밀 검사")
    print("=" * 70)

    try:
        env = gym.make('CartPole-v0', render_mode='rgb_array')
    except Exception:
        env = gym.make('CartPole-v1', render_mode='rgb_array')

    # 초기화
    reset_return = env.reset(seed=100)
    state = reset_return[0] if isinstance(reset_return, tuple) else reset_return

    print(f"[*] 초기 상태 (s_0): {state}\n")

    # 행동 수행: 카트를 오른쪽으로 밀기 (action = 1)
    action = 1
    print(f"[*] 에이전트가 행동 선택: a_0 = {action} (오른쪽 추진력 +10N 인가)")

    # 1스텝 전이 수행
    step_result = env.step(action)

    # 5-튜플 언패킹 (구버전 Gym 4개 반환 호환 처리)
    if len(step_result) == 5:
        next_state, reward, terminated, truncated, info = step_result
    else:
        next_state, reward, done, info = step_result
        terminated = done
        truncated = False

    print("\n" + "-" * 70)
    print(" env.step(action) 반환값 5-튜플 정밀 분석:")
    print("-" * 70)
    print(f"  1. next_state (차기 상태 s') : {next_state}")
    print(f"     - 상태 변화량 (Δs)         : {next_state - state}")
    print(f"  2. reward     (즉각 보상 R)   : {reward} (생존 성공 시 매 스텝 +1.0 지급)")
    print(f"  3. terminated (과제 실패 종료): {terminated}")
    print("     - 의미: 막대 각도 > 12° 이거나 카트 위치 > ±2.4m 도달 시 True")
    print(f"  4. truncated  (시간 초과 종료): {truncated}")
    print("     - 의미: MDP 외부 제약인 최대 스텝(200 또는 500) 도달 시 True")
    print(f"  5. info       (디버깅 부가정보): {info}")
    print("-" * 70)

    # 통합 종료 플래그 계산
    done = terminated or truncated
    print(f"\n[*] 에피소드 종료 여부 (done = terminated | truncated) : {done}")

    env.close()
    print("=" * 70)

if __name__ == '__main__':
    main()
