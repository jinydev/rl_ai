import time
import numpy as np
import gym

env = gym.make('CartPole-v0', render_mode='human')
state = env.reset()[0]
done = False
step_count = 0
total_reward = 0.0

print("=" * 60)
print(" [실습 4단계] 무작위(Random) 에이전트 에피소드 루프 시작")
print("=" * 60)
print(f"초기 상태: 카트 위치 {state[0]:.3f}m, 막대 각도 {np.degrees(state[2]):.2f}°")
print("-" * 60)
print(f"{'스텝':^6} | {'선택 행동':^10} | {'카트 위치':^12} | {'막대 각도':^12} | {'상태'}")
print("-" * 60)

while not done:
    env.render()
    
    # 1. 행동 선택 (무작위 0 또는 1)
    action = np.random.choice([0, 1])
    action_name = "0 (← 좌측)" if action == 0 else "1 (→ 우측)"
    
    # 2. 1스텝 전이
    next_state, reward, terminated, truncated, info = env.step(action)
    step_count += 1
    total_reward += reward
    done = terminated or truncated
    
    # 각도를 디그리(Degree)로 변환하여 출력
    cart_x = next_state[0]
    pole_deg = np.degrees(next_state[2])
    status = "정상 유지" if not done else ("실패 (12° 초과 쓰러짐!)" if terminated else "성공 (200스텝 만료)")
    
    print(f"{step_count:^6} | {action_name:^10} | {cart_x:^+10.3f} m | {pole_deg:^+10.2f}° | {status}")
    
    # 사람이 관찰할 수 있도록 약간의 딜레이 (0.05초)
    time.sleep(0.05)
    state = next_state

print("-" * 60)
print(f"[*] 에피소드 종료 요약:")
print(f"  - 총 버틴 스텝 수 : {step_count} 스텝")
print(f"  - 총 획득 누적 보상: {total_reward} 점 (최대 200점 만점 중)")
print(f"  - 종료 사유        : {'막대 전도 (Terminated)' if terminated else '시간 초과 (Truncated)'}")
print("=" * 60)

# 최종 쓰러진 화면을 확인할 수 있도록 잠시 대기
print("\n[안내] 최종 쓰러진 화면을 확인하세요. 2초 후 창이 자동으로 닫힙니다...")
time.sleep(5)
env.close()
