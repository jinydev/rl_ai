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
COLOR_CODE_BG = RGBColor(17, 24, 39)        # #111827 (Dark Charcoal Terminal)
COLOR_WHITE = RGBColor(255, 255, 255)

FONT_NAME = "나눔고딕"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
SLIDES_MD_PATH = os.path.join(BASE_DIR, "slides.md")
OUTPUT_PPTX_PATH = os.path.join(BASE_DIR, "11_신경망과_Q_러닝.pptx")

# ==========================================
# 2. 수식 및 텍스트 정제 엔진 (math_cleaner 연동)
# ==========================================
from math_cleaner import clean_slide_math, clean_notes_math

def clean_math_and_symbols(text):
    """마크다운 수식, HTML 태그, LaTeX 문법을 PPTX 가독성 높은 유니코드 기호로 100% 변환"""
    return clean_slide_math(text)

def convert_to_tts_script(text):
    """향후 TTS가 자연스러운 한국어 구술 음성으로 발음하도록 수식 코드를 한글 독음으로 100% 변환"""
    return clean_notes_math(text)

# ==========================================
# 3. PPTX 빌더 클래스
# ==========================================
class PresentationBuilder:
    def __init__(self):
        self.prs = Presentation()
        self.prs.slide_width = SLIDE_WIDTH
        self.prs.slide_height = SLIDE_HEIGHT
        self.blank_layout = self.prs.slide_layouts[6]

    def create_editable_cover_slide(self, script_text=""):
        """첫 번째 슬라이드: 16:9 커버 이미지 PNG를 전면 바탕(하위 레이어)으로 깔고, 상위 레이어에 편집 가능한 텍스트 배치"""
        slide = self.prs.slides.add_slide(self.blank_layout)

        # 1. 하위 레이어: 16:9 와이드스크린 커버 이미지 PNG 삽입 (전면 바탕)
        cover_png_path = os.path.join(BASE_DIR, "11_신경망과_Q_러닝.png")
        if os.path.exists(cover_png_path):
            slide.shapes.add_picture(cover_png_path, Inches(0), Inches(0), width=SLIDE_WIDTH, height=SLIDE_HEIGHT)

        # 2. 상위 레이어: 파란색 뱃지 (14pt Bold)
        badge = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.0), Inches(3.0), Inches(0.5)
        )
        badge.fill.solid()
        badge.fill.fore_color.rgb = COLOR_PRIMARY
        badge.line.color.rgb = COLOR_PRIMARY
        badge.adjustments[0] = 0.5

        tf = badge.text_frame
        tf.word_wrap = False
        p = tf.paragraphs[0]
        p.text = "PART 11 · 심층 강화학습"
        p.font.name = FONT_NAME
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = COLOR_WHITE
        p.alignment = PP_ALIGN.CENTER

        # 3. 상위 레이어: 메인 강의 타이틀 (44pt 볼드, 편집 가능 텍스트)
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.75), Inches(5.8), Inches(1.5))
        tf = title_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = "CHAPTER 11\n신경망과 Q 러닝"
        p.font.name = FONT_NAME
        p.font.size = Pt(44)
        p.font.bold = True
        p.font.color.rgb = COLOR_TITLE

        # 4. 상위 레이어: 부제목 설명문 (20pt 회색, 편집 가능 텍스트)
        sub_box = slide.shapes.add_textbox(Inches(0.8), Inches(3.45), Inches(5.8), Inches(1.8))
        tf = sub_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = "테이블의 한계를 넘어 무한한 상태 공간으로 확장하는\n인공신경망 기반 Q-러닝의 원리와 실전 구현"
        p.font.name = FONT_NAME
        p.font.size = Pt(20)
        p.font.color.rgb = COLOR_SUBTITLE

        # 5. 상위 레이어: 강사 정보
        p2 = tf.add_paragraph()
        p2.text = "\n강의: 이호진 교수 · 조교 지니와 도로시 탐험대"
        p2.font.name = FONT_NAME
        p2.font.size = Pt(16)
        p2.font.bold = True
        p2.font.color.rgb = RGBColor(55, 65, 81)

        # 6. 슬라이드 노트 (TTS 최적화 구술문)
        if script_text:
            notes_slide = slide.notes_slide
            notes_slide.notes_text_frame.text = convert_to_tts_script(script_text.strip())

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

        # 페이지 번호: 오른쪽 위 x 11.33, y 0.5, 14pt, '02 / 11' 형식, 오른쪽 정렬
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

    def create_body_slide(self, slide_data, page_num, total_pages):
        """일반 강의 슬라이드 생성 (2단 레이아웃 표준)"""
        slide = self.prs.slides.add_slide(self.blank_layout)

        title = slide_data.get("title", "") or "신경망과 Q 러닝"
        subtitle = slide_data.get("subtitle", "")
        page_str = f"{page_num:02d} / {total_pages:02d}"

        # 1. 헤더 생성
        self.add_common_header(slide, title, subtitle, page_str)

        # 2. 이미지 & 본문 2단 구성
        img_info = slide_data.get("image")
        body_text = slide_data.get("body", "")
        script = slide_data.get("script", "")

        if img_info and os.path.exists(img_info["path"]):
            self._render_two_column_layout(slide, img_info, body_text)
        else:
            self._render_wide_layout(slide, body_text)

        # 3. 슬라이드 노트 주입
        if script:
            notes_slide = slide.notes_slide
            tts_script = convert_to_tts_script(script.strip())
            notes_slide.notes_text_frame.text = tts_script

    def _render_two_column_layout(self, slide, img_info, body_text):
        img_path = img_info["path"]
        caption = img_info.get("caption", "")

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

        if caption:
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

        r_box = slide.shapes.add_textbox(Inches(6.6), Inches(2.0), Inches(5.9), Inches(4.4))
        tf = r_box.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf.margin_left = Inches(0.1)
        tf.margin_right = Inches(0.1)
        tf.margin_top = 0
        tf.margin_bottom = 0

        self._populate_text_frame(tf, body_text)

    def _render_wide_layout(self, slide, body_text):
        box = slide.shapes.add_textbox(Inches(0.8), Inches(2.0), Inches(11.733), Inches(4.6))
        tf = box.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        self._populate_text_frame(tf, body_text, is_wide=True)

    def _populate_text_frame(self, tf, body_text, is_wide=False):
        clean_text = re.sub(r"<div align=.*?>.*?</div>", "", body_text)
        clean_text = re.sub(r">\s*\[!CAUTION\]", "⚠️ [주의 및 약속]", clean_text)
        clean_text = re.sub(r">\s*\[!NOTE\]", "💡 [핵심 노트]", clean_text)
        clean_text = re.sub(r"###+\s*", "", clean_text)
        lines = [l for l in clean_text.split("\n") if l.strip()]

        first = True
        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue

            # 인용 블록 (도로시 비유 등)
            if line_str.startswith(">"):
                clean_quote = clean_math_and_symbols(re.sub(r"^>\s*", "", line_str))
                p = tf.paragraphs[0] if first else tf.add_paragraph()
                first = False
                p.text = clean_quote
                p.font.name = FONT_NAME
                p.font.size = Pt(18 if not is_wide else 20)
                p.font.color.rgb = COLOR_BODY
                p.line_spacing = 1.45
                p.space_after = Pt(6)
                continue

            # 불릿 포인트
            is_bullet = line_str.startswith("- ") or line_str.startswith("• ") or re.match(r"^\d+\.\s", line_str)
            text_content = clean_math_and_symbols(re.sub(r"^[-•]\s*", "• ", line_str))
            if not is_bullet and not text_content.startswith("💡") and not text_content.startswith("⚠️"):
                text_content = "• " + text_content

            base_pt = 22 if len(clean_text) < 180 else (19 if len(clean_text) < 280 else 17)

            p = tf.paragraphs[0] if first else tf.add_paragraph()
            first = False
            p.text = text_content
            p.font.name = FONT_NAME
            p.font.size = Pt(base_pt if not is_wide else base_pt + 1)
            p.font.color.rgb = COLOR_BODY
            p.space_before = Pt(4)
            p.space_after = Pt(8)
            p.line_spacing = 1.5

            if text_content.startswith("💡") or text_content.startswith("⚠️"):
                p.font.bold = True
                p.font.color.rgb = COLOR_PRIMARY

