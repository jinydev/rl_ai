import platform
import numpy as np
import matplotlib.pyplot as plt
from bandit1 import Bandit
from agent import Agent

"""
bandit_avg.py
다중 슬롯머신(Bandit)과 에이전트(Agent)의 상호작용을 200회 반복 실행하여,
개별 실험의 무작위성을 상쇄하고 알고리즘의 '평균적인 학습 성능 곡선'을 검증하는 실습 스크립트입니다.
"""

# ----------------------------------------------------
# 1. 한글 폰트 설정 (OS별 호환성 보장 및 마이너스 부호 깨짐 방지)
# ----------------------------------------------------
system_name = platform.system()
if system_name == 'Darwin':          # Mac OS 환경
    plt.rc('font', family='AppleGothic')
elif system_name == 'Windows':       # Windows OS 환경
    plt.rc('font', family='Malgun Gothic')
elif system_name == 'Linux':         # Linux OS 환경
    plt.rc('font', family='NanumGothic')

plt.rcParams['axes.unicode_minus'] = False  # 마이너스(-) 기호 깨짐 방지


def run_simulation(epsilon, runs=200, steps=1000):
    """
    지정된 탐색률(epsilon)로 슬롯머신 시뮬레이션을 runs(200)회 반복하고,
    각 스텝(1000)별 승률의 평균값(avg_rates)을 계산하여 반환합니다.
    
    :param epsilon: 무작위 탐색 확률 (예: 0.1)
    :param runs: 독립적인 실험 반복 횟수 (기본값: 200회)
    :param steps: 1회 실험당 플레이할 스텝 수 (기본값: 1,000단계)
    :return: 1,000개 스텝의 단계별 평균 승률 1차원 넘파이 배열 (형상: (1000,))
    """
    # 200번 실험의 1,000스텝 승률 데이터를 저장할 2차원 배열 생성 (형상: 200행 × 1000열)
    all_rates = np.zeros((runs, steps))

    # [외부 루프] 200번의 독립적인 시뮬레이션 반복
    for run in range(runs):
        bandit = Bandit()       # 매 실험마다 무작위 승률을 가진 새로운 슬롯머신 환경 생성
        agent = Agent(epsilon)  # 매 실험마다 초기 상태(Qs=0, ns=0)의 새 에이전트 생성
        total_reward = 0        # 1회 실험 동안의 누적 보상 합계
        rates = []              # 1회 실험 동안 스텝별 승률을 기록할 리스트

        # [내부 루프] 1,000스텝 상호작용 (행동 -> 보상 -> 학습 -> 승률 기록)
        for step in range(steps):
            action = agent.get_action()   # 1. 에이전트의 ε-탐욕 행동 선택
            reward = bandit.play(action)  # 2. 슬롯머신 환경의 보상 반환
            agent.update(action, reward)  # 3. 증분 방식으로 가치 추정치 Qs 갱신
            total_reward += reward        # 보상 누적 합산
            rates.append(total_reward / (step + 1))  # 현재 스텝까지의 승률 계산 (보상 합 / 현재 스텝수)

        # 1회 실험(1,000스텝)의 승률 리스트를 2차원 배열의 run번째 행에 저장
        all_rates[run] = rates

    # 200개 실험 결과(행들)에 대해 각 스텝(열, axis=0)별 평균을 계산하여 1차원 배열로 반환
    avg_rates = np.average(all_rates, axis=0)
    return avg_rates


if __name__ == "__main__":
    runs = 200      # 200회 반복 실험
    steps = 1000    # 1,000단계 플레이
    epsilon = 0.1   # 탐색률 10%
    
    print("=" * 60)
    print(f"다중 실행 시뮬레이션 시작: {runs}회 반복 × {steps}스텝 (ε = {epsilon})")
    print("=" * 60)
    
    # 1. ε = 0.1 단일 설정에 대한 200회 평균 승률 계산 (교재 그림 3-21)
    print(f"실험 1: ε = {epsilon}으로 {runs}회 반복 실험 중...")
    avg_rates = run_simulation(epsilon, runs, steps)
    
    # 그래프 1 시각화: 단계별 승률 (200번 실험 후 평균)
    plt.figure(figsize=(7, 4.5))
    plt.ylabel('Rates (승률)', fontsize=11)
    plt.xlabel('Steps (시행 횟수)', fontsize=11)
    plt.title('단계별 승률 (200번 실험 후 평균)', fontsize=13, fontweight='bold')
    plt.plot(avg_rates, color='#4A90E2', linewidth=2, label=f'ε = {epsilon} (200회 평균)')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend(fontsize=10)
    plt.tight_layout()
    plt.savefig('img/bandit_avg_200runs_result.png', dpi=150)
    print("평균 승률 그래프가 'img/bandit_avg_200runs_result.png'에 저장되었습니다.")
    # plt.show() # 대화형 창으로 확인할 때 주석 해제

    # 2. 다양한 ε 값 비교 실험 (0.01 vs 0.1 vs 0.3) (교재 그림 3-22)
    print("\n실험 2: 다양한 ε 값(0.01, 0.1, 0.3) 성능 비교 시뮬레이션 중...")
    epsilons = [0.01, 0.1, 0.3]
    colors = ['#E94E77', '#4A90E2', '#50E3C2']
    
    plt.figure(figsize=(8, 5))
    for eps, col in zip(epsilons, colors):
        print(f"  -> ε = {eps} ({runs}회 반복) 계산 중...")
        rates = run_simulation(eps, runs, steps)
        plt.plot(rates, label=f"ε = {eps}", color=col, linewidth=2)
        
    plt.ylabel('Rates (승률)', fontsize=11)
    plt.xlabel('Steps (시행 횟수)', fontsize=11)
    plt.title('ε-탐욕 정책의 ε값을 바꾼 결과 비교 (200회 평균)', fontsize=13, fontweight='bold')
    plt.legend(fontsize=10)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig('img/bandit_epsilons_comparison.png', dpi=150)
    print("ε 비교 그래프가 'img/bandit_epsilons_comparison.png'에 저장되었습니다.")
    # plt.show() # 대화형 창으로 확인할 때 주석 해제
