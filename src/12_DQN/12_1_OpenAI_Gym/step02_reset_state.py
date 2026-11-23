"""
[Step 02] 환경 초기화(reset) 및 4차원 상태 벡터 & 행동 공간 검사 스크립트

이 스크립트는 env.reset()을 호출하여 초기 상태를 획득하고,
카트폴의 4대 연속 물리 상태 변수와 Discrete(2) 행동 공간을 정밀 검사합니다.
"""

import sys
import numpy as np

try:
    import gymnasium as gym
except ImportError:
    import gym

def main():
    print("=" * 65)
    print(" 2단계: env.reset() 초기화 및 4차원 상태 벡터 / 행동 공간 검사")
    print("=" * 65)

    # 1. 환경 생성
    try:
        env = gym.make('CartPole-v0', render_mode='rgb_array')
    except Exception:
        env = gym.make('CartPole-v1', render_mode='rgb_array')

    # 2. 환경 초기화 및 상태 언패킹
    #    Gymnasium / 최신 Gym의 reset()은 (state, info) 튜플을 반환하므로 [0]으로 상태 추출
    reset_return = env.reset(seed=42)
    if isinstance(reset_return, tuple):
        state = reset_return[0]
        info = reset_return[1]
    else:
        state = reset_return
        info = {}

    print("\n[1] 상태(State/Observation) 검사:")
    print(f"  - 원시 상태 배열       : {state}")
    print(f"  - 데이터 타입(dtype)   : {state.dtype}")
    print(f"  - 텐서 형태 (Shape)    : {state.shape} (4차원 연속 벡터)")

    # 4대 물리 상태 변수 분해
    cart_pos, cart_vel, pole_angle, pole_vel = state
    print("\n[2] 오일러-라그랑주 역학계 4대 연속 상태 변수 분해:")
    print(f"  1. 카트 위치 ($x$)        : {cart_pos:+.6f} [m]       (실패 한계: ±2.4 m)")
    print(f"  2. 카트 속도 ($\dot{{x}}$)  : {cart_vel:+.6f} [m/s]")
    print(f"  3. 막대 각도 ($\\theta$)    : {pole_angle:+.6f} [rad]     (실패 한계: ±12° ≈ ±0.2094 rad)")
    print(f"  4. 막대 각속도 ($\dot{{\\theta}}$): {pole_vel:+.6f} [rad/s]")

    # 3. 행동 공간(Action Space) 검사
    action_space = env.action_space
    print("\n[3] 행동 공간(Action Space) 검사:")
    print(f"  - 행동 공간 클래스     : {action_space}")
    print(f"  - 가능한 이산 행동 수  : {action_space.n} 개 (Discrete(2))")
    print("  - 행동 0의 물리적 의미 : 카트를 '왼쪽'으로 밀기 (← Force = -10 N)")
    print("  - 행동 1의 물리적 의미 : 카트를 '오른쪽'으로 밀기 (→ Force = +10 N)")

    # 샘플링 테스트
    sample_actions = [action_space.sample() for _ in range(5)]
    print(f"  - 무작위 행동 샘플 5회 : {sample_actions}")

    env.close()
    print("\n[완료] 상태 및 행동 공간 사양 검증 완료.")
    print("=" * 65)

if __name__ == '__main__':
    main()
