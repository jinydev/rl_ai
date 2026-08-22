# 🧭 마법 요정 고양이 지니와 함께하는 도로시와 토토의 강화학습 모험

이 책은 오즈의 마법사에서 영감을 얻은 **도로시**와 그의 반려견 **토토**, 그리고 요술 램프에서 나타난 신비로운 마법 요정 고양이 **지니**가 함께 격자 세상을 탐험하는 이야기를 다룹니다. 다소 건조하고 수학적인 **인공지능 강화학습(Reinforcement Learning)**을 신밧드의 모험처럼 흥미진진한 보물 탐구의 여정으로 풀어내어, 가장 직관적이고 친근하게 학습할 수 있도록 안내하는 특별한 가이드 교재입니다.

![지니와 도로시, 토토의 모험](./img/dorothy_toto_jiny.png)

---

## 👥 캐릭터 소개 (Characters)

강화학습이라는 넓고 낯선 모험 지도를 헤쳐 나가는 세 명의 주인공입니다.

### 🧞‍♂️ 지니 (Jiny)
* **역할**: 마법 멘토 (Teacher) / 환경 (Environment)
* **시각적 특징**: 보라빛 털의 날씬하고 세련된 마법 고양이(Slender purple-blue magic cat), 이집트 스핑크스 고양이를 닮은 크고 곧게 선 귀(Large sharp ears), 공중에 둥둥 떠 있으며 마법 연기와 별가루에 둘러싸임, 3등신 SD 비율
* **캐릭터 이미지**:
  ![지니](./img/jiny.png)
* **성격 및 설명**: 
  요술 램프에서 나타나는 신비롭고 영리한 마법사 고양이이자, 도로시와 토토의 현명한 강화학습 교사입니다. 드래곤볼의 '파괴신 비루스'처럼 날렵하고 세련된 보랏빛 스핑크스 고양이의 외형을 지녔지만, 성격은 매우 상냥하고 귀여운 반전 매력이 있습니다. 신비로운 푸른 마법 연기와 반짝이는 별가루를 흩날리며 도로시에게 강화학습의 복잡한 수식을 장난스럽고 이해하기 쉽게 가르쳐주는 똑똑한 멘토입니다.

### 👧 도로시 (Dorothy)
* **역할**: 에이전트 (Agent) / 학습자 (Learner)
* **시각적 특징**: 갈색 단발머리(Short bob cut brown hair), 단정한 옅은 하늘색 스쿨 베스트(교복 조끼)와 주름치마, 검은색 점눈(Black dot eyes), 3등신 SD 비율
* **캐릭터 이미지**:
  ![도로시](./img/dorothy.png)
* **성격 및 설명**: 
  늘 호기심이 많고 긍정적인 소녀입니다. 새로운 격자 세상(Grid World)에 놓일 때마다 나침반과 수첩을 들고 기댓값을 계산하며, 최적의 가치(Value)와 정책(Policy)을 찾아 성장합니다.

### 🐶 토토 (Toto)
* **역할**: 동반자 (Companion) / 가이드 (Guide)
* **시각적 특징**: 복슬복슬한 갈색 아기 푸들형 강아지(Poodle-like curly brown dog), 앙증맞은 목줄, 2등신 SD 비율
* **캐릭터 이미지**:
  ![토토](./img/toto.png)
* **성격 및 설명**: 
  도로시의 충직한 반려견입니다. 도로시가 수학적 고민에 빠지거나 길을 잃었을 때 꼬리를 흔들며 사과 보상이 있는 방향을 앞발로 콕 가리켜주는 든든한 길잡이 역할을 합니다.

---

## 🎨 일러스트 생성 가이드 (Illustration Prompt Guide)

도로시, 토토, 그리고 지니의 모험에 사용되는 모든 삽화는 **일관성 있는 Chibi 화풍**을 유지해야 합니다. 향후 생성형 AI(예: Gemini/Imagen 등)를 통해 삽화를 생성하거나 수정할 때는 다음 공식 가이드를 철저하게 따릅니다.

### 1. 이미지 스타일 치트키 프롬프트 (Core Prompt Formula)
새로운 상황의 이미지를 생성할 때는 항상 아래 프롬프트 문구를 접두사(Prefix)로 사용하여 스타일 일관성을 보장합니다.

> **[필수 접두 프롬프트]**
> `Super cute chibi character, simple 2.5-3 head ratio SD style, thick clean black outlines, flat pastel colors, very simple facial features with black dot eyes, white background.`

