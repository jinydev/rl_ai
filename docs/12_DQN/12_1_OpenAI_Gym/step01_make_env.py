"""
[Step 01] OpenAI Gym 환경 생성 및 사양 검사 스크립트

이 스크립트는 강화학습 시뮬레이터인 CartPole 환경을 생성하고,
환경의 등록 사양(Spec)과 기본 인터페이스 메타데이터를 검사합니다.
"""

import sys

# Gym 또는 최신 Gymnasium 라이브러리 호환 임포트
try:
    import gymnasium as gym
    print(f"[알림] Gymnasium v{gym.__version__} 라이브러리를 사용합니다.")
except ImportError:
    try:
        import gym
        print(f"[알림] OpenAI Gym v{gym.__version__} 라이브러리를 사용합니다.")
    except ImportError:
        print("[오류] gym 또는 gymnasium 패키지가 설치되어 있지 않습니다.")
        print("  설치 명령: pip install gymnasium[classic-control] pygame")
        sys.exit(1)

def main():
    print("=" * 60)
    print(" 1단계: OpenAI Gym CartPole 환경 생성 및 기본 스펙 확인")
    print("=" * 60)

    # 1. CartPole 환경 인스턴스 생성
    #    v0 버전이 미지원 환경인 경우 v1으로 유연하게 폴백(Fallback) 처리
    env_id = 'CartPole-v0'
    try:
        env = gym.make(env_id, render_mode='rgb_array')
        print(f"[성공] '{env_id}' 환경이 성공적으로 생성되었습니다.")
    except Exception as e:
        print(f"[참고] '{env_id}' 생성 실패 ({e}), 최신 'CartPole-v1'으로 전환합니다.")
        env_id = 'CartPole-v1'
        env = gym.make(env_id, render_mode='rgb_array')
        print(f"[성공] '{env_id}' 환경이 생성되었습니다.")

    # 2. 환경 메타데이터 및 사양(Spec) 검사
    print("-" * 60)
    print(" 환경 사양 정보:")
    print(f"  - 환경 식별자 (ID)       : {env.spec.id}")
    print(f"  - 최대 에피소드 스텝 수 : {env.spec.max_episode_steps} 스텝")
    print(f"  - 성공/보상 임계치       : {getattr(env.spec, 'reward_threshold', 195.0)}")
    print(f"  - 렌더 모드 (Render Mode): {env.render_mode}")
    print("-" * 60)

    # 3. 환경 리소스 해제
    env.close()
    print("[완료] 환경 자원이 안전하게 해제되었습니다 (env.close()).")
    print("=" * 60)

if __name__ == '__main__':
    main()
