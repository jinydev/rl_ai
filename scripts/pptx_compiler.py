#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
Unified PPTX Presentation Compiler for 강화학습3
Compliant with: guides/PPTX_CONVERSION_GUIDE.md
=============================================================================
"""

import os
import re
import sys
import unicodedata
from PIL import Image
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.oxml import parse_xml
from pptx.oxml.ns import nsdecls

# Scripts dir import
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)
from math_cleaner import clean_slide_math, clean_notes_math

# Design Tokens (16:9 Widescreen & Color System)
SLIDE_WIDTH = Inches(13.333)
SLIDE_HEIGHT = Inches(7.500)

COLOR_PRIMARY = RGBColor(26, 115, 232)      # #1A73E8 (Brand Blue Badge)
COLOR_TITLE = RGBColor(17, 24, 39)          # #111827 (Dark Charcoal)
COLOR_SUBTITLE = RGBColor(107, 114, 128)    # #6B7280 (Medium Gray)
COLOR_BODY = RGBColor(31, 41, 55)           # #1F2937 (Body Text)
COLOR_DIVIDER = RGBColor(226, 232, 240)     # #E2E8F0 (Divider Line 1px)
COLOR_CAPTION = RGBColor(75, 85, 99)        # #4B5563 (Caption Gray)
COLOR_CODE_BG = RGBColor(17, 24, 39)        # #111827 (Dark Charcoal Terminal)
COLOR_CODE_BORDER = RGBColor(55, 65, 81)    # #374151
COLOR_WHITE = RGBColor(255, 255, 255)

FONT_NAME = "나눔고딕"


def clean_math_and_symbols(text):
    return clean_slide_math(text)


def convert_to_tts_script(text):
    return clean_notes_math(text)


def get_chapter_badge(folder_path, raw_title):
    folder_name = os.path.basename(folder_path)
    parent_name = os.path.basename(os.path.dirname(folder_path))

    ch_map = {
        "01_강화학습이란": "PART 01 · 강화학습이란",
        "02_확률과_기초수학": "PART 02 · 확률과 기초수학",
        "03_밴디트_문제": "PART 03 · 밴디트 문제",
        "04_마르코프": "PART 04 · 마르코프 과정",
        "05_마르코프_결정_과정": "PART 05 · 마르코프 결정 과정",
        "09_몬테카를로법": "PART 09 · 몬테카를로법",
        "10_TD법": "PART 10 · TD법",
        "11_신경망과_Q_러닝": "PART 11 · 심층 강화학습",
        "12_DQN": "PART 12 · DQN",
    }

    # 1. Match subchapters like 01.1, 2.3, 3_1, 5_4
    m_sub = re.search(r"(\d+)[._](\d+)", folder_name)
    if m_sub:
        ch_int = int(m_sub.group(1))
        sub_int = int(m_sub.group(2))
        return f"CHAPTER {ch_int:02d}.{sub_int}"

    m_title = re.search(r"(\d+\.\d+)", raw_title)
    if m_title:
        return f"CHAPTER {m_title.group(1)}"

    if folder_name in ch_map:
        return ch_map[folder_name]
    if parent_name in ch_map:
        return ch_map[parent_name]

    return "강화학습 마스터 클래스"


class PresentationBuilder:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.folder_name = os.path.basename(folder_path)
        self.prs = Presentation()
        self.prs.slide_width = SLIDE_WIDTH
        self.prs.slide_height = SLIDE_HEIGHT
        self.blank_layout = self.prs.slide_layouts[6]

    def create_editable_cover_slide(self, cover_data):
        slide = self.prs.slides.add_slide(self.blank_layout)

        # 1. 하위 레이어: 커버 PNG 이미지 84.5% 축소 우하단 고정
        cover_png_path = os.path.join(self.folder_path, f"{self.folder_name}.png")
        if not os.path.exists(cover_png_path):
            norm_name = unicodedata.normalize("NFC", self.folder_name)
            for f in os.listdir(self.folder_path):
                if f.endswith(".png") and not f.startswith("."):
                    if unicodedata.normalize("NFC", f) == f"{norm_name}.png":
                        cover_png_path = os.path.join(self.folder_path, f)
                        break
            if not os.path.exists(cover_png_path):
                for f in os.listdir(self.folder_path):
                    if f.endswith(".png") and not f.startswith("."):
                        cover_png_path = os.path.join(self.folder_path, f)
                        break

        if os.path.exists(cover_png_path):
            img_w = Inches(11.27)
            img_h = Inches(6.34)
            img_left = SLIDE_WIDTH - img_w
            img_top = SLIDE_HEIGHT - img_h
            slide.shapes.add_picture(cover_png_path, img_left, img_top, width=img_w, height=img_h)

        # 2. 상위 레이어: 챕터 정보 배지
        badge_text = cover_data.get("badge", "강화학습 마스터 클래스")
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

        # 3. 메인 강의 타이틀 (36pt Bold)
        title_text = cover_data.get("title", self.folder_name.replace("_", " "))
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

        # 4. 부제목 설명문 (18pt Regular)
        sub_text = cover_data.get("subtitle", "경험으로 미지의 세계를 개척하는 강화학습의 원리와 실전 구현")
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
        # 제목
        t_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(10.5), Inches(0.55))
        tf = t_box.text_frame
        tf.word_wrap = True
        tf.margin_top = 0
        tf.margin_bottom = 0
        tf.margin_left = 0
        tf.margin_right = 0
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

        # 페이지 번호
        p_box = slide.shapes.add_textbox(Inches(11.333), Inches(0.5), Inches(1.2), Inches(0.4))
        pf = p_box.text_frame
        pp = pf.paragraphs[0]
        pp.text = page_str
        pp.alignment = PP_ALIGN.RIGHT
        pp.font.name = FONT_NAME
        pp.font.size = Pt(14)
        pp.font.bold = True
        pp.font.color.rgb = RGBColor(156, 163, 175)

        # 구분선 1px 단색 실선
        line = slide.shapes.add_connector(
            MSO_CONNECTOR.STRAIGHT, Inches(0.8), Inches(1.7), Inches(12.533), Inches(1.7)
        )
        line.line.color.rgb = COLOR_DIVIDER
        line.line.width = Pt(1.0)

    def create_body_slide(self, slide_data, page_num, total_pages):
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

        try:
            with Image.open(img_path) as im:
                orig_w, orig_h = im.size
        except Exception:
            orig_w, orig_h = 1920, 1080

        max_w = Inches(4.2)
        max_h = Inches(3.9)
        aspect = orig_w / max(1, orig_h)
        box_aspect = max_w / max_h

        if aspect >= box_aspect:
            dest_w = max_w
            dest_h = dest_w / aspect
        else:
            dest_h = max_h
            dest_w = dest_h * aspect

        left = Inches(1.0) + (max_w - dest_w) / 2
        top = Inches(2.15) + (max_h - dest_h) / 2

        slide.shapes.add_picture(img_path, left, top, width=dest_w, height=dest_h)

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
            p.font.size = Pt(13)
            p.font.color.rgb = COLOR_CAPTION
            p.alignment = PP_ALIGN.CENTER
            p.line_spacing = 1.3

        r_left = Inches(6.0)
        r_width = Inches(6.5)
        top_y = Inches(1.90)
        avail_h = Inches(4.90)

        if code_block and code_block.strip():
            raw_code_lines = code_block.strip().split("\n")
            num_code_lines = len(raw_code_lines)
            clean_intro = clean_math_and_symbols(body_text.strip()) if body_text else ""
            clean_intro = re.sub(r">\s*\[!(?:IMPORTANT|NOTE|TIP|CAUTION|WARNING)\]", "", clean_intro)
            clean_intro = re.sub(r"^>\s?", "", clean_intro, flags=re.MULTILINE).strip()
            has_intro = bool(clean_intro)

            if has_intro:
                intro_len = len(clean_intro)
                if intro_len > 120:
                    text_h = Inches(1.30)
                    font_sz = Pt(14)
                elif intro_len > 60:
                    text_h = Inches(0.95)
                    font_sz = Pt(16)
                else:
                    text_h = Inches(0.55)
                    font_sz = Pt(17)

                t_box = slide.shapes.add_textbox(r_left, top_y, r_width, text_h)
                tf = t_box.text_frame
                tf.word_wrap = True
                tf.margin_left = 0
                tf.margin_right = 0
                tf.margin_top = 0
                tf.margin_bottom = 0
                p = tf.paragraphs[0]
                p.text = clean_intro
                p.font.name = FONT_NAME
                p.font.size = font_sz
                p.font.color.rgb = COLOR_BODY
                p.line_spacing = 1.3

                code_top = top_y + text_h + Inches(0.12)
                code_h = avail_h - text_h - Inches(0.12)
            else:
                code_top = top_y
                code_h = avail_h

            bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, r_left, code_top, r_width, code_h)
            bg.fill.solid()
            bg.fill.fore_color.rgb = COLOR_CODE_BG
            bg.line.color.rgb = COLOR_CODE_BORDER
            bg.line.width = Pt(1.0)

            pad_h = Inches(0.25)
            pad_v = Inches(0.20)
            c_font_size = Pt(11.5) if num_code_lines <= 6 else (Pt(10.0) if num_code_lines <= 12 else Pt(8.5))

            self._render_code_column(
                slide, raw_code_lines,
                r_left + pad_h, code_top + pad_v,
                r_width - (pad_h * 2), code_h - (pad_v * 2),
                c_font_size
            )
        else:
            r_box = slide.shapes.add_textbox(r_left, top_y, r_width, avail_h)
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
        has_intro = bool(body_text and body_text.strip())

        raw_lines = code_block.strip().split("\n")
        num_lines = len(raw_lines)

        code_left = Inches(0.8)
        code_width = Inches(11.733)

        if has_intro:
            intro_clean = clean_math_and_symbols(body_text.strip())
            intro_clean = re.sub(r">\s*\[!(?:IMPORTANT|NOTE|TIP|CAUTION|WARNING)\]", "", intro_clean)
            intro_clean = re.sub(r"^>\s?", "", intro_clean, flags=re.MULTILINE)
            intro_clean = intro_clean.replace("\n", " ").strip()
            intro_len = len(intro_clean)

            if intro_len > 250:
                intro_h = Inches(1.25)
                code_top = Inches(3.15)
                code_height = Inches(3.85)
                font_sz = Pt(13.5)
            elif intro_len > 120:
                intro_h = Inches(0.85)
                code_top = Inches(2.75)
                code_height = Inches(4.25)
                font_sz = Pt(15.0)
            elif intro_len > 60:
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

        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, code_left, code_top, code_width, code_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = COLOR_CODE_BG
        bg.line.color.rgb = COLOR_CODE_BORDER
        bg.line.width = Pt(1.0)

        pad_h = Inches(0.40)
        pad_v = Inches(0.30)

        if num_lines > 26:
            half = (num_lines + 1) // 2
            col1_lines = raw_lines[:half]
            col2_lines = raw_lines[half:]

            col_w = (code_width - (pad_h * 2) - Inches(0.5)) / 2
            font_size = Pt(10.5) if num_lines <= 38 else Pt(9.5)

            self._render_code_column(slide, col1_lines, code_left + pad_h, code_top + pad_v, col_w, code_height - (pad_v * 2), font_size)
            col2_left = code_left + pad_h + col_w + Inches(0.5)
            self._render_code_column(slide, col2_lines, col2_left, code_top + pad_v, col_w, code_height - (pad_v * 2), font_size)
        else:
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
                p.font.color.rgb = RGBColor(96, 165, 250)
                p.font.bold = True
            elif line.strip().startswith("#"):
                p.font.color.rgb = RGBColor(156, 163, 175)
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

            # 일반 본문 텍스트: 앞머리 기호 정제
            raw_clean = re.sub(r"^[-*•\d\.\)]\s*", "", line_str)
            clean_line = clean_math_and_symbols(raw_clean)

            p = tf.paragraphs[0] if first else tf.add_paragraph()
            first = False
            p.text = clean_line
            p.font.name = FONT_NAME
            p.font.size = Pt(21 if not is_wide else 22)
            p.font.color.rgb = COLOR_BODY
            p.line_spacing = 1.40
            p.space_after = Pt(10)

            pPr = p._p.get_or_add_pPr()
            pPr.set("marL", "457200")
            pPr.set("indent", "-274320")

            buClr = parse_xml(f'<a:buClr {nsdecls("a")}><a:srgbClr val="9CA3AF"/></a:buClr>')
            buChar = parse_xml(f'<a:buChar {nsdecls("a")} char="•"/>')
            pPr.append(buClr)
            pPr.append(buChar)

    def create_ending_slide(self, page_num, total_pages, chapter_title=""):
        slide = self.prs.slides.add_slide(self.blank_layout)

        p_box = slide.shapes.add_textbox(Inches(11.333), Inches(0.5), Inches(1.2), Inches(0.4))
        pf = p_box.text_frame
        pp = pf.paragraphs[0]
        pp.text = f"{page_num:02d} / {total_pages:02d}"
        pp.alignment = PP_ALIGN.RIGHT
        pp.font.name = FONT_NAME
        pp.font.size = Pt(14)
        pp.font.bold = True
        pp.font.color.rgb = RGBColor(156, 163, 175)

        badge = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, Inches(4.666), Inches(2.2), Inches(4.0), Inches(0.44)
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

        t_box = slide.shapes.add_textbox(Inches(2.0), Inches(2.9), Inches(9.333), Inches(1.0))
        tf = t_box.text_frame
        p = tf.paragraphs[0]
        p.text = "감사합니다"
        p.font.name = FONT_NAME
        p.font.size = Pt(46)
        p.font.bold = True
        p.font.color.rgb = COLOR_TITLE
        p.alignment = PP_ALIGN.CENTER

        s_box = slide.shapes.add_textbox(Inches(2.0), Inches(4.05), Inches(9.333), Inches(0.8))
        sf = s_box.text_frame
        sp = sf.paragraphs[0]
        sp.text = f"{chapter_title} 학습을 성공적으로 마치셨습니다.\n다음 강의에서 미지의 세계를 개척하는 더 깊은 강화학습의 탐험으로 이어집니다."
        sp.font.name = FONT_NAME
        sp.font.size = Pt(18)
        sp.font.color.rgb = COLOR_SUBTITLE
        sp.alignment = PP_ALIGN.CENTER
        sp.line_spacing = 1.4

        q_box = slide.shapes.add_textbox(Inches(2.0), Inches(5.1), Inches(9.333), Inches(0.45))
        qf = q_box.text_frame
        qp = qf.paragraphs[0]
        qp.text = "질의응답(Q&A) 및 토론"
        qp.font.name = FONT_NAME
        qp.font.size = Pt(15)
        qp.font.bold = True
        qp.font.color.rgb = COLOR_PRIMARY
        qp.alignment = PP_ALIGN.CENTER

        notes_slide = slide.notes_slide
        closing_script = (
            f"이상으로 {chapter_title} 강의를 모두 마치겠습니다. "
            "핵심 원리를 충실히 익혀주신 여러분께 감사드리며, "
            "다음 실전 구현 강의에서 더욱 발전된 모습으로 뵙겠습니다. "
            "경청해 주셔서 대단히 감사합니다."
        )
        notes_slide.notes_text_frame.text = convert_to_tts_script(closing_script)


def parse_slides_file(folder_path):
    slides_md_path = os.path.join(folder_path, "slides.md")
    if not os.path.exists(slides_md_path):
        raise FileNotFoundError(f"slides.md not found in {folder_path}")

    with open(slides_md_path, "r", encoding="utf-8") as f:
        content = f.read()

    parts = content.split("\n---\n")

    # Frontmatter
    frontmatter = parts[0]
    m_title = re.search(r'title:\s*["\']?(.*?)["\']?\s*$', frontmatter, re.MULTILINE)
    raw_chapter_title = m_title.group(1) if m_title else os.path.basename(folder_path).replace("_", " ")

    badge_text = get_chapter_badge(folder_path, raw_chapter_title)

    # Cover slide
    cover_part = parts[1] if len(parts) > 1 else ""
    cover_script = ""
    s_m = re.search(r">\s*\*\*\[강의 스크립트\]\*\*\s*\n((?:> .*\n?)+)", cover_part)
    if s_m:
        cover_script = s_m.group(1).replace(">", "").strip()

    desc_lines = []
    for l in cover_part.split("\n"):
        l = l.strip()
        if l and not l.startswith("#") and not l.startswith("![") and not l.startswith(">") and not l.startswith("**그림"):
            desc_lines.append(l)
    cover_subtitle = " ".join(desc_lines[:2]) if desc_lines else "경험으로 미지의 세계를 개척하는 강화학습의 원리와 실전 구현"

    cover_data = {
        "badge": badge_text,
        "title": raw_chapter_title,
        "subtitle": cover_subtitle,
        "script": cover_script
    }

    # Body slides
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

        # B. 코드 블록 추출 (zsh, powershell, cmd, bash, python, text, 블록인용구 `> ``` 등 모든 언어 태그 완벽 지원)
        raw_code_matches = list(re.finditer(r"(?:^|\n)>?[ \t]*```([^\n]*)\n([\s\S]*?)(?:^|\n)>?[ \t]*```", p_content))
        code_block = None
        if raw_code_matches:
            cleaned_blocks = []
            for m in raw_code_matches:
                lang = m.group(1).strip().lower()
                raw_lines = m.group(2).split("\n")
                cleaned_lines = [re.sub(r"^>\s?", "", l) for l in raw_lines]
                cleaned_text = "\n".join(cleaned_lines).rstrip()
                if cleaned_text:
                    cleaned_blocks.append((lang, cleaned_text))

            if len(cleaned_blocks) == 1:
                code_block = cleaned_blocks[0][1]
            elif len(cleaned_blocks) > 1:
                parts_out = []
                for idx, (lang, c_text) in enumerate(cleaned_blocks):
                    if idx > 0 and lang in ("text", "output"):
                        out_lines = "\n".join(f"# {l}" for l in c_text.split("\n"))
                        parts_out.append(f"# --- [실행 결과] ---\n{out_lines}")
                    elif idx > 0 and lang in ("bash", "zsh", "sh", "cmd", "powershell"):
                        parts_out.append(f"# --- [터미널 명령어] ---\n{c_text}")
                    elif idx > 0:
                        parts_out.append(f"\n# ----------------------------------------\n{c_text}")
                    else:
                        parts_out.append(c_text)
                code_block = "\n\n".join(parts_out)

        # C. 헤딩 파싱
        no_code = re.sub(r"(?:^|\n)>?[ \t]*```[\s\S]*?(?:^|\n)>?[ \t]*```", "", p_content)
        lines = [l.strip() for l in no_code.split("\n") if l.strip()]

        for l in lines:
            if re.match(r"^#\s+[^\d]", l) or l.startswith("# 0") or l.startswith("# 1") or l.startswith("# 2") or l.startswith("# 3") or l.startswith("# 4") or l.startswith("# 5") or l.startswith("# CHAPTER"):
                curr_h1 = re.sub(r"^#\s*", "", l)
            elif l.startswith("## "):
                curr_h2 = re.sub(r"^##\s*", "", l)
                curr_h3 = ""
            elif l.startswith("### "):
                curr_h3 = re.sub(r"^###\s*", "", l)

        subtitle = curr_h3 or curr_h2 or "개념 이해와 실습"

        # D. 이미지 및 캡션
        img_info = None
        img_match = re.search(r"!\[(.*?)\]\((.*?)\)", p_content)
        caption_match = re.search(r"\*\*(그림 [^\*]+)\*\*\s*(.*)", p_content)

        if img_match:
            img_rel_path = img_match.group(2)
            img_full_path = os.path.normpath(os.path.join(folder_path, img_rel_path))
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
            if "<div" in l:
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


def build_pptx_for_directory(folder_path):
    folder_name = os.path.basename(folder_path)
    output_pptx_path = os.path.join(folder_path, f"{folder_name}.pptx")

    cover_data, body_slides, chapter_title = parse_slides_file(folder_path)
    total_slides = len(body_slides) + 2

    builder = PresentationBuilder(folder_path)

    # 1. 표지 슬라이드
    builder.create_editable_cover_slide(cover_data)

    # 2. 본문 슬라이드
    for idx, slide_data in enumerate(body_slides):
        page_num = idx + 2
        builder.create_body_slide(slide_data, page_num, total_slides)

    # 3. 종료 슬라이드
    clean_ch_title = chapter_title.split(":")[0].strip()
    builder.create_ending_slide(total_slides, total_slides, clean_ch_title)

    # 4. 저장
    builder.prs.save(output_pptx_path)
    return output_pptx_path, total_slides
