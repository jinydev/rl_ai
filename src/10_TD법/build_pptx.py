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
COLOR_CODE_BG = RGBColor(17, 24, 39)        # #111827 (Square Black Code Box)
COLOR_WHITE = RGBColor(255, 255, 255)       # #FFFFFF (Pure White)

FONT_NAME = "나눔고딕"

BASE_DIR = "/Users/hojin9/dev/jinysite/강화학습3/src/10_TD법"
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
SLIDES_MD_PATH = os.path.join(BASE_DIR, "slides.md")
OUTPUT_PPTX_PATH = os.path.join(BASE_DIR, "10_TD법.pptx")

# ==========================================
# 2. 수식 및 텍스트 정제 엔진 (math_cleaner 연동)
# ==========================================
import sys
_CH10_ROOT = "/Users/hojin9/dev/jinysite/강화학습3/src/10_TD법"
if _CH10_ROOT not in sys.path:
    sys.path.insert(0, _CH10_ROOT)
from math_cleaner import clean_slide_math, clean_notes_math

def clean_math_and_symbols(text):
    """마크다운 수식, HTML 태그, LaTeX 문법을 PPTX 가독성 높은 유니코드 기호로 100% 변환"""
    return clean_slide_math(text)

def convert_to_tts_script(text):
    """향후 TTS가 자연스러운 한국어 구술 음성으로 발음하도록 수식 코드를 한글 독음으로 100% 변환"""
    return clean_notes_math(text)