# ==========================================
# 4. 슬라이드 파싱 및 메인 변환 로직
# ==========================================
def parse_ch11_slides():
    """slides.md 파일에서 슬라이드 목록 추출 및 정제"""
    with open(SLIDES_MD_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    parts = content.split("\n---\n")
    # parts[0]: frontmatter
    # parts[1]: Slide 1 (Cover / Intro)
    # parts[2~11]: Body Slides 2~11

    cover_script = ""
    # Part 1: Cover Slide
    p1 = parts[1].strip()
    c_m = re.search(r">\s*\*\*\[강의 스크립트\]\*\*\s*\n(.*?)(?=\n\n|$)", p1, re.DOTALL)
    if c_m:
        cover_script = c_m.group(1).replace(">", "").strip()

    # Define metadata for body slides 2 through 11
    body_slides_defs = [
        {
            "subtitle": "도로시와 토토의 비유로 이해하기",
            "img": "img/jiny_ch11_neural_q.png",
            "caption": "마법 요술봉으로 인공신경망 전구망을 켜서 상태 가치를 스마트하게 예측하는 도로시와 토토",
            "body": "• 도로시가 마법 요술봉을 지휘하자 거대하게 연결된 오색 전구망(인공신경망)이 켜집니다.\n• 격자 세상 전체의 매 상태가 입력되면 신경망이 그에 맞는 최적 행동 가치(Q-value)를 스마트하게 예측해 냅니다.\n• 이제 칠판에 일일이 적던 가치 표 없이도 무한히 넓은 세상의 상태 가치를 계산할 수 있게 된 것입니다!",
            "part_idx": 2
        },
        {
            "subtitle": "이산적 그리드 월드와 작은 Q 테이블",
            "img": "img/ch11_intro_01_gridworld_discrete_table.png",
            "caption": "이산적 그리드 월드와 작은 Q 테이블",
            "body": "• 지금까지는 상태와 행동의 가짓수가 적은 문제만 다뤘습니다.\n• 예를 들어 '3 × 4 그리드 월드' 문제에서는 상태 후보가 12개이고 행동 후보는 4개뿐이라서 Q 함수 후보는 총 12 × 4 = 48개였습니다.",
            "part_idx": 3
        },
        {
            "subtitle": "무한에 가까운 상태와 테이블 폭발",
            "img": "img/ch11_intro_02_infinite_table_explosion.png",
            "caption": "무한에 가까운 상태와 테이블 폭발",
            "body": "• 이 정도 크기라면 Q 함수를 테이블로(파이썬 코드에서는 딕셔너리로) 관리하는 데 아무런 문제가 없습니다.\n• 하지만 현실은 훨씬 복잡하여 상태와 행동의 후보가 엄청나게 많을 수 있습니다.\n• 이러한 문제에서는 Q 함수를 테이블로 관리하도록 구현하는 건 현실적이지 못합니다.",
            "part_idx": 4
        },
        {
            "subtitle": "천문학적인 체스 상태 수",
            "img": "img/ch11_intro_03_chess_astronomical_states.png",
            "caption": "천문학적인 체스 상태 수",
            "body": "• 예를 들어 체스는 보드의 배열 패턴이 10¹²³ 개나 될 만큼 다양합니다.\n• 즉, 상태가 이 수만큼 존재한다는 뜻입니다.\n• 이 많은 상태를 테이블로 관리하는 건 현실적이지 못합니다.",
            "part_idx": 5
        },
        {
            "subtitle": "모든 상태를 일일이 경험해야 하는 불가능한 탐색 부담",
            "img": "img/ch11_intro_04_impossible_experience_burden.png",
            "caption": "모든 상태를 일일이 경험해야 하는 불가능한 탐색 부담",
            "body": "• 문제는 여기서 끝이 아닙니다.\n• 더 큰 문제는 테이블의 원소 하나하나를 독립적으로 평가하고 개선해야 한다는 점입니다.\n• 이만큼 막대한 수를 모두 경험해보는 건 현실적으로 불가능합니다.",
            "part_idx": 6
        },
        {
            "subtitle": "상태 폭발의 돌파구: 새로운 발상의 전환",
            "img": "img/ch11_intro_05_hojin_lightbulb_solution.png",
            "caption": "이호진 교수가 제시하는 돌파구 솔루션",
            "body": "• 해결책은 무엇일까요?\n• 모든 상태를 일일이 표에 기록할 수 없다면, 상태와 가치 사이의 관계를 수학적 패턴으로 요약해 주는 똑똑한 근사 도구를 도입해야 합니다.",
            "part_idx": 7
        },
        {
            "subtitle": "Q 함수를 더 가벼운 함수로 근사하는 딥러닝",
            "img": "img/ch11_intro_06_neural_function_approximation.png",
            "caption": "지니의 신경망 함수 근사",
            "body": "• Q 함수를 더 가벼운 함수로 근사하는 방법을 생각해볼 수 있습니다.\n• 이 방식에서 가장 유력한 후보가 바로 딥러닝입니다.\n• 상태를 입력받아 가치를 매끄럽게 계산해 내는 함수 근사기로 전환합니다.",
            "part_idx": 8
        },
        {
            "subtitle": "심층 강화 학습 세계로의 첫발",
            "img": "img/ch11_intro_07_deep_rl_revolution_dawn.png",
            "caption": "심층 강화 학습의 여명과 아케이드 혁신",
            "body": "• 실제로 강화 학습에 딥러닝을 결합하여 지금까지 많은 혁신을 이루어왔습니다.\n• 아타리 비디오 게임 정복부터 알파고의 승리까지 인공지능 역사에 큰 획을 그었습니다.\n• 이제 우리도 드디어 심층 강화 학습 세계에 첫발을 내딛게 되었습니다.",
            "part_idx": 9
        },
        {
            "subtitle": "11장 학습 로드맵 3단계",
            "img": "img/ch11_intro_08_three_pillars_roadmap.png",
            "caption": "11장 학습 로드맵 3단계",
            "body": "• 이번 장에서는 먼저 DeZero라는 딥러닝 프레임워크의 사용법을 설명합니다.\n• 그런 다음 DeZero를 이용하여 신경망의 기초를 배웁니다.\n• 마지막으로 앞 장에서 구현한 Q 러닝을 신경망을 사용하여 구현해보겠습니다.",
            "part_idx": 10
        },
        {
            "subtitle": "신경망과 딥러닝의 용어 정의",
            "img": "img/ch11_intro_09_deep_learning_layers_stack.png",
            "caption": "깊은 다층 신경망 구조",
            "body": "💡 [핵심 주의]\n• 신경망의 층(layer)을 깊게 만든 것이 딥러닝입니다.\n• 이 책에서는 '딥러닝'과 '신경망'이라는 용어를 구분하지 않고 사용합니다.\n• 복잡한 비선형 관계를 학습하는 다층 구조로 이해하시면 되겠습니다.",
            "part_idx": 11
        }
    ]

    body_slides = []
    for sdef in body_slides_defs:
        part_content = parts[sdef["part_idx"]].strip()
        script = ""
        s_m = re.search(r">\s*\*\*\[강의 스크립트\]\*\*\s*\n(.*?)(?=\n\n|$)", part_content, re.DOTALL)
        if s_m:
            script = s_m.group(1).replace(">", "").strip()

        img_path = os.path.normpath(os.path.join(BASE_DIR, sdef["img"]))
        body_slides.append({
            "title": "신경망과 Q 러닝",
            "subtitle": sdef["subtitle"],
            "image": {
                "path": img_path,
                "caption": sdef["caption"]
            },
            "body": sdef["body"],
            "script": script
        })

    return cover_script, body_slides

def main():
    print(f"[1/3] Parsing Chapter 11 slides from: {SLIDES_MD_PATH}")
    cover_script, body_slides = parse_ch11_slides()
    total_slides = len(body_slides) + 1
    print(f"      Parsed cover slide + {len(body_slides)} body slides (Total {total_slides} slides)")

    print("[2/3] Building PPTX with python-pptx (16:9 Widescreen, Clean Unicode, TTS Narration)...")
    builder = PresentationBuilder()

    # 1. 표지 슬라이드 생성 (Page 1)
    builder.create_editable_cover_slide(cover_script)

    # 2. 본문 슬라이드 생성 (Pages 2 ~ 11)
    for idx, slide_data in enumerate(body_slides):
        page_num = idx + 2
        builder.create_body_slide(slide_data, page_num, total_slides)

    # 3. PPTX 저장
    print(f"[3/3] Saving final presentation to: {OUTPUT_PPTX_PATH}")
    builder.prs.save(OUTPUT_PPTX_PATH)
    print("      Done! PPTX presentation generated successfully!")

if __name__ == "__main__":
    main()
