import os
import re
from PIL import Image
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR

# ==========================================
# 1. 디자인 상수 정의 (16:9 규격 및 컬러 시스템)
# ==========================================
SLIDE_WIDTH = Inches(13.333)
SLIDE_HEIGHT = Inches(7.500)

COLOR_PRIMARY = RGBColor(26, 115, 232)      # #1A73E8 (Brand Blue Badge)
COLOR_TITLE = RGBColor(17, 24, 39)          # #111827 (Dark Charcoal, 거의 검정)
COLOR_SUBTITLE = RGBColor(107, 114, 128)    # #6B7280 (Medium Gray, 회색)
COLOR_BODY = RGBColor(31, 41, 55)           # #1F2937 (Body Text)
COLOR_DIVIDER = RGBColor(156, 163, 175)     # #9CA3AF (Divider Line, 실선)
COLOR_CAPTION = RGBColor(75, 85, 99)        # #4B5563 (Caption Gray)
COLOR_CODE_BG = RGBColor(248, 250, 252)     # #F8FAFC (Code BG)
COLOR_CODE_BORDER = RGBColor(226, 232, 240) # #E2E8F0 (Code Border)
COLOR_WHITE = RGBColor(255, 255, 255)

# 전체 폰트를 '나눔고딕'으로 통일
FONT_NAME = "나눔고딕"

BASE_DIR = "/Users/hojin9/dev/jinysite/강화학습3/src/10_TD법/10_1_TD법으로_정책_평가하기"
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
SLIDES_MD_PATH = os.path.join(BASE_DIR, "slides.md")
OUTPUT_PPTX_PATH = os.path.join(BASE_DIR, "10_1_TD법으로_정책_평가하기.pptx")

# ==========================================
# 2. 수식 및 텍스트 정제 엔진 (LaTeX/HTML -> PPTX 슬라이드 본문용)
# ==========================================
def convert_frac(text):
    """LaTeX 중첩 분수 \frac{num}{den}을 (num) / (den) 형태로 파싱"""
    while "\\frac" in text:
        idx = text.find("\\frac")
        open1 = text.find("{", idx)
        if open1 == -1:
            break
        depth, pos1 = 1, open1 + 1
        while pos1 < len(text) and depth > 0:
            if text[pos1] == "{":
                depth += 1
            elif text[pos1] == "}":
                depth -= 1
            pos1 += 1
        close1 = pos1 - 1
        num = text[open1 + 1 : close1]

        open2 = text.find("{", close1)
        if open2 == -1:
            break
        depth, pos2 = 1, open2 + 1
        while pos2 < len(text) and depth > 0:
            if text[pos2] == "{":
                depth += 1
            elif text[pos2] == "}":
                depth -= 1
            pos2 += 1
        close2 = pos2 - 1
        den = text[open2 + 1 : close2]

        text = text[:idx] + f"({num}) / ({den})" + text[close2 + 1 :]
    return text


def clean_math_and_symbols(text):
    """마크다운 수식, HTML 태그, LaTeX 문법을 PPTX 가독성 높은 기호로 100% 변환 (백슬래시/원화 기호 완전 박멸)"""
    if not text:
        return ""

    # 1. HTML 태그 및 마크다운 기호 선제거
    text = re.sub(r"<div align=.*?>.*?</div>", "", text)
    text = re.sub(r"\*+", "", text)
    text = text.replace("`", "").replace("$", "")

    # 2. HTML 첨자 변환
    text = re.sub(r"<sub\s*([a-zA-Z0-9+_-]+)\s*</sub>", r"_\1", text)
    text = re.sub(r"<sub>\s*([a-zA-Z0-9+_-]+)\s*</sub>", r"_\1", text)
    text = re.sub(r"<sup>\s*([a-zA-Z0-9+_-]+)\s*</sup>", r"^\1", text)
    text = re.sub(r"</?sub>", "", text)
    text = re.sub(r"</?sup>", "", text)

    # 3. 분수 변환
    text = convert_frac(text)

    # 4. LaTeX 서체 및 서식 명령어 언래핑
    for cmd in ["text", "mathbf", "operatorname", "hat"]:
        text = re.sub(r"\\" + cmd + r"\{([^{}]+)\}", r"\1", text)

    text = re.sub(r"\\left\s*([(\[{|])", r"\1", text)
    text = re.sub(r"\\right\s*([)\]}|])", r"\1", text)
    text = re.sub(r"\\left\.", "", text)
    text = re.sub(r"\\right\.", "", text)

    # 5. 그리스 문자 및 연산자 매핑 (긴 패턴 우선)
    math_map = [
        (r"\\varepsilon", "ε"),
        (r"\\epsilon", "ε"),
        (r"\\rho", "ρ"),
        (r"\\gamma", "γ"),
        (r"\\alpha", "α"),
        (r"\\delta", "δ"),
        (r"\\theta", "θ"),
        (r"\\sigma", "σ"),
        (r"\\pi", "π"),
        (r"\\sum", "∑"),
        (r"\\mathbb\{E\}|\\mathbb\s*E", "E"),
        (r"\\rightarrow|\\to", "→"),
        (r"\\xrightarrow\{.*?\}", "→"),
        (r"\\leftarrow", "←"),
        (r"\\implies", "⇒"),
        (r"\\dots|\\cdots|\\hellip|&hellip;", "…"),
        (r"\\times", "×"),
        (r"\\cdot", "·"),
        (r"\\approx", "≈"),
        (r"\\le\b|\\leq\b|≤", "≤"),
        (r"\\ge\b|\\geq\b|≥", "≥"),
        (r"\\neq", "≠"),
        (r"\\in", "∈"),
        (r"\\notin", "∉"),
        (r"\\mid", "|"),
        (r"\\sim", "~"),
        (r"\\arg\\max", "argmax"),
        (r"\\max_a|\bmax_a\b|\\maxa", "max_a"),
        (r"\\max", "max"),
        (r"\\min", "min"),
        (r"&nbsp;", " "),
    ]
    for pattern, rep in math_map:
        text = re.sub(pattern, rep, text)

    text = text.replace("^{2}", "²").replace("^2", "²")
    text = text.replace("_{t+1}", "_{t+1}").replace("_{t}", "_t").replace("_{T}", "_T")

    # 6. 최종 안전망: 남아 있는 모든 백슬래시 커맨드 및 백슬래시 문자 완전 소거 (원화 ₩ 노출 원천 방지)
    text = re.sub(r"\\[a-zA-Z]+", "", text)
    text = text.replace("\\", "")

    text = re.sub(r"^[>#\s]+", "", text)
    text = re.sub(r"[ \t]+", " ", text).strip()
    return text


