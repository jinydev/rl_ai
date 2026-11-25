"""
[실습 1단계] 아타리 팩맨(Atari Pac-Man) 환경 구조 확인 및 무작위 에이전트 실행
=================================================================================
아타리 2600 규격(210 x 160 RGB 화면, 13x11 클래식 미로, 쿠키 70개, 3인 유령, 4개 행동)
환경에서 학습되지 않은 무작위(Random) 에이전트가 유령을 피하지 못하고 벽에 부딪히며
금세 3개의 생명을 모두 잃는 모습을 확인합니다.
"""

import time
import numpy as np
from atari_pacman_env import AtariPacmanEnv


def main():
    np.random.seed(42)
    env = AtariPacmanEnv(render_mode="human", max_steps=400, lives=3)
    obs, info = env.reset(seed=42)
    rgb_frame = env.get_rgb_frame()

    print("=" * 74)
    print(" [실습 1단계] 아타리 팩맨(Pac-Man) 환경 스펙 및 무작위 에이전트")
    print("=" * 74)
    print(f" * 원본 아타리 RGB 화면 형상 : {rgb_frame.shape} (dtype: {rgb_frame.dtype})")
    print(f" * 정규화 상태 벡터 형상     : {obs.shape} -> [벽(4), 쿠키방향(4), 유령위협(4), 포식방향(4), 파워/진행(2)]")
    print(f" * 행동 공간 (Action Space)  : {env.action_space} (0: ↑ 위, 1: ↓ 아래, 2: ← 좌측, 3: → 우측)")
    print(f" * 전체 쿠키 수 / 초기 생명  : {info['total_pellets']}개 (파워 4개 포함) / {info['lives']}목숨")
    print("-" * 74)
    print(f"{'스텝':^6} | {'선택 행동':^12} | {'누적 점수':^10} | {'먹은 쿠키':^10} | {'포식 유령':^10} | {'생명'}")
    print("-" * 74)

    done = False
    step_count = 0
    action_names = {0: "0 (↑ 위)", 1: "1 (↓ 아래)", 2: "2 (← 좌측)", 3: "3 (→ 우측)"}

    while not done:
        env.render(" - Random Agent")
        action = int(np.random.choice([0, 1, 2, 3]))
        obs, reward, terminated, truncated, info = env.step(action)
        step_count += 1
        done = terminated or truncated

        if step_count == 1 or step_count % 25 == 0 or info["life_lost"] or info["ghost_eaten_now"] or done:
            tag = ""
            if info["life_lost"]:
                tag = " [유령 충돌! 생명 손실]"
            elif info["ghost_eaten_now"]:
                tag = " [파워 포식! +200]"
            print(
                f"{step_count:^6} | {action_names[action]:^12} | {info['score']:6d} 점   | "
                f"{info['pellets_eaten']:3d} / {info['total_pellets']}  | {info['ghosts_eaten']:5d} 마리  | "
                f"{info['lives']}{tag}"
            )

    print("-" * 74)
    print("[*] 무작위 에이전트 최종 요약:")
    print(f"  - 총 진행 스텝 : {step_count} 스텝")
    print(f"  - 먹은 쿠키 수 : {info['pellets_eaten']} / {info['total_pellets']} 개")
    print(f"  - 포식한 유령  : {info['ghosts_eaten']} 마리")
    print(f"  - 최종 점수    : {info['score']} 점")
    print("=" * 74)
    print("\n[안내] 무작위 에이전트는 미로와 유령을 파악하지 못합니다. 2초 후 창이 닫힙니다...")
    time.sleep(2)
    env.close()


if __name__ == "__main__":
    main()