# ==========================================
# 4. PPTX 빌더 클래스
# ==========================================
class PresentationBuilder:
    def __init__(self):
        self.prs = Presentation()
        self.prs.slide_width = SLIDE_WIDTH
        self.prs.slide_height = SLIDE_HEIGHT
        self.blank_layout = self.prs.slide_layouts[6]

    def create_editable_cover_slide(self):
        """첫 번째 슬라이드: 온전한 독립 투명 배경 애셋 4종을 삽입한 편집 가능 커버 슬라이드"""
        slide = self.prs.slides.add_slide(self.blank_layout)

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

        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.75), Inches(5.6), Inches(1.5))
        tf = title_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = "CHAPTER 10\nTD법: 시간차 학습"
        p.font.name = FONT_NAME
        p.font.size = Pt(44)
        p.font.bold = True
        p.font.color.rgb = COLOR_TITLE

        sub_box = slide.shapes.add_textbox(Inches(0.8), Inches(3.45), Inches(5.6), Inches(1.8))
        tf = sub_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = "동적 계획법의 부트스트랩과 몬테카를로 샘플링을 융합하여\n단 1-스텝의 경험으로 실시간 가치를 갱신하는\n현대 강화학습의 위대한 패러다임 전환"
        p.font.name = FONT_NAME
        p.font.size = Pt(20)
        p.font.color.rgb = COLOR_SUBTITLE

        auth_box = slide.shapes.add_textbox(Inches(0.8), Inches(5.15), Inches(5.6), Inches(0.6))
        tf = auth_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = "강의: 이호진 교수 · 조교 지니와 도로시 탐험대"
        p.font.name = FONT_NAME
        p.font.size = Pt(16)
        p.font.color.rgb = RGBColor(55, 65, 81)

        ground_y = Inches(6.0)

        p_jiny = os.path.join(ASSETS_DIR, "asset_01_jiny_scholar.png")
        if os.path.exists(p_jiny):
            slide.shapes.add_picture(p_jiny, Inches(6.5), ground_y - Inches(2.4), width=Inches(2.0))

        p_dorothy = os.path.join(ASSETS_DIR, "asset_02_dorothy_stepping.png")
        if os.path.exists(p_dorothy):
            slide.shapes.add_picture(p_dorothy, Inches(8.3), ground_y - Inches(4.0), width=Inches(2.0))

        p_toto = os.path.join(ASSETS_DIR, "asset_03_toto_running.png")
        if os.path.exists(p_toto):
            slide.shapes.add_picture(p_toto, Inches(9.8), ground_y - Inches(2.0), width=Inches(1.5))

        p_hojin = os.path.join(ASSETS_DIR, "asset_04_prof_hojin.png")
        if os.path.exists(p_hojin):
            slide.shapes.add_picture(p_hojin, Inches(11.0), ground_y - Inches(5.0), width=Inches(1.9))

        notes_slide = slide.notes_slide
        notes_slide.notes_text_frame.text = convert_to_tts_script(
            "반갑습니다. 이번 제10장에서는 모델 기반의 동적 계획법과 경험 기반의 몬테카를로법이라는 두 거대한 산맥을 하나로 융합하여 탄생한 현대 강화학습의 핵심, '시간차 학습(TD)'의 대장정을 시작합니다. 에피소드가 끝날 때까지 기다리지 않고 매 걸음마다 즉각적으로 가치를 갱신하는 놀라운 지능의 원리를 지금부터 함께 탐험해 보겠습니다."
        )

    def add_common_header(self, slide, title_text, subtitle_text, page_str):
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

        p_box = slide.shapes.add_textbox(Inches(11.333), Inches(0.5), Inches(1.2), Inches(0.4))
        pf = p_box.text_frame
        pp = pf.paragraphs[0]
        pp.text = page_str
        pp.alignment = PP_ALIGN.RIGHT
        pp.font.name = FONT_NAME
        pp.font.size = Pt(14)
        pp.font.bold = True
        pp.font.color.rgb = COLOR_DIVIDER

        line = slide.shapes.add_connector(
            MSO_CONNECTOR.STRAIGHT, Inches(0.8), Inches(1.7), Inches(12.533), Inches(1.7)
        )
        line.line.color.rgb = COLOR_DIVIDER
        line.line.width = Pt(0.75)

    def create_general_slide(self, slide_idx, raw_slide_data, page_num, total_pages):
        slide = self.prs.slides.add_slide(self.blank_layout)

        title = raw_slide_data.get("title", "")
        subtitle = raw_slide_data.get("subtitle", "")
        page_str = f"{page_num:02d} / {total_pages:02d}"

        self.add_common_header(slide, title, subtitle, page_str)

        img_info = raw_slide_data.get("image")
        body_text = raw_slide_data.get("body", "")
        code_block = raw_slide_data.get("code")
        table_data = raw_slide_data.get("table")
        script = raw_slide_data.get("script", "")

        if img_info:
            self._render_two_column_layout(slide, img_info, body_text, code_block)
        else:
            self._render_wide_layout(slide, body_text, code_block, table_data)

        if script:
            notes_slide = slide.notes_slide
            tts_script = convert_to_tts_script(script.strip())
            notes_slide.notes_text_frame.text = tts_script

    def _render_two_column_layout(self, slide, img_info, body_text, code_block):
        img_path = img_info["path"]
        caption = img_info["caption"]

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

        self._populate_text_frame(tf, body_text, code_block)

    def _render_wide_layout(self, slide, body_text, code_block, table_data):
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
        """검정 바탕의 정사각형 코드 박스 + 흰색 글자 슬라이드 (가이드 엄격 준수, 들여쓰기 100% 보존)"""
        code_sq_size = Inches(4.8)
        code_left = Inches(1.0)
        code_top = Inches(2.0)

        if body_text.strip():
            desc_box = slide.shapes.add_textbox(Inches(6.2), Inches(2.0), Inches(6.3), Inches(4.8))
            tf = desc_box.text_frame
            tf.word_wrap = True
            tf.vertical_anchor = MSO_ANCHOR.MIDDLE
            self._populate_text_frame(tf, body_text, None)
        else:
            code_left = (SLIDE_WIDTH - code_sq_size) / 2
            code_top = Inches(2.0)

        bg = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, code_left, code_top, code_sq_size, code_sq_size
        )
        bg.fill.solid()
        bg.fill.fore_color.rgb = COLOR_CODE_BG
        bg.line.color.rgb = COLOR_CODE_BG

        c_box = slide.shapes.add_textbox(
            code_left + Inches(0.2), code_top + Inches(0.2),
            code_sq_size - Inches(0.4), code_sq_size - Inches(0.4)
        )
        tf = c_box.text_frame
        tf.word_wrap = False
        lines = code_block.strip().split("\n")
        
        num_lines = len(lines)
        if num_lines > 30:
            font_size = Pt(9.5)
            line_spacing = 1.15
        elif num_lines > 22:
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
            p.font.color.rgb = COLOR_WHITE
            p.line_spacing = line_spacing
            
            # C. OpenXML schema ECMA-376 whitespace preservation 보장
            for t in p._p.xpath(".//a:t"):
                t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")

    def _render_table_slide(self, slide, body_text, table_data):
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
                ("=" in line_str and ("Q(" in line_str or "V(" in line_str or "←" in line_str or "δ" in line_str or "G" in line_str)) or
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
# 5. slides.md 파서
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

        lines = raw.split("\n")
        title = ""
        subtitle = ""
        body_start = 0
        for l_idx, line in enumerate(lines):
            l_str = line.strip()
            if l_str.startswith("# ") and not title:
                title = l_str[2:].strip()
            elif l_str.startswith("## ") and not subtitle:
                subtitle = l_str[3:].strip()
                body_start = l_idx + 1
                break
        data["title"] = title
        data["subtitle"] = subtitle

        body_lines = lines[body_start:]

        script_lines = []
        c_idx = len(body_lines) - 1
        while c_idx >= 0 and (body_lines[c_idx].strip().startswith(">") or (script_lines and not body_lines[c_idx].strip())):
            if body_lines[c_idx].strip().startswith(">"):
                script_lines.insert(0, re.sub(r"^>\s*", "", body_lines[c_idx].strip()))
            c_idx -= 1
        script = " ".join(script_lines).strip()
        if script.startswith('"') and script.endswith('"'):
            script = script[1:-1].strip()
        data["script"] = script

        body = "\n".join(body_lines[:c_idx+1]).strip()

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

        lines_clean = body.split("\n")
        remaining_lines = []
        for l in lines_clean:
            if re.match(r"^#+\s+", l.strip()):
                continue
            remaining_lines.append(l)

        data["body"] = "\n".join(remaining_lines).strip()
        parsed_list.append(data)

    return parsed_list

# ==========================================
# 6. 메인 실행 함수
# ==========================================
def main():
    print(f"[1/3] Parsing slides.md from: {SLIDES_MD_PATH}")
    slides_data = parse_slides_md()
    print(f"      Parsed {len(slides_data)} slides successfully.")

    print("[2/3] Building Presentation with python-pptx (TTS optimization + Zero-clipping assets)...")
    builder = PresentationBuilder()

    builder.create_editable_cover_slide()

    total_slides_count = len(slides_data) + 1
    for idx, sdata in enumerate(slides_data):
        page_num = idx + 2
        builder.create_general_slide(idx, sdata, page_num, total_slides_count)

    print(f"[3/3] Saving final PPTX to: {OUTPUT_PPTX_PATH}")
    builder.prs.save(OUTPUT_PPTX_PATH)
    print("      Done! PPTX presentation generated successfully!")

if __name__ == "__main__":
    main()