# ==========================================
# 3. 슬라이드 노트 전용 TTS 음성 구술 변환 엔진
# ==========================================
def convert_to_tts_script(text):
    """향후 TTS가 자연스러운 한국어 구술 음성으로 발음하도록 수식 코드를 한글 독음으로 100% 변환"""
    if not text:
        return ""

    # 1. 괄호 분수 변환: \frac{A}{B} -> B 분의 A
    while "\\frac" in text:
        idx = text.find("\\frac")
        open1 = text.find("{", idx)
        if open1 == -1:
            break
        depth, pos1 = 1, open1 + 1
        while pos1 < len(text) and depth > 0:
            if text[pos1] == "{":
                depth += 1
            elif text[pos1] == "}":
                depth -= 1
            pos1 += 1
        close1 = pos1 - 1
        num = text[open1 + 1 : close1]

        open2 = text.find("{", close1)
        if open2 == -1:
            break
        depth, pos2 = 1, open2 + 1
        while pos2 < len(text) and depth > 0:
            if text[pos2] == "{":
                depth += 1
            elif text[pos2] == "}":
                depth -= 1
            pos2 += 1
        close2 = pos2 - 1
        den = text[open2 + 1 : close2]

        text = text[:idx] + f" {den} 분의 {num} " + text[close2 + 1 :]

    # 2. LaTeX 괄호 및 태그 언래핑 선행 처리
    for cmd in ["text", "mathbf", "operatorname", "hat"]:
        text = re.sub(r"\\" + cmd + r"\{([^{}]+)\}", r"\1", text)
    text = re.sub(r"\\left\s*([(\[{|])", r"\1", text)
    text = re.sub(r"\\right\s*([)\]}|])", r"\1", text)
    text = re.sub(r"\\left\.", "", text)
    text = re.sub(r"\\right\.", "", text)

    # 3. 첨자 형태의 Q 및 V 함수 표준화
    text = re.sub(r"Q_\{?\\?pi\}?|Q_\\pi|Q_pi", "큐 파이", text)
    text = re.sub(r"V_\{?\\?pi\}?|V_\\pi|V_pi", "브이 파이", text)

    replacements = [
        # 확률/정책 표기
        (r"\\pi\(A_\{t\+1\}\|S_\{t\+1\}\)|\bpi\(A_\{t\+1\}\|S_\{t\+1\}\)", "파이 오브 다음 상태에서의 다음 행동"),
        (r"b\(A_\{t\+1\}\|S_\{t\+1\}\)", "비 오브 다음 상태에서의 다음 행동"),
        (r"\\pi\([aA]\|[sS]\)|\bpi\([aA]\|[sS]\)", "파이 오브 에스에서의 행동"),
        (r"b\([aA]\|[sS]\)", "비 오브 에스에서의 행동"),
        # Q 및 V 함수 상세
        (r"큐 파이\(S_\{t\+1\},\s*A_\{t\+1\}\)", "큐 파이 오브 다음 상태 다음 행동"),
        (r"큐 파이\(S_t,\s*A_t\)", "큐 파이 오브 에스티 에이티"),
        (r"Q\(S_\{t\+1\},\s*A_\{t\+1\}\)", "큐 오브 에스티 플러스 원 에이티 플러스 원"),
        (r"Q\(s\x27,\s*a\x27\)", "큐 오브 에스 프라임 에이 프라임"),
        (r"Q\(s\x27,\s*a\)", "큐 오브 에스 프라임 에이"),
        (r"Q\(S_t,\s*A_t\)", "큐 오브 에스티 에이티"),
        (r"Q\(s,\s*a\)", "큐 오브 에스 에이"),
        (r"V\(S_\{t\+1\}\)", "브이 오브 에스티 플러스 원"),
        (r"V\(s\x27\)", "브이 오브 에스 프라임"),
        (r"V\(S_t\)", "브이 오브 에스티"),
        (r"V\(s\)", "브이 오브 에스"),
        (r"v_\\pi\(s\)|v_pi\(s\)", "상태 가치 브이 파이 오브 에스"),
        (r"q_\\pi\(s,\s*a\)|q_pi\(s,\s*a\)", "행동 가치 큐 파이 오브 에스 에이"),
        # 수익, 보상, 상태, 행동
        (r"\$G_\{t\+1\}\$|G_\{t\+1\}", "수익 지티 플러스 원"),
        (r"\$G_t\$|\bG_t\b", "수익 지티"),
        (r"\$R_\{t\+1\}\$|R_\{t\+1\}", "보상 알티 플러스 원"),
        (r"\$R_t\$|\bR_t\b", "즉각 보상 알티"),
        (r"\$S_\{t\+1\}\$|S_\{t\+1\}", "다음 상태 에스티 플러스 원"),
        (r"\$S_t\$|\bS_t\b", "상태 에스티"),
        (r"\$A_\{t\+1\}\$|A_\{t\+1\}", "다음 행동 에이티 플러스 원"),
        (r"\$A_t\$|\bA_t\b", "행동 에이티"),
        (r"\$S_0\$|\bS_0\b", "초기 상태 에스 제로"),
        (r"\$S_T\$|\bS_T\b", "종료 상태 에스 티"),
        (r"\bs\x27\b", "에스 프라임"),
        (r"\ba\x27\b", "에이 프라임"),
        # 그리스 문자 (LaTeX 및 유니코드 동시 처리)
        (r"\\varepsilon|\\epsilon|\bepsilon\b|ε", "입실론"),
        (r"\\rho|\brho\b|ρ", "로"),
        (r"\\gamma|\bgamma\b|γ", "감마"),
        (r"\\alpha|\balpha\b|α", "알파"),
        (r"\\delta_t|δ_t", "시간차 오차 델타티"),
        (r"\\delta|\bdelta\b|δ", "델타"),
        (r"\\theta|\btheta\b|θ", "세타"),
        (r"\\pi|\bpi\b|π", "파이"),
        (r"\\sigma|\bsigma\b|σ", "시그마"),
        (r"\\sum|∑", "시그마 합"),
        (r"\\mathbb\{E\}|\\mathbb\s*E|\bE\[.*?\]", "기댓값 이"),
        # 연산자 및 기호
        (r"\\max_a|\bmax_a\b|\\maxa", "맥스 에이"),
        (r"\\arg\\max|\bargmax\b", "아그맥스"),
        (r"\\approx|≈", "약"),
        (r"\\leftarrow|←|<-", "로 갱신"),
        (r"\\rightarrow|\\to|→", "에서"),
        (r"\\cdot|·|\\times|×", " 곱하기 "),
        (r"\\le\b|\\leq\b|≤", " 이하 "),
        (r"\\ge\b|\\geq\b|≥", " 이상 "),
        (r"\\neq|≠", " 다르다 "),
        (r"\\dots|\\cdots|…", " 등 "),
        # 프로그래밍 및 알고리즘 용어
        (r"ε-탐욕|입실론-탐욕|\\epsilon-greedy", "입실론 탐욕"),
        (r"TD\(0\)", "티디 제로"),
        (r"\bTD\b", "티디"),
        (r"\bMC\b", "엠씨"),
        (r"\bDP\b", "디피"),
        (r"\bSARSA\b", "살사"),
        (r"Q-러닝|Q-Learning|\bQLearning\b", "큐러닝"),
        (r"\bDQN\b", "디큐엔"),
        (r"SarsaOffPolicyAgent", "살사 오프 정책 에이전트"),
        (r"SarsaAgent", "살사 에이전트"),
        (r"TdAgent", "티디 에이전트"),
        (r"QLearningAgentSimple", "큐러닝 에이전트 심플"),
        (r"QLearningAgentStep1", "큐러닝 에이전트 스텝 원"),
        (r"QLearningAgent", "큐러닝 에이전트"),
        (r"GridWorld", "그리드월드"),
        (r"defaultdict", "디폴트딕트"),
        (r"\bdeque\b", "디큐"),
        (r"maxlen", "맥스렌"),
        (r"get_action", "겟 액션 메서드"),
        (r"greedy_probs", "그리디 프랍스 함수"),
        (r"\bupdate\b", "업데이트 메서드"),
        (r"\breset\b", "리셋 메서드"),
        (r"\beval\b", "이밸 메서드"),
        (r"\bstep\b", "스텝 메서드"),
        (r"\bdone\b", "던 플래그"),
        (r"self\.pi", "셀프 닷 파이"),
        (r"self\.b", "셀프 닷 비"),
        (r"self\.Q", "셀프 닷 큐"),
        (r"self\.V", "셀프 닷 브이"),
        (r"self\.memory", "셀프 닷 메모리"),
        (r"self\.gamma", "셀프 닷 감마"),
        (r"self\.alpha", "셀프 닷 알파"),
        (r"self\.epsilon", "셀프 닷 입실론"),
        (r"next_state", "넥스트 스테이트"),
        (r"next_action", "넥스트 액션"),
        (r"next_q_max", "넥스트 큐 맥스"),
        (r"next_q", "넥스트 큐"),
        (r"\btarget\b", "타겟"),
    ]

    for pattern, rep in replacements:
        text = re.sub(pattern, rep, text)

    text = re.sub(r"\\[a-zA-Z]+", "", text)
    text = re.sub(r"[\$`\\{}_^|*#\[\]]", " ", text)
    text = re.sub(r"&nbsp;", " ", text)
    text = re.sub(r"[ \t]+", " ", text).strip()
    return text


