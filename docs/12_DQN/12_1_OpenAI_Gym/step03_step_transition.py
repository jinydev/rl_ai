import time
import gym

env = gym.make('CartPole-v0', render_mode='human')

# 1. 초기 상태 획득 (s_0)
state = env.reset()[0]
print("1. 행동 전 초기 상태 (state)     :", state)

# 2. 행동 선택 (0: 카트 왼쪽 밀기, 1: 카트 오른쪽 밀기)
action = 0
print(f"2. 에이전트의 선택 행동 (action)  : {action} (← 카트 좌측 밀기)")

# 3. 1스텝 환경 상호작용 (전이 수행)
next_state, reward, terminated, truncated, info = env.step(action)

print("\n3. env.step(action) 반환값 5-튜플:")
print("  - next_state (차기 상태)       :", next_state)
print("  - reward     (즉각 보상)       :", reward)
print("  - terminated (과제 실패 여부)  :", terminated)
print("  - truncated  (시간 초과 여부)  :", truncated)
print("  - info       (부가 진단 정보)  :", info)

# 4. 상태 변화량 (Δs) 분석
diff = next_state - state
print("\n4. 1스텝 동안의 물리 상태 변화량 (Δs):")
print(f"  - 카트 위치 변화 : {diff[0]:+.6f} m")
print(f"  - 카트 속도 변화 : {diff[1]:+.6f} m/s (왼쪽으로 가속)")
print(f"  - 막대 각도 변화 : {diff[2]:+.6f} rad")
print(f"  - 막대 각속도 변화: {diff[3]:+.6f} rad/s")

# 1스텝 상호작용 후 변화된 화면을 확인할 수 있도록 잠시 대기
print("\n[안내] 1스텝 행동 후 카트폴 화면을 확인하세요. 3초 후 자동으로 창이 닫힙니다...")
time.sleep(3)

env.close()
