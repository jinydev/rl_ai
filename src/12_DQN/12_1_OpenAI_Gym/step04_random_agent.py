"""
[Step 04] 무작위(Random) 에이전트 전체 에피소드 실행 및 성적 분석 스크립트

이 스크립트는 행동 가치 평가나 학습 없이 주사위를 던지듯 무작위(action = 0 or 1)로 카트를 조작하는
랜덤 에이전트를 구동하여, 몇 스텝 만에 균형을 잃고 실패하는지 정량적으로 측정하고 렌더 프레임을 캡처합니다.
"""

import os
import sys
import numpy as np

try:
    import gymnasium as gym
except ImportError:
    import gym

def main():
    print("=" * 65)
    print(" 4단계: 무작위(Random) 에이전트 에피소드 루프 실행 및 성능 분석")
    print("=" * 65)

    # 1. 시뮬레이터 환경 생성 (화면 프레임 렌더링 지원)
    try:
        env = gym.make('CartPole-v0', render_mode='rgb_array')
    except Exception:
        env = gym.make('CartPole-v1', render_mode='rgb_array')

    # 재현성을 위한 시드 설정
    reset_return = env.reset(seed=2024)
    state = reset_return[0] if isinstance(reset_return, tuple) else reset_return

    step_count = 0
    total_reward = 0.0
    done = False

    print("\n[*] 에피소드 시작 (시드: 2024)")
    print(f"  초기 상태: {state}")
    print("-" * 65)
    print(f"{'스텝':^6}|{'선택 행동':^12}|{'카트 위치':^12}|{'막대 각도(도)':^14}|{'즉각 보상':^8}|{'종료 여부':^8}")
    print("-" * 65)

    saved_frames = []

    while not done:
        # 화면 프레임 캡처
        frame = env.render()
        if frame is not None:
            saved_frames.append(frame)

        # 무작위 행동 선택 (0: 좌측 밀기, 1: 우측 밀기)
        action = np.random.choice([0, 1])

        # 1스텝 환경 상호작용
        step_result = env.step(action)
        if len(step_result) == 5:
            next_state, reward, terminated, truncated, info = step_result
        else:
            next_state, reward, done_flag, info = step_result
            terminated = done_flag
            truncated = False

        step_count += 1
        total_reward += reward
        done = terminated or truncated

        # 상태 물리량 변환 (라디안 -> 디그리)
        cart_x = next_state[0]
        pole_deg = np.degrees(next_state[2])
        action_str = "0 (좌측)" if action == 0 else "1 (우측)"

        print(f"{step_count:^6}|{action_str:^12}|{cart_x:^+11.3f}m|{pole_deg:^+13.2f}°|{reward:^8.1f}|{str(done):^8}")

        state = next_state

    env.close()

    print("-" * 65)
    print(f"\n[실행 요약]")
    print(f"  - 총 생존 타임스텝 : {step_count} 스텝")
    print(f"  - 총 획득 누적 보상: {total_reward} 점")
    print(f"  - 종료 원인        : {'막대 쓰러짐 또는 탈선 (Terminated)' if terminated else '최대 시간 도달 (Truncated)'}")
    print(f"  - 시사점           : 정책 학습이 없는 무작위 선택은 평균 10~20스텝 내외로 파국을 맞이함.")
    print("=" * 65)

    return saved_frames

if __name__ == '__main__':
    main()
