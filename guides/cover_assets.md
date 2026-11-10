# 도로시 세계관 커버 슬라이드 및 독립 애셋(Cover Assets) 제작 마스터 가이드

본 문서는 강의용 프레젠테이션(PPTX)의 첫 페이지인 **커버 슬라이드(Cover Slide)**와 유튜브/웹 대표 **커버 이미지(PNG)**를 제작할 때, **강의 본문(`index.md`)의 핵심 개념을 반영한 장면을 먼저 구상하고, 장면을 구성하는 캐릭터와 소품을 부분적 독립 애셋으로 선(先) 제작한 뒤 결합하는 마스터 워크플로우 가이드**입니다.

모든 캐릭터 스타일 및 규격은 [`/Users/hojin9/dev/projects/dorothy/prompt.md`](file:///Users/hojin9/dev/projects/dorothy/prompt.md) 및 도로시 프로젝트 6대 마스터 규격과 100% 동기화됩니다.

---

## 1. 핵심 제작 철학: 부분 애셋 선(先) 제작 후 결합 합성 (Component-First Composition)

> **[경고: 다중 인물 통합 씬 한 번에 생성 후 크롭 금지]**  
> 여러 인물이 함께 서 있는 그림을 한 번에 생성하여 사각형으로 잘라내면(Crop), 인물 간 경계선에서 팔, 다리, 손가락, 꼬리가 수직으로 잘리는 치명적인 결함(Clipping Glitch)이 발생합니다.

따라서 커버는 다음 5단계 파이프라인으로 제작합니다:
```
[1단계: 강의 본문 분석 & 연출 고민]
  → index.md의 핵심 개념 및 삽화 모티프 분석, 커버 장면 스토리 기획
        ↓
[2단계: 부분 애셋 분할 & 명세화]
  → 장면에 필요한 캐릭터 및 소품을 assets.md에 독립 애셋으로 지정
        ↓
[3단계: 단독 전신 투명 애셋 선(先) 제작]
  → 각 애셋을 순백색(#FFFFFF) 단독 피사체로 생성 후 알파 투명 PNG(RGBA)로 정밀 변환
        ↓
[4단계: 16:9 커버 이미지(PNG) 합성]
  → 개별 애셋들과 타이포그래피를 백색 캔버스에 Z-Order대로 결합
        ↓
[5단계: PPTX 커버 슬라이드 개별 Shape 삽입]
  → 파워포인트 슬라이드 1번에 개별 Picture 객체로 등록 (100% 자유 편집성 보장)
```

---

## 2. 1단계: 강의 본문(`index.md`) 분석 및 커버 장면 연출 기획

커버 이미지를 만들기 전, 해당 강의의 **핵심 알고리즘, 수학적 메커니즘, 개념적 은유(Metaphor)**를 먼저 깊이 고민합니다:

1. **강의의 핵심 질문**: 이 강의가 해결하고자 하는 핵심 문제는 무엇인가?
   - *예시 (10.1 TD법)*: "에피소드가 끝날 때까지 기다리지 않고, 단 1걸음만 이동하고도 가치를 즉시 갱신할 수 없을까?"
2. **개념적 은유(Metaphor)와 장면 연출**:
   - 이 메커니즘을 도로시 세계관에서 어떻게 생생하게 시각화할 것인가?
   - 도로시의 행동: 징검다리를 1-스텝 건너는 순간.
   - 조교 지니의 행동: 1-스텝 시간차를 정밀 측정하는 황금 회중시계와 연구 노트.
   - 토토의 반응: 도로시의 발걸음과 즉각 보상에 기뻐서 함께 달림.
   - 이호진 교수님의 멘토링: 점화식의 기초를 든든하게 받쳐주며 인자하게 지도.

---

## 3. 2단계: 부분 애셋 분할 및 지정 (`assets.md`)

연출이 결정되면, 장면에 등장하는 구성 요소들을 **독립된 부분 애셋(Component Assets)**으로 나눕니다:

```text
src/XX_대주제/XX_X_소주제/
├── assets.md                          # 기획된 부분 애셋 상세 명세서
├── XX_X_소주제.txt                     # 커버 기획 및 결합 합성 사양서
├── XX_X_소주제.png                     # 개별 애셋들을 결합한 최종 16:9 커버 이미지
└── assets/                            # Zero-Clipping 무결점 투명 배경(RGBA) 독립 애셋 저장소
    ├── asset_01_jiny_[동작].png       # 조교 지니의 맞춤 동작/소품
    ├── asset_02_dorothy_[동작].png    # 도로시의 맞춤 탐험 동작
    ├── asset_03_toto_[동작].png       # 토토의 맞춤 반응 동작
    └── asset_04_prof_hojin_[동작].png # 이호진 교수님의 맞춤 멘토링 포즈
```

---

## 4. 3단계: 개별 독립 애셋 생성 프롬프트 및 단독 피사체 원칙

각 애셋은 **다른 인물이나 소품이 침범하지 않는 완전한 단독 피사체(Solo Subject)**로 생성합니다.

### 4.1 이호진 교수님 (Prof. Hojin) - AI & 공학 멘토 (데이터셋 얼굴 모양 일치 절대 원칙)

> **[치명적 주의: 텍스트 프롬프트 단독 생성에 의한 얼굴 골격·형태 왜곡(Facial Identity Drift) 경고]**  
> AI 이미지 생성 모델에 텍스트 프롬프트로만 "40대 초반 동안, 솔트앤페퍼 헤어, 둥근 안경"이라고 지시할 경우, 모델은 고유 데이터셋의 미세한 얼굴 윤곽(부드러운 턱선, 특정 안경 비례, 눈매, 미소 라인)을 전혀 반영하지 못하고 **완전히 다른 엉뚱한 인물의 얼굴형(길쭉한 턱, 과장된 이목구비 등)을 임의로 생성**해 버립니다.
> 
> 따라서 **이호진 교수님의 얼굴은 텍스트 생성에 의존하는 것을 엄격히 금지**하며, 다음과 같은 원칙으로 얼굴 정체성을 100% 보존합니다:
> 1. **공식 데이터셋 직접 연동**: [`hojin_26.jpg`](file:///Users/hojin9/dev/projects/dorothy/data/dataset/hojin/hojin_26.jpg)의 검증된 오리지널 얼굴 및 전신 실루엣을 기준 마스터 애셋(`asset_04_prof_hojin.png`)으로 직접 사용합니다.
> 2. **신규 동작 생성 시 필수 참조**: 새로운 포즈가 필요한 경우에도 반드시 `hojin_26.jpg`를 레퍼런스 이미지(ControlNet / Image-to-Image / Inpainting)로 주입하여 데이터셋의 얼굴 형태와 이목구비가 1픽셀도 변형되지 않도록 고정해야 합니다.

- **데이터셋 공인 얼굴 특징 (`hojin_26` 표준)**:
  - **얼굴형 & 피부**: 갸름하고 부드러운 동안 얼굴 윤곽 (노안/각진 턱/긴 하관 절대 금지), 매끄러운 피부.
  - **헤어스타일**: 자연스럽게 가르마를 탄 단정한 솔트앤페퍼 흑발 (귀 윗부분에 과하지 않은 은빛 스트리크).
  - **안경 & 눈매**: 얇고 심플한 실버 라운드 메탈 와이어테 안경, 쌍꺼풀 있는 선하고 총명한 눈매.
  - **표정**: 입꼬리를 자연스럽게 올린 온화하고 다정한 멘토의 스마트한 미소.
  - **착장**: 로고/배지/SNU 문구가 일절 없는 무지 다크 차콜 네이비 반팔 폴로 셔츠, 중청 스트레이트 진, 그레이 스웨이드 스니커즈.
- **표준 애셋 파일**:
  - [`/Users/hojin9/dev/projects/dorothy/data/dataset/hojin/hojin_26.jpg`](file:///Users/hojin9/dev/projects/dorothy/data/dataset/hojin/hojin_26.jpg) 기반 정밀 투명화 애셋 (`373 x 984 px`, RGBA 투명 PNG).

### 4.2 도로시 (Dorothy) - 호기심 가득한 주니어 메이커 (인체학적 관절·다리 꼬임 방지 절대 규칙)

> **[치명적 주의: 몸통-골반-다리 방향 불일치 및 꼬임(Biomechanical Torso-Leg Twist Error) 금지]**  
> AI 이미지 생성 시 '앞으로 걷는 동작(Walking / Stepping)'을 유도할 때, 상체(어깨, 흉곽, STEM HERO 패치)는 정면을 향하고 있는데 골반과 다리는 측면으로 돌아가 가랑이선과 양 다리가 꽈배기처럼 비정상적으로 X자로 꼬이는 **인체 해부학적 왜곡(Anatomical Distortion)**이 빈번히 발생합니다.  
> 이는 인체 운동 역학(Kinematics)에 명백히 위배되므로 다음 검증 기준을 엄격히 준수합니다:
> 1. **관절 및 진행 축 정렬 (Kinematic Alignment)**:
>    - 어깨 중심선, 흉곽 축, 골반(Pelvis), 양 무릎, 발끝의 진행 방향이 하나의 자연스러운 인체 해부학적 척추 축을 따라 정렬되어야 합니다.
>    - 몸통이 정면일 때는 양다리 역시 정면을 향해 안정된 스탠스를 취해야 하며, 다리가 비틀려 가랑이 솔기가 꼬이는 현상을 전면 배제합니다.
> 2. **검증된 공식 데이터셋 애셋 활용**:
>    - 인체 비례와 관절 정렬이 완벽하게 검증된 공식 데이터셋([`dorothy_01.jpg`](file:///Users/hojin9/dev/projects/dorothy/data/dataset/dorothy/dorothy_01.jpg) 등) 기반의 무결점 애셋(`501 x 983 px`)을 우선 사용합니다.

- **체형 & 착장**: 정확한 4.5등신 치비/주니어 비례 (성인 비율 금지), 밤색 웨이브 양갈래 머리(구슬 방울 머리끈), 클래식 블루 데님 멜빵바지('STEM HERO' 패치), 주황 줄무늬 티, 새빨간 캔버스 운동화.
- **프롬프트 템플릿 (인체 정렬 검증형)**:
```text
Studio Ghibli 2D anime style, clean line art, warm vibrant flat cel shading, masterpiece. 
Full-body portrait of Dorothy, an adorable 9-year-old anime girl (4.5 heads tall junior proportions, wavy chestnut brown hair in twin pigtails with colorful beads, bangs, warm amber eyes, cheerful bright smile). 
Wearing classic medium blue denim overalls with a round 'STEM HERO' patch on the chest, orange striped t-shirt underneath, vibrant ruby red canvas sneakers. 
Standing with perfect natural anatomical balance and proper joint alignment (torso, hips, legs, and feet naturally facing forward without any twisting), both arms positioned naturally, full body visible from head to toe, generous white margins on all sides, pure solid clean white background (#FFFFFF), isolated character, zero clipping.
```

### 4.3 토토 (Toto) - 비타민 파트너 강아지
- **품종 & 착장**: 단색 웜밀크 화이트(`FBF6EB`) 비숑-말티즈 (얼룩 없음), 스카이블루 반다나, 핑크빛 혀.
- **프롬프트 템플릿**:
```text
Studio Ghibli 2D anime style, clean line art, soft cel shading, masterpiece. 
Full-body portrait of Toto the puppy, an adorable fluffy cream-white puppy (bichon-maltese mix) with a uniform solid warm milk-white coat and NO spots or patches, soft floppy ears, round black button eyes, glossy black button nose, cheerful happy open-mouthed dog smile with pink tongue. 
Wearing a vibrant sky-blue neckerchief bandana tied around his neck, curled plumey tail wagging cheerfully. 
Trotting happily on all four paws, complete full body uncropped with generous margins, pure solid clean white background (#FFFFFF), isolated puppy asset.
```

### 4.4 조교 지니 (Jiny the Assistant) - 천재 연구실 조교 냥이
- **외모 & 소품**: 턱시도 코숏, 올리브 눈, 미니 안경, 빨간 방울 목걸이, 원목 책상과 대형 황금 회중시계.
- **프롬프트 템플릿**:
```text
Studio Ghibli 2D anime style, clean sharp line art, soft warm flat cel shading, masterpiece. 
Jiny the lab assistant cat, an adorable slightly chubby black-and-white bicolor tuxedo cat with cow pattern fur, intelligent olive-green eyes, baby pink button nose, wearing tiny round scholar glasses perched on his nose and a red collar with a golden bell. 
Jiny sits smartly behind a small sturdy wooden scholar desk, holding up a glowing golden pocket watch with one paw and taking notes with the other, bushy black tail curled neatly beside him. 
Full silhouette completely visible without any cut edges, generous breathing room, pure solid clean white background (#FFFFFF), isolated asset.
```

---

## 5. 4단계: 알파 마스킹을 통한 순수 투명 PNG(RGBA) 변환

순백색 배경 이미지(`RGB`)에서 완벽한 알파 투명 배경(`RGBA`)을 추출하는 표준 파이썬 알고리즘:

```python
from PIL import Image
import numpy as np

def convert_to_transparent_asset(input_path, output_path, white_thresh_high=252, white_thresh_low=240):
    """
    순수 백색 배경을 티끌 없는 알파 투명 배경으로 변환 (안티앨리어싱 보존 및 테두리 자동 트리밍)
    """
    img = Image.open(input_path).convert("RGBA")
    arr = np.array(img)
    
    r, g, b, a = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2], arr[:, :, 3]
    min_rgb = np.minimum(np.minimum(r, g), b)
    
    # 252 이상: 100% 완전 투명 (alpha = 0)
    # 240 이하: 100% 완전 불투명 (alpha = 255)
    # 240 ~ 252 구간: 매끄러운 선형 보간 (Alpha Falloff)
    alpha = np.where(min_rgb >= white_thresh_high, 0,
            np.where(min_rgb < white_thresh_low, 255,
                     ((white_thresh_high - min_rgb) / float(white_thresh_high - white_thresh_low) * 255).astype(np.uint8)))
    arr[:, :, 3] = alpha
    
    # 투명 여백 자동 트리밍 (Trim Margins)
    non_zero = np.where(alpha > 10)
    if len(non_zero[0]) > 0:
        ymin, ymax = max(0, non_zero[0].min() - 8), min(arr.shape[0] - 1, non_zero[0].max() + 8)
        xmin, xmax = max(0, non_zero[1].min() - 8), min(arr.shape[1] - 1, non_zero[1].max() + 8)
        trimmed = arr[ymin:ymax+1, xmin:xmax+1]
        out_img = Image.fromarray(trimmed)
        out_img.save(output_path, "PNG")
```

---

## 6. 5단계: 개별 애셋들을 결합한 16:9 커버 이미지(PNG) 합성

개별 애셋이 준비되면, 1376x768 캔버스 위에 레이어 순서(Z-Order)대로 배치하고 타이포그래피와 결합합니다:

```python
from PIL import Image, ImageDraw, ImageFilter

def compose_cover_image(assets_spec, output_path, canvas_size=(1376, 768)):
    canvas = Image.new("RGBA", canvas_size, (255, 255, 255, 255))
    
    # Z-Order에 따라 순차 배치 (지니 Z=1 -> 도로시 Z=2 -> 토토 Z=3 -> 교수님 Z=4)
    for filename, target_h, target_x, target_y in assets_spec:
        asset = Image.open(filename).convert("RGBA")
        target_w = int(target_h * (asset.width / asset.height))
        resized = asset.resize((target_w, target_h), Image.Resampling.LANCZOS)
        
        # 발 밑 타원형 부드러운 앰비언트 오클루전 그림자 합성
        shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        s_draw = ImageDraw.Draw(shadow)
        foot_y = target_y + target_h - 10
        s_cx = target_x + target_w // 2
        s_draw.ellipse([s_cx - target_w//3, foot_y - 12, s_cx + target_w//3, foot_y + 12], fill=(0, 0, 0, 45))
        shadow = shadow.filter(ImageFilter.GaussianBlur(8))
        canvas.alpha_composite(shadow)
        
        # 피사체 합성
        canvas.paste(resized, (target_x, target_y), resized)
        
    # 좌측 타이포그래피(뱃지, 타이틀, 부제목, 강사 서명) 렌더링 후 저장
    canvas.convert("RGB").save(output_path, "PNG")
```

---

## 7. 6단계: PPTX 커버 슬라이드에 개별 Picture 객체 배치 (자유 편집성)

파워포인트 첫 번째 슬라이드에는 개별 투명 애셋을 독립된 Picture 객체로 삽입합니다:

```python
from pptx.util import Inches

def add_cover_slide(prs, assets_dir):
    slide = prs.slides.add_slide(prs.slide_layouts[6]) # 빈 슬라이드
    
    # 좌측 텍스트 상자들 배치 (뱃지, 타이틀 36pt, 부제목 20pt)
    # ...
    
    # 우측 개별 애셋 개별 객체로 삽입 (발표자가 파워포인트 내에서 드래그 이동/크기 조절 가능)
    slide.shapes.add_picture(f"{assets_dir}/asset_01_jiny_scholar.png", Inches(6.5), Inches(3.2), width=Inches(2.0))
    slide.shapes.add_picture(f"{assets_dir}/asset_02_dorothy_stepping.png", Inches(8.3), Inches(2.2), width=Inches(1.95))
    slide.shapes.add_picture(f"{assets_dir}/asset_03_toto_running.png", Inches(9.8), Inches(4.2), width=Inches(1.4))
    slide.shapes.add_picture(f"{assets_dir}/asset_04_prof_hojin.png", Inches(11.0), Inches(1.3), width=Inches(2.0))
```

이 체계를 통해:
1. **Zero-Clipping**: 인물들이 서로 겹치더라도 경계선이 잘리지 않고 자연스럽게 어우러집니다.
2. **100% 자유 편집성**: 발표자가 PPTX에서 인물 위치나 크기를 자유롭게 변경할 수 있습니다.
3. **완벽한 시각 일관성**: 커버 이미지(PNG)와 PPTX 커버 슬라이드의 비주얼이 완벽히 일치합니다.