class PresentationBuilder:
    def __init__(self):
        self.prs = Presentation()
        self.prs.slide_width = SLIDE_WIDTH
        self.prs.slide_height = SLIDE_HEIGHT
        self.blank_layout = self.prs.slide_layouts[6]

    def create_editable_cover_slide(self):
        """첫 번째 슬라이드: 손/몸통 잘림 없는 온전한 독립 투명 배경 애셋 4종을 삽입한 편집 가능 커버 슬라이드"""
        slide = self.prs.slides.add_slide(self.blank_layout)

        # 1. 좌측 상단 파란색 뱃지 (14pt Bold)
        badge = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.0), Inches(2.9), Inches(0.5)
        )
        badge.fill.solid()
        badge.fill.fore_color.rgb = COLOR_PRIMARY
        badge.line.color.rgb = COLOR_PRIMARY
        badge.adjustments[0] = 0.5

        tf = badge.text_frame
        tf.word_wrap = False
        p = tf.paragraphs[0]
        p.text = "PART 10 · 강화학습 이론"
        p.font.name = FONT_NAME
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = COLOR_WHITE
        p.alignment = PP_ALIGN.CENTER

        # 2. 메인 강의 타이틀 (44pt 볼드)
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.75), Inches(5.6), Inches(1.5))
        tf = title_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = "10.1 TD법으로\n정책 평가하기"
        p.font.name = FONT_NAME
        p.font.size = Pt(44)
        p.font.bold = True
        p.font.color.rgb = COLOR_TITLE

        # 3. 부제목 설명문 (20pt 회색)
        sub_box = slide.shapes.add_textbox(Inches(0.8), Inches(3.45), Inches(5.6), Inches(1.8))
        tf = sub_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = "단 1-스텝의 다음 상태 가치를 이용해\n실시간으로 가치 함수를 갱신하는\n시간차 학습(TD)의 원리와 구현"
        p.font.name = FONT_NAME
        p.font.size = Pt(20)
        p.font.color.rgb = COLOR_SUBTITLE

        p2 = tf.add_paragraph()
        p2.text = "\n강의: 이호진 교수 · 조교 지니와 도로시 탐험대"
        p2.font.name = FONT_NAME
        p2.font.size = Pt(16)
        p2.font.bold = True
        p2.font.color.rgb = RGBColor(55, 65, 81)

        # 4. 우측 등장인물 애셋 개별 Picture 삽입 (같은 바닥선 y=6.0에 맞춰 나란히 배치)
        ground_y = Inches(6.0)

        # Z-1: 조교 지니 (h=2.4 -> top=3.6)
        p_jiny = os.path.join(ASSETS_DIR, "asset_01_jiny_scholar.png")
        if os.path.exists(p_jiny):
            slide.shapes.add_picture(p_jiny, Inches(6.5), ground_y - Inches(2.4), width=Inches(2.0))

        # Z-2: 도로시 (h=4.0 -> top=2.0)
        p_dorothy = os.path.join(ASSETS_DIR, "asset_02_dorothy_stepping.png")
        if os.path.exists(p_dorothy):
            slide.shapes.add_picture(p_dorothy, Inches(8.3), ground_y - Inches(4.0), width=Inches(2.0))

        # Z-3: 토토 (h=2.0 -> top=4.0)
        p_toto = os.path.join(ASSETS_DIR, "asset_03_toto_running.png")
        if os.path.exists(p_toto):
            slide.shapes.add_picture(p_toto, Inches(9.8), ground_y - Inches(2.0), width=Inches(1.5))

        # Z-4: 이호진 교수님 (h=5.0 -> top=1.0)
        p_hojin = os.path.join(ASSETS_DIR, "asset_04_prof_hojin.png")
        if os.path.exists(p_hojin):
            slide.shapes.add_picture(p_hojin, Inches(11.0), ground_y - Inches(5.0), width=Inches(1.9))

        # 5. 슬라이드 노트 (TTS 최적화 구술문)
        notes_slide = slide.notes_slide
        notes_slide.notes_text_frame.text = convert_to_tts_script(
            "반갑습니다. 이번 10장에서는 동적 계획법(DP)의 부트스트랩과 "
            "몬테카를로법(MC)의 모델 프리 샘플링이라는 양대 산맥의 강력한 장점을 융합하여 탄생한 "
            "'TD(시간차, Temporal Difference) 정책 평가' 기법을 함께 공부하겠습니다. "
            "에피소드가 완결되기 전이라도 단 한 걸음 내딛자마자 실시간으로 가치를 갱신하는 "
            "현대 강화학습의 핵심 원리를 차근차근 짚어보겠습니다."
        )

    def add_common_header(self, slide, title_text, subtitle_text, page_str):
        """표준 상단 헤더: 제목 32pt Bold (y 0.4), 부제 20pt 회색 (y 1.05), 구분선 0.75pt (y 1.7)"""
        # 제목: x 0.8, y 0.4, 32pt, Bold, 왼쪽 정렬, 한 줄
        t_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(10.5), Inches(0.55))
        tf = t_box.text_frame
        tf.word_wrap = True
        tf.margin_top = 0
        tf.margin_bottom = 0
        tf.margin_left = 0
        p = tf.paragraphs[0]
        p.text = clean_math_and_symbols(title_text)
        p.font.name = FONT_NAME
        p.font.size = Pt(32)
        p.font.bold = True
        p.font.color.rgb = COLOR_TITLE

        # 부제: x 0.8, y 1.05, 20pt, 회색, 한 줄
        s_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.05), Inches(10.5), Inches(0.45))
        sf = s_box.text_frame
        sf.word_wrap = True
        sf.margin_top = 0
        sf.margin_bottom = 0
        sf.margin_left = 0
        sp = sf.paragraphs[0]
        sp.text = clean_math_and_symbols(subtitle_text)
        sp.font.name = FONT_NAME
        sp.font.size = Pt(20)
        sp.font.color.rgb = COLOR_SUBTITLE

        # 페이지 번호: 오른쪽 위 x 11.33, y 0.5, 14pt, '02 / 54' 형식, 오른쪽 정렬
        p_box = slide.shapes.add_textbox(Inches(11.333), Inches(0.5), Inches(1.2), Inches(0.4))
        pf = p_box.text_frame
        pp = pf.paragraphs[0]
        pp.text = page_str
        pp.alignment = PP_ALIGN.RIGHT
        pp.font.name = FONT_NAME
        pp.font.size = Pt(14)
        pp.font.bold = True
        pp.font.color.rgb = COLOR_DIVIDER

        # 구분선: y 1.7, 가로 x 0.8~12.53, 색 #9CA3AF, 굵기 0.75pt(1px), 실선
        line = slide.shapes.add_connector(
            MSO_CONNECTOR.STRAIGHT, Inches(0.8), Inches(1.7), Inches(12.533), Inches(1.7)
        )
        line.line.color.rgb = COLOR_DIVIDER
        line.line.width = Pt(0.75)

    def create_general_slide(self, slide_idx, raw_slide_data, page_num, total_pages):
        """일반 강의 슬라이드 생성"""
        slide = self.prs.slides.add_slide(self.blank_layout)

        title = raw_slide_data.get("title", "") or "10.1 TD법으로 정책 평가하기"
        subtitle = raw_slide_data.get("subtitle", "")
        page_str = f"{page_num:02d} / {total_pages:02d}"

        # 1. 헤더 생성
        self.add_common_header(slide, title, subtitle, page_str)

        # 2. 데이터 분리
        img_info = raw_slide_data.get("image")
        body_text = raw_slide_data.get("body", "")
        code_block = raw_slide_data.get("code")
        table_data = raw_slide_data.get("table")
        script = raw_slide_data.get("script", "")

        # 3. 레이아웃 분기
        if img_info:
            self._render_two_column_layout(slide, img_info, body_text, code_block)
        else:
            effective_body = re.sub(r"<div align=.*?>.*?</div>", "", body_text).strip()
            self._render_wide_layout(slide, effective_body, code_block, table_data)

        # 4. 슬라이드 노트 주입 (TTS 음성 최적화 구술문 적용)
        if script:
            notes_slide = slide.notes_slide
            tts_script = convert_to_tts_script(script.strip())
            notes_slide.notes_text_frame.text = tts_script

    def _render_two_column_layout(self, slide, img_info, body_text, code_block):
        """좌측 이미지(x 1.0, y 2.0, 4.4x4.4) + 우측 본문(x 6.6, y 2.0, 폭 5.9, 22pt, 줄간격 150%) 2열 레이아웃"""
        img_path = img_info["path"]
        caption = img_info["caption"]

        # A. 좌측 이미지 배치 (x 1.0, y 2.0, 4.4x4.4 정사각형 바운딩 박스 내 비율 유지)
        if os.path.exists(img_path):
            with Image.open(img_path) as im:
                orig_w, orig_h = im.size

            max_box = Inches(4.4)
            aspect = orig_w / orig_h

            if aspect >= 1.0:
                dest_w = max_box
                dest_h = dest_w / aspect
            else:
                dest_h = max_box
                dest_w = dest_h * aspect

            left = Inches(1.0) + (max_box - dest_w) / 2
            top = Inches(2.0) + (max_box - dest_h) / 2

            slide.shapes.add_picture(img_path, left, top, width=dest_w, height=dest_h)

            # 캡션: 이미지 아래 y 6.4, 11pt, 가운데 정렬, 2줄 이내
            cap_box = slide.shapes.add_textbox(Inches(1.0), Inches(6.4), Inches(4.4), Inches(0.55))
            tf = cap_box.text_frame
            tf.word_wrap = True
            tf.margin_top = 0
            tf.margin_bottom = 0
            p = tf.paragraphs[0]
            clean_cap = clean_math_and_symbols(caption)
            p.text = clean_cap
            p.font.name = FONT_NAME
            p.font.size = Pt(11)
            p.font.color.rgb = COLOR_CAPTION
            p.alignment = PP_ALIGN.CENTER

        # B. 우측 본문 배치 (x 6.6, y 2.0, 폭 5.9inch, 높이 4.4inch, 22pt, 줄간격 150%, 상하 가운데 정렬)
        r_box = slide.shapes.add_textbox(Inches(6.6), Inches(2.0), Inches(5.9), Inches(4.4))
        tf = r_box.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf.margin_left = Inches(0.1)
        tf.margin_right = Inches(0.1)
        tf.margin_top = 0
        tf.margin_bottom = 0

        self._populate_text_frame(tf, body_text, code_block)

    def _render_wide_layout(self, slide, body_text, code_block, table_data):
        """1열 와이드 레이아웃 (코드, 표, 텍스트 카드)"""
        if code_block:
            self._render_wide_code_slide(slide, body_text, code_block)
        elif table_data:
            self._render_table_slide(slide, body_text, table_data)
        else:
            box = slide.shapes.add_textbox(Inches(0.8), Inches(1.65), Inches(11.733), Inches(5.3))
            tf = box.text_frame
            tf.word_wrap = True
            self._populate_text_frame(tf, body_text, None, is_wide=True)

    def _render_wide_code_slide(self, slide, body_text, code_block):
        """검정 바탕의 와이드 터미널 코드 박스 + 흰색 글자 슬라이드 (가이드 엄격 준수, 들여쓰기 100% 보존)"""
        if body_text.strip():
            # 2단 레이아웃: 좌측 코드 (5.8"), 우측 설명 (5.6")
            code_left = Inches(0.8)
            code_top = Inches(2.0)
            code_width = Inches(5.8)
            code_height = Inches(4.8)

            desc_box = slide.shapes.add_textbox(Inches(6.9), Inches(2.0), Inches(5.6), Inches(4.8))
            tf_desc = desc_box.text_frame
            tf_desc.word_wrap = True
            tf_desc.vertical_anchor = MSO_ANCHOR.MIDDLE
            self._populate_text_frame(tf_desc, body_text, None)
            base_font_size = Pt(11.5)
            pad_h = Inches(0.3)
            pad_v = Inches(0.25)
        else:
            # 단독 와이드 터미널 레이아웃: 슬라이드 전체 작업 폭 활용 (11.733")
            code_left = Inches(0.8)
            code_top = Inches(2.0)
            code_width = Inches(11.733)
            code_height = Inches(4.9)
            base_font_size = Pt(13.5)
            pad_h = Inches(0.4)
            pad_v = Inches(0.3)

        # 다크 차콜 와이드 터미널 배경 박스 생성
        bg = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, code_left, code_top, code_width, code_height
        )
        bg.fill.solid()
        bg.fill.fore_color.rgb = COLOR_TITLE # #111827 순수 다크 차콜
        bg.line.color.rgb = RGBColor(55, 65, 81) # #374151
        bg.line.width = Pt(1.0)

        # 순수 흰색(#FFFFFF) 코드 텍스트 (Consolas 고정폭 폰트 + 들여쓰기 보존)
        c_box = slide.shapes.add_textbox(
            code_left + pad_h, code_top + pad_v,
            code_width - (pad_h * 2), code_height - (pad_v * 2)
        )
        tf = c_box.text_frame
        tf.word_wrap = False
        tf.margin_left = Inches(0)
        tf.margin_right = Inches(0)
        tf.margin_top = Inches(0)
        tf.margin_bottom = Inches(0)

        lines = code_block.strip().split("\n")
        num_lines = len(lines)
        if not body_text.strip():
            if num_lines > 20:
                font_size = Pt(11.0)
                line_spacing = 1.18
            elif num_lines > 15:
                font_size = Pt(12.0)
                line_spacing = 1.22
            elif num_lines > 10:
                font_size = Pt(13.0)
                line_spacing = 1.25
            else:
                font_size = Pt(13.5)
                line_spacing = 1.28
        else:
            if num_lines > 20:
                font_size = Pt(9.5)
                line_spacing = 1.15
            elif num_lines > 15:
                font_size = Pt(10.5)
                line_spacing = 1.2
            else:
                font_size = Pt(11.5)
                line_spacing = 1.25

        for i, line in enumerate(lines):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            
            # A. 탭을 4칸 공백으로 치환
            expanded_line = line.replace("\t", "    ")
            
            # B. 선행 공백(들여쓰기)을 유니코드 Non-Breaking Space(\u00A0)로 보존
            leading_count = len(expanded_line) - len(expanded_line.lstrip(" "))
            preserved_line = ("\u00A0" * leading_count) + expanded_line.lstrip(" ")
            
            p.text = preserved_line
            p.font.name = "Consolas"
            p.font.size = font_size
            p.font.color.rgb = COLOR_WHITE # 순수 흰색 글자
            p.line_spacing = line_spacing
            
            # C. OpenXML schema ECMA-376 whitespace preservation 보장
            for t in p._p.xpath(".//a:t"):
                t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")

    def _render_table_slide(self, slide, body_text, table_data):
        """와이드 테이블 슬라이드"""
        if body_text.strip():
            desc_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(11.733), Inches(0.5))
            tf = desc_box.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.text = clean_math_and_symbols(body_text.strip())
            p.font.name = FONT_NAME
            p.font.size = Pt(16)
            p.font.bold = True
            p.font.color.rgb = COLOR_BODY
            tbl_top = Inches(2.2)
        else:
            tbl_top = Inches(1.65)

        rows = len(table_data)
        cols = len(table_data[0])
        tbl_shape = slide.shapes.add_table(rows, cols, Inches(0.8), tbl_top, Inches(11.733), Inches(4.8))
        table = tbl_shape.table

        if cols == 3:
            table.columns[0].width = Inches(2.5)
            table.columns[1].width = Inches(4.6)
            table.columns[2].width = Inches(4.6)

        for r_idx, row in enumerate(table_data):
            for c_idx, cell_text in enumerate(row):
                cell = table.cell(r_idx, c_idx)
                cleaned = clean_math_and_symbols(cell_text.strip())
                cell.text = cleaned
                p = cell.text_frame.paragraphs[0]
                p.font.name = FONT_NAME
                if r_idx == 0:
                    p.font.bold = True
                    p.font.size = Pt(14)
                    p.font.color.rgb = COLOR_WHITE
                    cell.fill.solid()
                    cell.fill.fore_color.rgb = COLOR_PRIMARY
                else:
                    p.font.size = Pt(13)
                    p.font.color.rgb = COLOR_BODY
                    cell.fill.solid()
                    cell.fill.fore_color.rgb = RGBColor(255, 255, 255) if r_idx % 2 == 1 else RGBColor(248, 250, 252)

    def _populate_text_frame(self, tf, body_text, code_block, is_wide=False):
        """텍스트 프레임에 마크다운 문단, 불릿, 수식을 고품질로 채움"""
        clean_text = re.sub(r"<div align=.*?>.*?</div>", "", body_text)
        clean_text = re.sub(r">\s*\[!NOTE\]", "💡 [핵심 노트]", clean_text)
        clean_text = re.sub(r"###+\s*", "", clean_text)
        lines = [l for l in clean_text.split("\n") if l.strip()]

        first = True
        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue

            is_formula = (
                line_str.startswith(">") or 
                ("=" in line_str and ("G_t" in line_str or "V_" in line_str or "v_" in line_str or "←" in line_str or "δ" in line_str or "G" in line_str)) or
                ("←" in line_str)
            )

            p = tf.paragraphs[0] if first else tf.add_paragraph()
            first = False

            if is_formula:
                clean_formula = clean_math_and_symbols(line_str)
                p.text = clean_formula
                p.font.name = FONT_NAME
                p.font.size = Pt(22 if not is_wide else 24)
                p.font.bold = True
                p.font.color.rgb = COLOR_PRIMARY
                p.space_before = Pt(8)
                p.space_after = Pt(8)
                p.alignment = PP_ALIGN.CENTER
                p.line_spacing = 1.5
                continue

            is_bullet = line_str.startswith("- ") or line_str.startswith("• ") or re.match(r"^\d+\.\s", line_str)
            text_content = clean_math_and_symbols(re.sub(r"^[-•]\s*", "• ", line_str))

            # 총 텍스트 길이에 따른 포인트 미세 완충 (기본 22pt)
            base_pt = 22 if len(clean_text) < 180 else (19 if len(clean_text) < 280 else 16.5)

            p.text = text_content
            p.font.name = FONT_NAME
            p.font.size = Pt(base_pt if not is_wide else base_pt + 1)
            p.font.color.rgb = COLOR_BODY
            p.space_before = Pt(4)
            p.space_after = Pt(6)
            p.line_spacing = 1.5

            if is_bullet:
                p.level = 0
                if line_str.startswith("  "):
                    p.level = 1
                    p.font.size = Pt(base_pt - 2 if not is_wide else base_pt - 1)

