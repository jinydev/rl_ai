"""
===================================================================
05.4 2칸 그리드 월드(2-Grid World) MDP 가치 계산 및 시뮬레이션
===================================================================
- 설명: 4가지 결정적 정책(mu_1 ~ mu_4)에 대한 상태 가치 함수 v_pi(s)를
        1) 고교 수학의 무한등비급수 합 공식(이론 해석해)
        2) 100스텝 할인 보상 누적 파이썬 시뮬레이션(실험치)
        으로 각각 계산하여 최적 정책 mu_*를 찾고 완벽히 검증합니다.
===================================================================
"""

class TwoGridWorld:
    """2칸 그리드 월드 환경 (상태: L1, L2 / 행동: Left, Right)"""
    def __init__(self):
        self.STATES = ['L1', 'L2']
        self.ACTIONS = ['Left', 'Right']

    def step(self, state, action):
        """
        주어진 상태(state)에서 행동(action)을 취했을 때
        다음 상태(next_state)와 즉각 보상(reward)을 반환합니다.
        """
        if state == 'L1':
            if action == 'Right':
                return 'L2', 1.0   # 사과 획득 (+1)
            else:  # Left
                return 'L1', -1.0  # 왼쪽 벽 충돌 페널티 (-1)
        
        elif state == 'L2':
            if action == 'Left':
                return 'L1', 0.0   # 사과 재생성 (보상 0)
            else:  # Right
                return 'L2', -1.0  # 오른쪽 벽 충돌 페널티 (-1)


def simulate_policy(env, policy, start_state, gamma=0.9, steps=200):
    """
    주어진 정책(policy)을 따라 start_state에서 출발하여
    steps 동안 획득한 할인 누적 보상 수익(G_t)을 시뮬레이션합니다.
    """
    state = start_state
    total_return = 0.0
    discount = 1.0

    for _ in range(steps):
        action = policy[state]
        next_state, reward = env.step(state, action)
        total_return += discount * reward
        discount *= gamma
        state = next_state

    return total_return


def main():
    env = TwoGridWorld()
    gamma = 0.9

    # 4가지 결정적 정책 정의
    policies = {
        'μ_1 (Right, Right)': {'L1': 'Right', 'L2': 'Right'},
        'μ_2 (Left,  Left )': {'L1': 'Left',  'L2': 'Left'},
        'μ_3 (Right, Left )': {'L1': 'Right', 'L2': 'Left'},   # 핑퐁 왕복 정책 (최적 정책)
        'μ_4 (Left,  Right)': {'L1': 'Left',  'L2': 'Right'},
    }

    # 이론적 수식 해석해 (무한등비급수 합 공식 1 / (1 - r))
    theoretical_values = {
        'μ_1 (Right, Right)': {
            'L1': 1.0 - (gamma / (1.0 - gamma)),         # 1 - 9.0 = -8.0
            'L2': -1.0 / (1.0 - gamma),                  # -10.0
        },
        'μ_2 (Left,  Left )': {
            'L1': -1.0 / (1.0 - gamma),                  # -10.0
            'L2': 0.0 - (gamma / (1.0 - gamma)),         # 0 - 9.0 = -9.0
        },
        'μ_3 (Right, Left )': {
            'L1': 1.0 / (1.0 - (gamma ** 2)),            # 1 / 0.19 ≈ +5.2632
            'L2': gamma / (1.0 - (gamma ** 2)),          # 0.9 / 0.19 ≈ +4.7368
        },
        'μ_4 (Left,  Right)': {
            'L1': -1.0 / (1.0 - gamma),                  # -10.0
            'L2': -1.0 / (1.0 - gamma),                  # -10.0
        },
    }

    print("=" * 72)
    print("      05.4 2칸 그리드 월드: 4가지 결정적 정책 가치 계산 및 검증")
    print("=" * 72)
    print(f"{'정책 (Policy)':<22} | {'상태':<4} | {'시뮬레이션 (200스텝)':<18} | {'이론 수식 해석해':<16} | {'일치 여부'}")
    print("-" * 72)

    for name, pol in policies.items():
        for state in ['L1', 'L2']:
            sim_val = simulate_policy(env, pol, state, gamma=gamma, steps=200)
            theo_val = theoretical_values[name][state]
            match = "✓ 일치" if abs(sim_val - theo_val) < 1e-4 else "불일치"
            print(f"{name:<20} | {state:<4} | {sim_val:>16.4f} | {theo_val:>16.4f} | {match}")
        print("-" * 72)

    print("\n[★ 결론 및 최적 정책 판정]")
    print("1. 모든 상태(L1, L2)에서 v(L1)=+5.2632, v(L2)=+4.7368로 가장 높은 양수 가치를 기록한")
    print("   'μ_3 (Right, Left)' 정책이 유일무이한 최적 정책(μ_*)으로 판정되었습니다!")
    print("2. 파이썬 시뮬레이션 결과와 무한등비급수 수식 해가 소수점 넷째 자리까지 100% 일치합니다.")
    print("=" * 72)


if __name__ == '__main__':
    main()
