"""
=============================================================================
CHAPTER 15 실전 예제: CartPole-v1 REINFORCE 에이전트 구현
=============================================================================
- 환경: Gymnasium CartPole-v1 (4차원 연속 상태, 2가지 이산 행동)
- 알고리즘: REINFORCE (Monte-Carlo Policy Gradient)
- 프레임워크: PyTorch + Gymnasium
=============================================================================
"""

import gymnasium as gym
import torch
import torch.nn as nn
import torch.optim as optim
from torch.distributions import Categorical
import numpy as np


# ---------------------------------------------------------------------------
# 1. 정책 신경망 (Policy Network) 모델 정의
# ---------------------------------------------------------------------------
class PolicyNetwork(nn.Module):
    def __init__(self, state_dim, action_dim, hidden_dim=128):
        super(PolicyNetwork, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, action_dim),
            nn.Softmax(dim=-1) # 각 행동의 확률 분포 (합이 1)
        )

    def forward(self, state):
        return self.net(state)


# ---------------------------------------------------------------------------
# 2. REINFORCE 에이전트 클래스 정의
# ---------------------------------------------------------------------------
class REINFORCEAgent:
    def __init__(self, state_dim, action_dim, lr=1e-3, gamma=0.99):
        self.gamma = gamma
        self.policy = PolicyNetwork(state_dim, action_dim)
        self.optimizer = optim.Adam(self.policy.parameters(), lr=lr)

        # 에피소드 단위 경험 저장소
        self.saved_log_probs = []
        self.rewards = []

    def select_action(self, state):
        """상태를 입력받아 확률 분포로부터 행동을 샘플링하고 로그 확률을 보관"""
        state_tensor = torch.from_numpy(state).float().unsqueeze(0)
        probs = self.policy(state_tensor)
        
        # Categorical 분포를 통한 확률적 행동 샘플링 (탐색과 활용 통합)
        dist = Categorical(probs)
        action = dist.sample()
        
        # 점수 함수 계산을 위해 log π(a|s) 저장
        self.saved_log_probs.append(dist.log_prob(action))
        return action.item()

    def update(self):
        """에피소드가 끝난 후 역순으로 누적 반환값 G_t를 계산하고 정책망 갱신"""
        discounted_returns = []
        G = 0.0
        # 에피소드 보상을 뒤에서부터 역순으로 누적
        for r in reversed(self.rewards):
            G = r + self.gamma * G
            discounted_returns.insert(0, G)

        returns = torch.tensor(discounted_returns, dtype=torch.float32)

        # 분산 완화를 위한 반환값 정규화 (Z-score 표준화)
        if len(returns) > 1:
            returns = (returns - returns.mean()) / (returns.std() + 1e-8)

        # 정책 손실 함수 계산: L = - Σ log π(a_t | s_t) * G_t
        policy_loss = []
        for log_prob, G_t in zip(self.saved_log_probs, returns):
            policy_loss.append(-log_prob * G_t)
        
        loss = torch.stack(policy_loss).sum()

        # 역전파 및 경사상승(Surrogate Loss 최소화) 최적화
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        # 메모리 초기화
        self.saved_log_probs.clear()
        self.rewards.clear()


# ---------------------------------------------------------------------------
# 3. 메인 훈련 루프
# ---------------------------------------------------------------------------
def main():
    env = gym.make("CartPole-v1")
    state_dim = env.observation_space.shape[0]  # 4
    action_dim = env.action_space.n             # 2

    agent = REINFORCEAgent(state_dim, action_dim, lr=1e-3, gamma=0.99)
    max_episodes = 500
    target_score = 475.0
    scores_window = []

    print(f"=== CartPole-v1 REINFORCE 학습 시작 (목표 점수: {target_score}) ===")

    for episode in range(1, max_episodes + 1):
        state, _ = env.reset()
        episode_reward = 0.0

        while True:
            action = agent.select_action(state)
            next_state, reward, terminated, truncated, _ = env.step(action)
            agent.rewards.append(reward)

            state = next_state
            episode_reward += reward

            if terminated or truncated:
                break

        # 에피소드 종료 후 정책망 1회 업데이트
        agent.update()

        scores_window.append(episode_reward)
        if len(scores_window) > 100:
            scores_window.pop(0)

        mean_score = np.mean(scores_window)

        if episode % 20 == 0 or mean_score >= target_score:
            print(f"에피소드 {episode:3d} | 최근 100회 평균 점수: {mean_score:6.2f} | 이번 에피소드: {episode_reward:4.0f}")

        if mean_score >= target_score:
            print(f"\n🎉 축하합니다! 에피소드 {episode}에서 목표 점수({target_score})를 달성하며 조기 종료합니다!")
            break

    env.close()


if __name__ == "__main__":
    main()
