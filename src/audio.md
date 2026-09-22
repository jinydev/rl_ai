---
layout: docs
title: "생성형 대화 오디오(TTS) 제작 가이드라인"
permalink: /audio/
---

# 🎧 생성형 대화 오디오(TTS) 제작 및 플레이어 연동 가이드라인

본 가이드라인은 **지니와 도로시의 강화학습 모험** 교재에 수록되는 모든 캐릭터 대화 장면(도로시, 지니, 토토)의 **생성형 신경망 TTS(Text-to-Speech) 음성 제작 표준**과 **웹 인터랙티브 플레이어 연동 규격**을 정의합니다.

다소 건조하고 어렵게 느껴질 수 있는 수학 수식과 알고리즘 유도 과정을, 친근한 캐릭터들의 생생한 목소리를 통해 오디오북처럼 귀로 들으며 직관적으로 이해할 수 있도록 돕는 멀티모달 학습 환경을 구축하는 것이 목표입니다.

---

## 🎙️ 1. 캐릭터별 음성 프로필 (Voice Profiles)

본 프로젝트는 고품질 인공신경망 음성 엔진인 **Edge TTS (Microsoft Azure Neural Voice 엔진 기반)**를 표준으로 사용합니다. 각 캐릭터의 성격과 나이, 역할에 맞추어 음성 모델, 피치(Pitch), 속도(Rate)를 정밀하게 조율합니다.

| 캐릭터 | 역할 및 페르소나 | 기본 보이스 ID | 피치 (Pitch) | 말하기 속도 (Rate) |
| :--- | :--- | :--- | :---: | :---: |
| 👧 **도로시 (Dorothy)** | **에이전트 / 학습자**<br>8~9세 초등학교 저학년 소녀, 호기심 가득하고 똘망똘망하며 순수한 목소리 | `ko-KR-SunHiNeural` | `+22Hz` | `+3%` |
| 🐱 **지니 (Jiny)** | **마법 멘토 / 환경**<br>지혜롭고 다정하며 장난기 넘치고 신비로운 마법사 고양이 | `ko-KR-InJoonNeural` | `+2Hz` | `+0%` |
| 🐶 **토토 (Toto)** | **동반자 / 가이드**<br>복슬복슬 귀여운 반려견, 밝고 앙증맞은 말소리 | `ko-KR-SunHiNeural` | `+38Hz` | `+8%` |

> [!TIP]
> **캐릭터 톤 유지 원칙**:
> - **도로시**: 질문을 던지거나 새로운 깨달음을 얻을 때 살짝 들뜬 듯한 호기심 어린 어조를 유지합니다.
> - **지니**: 도로시의 질문을 부드럽게 칭찬하며 수식의 본질을 짚어주는 다정하고 신뢰감 있는 멘토 톤을 유지합니다.

---

## 📐 2. 텍스트 정제 및 수식 발음 규칙 (Text Preprocessing)

