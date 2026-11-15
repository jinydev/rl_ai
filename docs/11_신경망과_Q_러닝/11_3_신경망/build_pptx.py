import os
import re
import sys
from PIL import Image
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.oxml import parse_xml
from pptx.oxml.ns import nsdecls

# ==========================================
# 1. 디자인 상수 정의 (16:9 규격 및 컬러 시스템)
# ==========================================
SLIDE_WIDTH = Inches(13.333)
SLIDE_HEIGHT = Inches(7.500)

COLOR_PRIMARY = RGBColor(26, 115, 232)      # #1A73E8 (Brand Blue Badge)
COLOR_TITLE = RGBColor(17, 24, 39)          # #111827 (Dark Charcoal, 거의 검정)
COLOR_SUBTITLE = RGBColor(107, 114, 128)    # #6B7280 (Medium Gray, 회색)
COLOR_BODY = RGBColor(31, 41, 55)           # #1F2937 (Body Text)
COLOR_DIVIDER = RGBColor(226, 232, 240)     # #E2E8F0 (Divider Line, 깔끔하고 심플한 1px 연회색 실선)
COLOR_CAPTION = RGBColor(75, 85, 99)        # #4B5563 (Caption Gray)
COLOR_CODE_BG = RGBColor(17, 24, 39)        # #111827 (Dark Charcoal Terminal)
COLOR_CODE_BORDER = RGBColor(55, 65, 81)    # #374151
COLOR_WHITE = RGBColor(255, 255, 255)

FONT_NAME = "나눔고딕"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(BASE_DIR)
FOLDER_NAME = os.path.basename(BASE_DIR)
SLIDES_MD_PATH = os.path.join(BASE_DIR, "slides.md")
OUTPUT_PPTX_PATH = os.path.join(BASE_DIR, f"{FOLDER_NAME}.pptx")

# math_cleaner 연동
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)
from math_cleaner import clean_slide_math, clean_notes_math

def clean_math_and_symbols(text):
    return clean_slide_math(text)

def convert_to_tts_script(text):
    return clean_notes_math(text)