### 2. 캐릭터별 묘사 프롬프트 (Character Description)
* **지니 (Jiny)**: `A slender and sleek purple-blue magical cat with large tall pointed ears, inspired by the style of a Sphynx cat but drawn in an extremely cute and friendly way. It floats in mid-air with tiny sparkling stars and soft blue magical smoke around it, smiling warmly. No hat and no boots. Cozy, warm, educational textbook style illustration.`
* **도로시 (Dorothy)**: `A cute young school girl with short bob cut hair (brown), wearing a simple sky blue school vest and a pleated skirt. Cozy, warm, educational textbook style illustration.`
* **토토 (Toto)**: `A fluffy curly brown puppy with a cute collar happily. Cozy, warm, educational textbook style illustration.`

### 3. 디자인 및 화풍 상세 규칙 (Design Rules)
* **라인 아트**: 카툰 느낌의 두껍고 깔끔한 **검은색 외곽 테두리선(Thick clean black outlines)**을 반드시 유지합니다.
* **색상 팔레트**: 너무 자극적이거나 원색적인 톤은 피하고, 따뜻하고 화사한 **플랫 파스텔톤(Flat pastel colors)**의 색상을 사용합니다.
* **눈 표현**: 복잡하고 화려한 만화식 눈망울 대신, 검고 심플한 **점눈(Black dot eyes)**으로 단순화하여 도로시의 귀여움을 극대화합니다.
* **배경**: 인물과 다이어그램이 돋보이도록 원칙적으로 깔끔한 **흰색 배경(White background)**을 바탕으로 생성합니다.

---

## 📚 교재 기술 및 서술 가이드라인 (Textbook Guidelines)

본 교재의 마크다운 콘텐츠를 집필하거나 수정할 때는 독자의 학습 몰입감을 높이기 위해 다음 3대 원칙을 철저하게 고수합니다.

### 1. 수식 렌더링 호환성 유지 (No MathJax/LaTeX dependency)
특수 수식 렌더링 플러그인이 깔려있지 않은 일반 마크다운 리더나 브라우저에서도 수식이 깨지지 않고 직관적으로 읽히도록 아래의 포맷을 사용합니다.
* **LaTeX 기호($) 사용 제한**: 줄바꿈이나 특정 뷰어에서 깨지기 쉬운 인라인 `$` 문법을 지양합니다.
* **대체 서식 활용**:
  - 변수나 수식은 마크다운 이탤릭체(`*s*`, `*a*`, `*v*`)로 캡슐화합니다.
  - 첨자가 HTML 태그(`<sub>`, `<sup>`)를 사용합니다. (예: *v*<sub>*π*</sub>(*s*))
  - 수학 연산자가 직관적인 유니코드 문자(`×`, `≥`, `∑`)를 사용합니다.

### 2. 지니와 함께하는 도로시/토토의 모험 비유 (Adventure Metaphor)
복잡하고 추상적인 강화학습의 수학적 개념을 지니가 도로시와 토토에게 친절하게 설명하는 마법 도구와 스토리에 비유하여 소개합니다.
* **상태 가치 함수 *v*(*s*)**: 도로시가 특정 땅(상태)에 발을 디뎠을 때, 그 땅이 가진 잠재적 가치(보물상자의 크기).
* **행동 가치 함수 *q*(*s*, *a*)**: 도로시가 특정 땅(상태)에서 특정 방향으로 발걸음을 떼는 행동(행동)을 저질렀을 때의 성적표.
* **즉각 보상 *R* / 할인율 *γ***: 오늘 먹는 달콤한 사과(+10)와 먼 미래에 열릴 보물상자의 시간 가치 할인(할인율). 지니의 '사과 마법'과 '유통기한 마법'에 대응됩니다.
* **벨만 방정식**: 오늘 얻을 사과와 내일 도착할 땅의 가치의 합을 구하기 위해 지니가 칠판에 적어주는 마법의 계산식.
* **무한 루프 문제**: 다람쥐 쳇바퀴에 갇혀 끝없이 달리는 도로시를 지니가 벨만 방정식이라는 연립방정식 열쇠로 탈출시키는 비유.
* **정책 평가와 개선**: 도로시가 들고 다니는 엉성한 지도(*μ*)를 보고 지니가 돋보기로 계산하여 더 좋은 방향의 화살표로 지도를 업그레이드(탐욕화)해주는 교육 과정.

### 3. 코드와 그림의 정합성
* 코드 blocks는 설명이나 마크다운 파싱 문제로 쪼개어 렌더링되지 않도록 하나의 완전한 블록으로 병합하여 제공합니다.
* 파이썬 문법(예: `yield`, `@property`, `defaultdict`)에 대한 직관적인 비유 설명(자판기, 가면, 마법의 상자)을 지니의 대사나 삽화로 곁들여 설명합니다.