마크다운 원문에는 LaTeX 수식(`$v_\pi(s)$`, `\sum`)과 강조 기호(`**bold**`)가 포함되어 있습니다. TTS 엔진에 이를 그대로 전달하면 영어 기호나 백슬래시(`\`)를 기계적으로 읽어 청취감이 크게 저하되므로, **한국어 구어체 변환 전처리**를 반드시 수행해야 합니다.

### (1) 마크다운 및 특수문자 제거
- `**텍스트**`, `*텍스트*`, `` `텍스트` `` $\rightarrow$ 강조 기호 제거 후 순수 텍스트만 추출
- 따옴표(`"`, `'`), 화살표(`->`, `=>`) 등은 문맥에 맞게 정제

### (2) 강화학습 핵심 수식 변환표

| 원문 표기 (Markdown/LaTeX) | 구어체 변환 발음 | 설명 |
| :--- | :--- | :--- |
| `$v_\pi(s)$` | **"상태 가치 브이 파이 에스"** | 상태 가치 함수 |
| `$v_\pi(s')$` | **"다음 상태 가치 브이 파이 에스 프라임"** | 한 스텝 뒤의 가치 |
| `$v_\pi(s_1)$` | **"다음 상태 가치 브이 파이 에스 원"** | 특정 다음 상태 가치 |
| `$G_t$` | **"수익 지 티"** | 시점 $t$에서의 할인 누적 보상 |
| `$G_{t+1}$` | **"다음 시간 수익 지 티 플러스 일"** | 시점 $t+1$에서의 수익 |
| `$R_t$` | **"즉각 보상 알 티"** | 행동 직후 받는 보상 |
| `$S_t = s$` | **"현재 상태 에스 티가 에스"** | 조건부 확률의 현재 상태 조건 |
| `$S_{t+1} = s'$` | **"다음 상태 에스 티 플러스 일이 에스 프라임"** | 전이 후 다음 상태 조건 |
| `$\mathbb{E}$` | **"기댓값"** 또는 **"기댓값 이"** | 평균 기댓값 연산자 |
| `$\gamma$` | **"할인율 감마"** | 미래 보상 감쇠 계수 |
| `$\pi(a \mid s)$` | **"정책 파이 오브 에이 기븐 에스"** | 상태 조건부 행동 정책 |
| `$p(s' \mid s, a)$` | **"상태 전이 확률 피"** | 환경의 상태 전이 함수 |
| `$p(x, y) = p(x) p(y \mid x)$` | **"동시 확률 피 엑스 와이는 피 엑스 곱하기 피 와이 기븐 엑스"** | 확률의 곱셈 정리 |
| `$\sum_{a, s'}$` | **"모든 행동과 다음 상태에 대한 시그마"** | 합산 기호 |
| `$\sum_x \sum_y$` | **"시그마 엑스, 시그마 와이"** | 2중 시그마 기호 |

### (3) 숫자, 분수 및 백분율 변환
- `1/12`, `1/6`, `1/2` $\rightarrow$ **"십이분의 일"**, **"육분의 일"**, **"이분의 일"**
- `4/5`, `1/5` $\rightarrow$ **"오분의 사"**, **"오분의 일"**
- `80%`, `20%`, `100%` $\rightarrow$ **"팔십 퍼센트"**, **"이십 퍼센트"**, **"백 퍼센트"**
- `0.8`, `0.12`, `2.35` $\rightarrow$ **"영 점 팔"**, **"영 점 일 이"**, **"이 점 삼 오"**
- `MDP`, `DP` $\rightarrow$ **"엠디피"**, **"동적 계획법 디피"**
- `Q 함수` $\rightarrow$ **"큐 함수"**

---

## 📁 3. 파일 저장 경로 및 네이밍 규칙

대화 음성 파일은 장(Chapter) 및 절(Section) 단위로 독립된 디렉터리에 격리 관리하며, Jekyll 정적 사이트 빌드 시 배포 경로로 동기화됩니다.

### 디렉터리 구조
```bash
강화학습/
├── src/
│   ├── 06_벨만_방정식/
│   │   ├── 6_1_벨만_소개와_사전_학습/
│   │   │   ├── audio/                     # 6.1절 음성 파일 보관
│   │   │   │   ├── dialogue_6_1_scene1.mp3
│   │   │   │   └── ...
│   │   │   └── index.md
│   │   └── 6_2_벨만_방정식_도출/
│   │       ├── audio/                     # 6.2절 음성 파일 보관
│   │       │   ├── dialogue_6_2_scene1.mp3
│   │       │   └── ...
│   │       └── index.md
│   └── assets/
│       └── js/
│           └── audio.js                   # 공용 대화 오디오 플레이어 컨트롤러
└── docs/                                  # Jekyll 빌드 출력물 (GitHub Pages 서비스 경로)
    └── 06_벨만_방정식/.../audio/
```

### 파일명 명명 규칙 (Naming Convention)
- `dialogue_{chapter}_{section}_scene{N}.mp3`
- 예시:
  - 06.1절의 1번 대화 씬: `dialogue_6_1_scene1.mp3`
  - 06.2절의 14번 대화 씬: `dialogue_6_2_scene14.mp3`

> [!IMPORTANT]
> 도로시와 지니(또는 토토)의 개별 발화 음성을 각각 임시 생성한 후, 대화 순서대로 바이너리 병합하여 **단일 씬 MP3 파일**로 최종 완성해야 플레이어 클릭 한 번으로 연속 청취가 가능합니다.

---

## 💻 4. 웹 오디오 플레이어 UI 및 연동 스크립트

### (1) 마크다운 삽입용 HTML 컴포넌트
마크다운 문서에서 대화 블록(`> 👧 **도로시**:`) 바로 위에 다음 표준 HTML 플레이어를 배치합니다.

```html
<div class="dialogue-audio-player" style="display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 8px; background: #f8fafc; border-left: 4px solid #0284c7; border-radius: 6px; padding: 8px 14px; margin: 16px 0 10px 0; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
  <div style="display: flex; align-items: center; gap: 6px;">
    <span style="font-size: 1.1rem;">🎧</span>
    <span style="font-weight: 600; font-size: 0.9rem; color: #0369a1;">대화 음성 듣기 (도로시 & 지니)</span>
  </div>
  <div style="display: flex; align-items: center; gap: 6px;">
    <button type="button" class="btn-audio-play" style="background: #0284c7; color: #ffffff; border: none; border-radius: 16px; padding: 5px 13px; font-size: 0.82rem; font-weight: 600; cursor: pointer; display: inline-flex; align-items: center; gap: 4px; box-shadow: 0 1px 2px rgba(2,132,199,0.3);">
      <span>▶️ 재생</span>
    </button>
    <button type="button" class="btn-audio-stop" style="background: #e2e8f0; color: #475569; border: none; border-radius: 16px; padding: 5px 11px; font-size: 0.82rem; font-weight: 600; cursor: pointer; display: inline-flex; align-items: center; gap: 4px;">
      <span>⏹️ 정지</span>
    </button>
  </div>
  <audio src="./audio/dialogue_6_2_scene1.mp3" preload="none"></audio>
</div>

> 👧 **도로시**: "지니! 현재 상태의 가치가 다음 상태 가치들의 합으로 이어진다는 게 정말 신기해!"
> 
> 🐱 **지니**: "맞아 도로시! 종이비행기가 어느 타일로 날아가든, 앞으로 받을 보상들의 평균값을 계산하면 단번에 알 수 있단다!"
```

### (2) 공용 컨트롤러 자바스크립트 (`audio.js`) 동작 원리
모든 플레이어는 `src/assets/js/audio.js` 스크립트를 통해 자동으로 이벤트가 바인딩됩니다.
1. **재생 / 일시정지 토글**: `btn-audio-play` 클릭 시 재생(`▶️ 재생`)과 일시정지(`⏸️ 일시정지`) 상태가 전환됩니다.
2. **단일 오디오 재생 보장 (Mutual Exclusion)**: 한 오디오가 재생되면 페이지 내 다른 모든 재생 중인 오디오는 즉시 일시정지 및 처음 위치로 초기화됩니다.
3. **정지 및 완료 초기화**: `btn-audio-stop` 클릭 시 음성이 멈추고 처음으로 되감기며 버튼 상태가 초기화됩니다. 오디오가 끝까지 재생되었을 때(`ended` 이벤트)도 자동으로 재생 버튼으로 복귀합니다.

---

## 🐍 5. 자동 생성 파이썬 스크립트 템플릿

새로운 챕터에 대화 음성을 추가할 때 재사용할 수 있는 표준 파이썬 스크립트 구조입니다.

```python
import asyncio
import os
import re
import shutil
import edge_tts

# 1. 설정
OUTPUT_DIR = './audio'
TEMP_DIR = '/tmp/tts_temp'
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

VOICES = {
    'dorothy': {'voice': 'ko-KR-SunHiNeural', 'pitch': '+22Hz', 'rate': '+3%'},
    'jiny': {'voice': 'ko-KR-InJoonNeural', 'pitch': '+2Hz', 'rate': '+0%'},
    'toto': {'voice': 'ko-KR-SunHiNeural', 'pitch': '+38Hz', 'rate': '+8%'},
}

# 2. 음성 생성 및 파일 병합
async def generate_scene(scene_num, lines, filename):
    temp_files = []
    for idx, (role, text) in enumerate(lines):
        clean_text = preprocess_text(text)
        temp_path = os.path.join(TEMP_DIR, f's{scene_num}_{idx}.mp3')
        prof = VOICES[role]
        comm = edge_tts.Communicate(clean_text, prof['voice'], pitch=prof['pitch'], rate=prof['rate'])
        await comm.save(temp_path)
        temp_files.append(temp_path)

    # 바이너리 이어붙이기 (단일 씬 MP3 파일 완성)
    final_path = os.path.join(OUTPUT_DIR, filename)
    with open(final_path, 'wb') as outfile:
        for tf in temp_files:
            with open(tf, 'rb') as infile:
                outfile.write(infile.read())
    print(f'Scene {scene_num} 완성: {final_path}')
```

---

## 📝 6. 대화문 작성 및 배치 원칙 (Content Guidelines)

1. **대화 배치의 황금률**:
   - **대화문은 항상 생성형 이미지(삽화)의 앞쪽에 배치**합니다. (독자가 캐릭터들의 호기심 어린 대화를 먼저 읽고 들은 뒤, 그 아래의 시각 다이어그램을 보며 자연스럽게 내용을 이해하도록 유도)
2. **역할 분담의 명확성**:
   - 도로시는 독자의 시선에서 가질 법한 자연스러운 의문("왜 기댓값이 3.5지?", "시간 $t$와 $t+1$이 왜 다르지?")을 질문합니다.
   - 지니는 수학적 정의에 얽매이기보다 일상적인 비유(비디오 게임, 서울-부산 여행, 보물 상자)로 핵심 직관을 짚어줍니다.
3. **오디오 용량 최적화**:
   - `<audio preload="none">` 설정을 사용하여 페이지 초기 로딩 시 불필요한 네트워크 트래픽을 방지하고, 사용자가 재생 버튼을 누를 때만 스트리밍되도록 최적화합니다.