# ==========================================
# 6. slides.md 파서
# ==========================================
def parse_slides_md():
    with open(SLIDES_MD_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    raw_slides = content.split("\n---\n")[1:]
    parsed_list = []
    base_dir = BASE_DIR

    for idx, raw in enumerate(raw_slides):
        raw = raw.strip()
        data = {"idx": idx}

        script = ""
        script_match = re.search(r"> \*\*\[강의 스크립트\]\*\*\s*\n((?:> .*\n?)+)", raw)
        if script_match:
            script_lines = [line[2:].strip() for line in script_match.group(1).split("\n") if line.startswith("> ") or line == ">"]
            script = "\n".join(script_lines)
            body = raw[:script_match.start()].strip()
        else:
            body = raw
        data["script"] = script

        img_match = re.search(r"!\[(.*?)\]\((.*?)\)", body)
        caption_match = re.search(r"\*\*(그림 \d+-\d+-\d+)\*\*\s*(.*)", body)

        if img_match:
            img_rel_path = img_match.group(2)
            img_full_path = os.path.normpath(os.path.join(base_dir, img_rel_path))
            caption_text = ""
            if caption_match:
                caption_text = f"{caption_match.group(1)} {caption_match.group(2)}"
            else:
                caption_text = img_match.group(1)

            data["image"] = {
                "path": img_full_path,
                "caption": caption_text
            }
            body = re.sub(r"!\[.*?\]\(.*?\)", "", body)
            body = re.sub(r"\*\*그림 \d+-\d+-\d+\*\*.*", "", body)

        code_match = re.search(r"```python\s*(.*?)```", body, re.DOTALL)
        if code_match:
            data["code"] = code_match.group(1)
            body = re.sub(r"```python.*?```", "", body, flags=re.DOTALL)

        table_lines = [l for l in body.split("\n") if l.strip().startswith("|") and l.strip().endswith("|")]
        if len(table_lines) >= 3:
            table_data = []
            for tline in table_lines:
                if re.match(r"^\|(\s*:?-+:?\s*\|)+$", tline.strip()):
                    continue
                cells = [c.strip() for c in tline.strip().split("|")[1:-1]]
                table_data.append(cells)
            data["table"] = table_data
            for tline in table_lines:
                body = body.replace(tline, "")

        lines = body.split("\n")
        remaining_lines = []
        title = ""
        subtitle = ""
        for l in lines:
            l_str = l.strip()
            if l_str.startswith("# "):
                title = l_str[2:].strip()
            elif l_str.startswith("## "):
                subtitle = l_str[3:].strip()
            elif l_str.startswith("### ") and not subtitle:
                subtitle = l_str[4:].strip()
            elif l_str.startswith("#### ") and not subtitle:
                subtitle = l_str[5:].strip()
            elif l_str.startswith("#"):
                continue
            else:
                remaining_lines.append(l)

        data["title"] = title
        data["subtitle"] = subtitle
        data["body"] = "\n".join(remaining_lines).strip()
        parsed_list.append(data)

    return parsed_list

# ==========================================
# 7. 메인 실행 함수
# ==========================================
def main():
    print(f"[1/3] Parsing slides.md from: {SLIDES_MD_PATH}")
    slides_data = parse_slides_md()
    print(f"      Parsed {len(slides_data)} slides successfully.")

    print("[2/3] Building Presentation with python-pptx (TTS optimization + Zero-clipping assets)...")
    builder = PresentationBuilder()

    # 1페이지 커버 슬라이드 생성
    builder.create_editable_cover_slide()

    # 2 ~ 54페이지 일반 슬라이드 생성
    total_slides_count = len(slides_data) + 1
    for idx, sdata in enumerate(slides_data):
        page_num = idx + 2
        builder.create_general_slide(idx, sdata, page_num, total_slides_count)

    print(f"[3/3] Saving final PPTX to: {OUTPUT_PPTX_PATH}")
    builder.prs.save(OUTPUT_PPTX_PATH)
    print("      Done! PPTX presentation generated successfully with perfect TTS scripts & zero-clipping cover assets!")

if __name__ == "__main__":
    main()
