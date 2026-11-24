"""
[실습 1단계] 아타리 벽돌깨기(Atari Breakout) 환경 구조 확인 및 무작위 에이전트 실행
=================================================================================
아타리 2600 규격(210 x 160 RGB 화면, 6색 60개 벽돌, 3개 행동) 환경에서
학습되지 않은 무작위(Random) 에이전트가 공을 제대로 받아내지 못하고
금세 3개의 생명을 모두 잃는 모습을 확인합니다.
"""

import time
import numpy as np
from atari_breakout_env import AtariBreakoutEnv


def main():
    np.random.seed(42)
    env = AtariBreakoutEnv(render_mode="human", max_steps=1000, lives=3)
    obs, info = env.reset(seed=42)
    rgb_frame = env.get_rgb_frame()

    print("=" * 70)
    print(" [실습 1단계] 아타리 벽돌깨기(Breakout) 환경 스펙 및 무작위 에이전트")
    print("=" * 70)
    print(f" * 원본 아타리 RGB 화면 형상 : {rgb_frame.shape} (dtype: {rgb_frame.dtype})")
    print(f" * 정규화 상태 벡터 형상     : {obs.shape} -> [패들X, 공X, 공Y, 공VX, 공VY]")
    print(f" * 행동 공간 (Action Space)  : {env.action_space} (0: ← 좌측, 1: · 정지, 2: → 우측)")
    print(f" * 전체 벽돌 수 / 초기 생명  : {info['bricks_remaining']}개 / {info['lives']}목숨")
    print("-" * 70)
    print(f"{'스텝':^6} | {'선택 행동':^12} | {'누적 점수':^10} | {'깬 벽돌':^10} | {'남은 생명':^10}")
    print("-" * 70)

    done = False
    step_count = 0
    action_names = {0: "0 (← 좌측)", 1: "1 (· 정지)", 2: "2 (→ 우측)"}

    while not done:
        env.render(" - Random Agent")
        action = int(np.random.choice([0, 1, 2]))
        obs, reward, terminated, truncated, info = env.step(action)
        step_count += 1
        done = terminated or truncated

        if step_count == 1 or step_count % 40 == 0 or info["life_lost"] or done:
            tag = " [생명 손실!]" if info["life_lost"] else ""
            print(f"{step_count:^6} | {action_names[action]:^12} | {info['score']:6d} 점   | {info['bricks_broken']:3d} / 60  | {info['lives']:^10}{tag}")

    print("-" * 70)
    print("[*] 무작위 에이전트 최종 요약:")
    print(f"  - 총 진행 스텝 : {step_count} 스텝")
    print(f"  - 패들 반사 수 : {info['paddle_hits']} 회")
    print(f"  - 파괴한 벽돌  : {info['bricks_broken']} / 60 개")
    print(f"  - 최종 점수    : {info['score']} 점")
    print("=" * 70)
    print("\n[안내] 무작위 에이전트는 공을 추적하지 못합니다. 2초 후 창이 닫힙니다...")
    time.sleep(2)
    env.close()


if __name__ == "__main__":
    main()
