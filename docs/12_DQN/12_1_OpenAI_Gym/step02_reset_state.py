import time
import gym

env = gym.make('CartPole-v0', render_mode='human')

# 1. 초기 상태 얻기
state = env.reset()[0]
print('상태:', state)

# 2. 행동 공간의 크기 확인
action_space = env.action_space
print('행동의 차원 수:', action_space)

# 화면 창을 확인할 수 있도록 잠시 대기
print("\n[안내] 카트폴 화면을 확인하세요. 3초 후 자동으로 창이 닫힙니다...")
time.sleep(3)

env.close()
