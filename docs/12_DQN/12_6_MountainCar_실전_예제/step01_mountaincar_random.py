"""
[실습 1단계] 마운틴 카(MountainCar-v0) 환경 구조 확인 및 무작위 에이전트 체험
============================================================================
카트폴과 달리 마운틴 카는 자동차 엔진 출력이 약해 정면으로는 언덕을 오를 수 없으며,
오른쪽 정상 깃발(position >= 0.5)에 도달하기 전까지 매 스텝 -1의 희소(Sparse) 보상을 받습니다.
무작위 에이전트가 200스텝 동안 계곡 바닥에서 헛바퀴만 돌다 실패하는 모습을 확인합니다.
"""

import time
import warnings
import numpy as np
import gym

warnings.filterwarnings('ignore')


def main():
    np.random.seed(42)
    env = gym.make('MountainCar-v0', render_mode='human')

    print("=" * 68)
    print(" [실습 1단계] MountainCar-v0 환경 스펙 및 무작위 에이전트 실행")
    print("=" * 68)
    print(f" * 환경 식별자 (Spec ID)  : {env.spec.id}")
    print(f" * 관찰 공간 (State Space): {env.observation_space}")
    print("     -> [0] 위치(Position): -1.2 ~ +0.6 (목표 깃발: +0.5 이상)")
    print("     -> [1] 속도(Velocity): -0.07 ~ +0.07")
    print(f" * 행동 공간 (Action Space): {env.action_space}")
    print("     -> 0: 좌측 가속(←) | 1: 정지/관성(·) | 2: 우측 가속(→)")
    print("-" * 68)
    print(f"{'스텝':^6} | {'선택 행동':^12} | {'자동차 위치':^12} | {'자동차 속도':^12} | {'상태'}")
    print("-" * 68)

    state = env.reset(seed=42)[0]
    done = False
    step_count = 0
    total_reward = 0.0
    max_position = state[0]
    action_labels = {0: "0 (← 좌측)", 1: "1 (· 관성)", 2: "2 (→ 우측)"}

    while not done:
        env.render()
        action = int(np.random.choice([0, 1, 2]))
        next_state, reward, terminated, truncated, _ = env.step(action)

        step_count += 1
        total_reward += reward
        done = terminated or truncated
        max_position = max(max_position, float(next_state[0]))

        if step_count == 1 or step_count % 40 == 0 or done:
            if terminated:
                status = "★ 정상 깃발 도달 성공!"
            elif truncated:
                status = "실패 (200스텝 시간 초과)"
            else:
                status = "계곡 진동 중..."
            print(f"{step_count:^6} | {action_labels[action]:^12} | {next_state[0]:^+10.3f}   | {next_state[1]:^+10.4f}   | {status}")

        time.sleep(0.01)
        state = next_state

    print("-" * 68)
    print("[*] 무작위 에이전트 종료 요약:")
    print(f"  - 총 진행 스텝     : {step_count} 스텝")
    print(f"  - 총 획득 보상     : {total_reward:.1f} 점 (도달 실패 시 -200.0점)")
    print(f"  - 도달한 최고 위치 : {max_position:+.3f} (목표 깃발 +0.500 대비 미달)")
    print(f"  - 깃발 도달 여부   : {'성공 (Terminated)' if terminated else '실패 (Truncated)'}")
    print("=" * 68)
    print("\n[안내] 무작위 조작으로는 언덕에 오를 수 없습니다. 2초 후 창이 닫힙니다...")
    time.sleep(2)
    env.close()


if __name__ == '__main__':
    main()
