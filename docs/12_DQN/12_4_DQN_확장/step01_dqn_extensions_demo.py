"""
step01_dqn_extensions_demo.py: DQN 3대 확장 기술(Double DQN, PER, Dueling DQN) 원리 실습

주요 학습 내용:
1. Double DQN: max 연산자의 과대평가(Overestimation) 편향 실증 및 행동 선택-평가 분리 효과 검증
2. 우선순위 경험 재생(PER): TD 오차(|delta|) 비례 우선순위 룰렛 샘플링 메커니즘 검증
3. Dueling DQN: 상태 가치 V(s)와 어드밴티지 A(s, a)의 분기 및 평균 차감 재결합(Identifiability) 수식 구현
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def demo_double_dqn():
    """1. Double DQN: 과대평가 편향 실증"""
    print("\n" + "=" * 65)
    print(" [1] Double DQN: max 연산자의 과대평가 편향 vs 분리 평가")
    print("=" * 65)
    
    np.random.seed(42)
    true_q = 10.0 # 모든 행동의 참된 Q 가치가 10.0이라고 가정
    n_actions = 10
    n_trials = 1000
    noise_std = 2.0
    
    # 표준 DQN (max 연산자 사용)
    # 추정치 Q_target = 참값(10) + 정규분포 노이즈
    noisy_estimates_theta_prime = true_q + np.random.normal(0, noise_std, (n_trials, n_actions))
    dqn_max_values = np.max(noisy_estimates_theta_prime, axis=1)
    dqn_mean_overestimation = np.mean(dqn_max_values)
    
    # Double DQN (메인망 theta로 행동 선택 후, 타깃망 theta_prime으로 평가)
    noisy_estimates_theta = true_q + np.random.normal(0, noise_std, (n_trials, n_actions))
    best_actions = np.argmax(noisy_estimates_theta, axis=1) # theta가 행동 선택
    # theta_prime이 해당 행동의 가치를 평가
    double_dqn_values = noisy_estimates_theta_prime[np.arange(n_trials), best_actions]
    double_dqn_mean = np.mean(double_dqn_values)
    
    print(f" * 참된 행동 가치(Ground Truth)       : {true_q:.2f}")
    print(f" * 표준 DQN의 타깃 추정치 평균 (max) : {dqn_mean_overestimation:.2f} (편향: +{dqn_mean_overestimation - true_q:.2f}) -> 심각한 과대평가!")
    print(f" * Double DQN의 타깃 추정치 평균     : {double_dqn_mean:.2f} (편향: {double_dqn_mean - true_q:+.2f}) -> 편향 완벽 제거!")

    return dqn_max_values, double_dqn_values, true_q

def demo_per():
    """2. 우선순위 경험 재생(PER): TD 오차 기반 샘플링"""
    print("\n" + "=" * 65)
    print(" [2] 우선순위 경험 재생(PER): TD 오차(|delta|) 비례 우선순위 샘플링")
    print("=" * 65)
    
    # 버퍼에 저장된 5개 가상 경험 데이터
    experiences = [
        {"id": "Exp_A (평범한 일상 전이)", "delta": 0.05},
        {"id": "Exp_B (미미한 전이)       ", "delta": 0.08},
        {"id": "Exp_C (충돌 직전 돌발위기)", "delta": 1.45},
        {"id": "Exp_D (극적인 보너스 획득)", "delta": 2.10},
        {"id": "Exp_E (안정적 전진)       ", "delta": 0.12},
    ]
    
    deltas = np.array([e["delta"] for e in experiences])
    total_delta = np.sum(deltas)
    probabilities = deltas / total_delta
    
    print(f" * 경험 버퍼 내 데이터별 TD 오차 및 PER 추출 확률:")
    for i, exp in enumerate(experiences):
        print(f"   [{i+1}] {exp['id']} : |delta| = {exp['delta']:.2f} -> 추출 확률 P = {probabilities[i]*100:5.2f}%")
        
    print(f"\n * 일반 균등 버퍼 대비:")
    print(f"   - 일반 균등 재생: 모든 경험이 동일하게 20.00% 확률로 추출됨")
    print(f"   - PER: 핵심 경험(Exp_D)이 일상 경험(Exp_A)보다 약 {probabilities[3]/probabilities[0]:.1f}배 더 자주 추출되어 학습 가속!")
    
    return [e["id"].strip() for e in experiences], probabilities

def demo_dueling_dqn():
    """3. Dueling DQN: 상태 가치 V(s)와 어드밴티지 A(s, a) 분리"""
    print("\n" + "=" * 65)
    print(" [3] Dueling DQN: 가치 V(s)와 어드밴티지 A(s, a)의 분기 및 재결합")
    print("=" * 65)
    
    batch_size = 2
    n_actions = 3 # 행동: [좌, 정지, 우]
    
    # 가상의 네트워크 출력값
    # 샘플 1: 공이 멀리 있어 패배가 불가피한 위기 상태 (V(s)가 매우 낮음)
    # 샘플 2: 공을 받아치기 직전인 찬스 상태 (V(s)가 높음)
    V = np.array([[ -8.5 ],   # 상태 1 가치
                  [ +12.0 ]]) # 상태 2 가치
    
    # 각 행동별 어드밴티지 A(s, a)
    A = np.array([[ 0.2, -0.1, -0.1 ],  # 상태 1: 무슨 짓을 해도 별 차이 없음
                  [ 5.0, -2.0, -3.0 ]]) # 상태 2: 좌로 움직여야만 공을 받아침!
                  
    # 논문 공식: Q(s, a) = V(s) + (A(s, a) - mean(A(s, a')))
    A_mean = np.mean(A, axis=1, keepdims=True)
    Q = V + (A - A_mean)
    
    print(f" * 입력 미니배치 크기: {batch_size}, 행동 후보 수: {n_actions}")
    print(f"\n [상태 1: 위기 상황]")
    print(f"   - 상태 가치 V(s1)       : {V[0, 0]:+.2f} (상태 자체가 절망적)")
    print(f"   - 어드밴티지 A(s1, a)   : {A[0]} (행동 간 격차가 거의 없음)")
    print(f"   - 최종 복원 Q(s1, a)    : {Q[0]} (V(s) 하나만 학습해도 3개 Q가 동시 갱신!)")
    
    print(f"\n [상태 2: 승부처 상황]")
    print(f"   - 상태 가치 V(s2)       : {V[1, 0]:+.2f} (유리한 찬스 상태)")
    print(f"   - 어드밴티지 A(s2, a)   : {A[1]} (행동 1(좌)이 압도적으로 우세: +5.0)")
    print(f"   - 최종 복원 Q(s2, a)    : {Q[1]} (행동 1이 최적 행동으로 명확히 부각)")
    print("=" * 65)

def main():
    dqn_vals, ddqn_vals, true_q = demo_double_dqn()
    exp_labels, probs = demo_per()
    demo_dueling_dqn()
    
    # 시각화 저장
    script_dir = os.path.dirname(os.path.abspath(__file__))
    img_dir = os.path.join(script_dir, "img")
    os.makedirs(img_dir, exist_ok=True)
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))
    plt.subplots_adjust(wspace=0.3)
    
    # 1. Double DQN 편향 히스토그램
    axes[0].axvline(true_q, color='red', linestyle='--', linewidth=2.5, label=f'True Q Value ({true_q:.1f})')
    axes[0].hist(dqn_vals, bins=30, alpha=0.6, color='coral', label=f'Standard DQN (max)\nMean = {np.mean(dqn_vals):.2f}')
    axes[0].hist(ddqn_vals, bins=30, alpha=0.6, color='royalblue', label=f'Double DQN (Decoupled)\nMean = {np.mean(ddqn_vals):.2f}')
    axes[0].set_title("Double DQN vs Standard DQN: Overestimation Bias", fontsize=12, fontweight='bold')
    axes[0].set_xlabel("Target Q Value", fontsize=11)
    axes[0].set_ylabel("Frequency", fontsize=11)
    axes[0].legend(fontsize=10)
    axes[0].grid(True, alpha=0.3)
    
    # 2. PER 확률 바차트
    short_labels = ["Exp A\n(Normal)", "Exp B\n(Tiny)", "Exp C\n(Danger)", "Exp D\n(Bonus)", "Exp E\n(Normal)"]
    bars = axes[1].bar(short_labels, probs * 100, color=['#a0aec0', '#a0aec0', '#ed8936', '#48bb78', '#a0aec0'], width=0.55)
    axes[1].axhline(20.0, color='gray', linestyle=':', linewidth=2, label='Uniform Replay (20%)')
    for bar in bars:
        h = bar.get_height()
        axes[1].text(bar.get_x() + bar.get_width()/2., h + 1.0, f'{h:.1f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')
    axes[1].set_title("Prioritized Experience Replay (PER): Sampling Probability", fontsize=12, fontweight='bold')
    axes[1].set_ylabel("Sampling Probability (%)", fontsize=11)
    axes[1].set_ylim(0, 65)
    axes[1].legend(fontsize=10)
    axes[1].grid(True, alpha=0.3)
    
    out_path = os.path.join(img_dir, "ch12_4_step01_extensions_graph.png")
    plt.savefig(out_path, dpi=200, bbox_inches='tight')
    plt.close()
    print(f"\n[저장 완료] DQN 확장 검증 시각화 그래프: {out_path}")

if __name__ == "__main__":
    main()
