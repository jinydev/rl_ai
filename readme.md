# 밑바닥부터 시작하는 딥러닝 4 (Deep Learning from Scratch 4) 강의 노트

직접 구현하며 익히는 강화 학습 알고리즘 학습을 위한 강의 노트 프로젝트입니다. 이 저장소는 수강생들이 강화 학습의 핵심 수학 기초부터 실전 딥러닝 알고리즘(DQN, 정책 경사법 등)까지 단계별로 학습할 수 있도록 구성된 온라인 웹사이트의 소스 코드를 담고 있습니다. Jekyll 기반의 정적 사이트로 만들어졌으며, Markdown 문서를 통해 강의 자료가 관리됩니다.

## 1. 주요 강의 내용

본 강의는 강화 학습의 기초 수학 이론부터 시작하여 최신 심층 강화 학습(Deep Reinforcement Learning)까지의 로드맵을 제공합니다:

- **01 강화학습 소개:** 에이전트, 환경, 보상, 행동 등 강화학습의 4대 요소 및 탐색과 활용의 딜레마
- **02 확률과 기초수학:** 등비수열, 시그마 기호, 재귀적 증분 평균 업데이트 공식, 확률의 정의와 성질, 조건부 확률(몬티 홀, 생일 패러독스), 선형대수 행렬과 벡터의 연산 기초
- **03 밴디트 문제:** 다중 슬롯머신(Multi-armed Bandit) 문제, 에psilon-greedy 알고리즘 구현 및 비정상 문제 해결
- **04 마르코프 체인/과정:** 상태 전이 확률과 마르코프 과정, 은닉 마르코프 모델(HMM) 기초
- **05 마르코프 결정 과정 (MDP):** 에이전트와 환경의 상호작용 수식화 및 강화학습의 목표인 할인 누적 반환값 정의
- **06 벨만 방정식 (Bellman Equation):** 상태 가치 함수와 행동 가치 함수(Q-함수)의 유도 및 벨만 최적 방정식
- **07 동적 프로그래밍 (Dynamic Programming):** 그리드월드 예제를 통한 정책 평가, 정책 반복법(Policy Iteration), 가치 반복법(Value Iteration) 구현
- **09 몬테카를로법 (Monte Carlo):** 샘플 경험 기반의 정책 평가 및 제어, 중요도 샘플링을 활용한 오프-정책(Off-policy) MC 기초
- **10 TD법 (Temporal Difference):** 시간차 성능 비교, SARSA, 오프-정책 SARSA 및 대표적인 Q-러닝(Q-Learning) 알고리즘
- **11 신경망과 Q 러닝:** DeZero 프레임워크 기초 및 선형 회귀, 다층 신경망(Neural Network)을 결합한 가치 함수 근사
- **12 DQN (Deep Q-Network):** OpenAI Gym 환경 다루기, Experience Replay(경험 재생), Target Network의 핵심 기술 및 아타리 게임 적용
- **13 정책 경사법 (Policy Gradient):** REINFORCE 알고리즘, Baseline 도입 및 Actor-Critic(행위자-비평자) 모델 구현
- **14 한 걸음 더:** DQN 및 Policy Gradient 계열의 고급 확장 알고리즘(DDPG, PPO 등) 및 학습 과제
- **부록:** 오프-정책 몬테카를로법, n단계 TD법, Double DQN 및 정책 경사법 수학적 증명

## 2. 개발 환경 설정 및 빌드 (Jekyll)

이 웹사이트는 **Ruby**와 **Jekyll**을 사용하여 정적 사이트로 빌드됩니다. 로컬 환경에서 문서를 작성하고 사이트를 띄워보려면 아래 과정을 진행하세요.

### 2.1. 설치 단계

macOS의 경우 시스템 기본 Ruby 권한 문제가 발생할 수 있으므로 Homebrew를 통해 최신 버전을 설치하는 것을 권장합니다.

```bash
# 1. 최신 Ruby 설치 (macOS)
brew install ruby

# 2. Bundler와 Jekyll 설치
gem install bundler jekyll

# 3. 프로젝트 루트 디렉토리에서 패키지 의존성 설치
bundle install
```

### 2.2. 로컬 서버 실행 및 사이트 빌드

마크다운 문서를 작성하면서 로컬에서 실시간으로 렌더링된 결과를 확인할 수 있습니다.

```bash
# 로컬 개발용 서버 실행 (접속 주소: http://127.0.0.1:4000)
bundle exec jekyll serve

# 핫 리로드(Live Reload) 서버 실행 (파일 저장 시 브라우저 자동 새로고침)
bundle exec jekyll serve --livereload

# 사이트 전체 빌드 (docs/ 폴더에 생성됨)
bundle exec jekyll build
```

- **Source**: `src/` (작업할 마크다운 파일 경로)
- **Destination**: `docs/` (빌드 결과물 출력 경로)

> **주의사항**: 빌드 대상은 `src` 폴더에 한정되며, 루트의 다른 폴더에 있는 파일은 빌드에 포함되지 않습니다. 
> **Troubleshooting**: `bundle` 관련 명령어를 찾을 수 없다는 오류가 발생한다면, 터미널 환경 설정(`.zshrc` 등)에 Ruby 경로가 제대로 추가되었는지 확인해 주세요. (예: `export PATH="/usr/local/opt/ruby/bin:$PATH"`)

### 2.3. 배포 (Deployment)

웹사이트는 GitHub Pages를 통해 배포됩니다. 배포 환경 구성 방법은 다음과 같습니다.

1. 수정한 내용을 `git push`로 저장소에 업로드합니다.
2. 저장소의 **Settings -> Pages** 메뉴로 이동합니다.
3. **Build and deployment** 항목 설정:
    - **Source**: Deploy from a branch
    - **Branch**: `main` (또는 `master`) 브랜치의 `/docs` 폴더 지정
4. **Custom Domain**: `rl.ai.jiny.dev`

설정이 완료되면 `docs` 폴더 내의 변경 사항이 자동으로 실제 사이트에 반영됩니다.

## 3. 기여 가이드 (Contributing)

본 프로젝트는 누구나 자유롭게 참여하고 개선할 수 있는 오픈소스 강의 자료를 지향합니다. 오타 수정, 내용 보강, 더 좋은 예제 추가 등 어떠한 형태의 기여도 환영합니다.

1. 이 저장소를 **Fork** 하여 본인의 계정으로 복사합니다.
2. 로컬 환경으로 clone 후 새로운 브랜치를 생성합니다. (`git checkout -b feature/new-content`)
3. 문서를 수정하거나 새로운 내용을 추가한 후 커밋합니다. (`git commit -m "docs: 가치 반복법 설명 보강"`)
4. 작업한 브랜치를 원격 저장소에 푸시합니다. (`git push origin feature/new-content`)
5. 원본 저장소에 **Pull Request(PR)**를 생성하여 변경 사항 리뷰를 요청합니다.

## 4. 라이선스 (License)

이 프로젝트에 포함된 문서 및 소스 코드는 **MIT 라이선스 (MIT License)** 하에 배포됩니다.
누구나 상업적 또는 비상업적 목적으로 자유롭게 활용, 복제, 수정, 배포할 수 있습니다.