# ==========================================
# 2. PPTX 프레젠테이션 빌더 클래스
# ==========================================
class PresentationBuilder:
    def __init__(self):
        self.prs = Presentation()
        self.prs.slide_width = SLIDE_WIDTH
        self.prs.slide_height = SLIDE_HEIGHT
        self.blank_layout = self.prs.slide_layouts[6]

    def create_editable_cover_slide(self, cover_data):
        """첫 번째 슬라이드: 커버 이미지를 약 84.5%로 축소하여 우하단에 고정하고, 좌상단 여백에 챕터정보, 타이틀, 서브설명만 배치"""
        slide = self.prs.slides.add_slide(self.blank_layout)

        # 1. 하위 레이어: 16:9 와이드스크린 커버 이미지 PNG를 약 84.5%로 축소하여 우하단 고정
        cover_png_path = os.path.join(BASE_DIR, f"{FOLDER_NAME}.png")
        if not os.path.exists(cover_png_path):
            # 대체 탐색
            for f in os.listdir(BASE_DIR):
                if f.endswith(".png") and not f.startswith("."):
                    cover_png_path = os.path.join(BASE_DIR, f)
                    break

        if os.path.exists(cover_png_path):
            img_w = Inches(11.27)
            img_h = Inches(6.34)
            img_left = SLIDE_WIDTH - img_w
            img_top = SLIDE_HEIGHT - img_h
            slide.shapes.add_picture(cover_png_path, img_left, img_top, width=img_w, height=img_h)

        # 2. 상위 레이어: 챕터 정보 배지
        badge_text = cover_data.get("badge", "PART 11 · 심층 강화학습")
        badge = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.60), Inches(2.8), Inches(0.42)
        )
        badge.fill.solid()
        badge.fill.fore_color.rgb = COLOR_PRIMARY
        badge.line.color.rgb = COLOR_PRIMARY
        badge.adjustments[0] = 0.5

        tf = badge.text_frame
        tf.word_wrap = False
        tf.margin_top = 0
        tf.margin_bottom = 0
        p = tf.paragraphs[0]
        p.text = badge_text
        p.font.name = FONT_NAME
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = COLOR_WHITE
        p.alignment = PP_ALIGN.CENTER

        # 3. 상위 레이어: 메인 강의 타이틀 (38pt Bold, x=0.8", y=1.22", w=7.5")
        title_text = cover_data.get("title", FOLDER_NAME.replace("_", " "))
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.22), Inches(7.5), Inches(0.65))
        tf = title_box.text_frame
        tf.word_wrap = True
        tf.margin_top = 0
        tf.margin_bottom = 0
        tf.margin_left = 0
        tf.margin_right = 0
        p = tf.paragraphs[0]
        p.text = clean_math_and_symbols(title_text)
        p.font.name = FONT_NAME
        p.font.size = Pt(36)
        p.font.bold = True
        p.font.color.rgb = COLOR_TITLE

        # 4. 상위 레이어: 부제목 설명문 (19pt Regular, x=0.8", y=1.98", w=7.5")
        sub_text = cover_data.get("subtitle", "핵심 원리와 이론을 직관적으로 이해하고 실전 코드로 구현합니다.")
        sub_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.98), Inches(7.5), Inches(1.10))
        tf = sub_box.text_frame
        tf.word_wrap = True
        tf.margin_top = 0
        tf.margin_bottom = 0
        tf.margin_left = 0
        tf.margin_right = 0
        p = tf.paragraphs[0]
        p.text = clean_math_and_symbols(sub_text)
        p.font.name = FONT_NAME
        p.font.size = Pt(18)
        p.font.color.rgb = COLOR_SUBTITLE

        # 5. 슬라이드 노트 (TTS 최적화 구술문)
        script_text = cover_data.get("script", "")
        if script_text:
            notes_slide = slide.notes_slide
            notes_slide.notes_text_frame.text = convert_to_tts_script(script_text.strip())

    def add_common_header(self, slide, title_text, subtitle_text, page_str):
        """표준 상단 헤더: 제목 32pt Bold (y 0.4), 부제 20pt 회색 (y 1.05), 구분선 1px 단색 실선 (y 1.7)"""
        # 제목
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

        # 부제
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

        # 페이지 번호: 오른쪽 위 x 11.33, y 0.5
        p_box = slide.shapes.add_textbox(Inches(11.333), Inches(0.5), Inches(1.2), Inches(0.4))
        pf = p_box.text_frame
        pp = pf.paragraphs[0]
        pp.text = page_str
        pp.alignment = PP_ALIGN.RIGHT
        pp.font.name = FONT_NAME
        pp.font.size = Pt(14)
        pp.font.bold = True
        pp.font.color.rgb = RGBColor(156, 163, 175)

        # 구분선: y 1.7, 가로 x 0.8~12.533, 색 #E2E8F0, 굵기 1.0pt(1px), 단색 실선
        line = slide.shapes.add_connector(
            MSO_CONNECTOR.STRAIGHT, Inches(0.8), Inches(1.7), Inches(12.533), Inches(1.7)
        )
        line.line.color.rgb = COLOR_DIVIDER
        line.line.width = Pt(1.0)

    def create_body_slide(self, slide_data, page_num, total_pages):
        """일반 강의 슬라이드 생성 (2단 레이아웃 또는 와이드 코드 레이아웃)"""
        slide = self.prs.slides.add_slide(self.blank_layout)

        title = slide_data.get("title", "")
        subtitle = slide_data.get("subtitle", "")
        page_str = f"{page_num:02d} / {total_pages:02d}"

        # 1. 헤더 생성
        self.add_common_header(slide, title, subtitle, page_str)

        # 2. 이미지 & 본문 분기
        img_info = slide_data.get("image")
        body_text = slide_data.get("body", "")
        code_block = slide_data.get("code")
        script = slide_data.get("script", "")

        if img_info and os.path.exists(img_info["path"]):
            self._render_two_column_layout(slide, img_info, body_text, code_block)
        elif code_block:
            self._render_wide_code_slide(slide, body_text, code_block)
        else:
            self._render_wide_text_layout(slide, body_text)

        # 3. 슬라이드 노트 주입
        if script:
            notes_slide = slide.notes_slide
            tts_script = convert_to_tts_script(script.strip())
            notes_slide.notes_text_frame.text = tts_script

    def _render_two_column_layout(self, slide, img_info, body_text, code_block=None):
        img_path = img_info["path"]
        caption = img_info.get("caption", "")

        with Image.open(img_path) as im:
            orig_w, orig_h = im.size

        # 좌측 이미지 바운딩 박스: 폭 4.2", 높이 3.9" (비율 유지)
        max_w = Inches(4.2)
        max_h = Inches(3.9)
        aspect = orig_w / orig_h
        box_aspect = max_w / max_h

        if aspect >= box_aspect:
            dest_w = max_w
            dest_h = dest_w / aspect
        else:
            dest_h = max_h
            dest_w = dest_h * aspect

        left = Inches(1.0) + (max_w - dest_w) / 2
        top = Inches(2.15) + (max_h - dest_h) / 2

        # 1. 레이어 순서 맨 뒤 (가장 먼저 삽입)
        slide.shapes.add_picture(img_path, left, top, width=dest_w, height=dest_h)

        # 2. 이미지 캡션: 이미지 바로 아래, 13pt, 가운데 정렬
        if caption:
            cap_top = top + dest_h + Inches(0.18)
            cap_box = slide.shapes.add_textbox(left, cap_top, dest_w, Inches(0.65))
            tf = cap_box.text_frame
            tf.word_wrap = True
            tf.margin_top = 0
            tf.margin_bottom = 0
            tf.margin_left = 0
            tf.margin_right = 0
            p = tf.paragraphs[0]
            clean_cap = clean_math_and_symbols(caption)
            p.text = clean_cap
            p.font.name = FONT_NAME
            p.font.size = Pt(13)  # 13pt
            p.font.color.rgb = COLOR_CAPTION
            p.alignment = PP_ALIGN.CENTER
            p.line_spacing = 1.3

        # 3. 우측 본문 텍스트 영역: 세로 중앙 맞춤, 22pt, 네이티브 글머리 기호
        r_box = slide.shapes.add_textbox(Inches(6.0), Inches(1.90), Inches(6.4), Inches(4.8))
        tf = r_box.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf.margin_left = 0
        tf.margin_right = 0
        tf.margin_top = 0
        tf.margin_bottom = 0

        self._populate_text_frame(tf, body_text)

    def _render_wide_text_layout(self, slide, body_text):
        box = slide.shapes.add_textbox(Inches(1.0), Inches(1.90), Inches(11.333), Inches(4.8))
        tf = box.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf.margin_left = 0
        tf.margin_right = 0
        tf.margin_top = 0
        tf.margin_bottom = 0
        self._populate_text_frame(tf, body_text, is_wide=True)

    def _render_wide_code_slide(self, slide, body_text, code_block):
        """검정 바탕의 와이드 터미널 코드 박스 + 흰색 글자 슬라이드 (폭 11.733" 와이드 전체 활용, 들여쓰기 100% 보존)"""
        has_intro = bool(body_text and body_text.strip())

        raw_lines = code_block.strip().split("\n")
        num_lines = len(raw_lines)

        code_left = Inches(0.8)
        code_width = Inches(11.733)

        # 1. 상단 안내/도입 텍스트가 있는 경우 (폭 11.733", 동적 높이 및 y 조정)
        if has_intro:
            intro_clean = clean_math_and_symbols(body_text.replace("\n", " ").strip())
            if len(intro_clean) > 80:
                intro_h = Inches(0.55)
                code_top = Inches(2.45)
                code_height = Inches(4.55)
                font_sz = Pt(16.5)
            else:
                intro_h = Inches(0.38)
                code_top = Inches(2.25)
                code_height = Inches(4.75)
                font_sz = Pt(18.0)

            intro_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.78), Inches(11.733), intro_h)
            itf = intro_box.text_frame
            itf.word_wrap = True
            itf.margin_top = 0
            itf.margin_bottom = 0
            itf.margin_left = 0
            itf.margin_right = 0
            ip = itf.paragraphs[0]
            ip.text = intro_clean
            ip.font.name = FONT_NAME
            ip.font.size = font_sz
            ip.font.color.rgb = COLOR_BODY
            ip.line_spacing = 1.3
        else:
            code_top = Inches(1.95)
            code_height = Inches(5.05)

        # 2. 다크 터미널 박스 배경 도형 (폭 11.733" 와이드 전체)
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, code_left, code_top, code_width, code_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = COLOR_CODE_BG
        bg.line.color.rgb = COLOR_CODE_BORDER
        bg.line.width = Pt(1.0)

        # 3. 내부 코드 렌더링
        pad_h = Inches(0.40)
        pad_v = Inches(0.30)

        if num_lines > 26:
            # 26줄 초과 시: 터미널 내부를 2단(Left/Right) 분할 렌더링하여 세로 넘침 및 폰트 급락 방지
            half = (num_lines + 1) // 2
            col1_lines = raw_lines[:half]
            col2_lines = raw_lines[half:]

            col_w = (code_width - (pad_h * 2) - Inches(0.5)) / 2  # 약 5.2 inch
            font_size = Pt(10.5) if num_lines <= 38 else Pt(9.5)

            # Left Column
            self._render_code_column(slide, col1_lines, code_left + pad_h, code_top + pad_v, col_w, code_height - (pad_v * 2), font_size)
            # Right Column
            col2_left = code_left + pad_h + col_w + Inches(0.5)
            self._render_code_column(slide, col2_lines, col2_left, code_top + pad_v, col_w, code_height - (pad_v * 2), font_size)
        else:
            # 26줄 이하: 단일 와이드 컬럼 렌더링
            font_size = Pt(13.5) if num_lines <= 12 else (Pt(12.0) if num_lines <= 18 else Pt(11.0))
            self._render_code_column(
                slide, raw_lines,
                code_left + pad_h, code_top + pad_v,
                code_width - (pad_h * 2), code_height - (pad_v * 2),
                font_size
            )

    def _render_code_column(self, slide, lines, left, top, width, height, font_size):
        c_box = slide.shapes.add_textbox(left, top, width, height)
        tf = c_box.text_frame
        tf.word_wrap = False
        tf.margin_left = 0
        tf.margin_right = 0
        tf.margin_top = 0
        tf.margin_bottom = 0

        first = True
        for line in lines:
            p = tf.paragraphs[0] if first else tf.add_paragraph()
            first = False

            leading_match = re.match(r"^(\s+)", line)
            if leading_match:
                spaces = leading_match.group(1)
                preserved_spaces = spaces.replace(" ", "\u00A0")
                line_content = preserved_spaces + line[len(spaces):]
            else:
                line_content = line

            p.text = line_content
            p.font.name = "Consolas"
            p.font.size = font_size
            if line.strip().startswith("# --- [") or line.strip().startswith("# [실행 결과"):
                p.font.color.rgb = RGBColor(96, 165, 250)  # 연파랑 (결과 헤더)
                p.font.bold = True
            elif line.strip().startswith("#"):
                p.font.color.rgb = RGBColor(156, 163, 175) # 주석 회색
            else:
                p.font.color.rgb = COLOR_WHITE
            p.line_spacing = 1.25

            pPr = p._p.get_or_add_pPr()
            buNone = parse_xml(f'<a:buNone {nsdecls("a")}/>')
            pPr.append(buNone)

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

            # 인용 블록
            if line_str.startswith(">"):
                clean_quote = clean_math_and_symbols(re.sub(r"^>\s*", "", line_str))
                p = tf.paragraphs[0] if first else tf.add_paragraph()
                first = False
                p.text = clean_quote
                p.font.name = FONT_NAME
                p.font.size = Pt(20 if not is_wide else 21)
                p.font.color.rgb = COLOR_BODY
                p.line_spacing = 1.45
                p.space_after = Pt(14)
                continue

            # 본문 텍스트: 앞머리 기호 제거
            text_content = clean_math_and_symbols(re.sub(r"^([-•]|\d+\.)\s*", "", line_str))

            p = tf.paragraphs[0] if first else tf.add_paragraph()
            first = False
            p.text = text_content
            p.font.name = FONT_NAME
            p.font.size = Pt(22)  # 본문 22pt 유지
            p.font.color.rgb = COLOR_BODY
            p.line_spacing = 1.45
            p.space_after = Pt(20)

            # 실제 파워포인트 글머리 기호(buChar •) 및 Hanging Indent 설정
            pPr = p._p.get_or_add_pPr()
            pPr.set('marL', '342900')    # 0.375 inch left margin
            pPr.set('indent', '-342900') # -0.375 inch hanging indent
            for child in list(pPr):
                if child.tag.endswith(('buClr', 'buSzPct', 'buSzPts', 'buFont', 'buChar', 'buNone')):
                    pPr.remove(child)

            if text_content.startswith("💡") or text_content.startswith("⚠️"):
                p.font.bold = True
                p.font.color.rgb = COLOR_PRIMARY
                buNone = parse_xml(f'<a:buNone {nsdecls("a")}/>')
                pPr.append(buNone)
                pPr.set('marL', '0')
                pPr.set('indent', '0')
            else:
                buClr = parse_xml(f'<a:buClr {nsdecls("a")}><a:srgbClr val="2563EB"/></a:buClr>')
                buChar = parse_xml(f'<a:buChar {nsdecls("a")} char="•"/>')
                pPr.append(buClr)
                pPr.append(buChar)

    def create_ending_slide(self, page_num, total_pages, chapter_title=""):
        """마지막 슬라이드: 감사합니다 인사말로 강의 슬라이드 종료"""
        slide = self.prs.slides.add_slide(self.blank_layout)

        # 페이지 번호
        p_box = slide.shapes.add_textbox(Inches(11.333), Inches(0.5), Inches(1.2), Inches(0.4))
        pf = p_box.text_frame
        pp = pf.paragraphs[0]
        pp.text = f"{page_num:02d} / {total_pages:02d}"
        pp.alignment = PP_ALIGN.RIGHT
        pp.font.name = FONT_NAME
        pp.font.size = Pt(14)
        pp.font.bold = True
        pp.font.color.rgb = RGBColor(156, 163, 175)

        # 완강 배지
        badge = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, Inches(4.916), Inches(2.2), Inches(3.5), Inches(0.44)
        )
        badge.fill.solid()
        badge.fill.fore_color.rgb = COLOR_PRIMARY
        badge.line.color.rgb = COLOR_PRIMARY
        badge.adjustments[0] = 0.5

        tf = badge.text_frame
        tf.word_wrap = False
        p = tf.paragraphs[0]
        p.text = f"{chapter_title} 완강"
        p.font.name = FONT_NAME
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = COLOR_WHITE
        p.alignment = PP_ALIGN.CENTER

        # 메인 감사 타이틀: "감사합니다"
        t_box = slide.shapes.add_textbox(Inches(2.0), Inches(2.9), Inches(9.333), Inches(1.0))
        tf = t_box.text_frame
        p = tf.paragraphs[0]
        p.text = "감사합니다"
        p.font.name = FONT_NAME
        p.font.size = Pt(46)
        p.font.bold = True
        p.font.color.rgb = COLOR_TITLE
        p.alignment = PP_ALIGN.CENTER

        # 서브 설명문
        s_box = slide.shapes.add_textbox(Inches(2.0), Inches(4.05), Inches(9.333), Inches(0.8))
        sf = s_box.text_frame
        sp = sf.paragraphs[0]
        sp.text = f"{chapter_title} 학습을 성공적으로 마치셨습니다.\n다음 강의에서 심층 강화학습의 더 깊은 탐험으로 이어집니다."
        sp.font.name = FONT_NAME
        sp.font.size = Pt(18)
        sp.font.color.rgb = COLOR_SUBTITLE
        sp.alignment = PP_ALIGN.CENTER
        sp.line_spacing = 1.4

        # Q&A 안내
        q_box = slide.shapes.add_textbox(Inches(2.0), Inches(5.1), Inches(9.333), Inches(0.45))
        qf = q_box.text_frame
        qp = qf.paragraphs[0]
        qp.text = "질의응답(Q&A) 및 토론"
        qp.font.name = FONT_NAME
        qp.font.size = Pt(15)
        qp.font.bold = True
        qp.font.color.rgb = COLOR_PRIMARY
        qp.alignment = PP_ALIGN.CENTER

        # 슬라이드 노트
        notes_slide = slide.notes_slide
        closing_script = (
            f"이상으로 {chapter_title} 강의를 모두 마치겠습니다. "
            "핵심 원리를 충실히 익혀주신 여러분께 감사드리며, "
            "다음 실전 구현 강의에서 더욱 발전된 모습으로 뵙겠습니다. "
            "경청해 주셔서 대단히 감사합니다."
        )
        notes_slide.notes_text_frame.text = convert_to_tts_script(closing_script)

