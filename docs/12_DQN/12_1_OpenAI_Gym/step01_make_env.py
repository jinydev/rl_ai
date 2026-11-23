import gym

# 1. CartPole 환경 생성 (render_mode='human': 시각화 창 활성화)
env = gym.make('CartPole-v0', render_mode='human')

# 2. 생성 확인 및 자원 해제
print("카트폴 환경이 성공적으로 생성되었습니다:", env)
print("환경 식별자 (Spec ID):", env.spec.id)

env.close()
