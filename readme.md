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

## 2. 강의 노트 웹사이트 개발 환경 (Ruby & Jekyll)

이 웹사이트는 **Ruby**와 **Jekyll**을 사용하여 정적 웹 문서로 빌드됩니다. 로컬 환경에서 강의 노트를 실시간으로 확인하고 편집하려면 아래 절차를 진행하세요.

> [!IMPORTANT]
> 모든 터미널 명령어는 반드시 **`강화학습` 프로젝트 루트 폴더**(`c:\dev\sites\강화학습`)에서 실행해야 합니다.  
> 상위 폴더에서 실행 시 `Could not locate Gemfile` 오류가 발생합니다.

### 2.1. 필수 도구 설치

#### Windows 환경
1. **Ruby 및 Devkit 설치**:
   - [RubyInstaller 공식 사이트](https://rubyinstaller.org/downloads/)에서 **`Ruby+Devkit 3.3.x (x64)`** 다운로드 및 설치
   - 또는 Windows 터미널(PowerShell)에서 `winget`으로 설치:
     ```powershell
     winget install RubyInstallerTeam.RubyWithDevKit.3.3
     ```
2. **PowerShell 스크립트 실행 권한 설정**:
   - 처음 실행 시 스크립트 보안 정책 에러가 발생할 수 있으므로 권한을 부여합니다:
     ```powershell
     Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
     ```
3. **의존성 Gem 설치**:
   ```powershell
   cd c:\dev\sites\강화학습
   gem install bundler jekyll
   bundle install
   ```

#### macOS 환경
```bash
# 1. Homebrew로 최신 Ruby 설치
brew install ruby

# 2. 터미널 환경설정에 Ruby 경로 추가 (~/.zshrc)
echo 'export PATH="/usr/local/opt/ruby/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# 3. 프로젝트 루트로 이동 후 의존성 설치
cd 강화학습
gem install bundler jekyll
bundle install
```

---

### 2.2. 로컬 서버 실행 및 빌드

```bash
# 핫 리로드(LiveReload) 서버 실행 (파일 수정 시 브라우저 자동 새로고침)
bundle exec jekyll serve --livereload

# 사이트 정적 빌드 (결과물은 docs/ 폴더에 생성)
bundle exec jekyll build
```

- **로컬 접속 주소**: [http://localhost:4000](http://localhost:4000) (또는 `http://127.0.0.1:4000`)
- **소스 디렉토리**: `src/` (강의 노트 마크다운 및 리소스)
- **출력 디렉토리**: `docs/` (GitHub Pages 배포 타깃)

---

### 2.3. 웹사이트 배포 (GitHub Pages)

1. 수정한 내용을 커밋 후 `main` 브랜치에 푸시합니다:
   ```bash
   git add .
   git commit -m "docs: 강의 내용 업데이트"
   git push origin main
   ```
2. GitHub 저장소 **Settings ➔ Pages** 설정:
   - **Source**: `Deploy from a branch`
   - **Branch**: `main` 브랜치의 `/docs` 디렉토리 선택
3. 사용자 지정 도메인: `rl.ai.jiny.dev` (CNAME 자동 연동)

---

## 3. 강화학습 실습 코드 실행 환경 (Python)

강의 노트에 포함된 다양한 강화학습 알고리즘 구현 코드(`src/**/*.py`)를 직접 실행하고 실습하기 위한 환경 설정입니다.

### 3.1. 권장 사양 및 필수 패키지
- **Python 버전**: Python 3.10 ~ 3.12 권장
- **필수 라이브러리**:
  - `numpy` (수치 연산, 행렬 계산 및 통계 처리)
  - `matplotlib` (강화학습 학습 곡선, 승률 그래프 시각화)

### 3.2. 패키지 설치

프로젝트 루트 폴더에서 다음 명령어로 필수 라이브러리를 한 번에 설치합니다:

```bash
# requirements.txt 기반 일괄 설치
pip install -r requirements.txt

# 또는 개별 설치
pip install numpy matplotlib
```

> [!TIP]
> **가상환경(venv) 사용을 권장하는 경우:**
> ```bash
> # 1. 가상환경 생성 (.venv)
> python -m venv .venv
>
> # 2. 가상환경 활성화
> # Windows PowerShell:
> .\.venv\Scripts\Activate.ps1
> # macOS / Linux:
> source .venv/bin/activate
>
> # 3. 패키지 설치
> pip install -r requirements.txt
> ```

---

### 3.3. 실습 예제 실행 방법

모든 파이썬 실습 스크립트는 프로젝트 루트나 임의의 경로에서 실행해도 내부적으로 경로를 자동 감지하도록 구성되어 있습니다.

```bash
# 예제 1: 슬롯머신 1,000단계 상호작용 및 누적 보상 시각화
python src/03_밴디트_문제/3_4_밴디트_알고리즘_구현/bandit_play.py

# 예제 2: 200회 반복 시뮬레이션을 통한 ε-탐욕 알고리즘 평균 학습 곡선 검증
python src/03_밴디트_문제/3_4_밴디트_알고리즘_구현/bandit_avg.py

# 예제 3: 비정상(Non-stationary) 밴디트 문제 비교 (표본 평균 vs 고정값 α 갱신)
python src/03_밴디트_문제/3_5_비정상_문제/non_stationary.py
```

> [!NOTE]
> **그래프 출력 및 저장 안내:**
> - 스크립트를 실행하면 화면에 대화형 인터랙티브 차트 창(`plt.show()`)이 팝업됩니다.
> - 차트 창을 닫으면 해당 실습 폴더 내의 `img/` 디렉토리에 고해상도 이미지 파일(`.png`)로도 자동 보존됩니다.

---

## 4. 자주 발생하는 문제 해결 (Troubleshooting FAQ)

| 증상 | 원인 | 해결 방법 |
| :--- | :--- | :--- |
| `Could not locate Gemfile` | 터미널 작업 위치가 상위 폴더인 경우 | `cd c:\dev\sites\강화학습` 명령어로 프로젝트 폴더로 이동 후 재실행 |
| `FileNotFoundError: ... 'img/...'` | 상대 경로 탐색 문제 | 최신 버전 코드에서는 `os.path` 절대 경로 처리가 적용되어 있으므로 저장소 최신 상태 유지 |
| 그래프 창이 화면에 뜨지 않음 | `plt.show()` 주석 처리 상태 | 스크립트 하단의 `plt.show()` 주석이 해제되어 있는지 확인 |
| PowerShell 스크립트 실행 불가 (`PSSecurityException`) | Windows 실행 정책 제한 | `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` 실행 후 터미널 재시작 |
| `Faraday v2.0+` 경고 메시지 출력 | Faraday 미들웨어 알림 (무시 가능) | 사이트 빌드 및 실행에는 영향이 없으며, 필요 시 `gem install faraday-retry` 실행 |

---

## 5. 기여 가이드 (Contributing)

본 프로젝트는 누구나 자유롭게 참여하고 개선할 수 있는 오픈소스 강의 자료를 지향합니다. 오타 수정, 내용 보강, 더 좋은 예제 추가 등 어떠한 형태의 기여도 환영합니다.

1. 이 저장소를 **Fork** 하여 본인의 계정으로 복사합니다.
2. 로컬 환경으로 clone 후 새로운 브랜치를 생성합니다. (`git checkout -b feature/new-content`)
3. 문서를 수정하거나 새로운 내용을 추가한 후 커밋합니다. (`git commit -m "docs: 가치 반복법 설명 보강"`)
4. 작업한 브랜치를 원격 저장소에 푸시합니다. (`git push origin feature/new-content`)
5. 원본 저장소에 **Pull Request(PR)**를 생성하여 변경 사항 리뷰를 요청합니다.

## 6. 라이선스 (License)

이 프로젝트에 포함된 문서 및 소스 코드는 **MIT 라이선스 (MIT License)** 하에 배포됩니다.
누구나 상업적 또는 비상업적 목적으로 자유롭게 활용, 복제, 수정, 배포할 수 있습니다.
