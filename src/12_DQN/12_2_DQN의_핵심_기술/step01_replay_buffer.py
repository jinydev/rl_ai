"""
[실습 1단계] 경험 재생 버퍼 (Replay Buffer) 구현 및 검증
======================================================
카트폴 환경에서 경험 데이터 (state, action, reward, next_state, done)를
수집하여 버퍼에 적재하고, 무작위 미니배치를 추출하여 텐서 형상을 검증합니다.
"""

from collections import deque
import random
import warnings
import numpy as np
import gym

warnings.filterwarnings('ignore')


class ReplayBuffer:
    """경험 재생(Experience Replay)을 위한 고속 FIFO 순환 버퍼"""
    def __init__(self, buffer_size: int, batch_size: int):
        self.buffer = deque(maxlen=buffer_size)
        self.batch_size = batch_size

    def add(self, state, action, reward, next_state, done):
        """1스텝 전이 경험 튜플 (s, a, r, s', done)을 버퍼에 추가"""
        data = (state, action, reward, next_state, done)
        self.buffer.append(data)

    def __len__(self):
        """버퍼에 현재 저장된 경험 데이터의 총 개수 반환"""
        return len(self.buffer)

    def get_batch(self):
        """버퍼에서 batch_size만큼의 경험을 무작위 추출하여 NumPy 배열 묶음으로 반환"""
        data = random.sample(self.buffer, self.batch_size)

        state = np.stack([x[0] for x in data])
        action = np.array([x[1] for x in data])
        reward = np.array([x[2] for x in data])
        next_state = np.stack([x[3] for x in data])
        done = np.array([x[4] for x in data]).astype(np.int32)
        return state, action, reward, next_state, done


if __name__ == '__main__':
    print("=" * 65)
    print(" [실습 1단계] ReplayBuffer 생성 및 카트폴 경험 수집 시작")
    print("=" * 65)

    # 1. 환경 및 버퍼 초기화
    env = gym.make('CartPole-v0')
    buffer_capacity = 10000
    batch_size = 32
    replay_buffer = ReplayBuffer(buffer_size=buffer_capacity, batch_size=batch_size)

    print(f"[*] 버퍼 최대 용량 (buffer_size) : {buffer_capacity:,} 개")
    print(f"[*] 미니배치 크기  (batch_size)  : {batch_size} 개")
    print("-" * 65)

    # 2. 카트폴 환경에서 10회 에피소드 동안 경험 데이터 수집
    total_episodes = 10
    total_steps = 0

    for episode in range(1, total_episodes + 1):
        state = env.reset()[0]
        done = False
        episode_reward = 0.0
        step_count = 0

        while not done:
            # 0번(좌측 밀기) 또는 1번(우측 밀기) 행동 수행
            action = env.action_space.sample()  # 무작위 탐색
            next_state, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated

            # 버퍼에 5-튜플 경험 데이터 적재
            replay_buffer.add(state, action, reward, next_state, done)

            state = next_state
            episode_reward += reward
            step_count += 1

        total_steps += step_count
        print(f"  - 에피소드 {episode:2d}/10 완료 | 버틴 스텝: {step_count:2d} | 획득 보상: {episode_reward:4.1f} | 버퍼 적재량: {len(replay_buffer):3d}개")

    env.close()

    print("-" * 65)
    print(f"[*] 총 10회 에피소드 완료! 수집된 총 경험 데이터: {len(replay_buffer)} 개")
    print("=" * 65)

    # 3. 버퍼에서 무작위 미니배치 추출 및 텐서 형상 검증
    print("\n" + "=" * 65)
    print(f" [검증] replay_buffer.get_batch() 실행 (배치 크기: {batch_size})")
    print("=" * 65)

    state_b, action_b, reward_b, next_state_b, done_b = replay_buffer.get_batch()

    print(f"  1. state_batch      (현재 상태 행렬)   : 형상 {state_b.shape} (dtype: {state_b.dtype})")
    print(f"  2. action_batch     (선택 행동 벡터)   : 형상 {action_b.shape}      (dtype: {action_b.dtype})")
    print(f"  3. reward_batch     (즉각 보상 벡터)   : 형상 {reward_b.shape}      (dtype: {reward_b.dtype})")
    print(f"  4. next_state_batch (차기 상태 행렬)   : 형상 {next_state_b.shape} (dtype: {next_state_b.dtype})")
    print(f"  5. done_batch       (종료 플래그 벡터) : 형상 {done_b.shape}      (dtype: {done_b.dtype})")
    print("-" * 65)
    print("  [*] 샘플 0번째 데이터 상세 내용:")
    print(f"      - State     : {state_b[0]}")
    print(f"      - Action    : {action_b[0]} ({'0: 좌측 밀기' if action_b[0] == 0 else '1: 우측 밀기'})")
    print(f"      - Reward    : {reward_b[0]}")
    print(f"      - Next State: {next_state_b[0]}")
    print(f"      - Done      : {done_b[0]} ({'종료(Terminated/Truncated)' if done_b[0] == 1 else '진행 중'})")
    print("=" * 65)
    print(">>> ReplayBuffer 정상 작동 검증 완료! 신경망 학습용 텐서 준비 완료.\n")