# ==========================================
# 3. slides.md 정밀 파서
# ==========================================
def parse_subchapter_slides():
    with open(SLIDES_MD_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    parts = content.split("\n---\n")

    # 1. Frontmatter 파싱
    frontmatter = parts[0]
    m_title = re.search(r'title:\s*["\']?(.*?)["\']?\s*$', frontmatter, re.MULTILINE)
    raw_chapter_title = m_title.group(1) if m_title else FOLDER_NAME.replace("_", " ")

    # 배지용 챕터 라벨
    chapter_num_match = re.search(r"(\d+\.\d+)", raw_chapter_title)
    if chapter_num_match:
        ch_num = chapter_num_match.group(1)
        badge_text = f"CHAPTER {ch_num}"
    else:
        badge_text = "PART 11 · 심층 강화학습"

    # 표지 데이터
    cover_part = parts[1] if len(parts) > 1 else ""
    cover_script = ""
    s_m = re.search(r">\s*\*\*\[강의 스크립트\]\*\*\s*\n((?:> .*\n?)+)", cover_part)
    if s_m:
        cover_script = s_m.group(1).replace(">", "").strip()

    # 표지 설명문
    desc_lines = []
    for l in cover_part.split("\n"):
        l = l.strip()
        if l and not l.startswith("#") and not l.startswith("![") and not l.startswith(">") and not l.startswith("**그림"):
            desc_lines.append(l)
    cover_subtitle = " ".join(desc_lines[:2]) if desc_lines else "딥러닝과 자동 미분의 세계를 밑바닥부터 체계적으로 학습합니다."

    cover_data = {
        "badge": badge_text,
        "title": raw_chapter_title,
        "subtitle": cover_subtitle,
        "script": cover_script
    }

    # 2. 본문 슬라이드 파싱 (parts[2:]부터)
    body_slides = []
    curr_h1 = raw_chapter_title
    curr_h2 = ""
    curr_h3 = ""

    for p_idx in range(2, len(parts)):
        p_raw = parts[p_idx].strip()
        if not p_raw:
            continue

        # A. 스크립트 추출
        script = ""
        s_m = re.search(r">\s*\*\*\[강의 스크립트\]\*\*\s*\n((?:> .*\n?)+)", p_raw)
        if s_m:
            script = s_m.group(1).replace(">", "").strip()
            p_content = p_raw[:s_m.start()].strip()
        else:
            p_content = p_raw

        # B. 코드 블록 추출
        code_matches = list(re.finditer(r"```(?:python|bash|text)?\n([\s\S]*?)```", p_content))
        code_block = None
        if code_matches:
            if len(code_matches) == 1:
                code_block = code_matches[0].group(1)
            else:
                main_code = code_matches[0].group(1).rstrip()
                output_code = code_matches[1].group(1).strip()
                out_lines = "\n".join(f"# {l}" for l in output_code.split("\n"))
                code_block = f"{main_code}\n\n# --- [실행 결과] ---\n{out_lines}"

        # C. 헤딩 파싱 (코드 블록 제외)
        no_code = re.sub(r"```[\s\S]*?```", "", p_content)
        lines = [l.strip() for l in no_code.split("\n") if l.strip()]

        for l in lines:
            if re.match(r"^#\s+[^\d]", l) or l.startswith("# 11."):
                curr_h1 = re.sub(r"^#\s*", "", l)
            elif l.startswith("## "):
                curr_h2 = re.sub(r"^##\s*", "", l)
                curr_h3 = ""
            elif l.startswith("### "):
                curr_h3 = re.sub(r"^###\s*", "", l)

        # 부제목 결정
        subtitle = curr_h3 or curr_h2 or "개념 이해와 실습"

        # D. 이미지 및 캡션 파싱
        img_info = None
        img_match = re.search(r"!\[(.*?)\]\((.*?)\)", p_content)
        caption_match = re.search(r"\*\*(그림 \d+-\d+-\d+)\*\*\s*(.*)", p_content)

        if img_match:
            img_rel_path = img_match.group(2)
            img_full_path = os.path.normpath(os.path.join(BASE_DIR, img_rel_path))
            caption_text = ""
            if caption_match:
                caption_text = f"{caption_match.group(1)} {caption_match.group(2)}"
            else:
                caption_text = img_match.group(1)

            if os.path.exists(img_full_path):
                img_info = {
                    "path": img_full_path,
                    "caption": caption_text
                }

        # E. 본문 텍스트 정제
        text_lines = []
        for l in lines:
            if l.startswith("#"):
                continue
            if l.startswith("![") or l.startswith("**그림"):
                continue
            if "<div" in l and ("ch07/" in l or "dezero" in l or "py" in l):
                continue
            clean_l = clean_math_and_symbols(l)
            if clean_l.startswith("출력 결과:") or clean_l.startswith("학습 진행 로그:"):
                continue
            if clean_l:
                text_lines.append(clean_l)

        body_text = "\n".join(text_lines).strip()

        body_slides.append({
            "title": curr_h1,
            "subtitle": subtitle,
            "image": img_info,
            "code": code_block,
            "body": body_text,
            "script": script
        })

    return cover_data, body_slides, raw_chapter_title

# ==========================================
# 4. 메인 실행 루틴
# ==========================================
def main():
    print(f"[{FOLDER_NAME}] [1/3] Parsing slides from: {SLIDES_MD_PATH}")
    cover_data, body_slides, chapter_title = parse_subchapter_slides()
    total_slides = len(body_slides) + 2  # Cover + Body + Ending Slide
    print(f"[{FOLDER_NAME}]       Parsed cover + {len(body_slides)} body + 1 ending (Total {total_slides} slides)")

    print(f"[{FOLDER_NAME}] [2/3] Building PPTX (16:9, Native Bullets, 22pt, TTS)...")
    builder = PresentationBuilder()

    # 1. 표지 슬라이드
    builder.create_editable_cover_slide(cover_data)

    # 2. 본문 슬라이드
    for idx, slide_data in enumerate(body_slides):
        page_num = idx + 2
        builder.create_body_slide(slide_data, page_num, total_slides)

    # 3. 종료 슬라이드
    clean_ch_title = chapter_title.split(":")[0].strip()
    builder.create_ending_slide(total_slides, total_slides, clean_ch_title)

    # 4. PPTX 저장
    print(f"[{FOLDER_NAME}] [3/3] Saving final presentation to: {OUTPUT_PPTX_PATH}")
    builder.prs.save(OUTPUT_PPTX_PATH)
    print(f"[{FOLDER_NAME}]       Done! {OUTPUT_PPTX_PATH} generated successfully!\n")

if __name__ == "__main__":
    main()
