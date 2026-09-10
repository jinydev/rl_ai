import platform
import matplotlib.pyplot as plt
import numpy as np
from bandit1 import Bandit
from agent import Agent

"""
bandit_play.py
슬롯머신 환경(Bandit)과 강화학습 에이전트(Agent)의 1,000단계 상호작용 실습 스크립트
"""

# ----------------------------------------------------
# 한글 폰트 설정 (OS별 호환성 보장)
# ----------------------------------------------------
system_name = platform.system()
if system_name == 'Darwin':          # Mac OS
    plt.rc('font', family='AppleGothic')
elif system_name == 'Windows':       # Windows OS
    plt.rc('font', family='Malgun Gothic')
elif system_name == 'Linux':         # Linux OS
    plt.rc('font', family='NanumGothic')

plt.rcParams['axes.unicode_minus'] = False  # 마이너스(-) 기호 깨짐 방지

if __name__ == "__main__":
    # ----------------------------------------------------
    # 1. 시뮬레이션 설정 (하이퍼파라미터)
    # ----------------------------------------------------
    steps = 1000      # 총 플레이 횟수 (1,000단계)
    epsilon = 0.1     # 탐색률 ε (10% 확률로 무작위 탐색, 90% 확률로 최고 머신 활용)

    # ----------------------------------------------------
    # 2. 환경(Bandit: 10대 슬롯머신)과 에이전트(Agent) 객체 생성
    # ----------------------------------------------------
    bandit = Bandit()       # 승률이 무작위로 설정된 10대 슬롯머신 환경
    agent = Agent(epsilon)  # ε-탐욕 정책 기반 강화학습 에이전트

    total_reward = 0        # 전체 누적 보상 합산 변수
    total_rewards = []      # 각 스텝별 누적 보상 기록 리스트 (그림 3-19 시각화용)
    rates = []              # 각 스텝별 평균 승률 기록 리스트 (그림 3-20 시각화용)

    print("=== 1,000스텝 밴디트 상호작용 시뮬레이션 시작 ===")

    # ----------------------------------------------------
    # 3. 1,000스텝 상호작용 루프 실행 (행동 -> 보상 -> 학습 -> 기록)
    # ----------------------------------------------------
    for step in range(steps):
        # [1단계] 행동 선택: 에이전트가 ε-탐욕 정책에 따라 슬롯머신(0~9) 번호 선택
        action = agent.get_action()
        
        # [2단계] 환경 반응: 선택한 슬롯머신의 레버를 당겨 보상(1: 당첨, 0: 꽝) 획득
        reward = bandit.play(action)
        
        # [3단계] 경험 학습: 획득한 보상으로 에이전트의 가치 추정치(Qs)를 증분 갱신
        agent.update(action, reward)
        
        # [4단계] 통계 기록: 누적 보상 합산 및 현재 스텝까지의 승률 계산
        total_reward += reward
        total_rewards.append(total_reward)          # 현재까지의 누적 보상 저장
        rates.append(total_reward / (step + 1))      # 현재까지의 승률 저장 (누적 보상 / 현재 스텝수)

    print(f"1,000회 플레이 후 최종 누적 보상: {total_reward} (평균 승률: {total_reward / steps:.3f})")

    # ----------------------------------------------------
    # 4. 그래프 시각화 (교재 그림 3-19 & 그림 3-20)
    # ----------------------------------------------------
    plt.figure(figsize=(10, 4))
    
    # (1) 단계별 보상 총합 그래프 (그림 3-19)
    plt.subplot(1, 2, 1)
    plt.title('단계별 보상 총합 (Total Reward)', fontsize=12)
    plt.ylabel('Total reward (누적 보상)', fontsize=10)
    plt.xlabel('Steps (시행 횟수)', fontsize=10)
    plt.plot(total_rewards, color='#4A90E2', linewidth=2)
    plt.grid(True, linestyle='--', alpha=0.5)

    # (2) 단계별 승률 그래프 (그림 3-20)
    plt.subplot(1, 2, 2)
    plt.title('단계별 승률 (Winning Rates)', fontsize=12)
    plt.ylabel('Rates (승률)', fontsize=10)
    plt.xlabel('Steps (시행 횟수)', fontsize=10)
    plt.plot(rates, color='#E94E77', linewidth=2)
    plt.grid(True, linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.savefig('img/bandit_simulation_result.png', dpi=150)
    print("시뮬레이션 결과 그래프가 'img/bandit_simulation_result.png'에 저장되었습니다.")
    # plt.show() # 대화형 창으로 확인할 때 주석 해제
