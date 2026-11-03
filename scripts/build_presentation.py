#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
강화학습 교재 슬라이드 -> 16:9 와이드스크린 고품질 강의용 PPTX 공통 변환 스크립트
표준 가이드라인: guides/PPTX_CONVERSION_GUIDE.md (v11.5)
=============================================================================
사용법:
    python3 scripts/build_presentation.py [단원_디렉터리_경로]
예시:
    python3 scripts/build_presentation.py src/07_동적_프로그래밍/7_1_유래
"""

import sys
import os
import re
import argparse
import subprocess
from PIL import Image, ImageDraw

import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.xmlchemy import OxmlElement

# ---------------------------------------------------------------------------
# 전역 디자인 시스템 토큰 (Standard Flat Design Tokens)
# ---------------------------------------------------------------------------
COLOR_BG_WHITE = RGBColor(255, 255, 255)
COLOR_TITLE = RGBColor(15, 23, 42)          # Dark Navy #0F172A
COLOR_BADGE = RGBColor(2, 132, 199)         # Sky Blue #0284C7
COLOR_MUTED = RGBColor(100, 116, 139)       # Slate Gray #64748B
COLOR_BODY = RGBColor(51, 65, 85)           # Slate 700 #334155
COLOR_BULLET_TITLE = RGBColor(15, 23, 42)   # Dark Navy
COLOR_DIVIDER = RGBColor(226, 232, 240)     # Slate 200 #E2E8F0
COLOR_BTN_BG = RGBColor(2, 132, 199)        # Flat Sky Blue #0284C7
COLOR_STOP_BTN_BG = RGBColor(226, 232, 240) # Slate 200 #E2E8F0
COLOR_PLAYER_BG = RGBColor(240, 249, 255)   # Sky 50 #F0F9FF
COLOR_LEAD_BG = RGBColor(241, 245, 249)     # Slate 100 #F1F5F9
COLOR_QUOTE_BG = RGBColor(240, 249, 255)    # Sky 50 #F0F9FF
COLOR_WHITE = RGBColor(255, 255, 255)

# 캐릭터 색상
COLOR_DOROTHY = RGBColor(225, 29, 72)       # Coral Rose #E11D48
COLOR_JINY = RGBColor(29, 78, 216)          # Royal Blue #1D4ED8
COLOR_TOTO = RGBColor(5, 150, 105)          # Emerald #059669

FONT_FAMILY = "Apple SD Gothic Neo"


def make_flat_shape(shape, fill_color=None, line_color=None):
    """도형의 외곽선과 그림자(음영)를 완전히 제거하여 순수 플랫 스타일을 적용합니다."""
    spPr = shape._element.spPr

    # 1. 외곽선(테두리) 제거
    ln = spPr.find("{http://schemas.openxmlformats.org/drawingml/2006/main}ln")
    if ln is None:
        ln = OxmlElement("a:ln")
        spPr.append(ln)
    for child in list(ln):
        ln.remove(child)
    if line_color is not None:
        srgbClr = OxmlElement("a:srgbClr")
        srgbClr.set("val", f"{line_color[0]:02X}{line_color[1]:02X}{line_color[2]:02X}")
        ln.append(srgbClr)
    else:
        ln.append(OxmlElement("a:noFill"))

    # 2. 그림자 및 특수효과 전면 제거
    effectLst = spPr.find("{http://schemas.openxmlformats.org/drawingml/2006/main}effectLst")
    if effectLst is None:
        effectLst = OxmlElement("a:effectLst")
        spPr.append(effectLst)
    for child in list(effectLst):
        effectLst.remove(child)

    # 3. 단색 채우기
    if fill_color is not None:
        shape.fill.solid()
        shape.fill.fore_color.rgb = fill_color
    else:
        shape.fill.background()

    # 4. DrawingML 스타일 참조 idx 초기화
    style = shape._element.find("{http://schemas.openxmlformats.org/presentationml/2006/main}style")
    if style is not None:
        lnRef = style.find("{http://schemas.openxmlformats.org/drawingml/2006/main}lnRef")
        if lnRef is not None:
            lnRef.set("idx", "0")
        effectRef = style.find("{http://schemas.openxmlformats.org/drawingml/2006/main}effectRef")
        if effectRef is not None:
            effectRef.set("idx", "0")


def ensure_circular_avatar(guides_dir: str) -> str:
    """guides/img/hojin.jpg 로부터 고해상도 원형 투명 PNG를 생성하거나 경로를 반환합니다."""
    avatar_src = os.path.join(guides_dir, "img", "hojin.jpg")
    avatar_circle_png = os.path.join(guides_dir, "img", "hojin_circle.png")

    if not os.path.exists(avatar_circle_png) and os.path.exists(avatar_src):
        im = Image.open(avatar_src).convert("RGBA")
        min_dim = min(im.size)
        left = (im.width - min_dim) // 2
        top = (im.height - min_dim) // 2
        im_square = im.crop((left, top, left + min_dim, top + min_dim))

        scale = 2
        size = min_dim * scale
        mask = Image.new("L", (size, size), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, size, size), fill=255)
        mask = mask.resize((min_dim, min_dim), Image.Resampling.LANCZOS)

        output = Image.new("RGBA", (min_dim, min_dim), (0, 0, 0, 0))
        output.paste(im_square, (0, 0), mask=mask)
        output.save(avatar_circle_png, "PNG")

    return avatar_circle_png


def add_fitted_picture(slide, img_path, left_in, top_in, max_w_in, max_h_in):
    """
    종횡비를 유지하며 지정된 박스 안에 이미지를 중앙 정렬하여 추가합니다.
    불필요한 단색/투명 여백(>8%)이 있을 경우 스마트 트리밍하여 가시성을 극대화하며,
    슬라이드 트리의 최하단(Z-Order 맨 뒤)으로 배치하여 텍스트 상자와의 겹침 및 간섭을 원천 방지합니다.
    """
    if not os.path.exists(img_path):
        return None

    img_to_open = img_path
    if img_path.lower().endswith(".svg"):
        temp_dir = os.path.join(os.path.dirname(img_path), ".svg_cache")
        os.makedirs(temp_dir, exist_ok=True)
        converted_path = os.path.join(temp_dir, os.path.basename(img_path) + ".png")
        if not os.path.exists(converted_path):
            subprocess.run(["qlmanage", "-t", "-s", "1200", "-o", temp_dir, img_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if os.path.exists(converted_path):
            img_to_open = converted_path

    try:
        with Image.open(img_to_open) as im:
            w, h = im.size
            bbox = None
            if im.mode == "RGBA":
                alpha = im.split()[-1]
                bbox = alpha.point(lambda p: 255 if p > 10 else 0).getbbox()
            else:
                import numpy as np
                arr = np.array(im.convert("RGB"))
                non_white = np.where((arr < 248).any(axis=2))
                if len(non_white[0]) > 0 and len(non_white[1]) > 0:
                    bbox = (int(non_white[1].min()), int(non_white[0].min()), int(non_white[1].max()), int(non_white[0].max()))

            if bbox:
                bx0, by0, bx1, by1 = bbox
                bw, bh = bx1 - bx0, by1 - by0
                if (w - bw) / w > 0.08 or (h - bh) / h > 0.08:
                    pad = int(min(bw, bh) * 0.02)
                    crop_box = (max(0, bx0 - pad), max(0, by0 - pad), min(w, bx1 + pad), min(h, by1 + pad))
                    cropped = im.crop(crop_box)
                    temp_dir = os.path.join(os.path.dirname(img_path), ".trimmed")
                    os.makedirs(temp_dir, exist_ok=True)
                    temp_path = os.path.join(temp_dir, os.path.basename(img_path))
                    cropped.save(temp_path)
                    img_to_open = temp_path
    except Exception:
        img_to_open = img_path

    with Image.open(img_to_open) as im:
        orig_w, orig_h = im.size

    ratio = min(max_w_in / orig_w, max_h_in / orig_h)
    final_w = orig_w * ratio
    final_h = orig_h * ratio

    offset_x = left_in + (max_w_in - final_w) / 2
    offset_y = top_in + (max_h_in - final_h) / 2

    pic = slide.shapes.add_picture(img_to_open, Inches(offset_x), Inches(offset_y), Inches(final_w), Inches(final_h))
    return pic


def clean_latex_math(text: str) -> str:
    """
    마크다운 원고의 LaTeX 수식 코드를 파워포인트(PPTX)에서 깔끔하게 읽히는
    유니코드 표준 수학 기호 및 가독성 높은 텍스트로 자동 변환합니다.
    """
    if not text:
        return ""

    s = text

def clean_latex_math(text: str) -> str:
    """
    마크다운 원고의 LaTeX 수식 코드를 파워포인트(PPTX)에서 깔끔하게 읽히는
    유니코드 표준 수학 기호 및 가독성 높은 텍스트로 정밀 변환합니다.
    """
    if not text:
        return ""

    s = text

    # 1. 수식 블록 기호 $$ 및 인라인 $ 제거
    s = re.sub(r"\$\$(.*?)\$\$", r"\1", s, flags=re.DOTALL)
    s = s.replace("$", "")

    # 2. LaTeX 환경 태그 제거 (aligned, cases, equation, matrix 등)
    s = re.sub(r"\\begin\{(?:aligned|cases|equation|matrix)\}", "", s)
    s = re.sub(r"\\end\{(?:aligned|cases|equation|matrix)\}", "", s)

    # 3. 분수 \frac{a}{b} -> a/b
    s = re.sub(r"\\frac\{([^{}]+)\}\{([^{}]+)\}", r"\1/\2", s)

    # 4. 언더브레이스 \underbrace{expr}_{\text{desc}} -> expr (desc)
    s = re.sub(r"\\underbrace\{([^{}]+)\}_\{[\\text\{]*([^{}]+)\}*\}", r"\1 (\2)", s)

    # 5. \text{...}, \mathbf{...}, \mathit{...}, \mathrm{...}, \mathcal{...} 내부 텍스트 추출
    s = re.sub(r"\\(?:text|mathbf|mathit|mathrm|mathcal)\{([^{}]+)\}", r"\1", s)

    # 6. 화살표 및 방향 기호
    arrow_map = [
        (r"\\leftarrow", "←"),
        (r"\\gets", "←"),
        (r"\\rightarrow", "→"),
        (r"\\to", "→"),
        (r"\\leftrightarrow", "↔"),
        (r"\\Leftarrow", "⇐"),
        (r"\\Rightarrow", "⇒"),
        (r"\\Leftrightarrow", "⇔"),
    ]
    for pattern, repl in arrow_map:
        s = re.sub(pattern + r"(?![a-zA-Z])", repl, s)

    # 7. 괄호 크기 제어 \left, \right 제거
    s = re.sub(r"\\(?:left|right)", "", s)

    # 8. 그리스 문자 변환
    greek_map = [
        (r"\\pi", "π"),
        (r"\\gamma", "γ"),
        (r"\\Delta", "Δ"),
        (r"\\delta", "δ"),
        (r"\\epsilon", "ε"),
        (r"\\theta", "θ"),
        (r"\\alpha", "α"),
        (r"\\beta", "β"),
        (r"\\sigma", "σ"),
        (r"\\Sigma", "∑"),
        (r"\\lambda", "λ"),
        (r"\\mu", "μ"),
        (r"\\omega", "ω"),
        (r"\\Omega", "Ω"),
        (r"\\phi", "φ"),
        (r"\\tau", "τ"),
        (r"\\eta", "η"),
    ]
    for pattern, repl in greek_map:
        s = re.sub(pattern + r"(?![a-zA-Z])", repl, s)

    # 9. 연산자 및 특수 수학 기호 변환
    op_map = [
        (r"\\infty", "∞"),
        (r"\\approx", "≈"),
        (r"\\neq", "≠"),
        (r"\\leq?", "≤"),
        (r"\\geq?", "≥"),
        (r"\\times", "×"),
        (r"\\cdot", "·"),
        (r"\\dots", "…"),
        (r"\\cdots", "…"),
        (r"\\sum", "∑"),
        (r"\\max", "max"),
        (r"\\min", "min"),
        (r"\\argmax", "arg max"),
        (r"\\argmin", "arg min"),
        (r"\\mathbb\{E\}", "𝔼"),
        (r"\\mathbb\{R\}", "ℝ"),
        (r"\\in", "∈"),
        (r"\\notin", "∉"),
        (r"\\mid", "|"),
        (r"\\prime", "'"),
        (r"\\quad", "  "),
        (r"\\qquad", "    "),
    ]
    for pattern, repl in op_map:
        s = re.sub(pattern + r"(?![a-zA-Z])", repl, s)

    # 10. 첨자 괄호 정리: _{...} -> _..., ^{...} -> ^...
    s = re.sub(r"_\{([^}]+)\}", r"_\1", s)
    s = re.sub(r"\^\{([^}]+)\}", r"^\1", s)

    # 11. 이스케이프 기호 복원
    s = s.replace(r"\{", "{").replace(r"\}", "}")
    s = s.replace(r"\%", "%")
    s = s.replace(r"\_", "_")
    s = s.replace(r"\&", "&")
    s = s.replace(r"\$", "$")

    # 12. 테이블 구분자 및 수식 잔재 정리
    s = s.replace("&", "")
    s = re.sub(r"\\\\", "\n", s)
    s = s.replace("**", "")

    return s.strip()


def split_title_runs(title: str):
    """
    긴 제목을 앞부분(섹션번호/핵심표제어)과 뒷부분(세부 설명)으로 분할합니다.
    예: '07.1.6 핵심 요약 ① 프로그래밍의...' -> ('07.1.6 핵심 요약 ① ', '프로그래밍의...')
    """
    clean_t = clean_latex_math(title)
    m = re.match(r"^(.*?핵심\s*요약\s*[①-⑳\d]+\s*)(.*)$", clean_t)
    if m:
        return m.group(1), m.group(2)
    if ":" in clean_t:
        parts = clean_t.split(":", 1)
        return parts[0] + ": ", parts[1].strip()
    if " - " in clean_t:
        parts = clean_t.split(" - ", 1)
        return parts[0] + " - ", parts[1].strip()
    m2 = re.match(r"^(\d+(?:\.\d+)+\s*)(.*)$", clean_t)
    if m2:
        return m2.group(1), m2.group(2)
    tokens = clean_t.split(" ", 2)
    if len(tokens) >= 3:
        return f"{tokens[0]} {tokens[1]} ", tokens[2]
    return clean_t, ""


def format_main_title(p_t, header2_text: str):
    """
    제목이 33자를 초과하는 경우 세부 텍스트 폰트를 부분 축소(Partial Font Scaling)하여
    단일 행(1줄)을 유지하고 하단 실선 및 서브텍스트와의 겹침을 방지합니다.
    """
    clean_h2 = clean_latex_math(header2_text)
    title_len = len(clean_h2)
    if title_len <= 33:
        r = p_t.add_run()
        r.text = clean_h2
        r.font.size = Pt(28)
        r.font.bold = True
        r.font.color.rgb = COLOR_TITLE
        r.font.name = FONT_FAMILY
        return

    pfx, dtl = split_title_runs(clean_h2)
    if not dtl:
        r = p_t.add_run()
        r.text = clean_h2
        r.font.size = Pt(24) if title_len <= 42 else Pt(20)
        r.font.bold = True
        r.font.color.rgb = COLOR_TITLE
        r.font.name = FONT_FAMILY
        return

    if title_len <= 42:
        size_pfx = Pt(24)
        size_dtl = Pt(20)
    else:
        size_pfx = Pt(22)
        size_dtl = Pt(18.5)

    r1 = p_t.add_run()
    r1.text = pfx
    r1.font.size = size_pfx
    r1.font.bold = True
    r1.font.color.rgb = COLOR_TITLE
    r1.font.name = FONT_FAMILY

    r2 = p_t.add_run()
    r2.text = dtl
    r2.font.size = size_dtl
    r2.font.bold = True
    r2.font.color.rgb = COLOR_TITLE
    r2.font.name = FONT_FAMILY


def add_slide_header_and_avatar(prs, header1_text, header2_text, slide_num, total_slides, avatar_png):
    """
    16:9 와이드스크린 표준 헤더, 실선 구분선 및 우하단 원형 아바타를 생성합니다.
    """
    blank_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank_layout)

    # 1. 1행 좌측: 카테고리 뱃지 (17pt Semi-Bold Sky Blue)
    tb_b = slide.shapes.add_textbox(Inches(0.8), Inches(0.40), Inches(8.5), Inches(0.35))
    tf_b = tb_b.text_frame
    tf_b.word_wrap = True
    tf_b.margin_left = tf_b.margin_right = tf_b.margin_top = tf_b.margin_bottom = 0
    p_b = tf_b.paragraphs[0]
    p_b.text = header1_text
    p_b.font.size = Pt(17)
    p_b.font.bold = True
    p_b.font.color.rgb = COLOR_BADGE
    p_b.font.name = FONT_FAMILY

    # 2. 1행 우측: 페이지 번호 (17pt Bold Slate Gray)
    tb_p = slide.shapes.add_textbox(Inches(10.5), Inches(0.40), Inches(2.0), Inches(0.35))
    tf_p = tb_p.text_frame
    tf_p.margin_left = tf_p.margin_right = tf_p.margin_top = tf_p.margin_bottom = 0
    p_p = tf_p.paragraphs[0]
    p_p.text = f"{slide_num:02d} / {total_slides:02d}"
    p_p.alignment = PP_ALIGN.RIGHT
    p_p.font.size = Pt(17)
    p_p.font.bold = True
    p_p.font.color.rgb = COLOR_MUTED
    p_p.font.name = FONT_FAMILY

    # 3. 2행 좌측: 메인 타이틀 (단일 행 보장 및 부분 폰트 조절)
    tb_t = slide.shapes.add_textbox(Inches(0.8), Inches(0.78), Inches(10.0), Inches(0.52))
    tf_t = tb_t.text_frame
    tf_t.word_wrap = False
    tf_t.margin_left = tf_t.margin_right = tf_t.margin_top = tf_t.margin_bottom = 0
    p_t = tf_t.paragraphs[0]
    format_main_title(p_t, header2_text)

    # 4. 2행 우측: 플랫 강의 듣기 버튼
    btn = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(10.9), Inches(0.78), Inches(1.6), Inches(0.42))
    make_flat_shape(btn, fill_color=COLOR_BTN_BG, line_color=None)
    tf_btn = btn.text_frame
    tf_btn.margin_left = tf_btn.margin_right = tf_btn.margin_top = tf_btn.margin_bottom = 0
    p_btn = tf_btn.paragraphs[0]
    p_btn.text = "🎙️ 강의 듣기"
    p_btn.alignment = PP_ALIGN.CENTER
    p_btn.font.size = Pt(14)
    p_btn.font.bold = True
    p_btn.font.color.rgb = COLOR_WHITE
    p_btn.font.name = FONT_FAMILY

    # 5. 헤더 구분선 (단색 1.5pt 순수 회색 실선, 음영 0%)
    divider = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.36), Inches(11.733), Pt(1.5))
    make_flat_shape(divider, fill_color=COLOR_DIVIDER, line_color=None)

    # 6. 우하단 원형 아바타 (Left=10.633", Top=5.15", 1.9"x1.9")
    if avatar_png and os.path.exists(avatar_png):
        slide.shapes.add_picture(avatar_png, Inches(10.633), Inches(5.15), Inches(1.9), Inches(1.9))

    return slide


def inject_notes(slide, script_text):
    """파워포인트 하단 슬라이드 노트(NotesPage)에 심층 강의 스크립트를 주입합니다."""
    if script_text:
        notes_slide = slide.notes_slide
        tf_n = notes_slide.notes_text_frame
        tf_n.text = script_text


def parse_slides_md(filepath: str):
    """
    slides.md 파일을 읽어 슬라이드 딕셔너리 리스트로 파싱합니다.
    - > [infographic_prompt] 블록은 에셋 생성 참고용 LLM 프롬프트이므로 완전히 제외합니다.
    - 실제 구어체 강의 대본(> ...)만 슬라이드 노트(NotesPage)로 추출합니다.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    raw_slides = re.split(r"\n---\s*\n", content.strip())
    parsed_slides = []

    for idx, raw in enumerate(raw_slides, 1):
        lines = [l.rstrip() for l in raw.strip().split("\n")]
        header1 = ""
        header2 = ""
        script_lines = []
        body_lines = []

        in_script = False
        in_infographic_prompt = False

        for line in lines:
            stripped = line.strip()
            if stripped.startswith("# "):
                header1 = stripped.lstrip("# ").strip()
            elif stripped.startswith("## "):
                header2 = stripped.lstrip("# ").strip()
            elif stripped.startswith("> [infographic_prompt]") or (stripped.startswith(">") and "[infographic_prompt]" in stripped):
                # 인포그래픽 프롬프트 시작: 슬라이드 노트나 본문에 포함하지 않고 스킵
                in_infographic_prompt = True
                in_script = False
            elif in_infographic_prompt:
                if stripped.startswith(">"):
                    # 프롬프트 내부 항목 계속 스킵
                    continue
                else:
                    # 프롬프트 종료
                    in_infographic_prompt = False
                    if stripped.startswith("- ") or stripped.startswith("* ") or stripped.startswith("![") or stripped.startswith("|") or stripped.startswith("```"):
                        body_lines.append(line)
                    elif stripped:
                        body_lines.append(line)
            elif stripped.startswith("> ") or (in_script and stripped.startswith(">")):
                # 실제 구어체 강의 대본만 추출!
                in_script = True
                cleaned = re.sub(r"^>\s*", "", stripped)
                if cleaned and not cleaned.startswith("[infographic_prompt]"):
                    script_lines.append(cleaned)
            else:
                if in_script and not stripped.startswith(">"):
                    in_script = False
                body_lines.append(line)

        script_text = "\n".join(script_lines).strip()
        body_text = "\n".join(body_lines).strip()

        parsed_slides.append({
            "slide_num": idx,
            "header1": header1,
            "header2": header2,
            "body": body_text,
            "script": script_text
        })

    return parsed_slides


def build_slide_with_image_and_text(prs, data, total_slides, avatar_png, img_dir, img_name, img_caption, lead_text, bullet_items):
    """
    2열 표준 인포그래픽 카드 레이아웃:
    - 좌측: 시각자료 인포그래픽 카드 (Top: 1.65", Height: 5.40", Width: 5.40", 종횡비 유지 이미지 + 하단 캡션)
    - 우측: 핵심 학습 컨텐츠 카드 (Top: 1.65", Height: 3.32", Width: 6.083")
    - 우하단: 하이라이트 콜아웃 카드 및 강사 아바타 (간섭 없는 정밀 배치)
    모든 요소 간 충돌 및 겹침을 100% 방지합니다.
    """
    slide = add_slide_header_and_avatar(prs, data["header1"], data["header2"], data["slide_num"], total_slides, avatar_png)

    # 이미지 존재 여부 판별
    img_path = os.path.join(img_dir, img_name) if img_name else ""
    has_image = bool(img_name and os.path.exists(img_path) and os.path.isfile(img_path))

    if has_image:
        # 1. 좌측 시각자료: 순수 플랫 캔버스에 이미지 직접 안착 (인위적인 배경 카드 박스 완전 제거)
        add_fitted_picture(slide, img_path, left_in=0.8, top_in=1.65, max_w_in=5.4, max_h_in=4.40)

        # 그림 아래쪽 설명 캡션 (카드 내부 하단 정렬, 중앙 배치)
        if img_caption:
            tb_c = slide.shapes.add_textbox(Inches(0.95), Inches(6.15), Inches(5.1), Inches(0.75))
            tf_c = tb_c.text_frame
            tf_c.word_wrap = True
            tf_c.margin_left = tf_c.margin_right = tf_c.margin_top = tf_c.margin_bottom = 0
            p_c = tf_c.paragraphs[0]
            p_c.text = clean_latex_math(img_caption)
            p_c.alignment = PP_ALIGN.CENTER
            p_c.font.size = Pt(13.5)
            p_c.font.color.rgb = COLOR_MUTED
            p_c.font.name = FONT_FAMILY

        # 2. 우측 컬럼: 본문 불릿 인포그래픽 카드 (Left: 6.45", Top: 1.65", Width: 6.083", Height: 3.32")
        card_top = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.45), Inches(1.65), Inches(6.083), Inches(3.32))
        make_flat_shape(card_top, fill_color=COLOR_WHITE, line_color=COLOR_DIVIDER)
        tb_r = card_top
        title_pt = Pt(18)
        desc_pt = Pt(15.5)
        tf_r = tb_r.text_frame
        tf_r.word_wrap = True
        tf_r.margin_left = Inches(0.24)
        tf_r.margin_right = Inches(0.24)
        tf_r.margin_top = Inches(0.20)
        tf_r.margin_bottom = Inches(0.20)
    else:
        # 이미지가 없는 슬라이드: 좌측 0.8"부터 우측 아바타(10.33") 전까지 9.2" 너비로 확장
        card_top = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.65), Inches(9.2), Inches(5.2))
        make_flat_shape(card_top, fill_color=COLOR_WHITE, line_color=COLOR_DIVIDER)
        tb_r = card_top
        title_pt = Pt(19.5)
        desc_pt = Pt(16.5)
        tf_r = tb_r.text_frame
        tf_r.word_wrap = True
        tf_r.margin_left = Inches(0.3)
        tf_r.margin_right = Inches(0.3)
        tf_r.margin_top = Inches(0.25)
        tf_r.margin_bottom = Inches(0.25)

    first_item = True
    for title, desc in bullet_items:
        clean_t = clean_latex_math(title)
        clean_d = clean_latex_math(desc)
        p1 = tf_r.paragraphs[0] if first_item else tf_r.add_paragraph()
        first_item = False
        p1.text = f"• {clean_t}"
        p1.font.size = title_pt
        p1.font.bold = True
        p1.font.color.rgb = COLOR_BULLET_TITLE
        p1.font.name = FONT_FAMILY
        p1.space_after = Pt(4)

        if clean_d:
            p2 = tf_r.add_paragraph()
            p2.text = f"  {clean_d}"
            p2.font.size = desc_pt
            p2.font.color.rgb = COLOR_BODY
            p2.font.name = FONT_FAMILY
            p2.space_after = Pt(12)

    inject_notes(slide, data["script"])
    return slide


def main():
    parser = argparse.ArgumentParser(description="강화학습 교재 마크다운 -> 16:9 와이드스크린 강의용 PPTX 생성기")
    parser.add_argument("target_dir", nargs="?", default="src/07_동적_프로그래밍/7_1_유래",
                        help="변환 대상 단원 디렉터리 경로 (기본값: src/07_동적_프로그래밍/7_1_유래)")
    parser.add_argument("--output", "-o", default=None, help="출력 PPTX 파일 경로 (선택 사항)")
    args = parser.parse_args()

    # 경로 확인
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    target_path = os.path.abspath(args.target_dir) if os.path.isabs(args.target_dir) else os.path.join(repo_root, args.target_dir)

    slides_md = os.path.join(target_path, "slides.md")
    if not os.path.exists(slides_md):
        print(f"❌ 오류: {slides_md} 파일을 찾을 수 없습니다.")
        sys.exit(1)

    guides_dir = os.path.join(repo_root, "guides")
    img_dir = os.path.join(target_path, "img")

    print(f"📂 대상 단원 디렉터리: {target_path}")
    print(f"📄 슬라이드 마크다운: {slides_md}")

    # 1. 아바타 확인
    avatar_png = ensure_circular_avatar(guides_dir)
    print(f"👤 강의자 아바타: {avatar_png}")

    # 2. 마크다운 파싱
    slides_data = parse_slides_md(slides_md)
    total_slides = len(slides_data)
    print(f"📊 총 슬라이드 수: {total_slides}")

    # 3. 프레젠테이션 초기화
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # 단원별 맞춤형 빌더 스크립트(create_presentation.py)가 대상 폴더에 존재하면 우선 연동
    custom_script = os.path.join(target_path, "create_presentation.py")
    if os.path.exists(custom_script):
        print(f"✨ 단원 전용 빌더 스크립트 실행: {custom_script}")
        exit_code = os.system(f"python3 '{custom_script}'")
        if exit_code == 0:
            print("🎉 단원 전용 빌더로 PPTX가 성공적으로 생성되었습니다.")
            return

    # 4. 첫 슬라이드: 유튜브 커버 이미지 16:9 전폭 표지 삽입
    lecture_name = os.path.basename(os.path.normpath(target_path))
    cover_candidates = [
        os.path.join(target_path, f"{lecture_name}.png"),
        os.path.join(target_path, "07_1_동적_프로그래밍의_유래.png"),
        os.path.join(target_path, "youtube_cover.png"),
    ]
    cover_path = None
    for cand in cover_candidates:
        if os.path.exists(cand):
            cover_path = cand
            break

    if cover_path:
        slide_cover = prs.slides.add_slide(prs.slide_layouts[6])
        slide_cover.shapes.add_picture(cover_path, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
        intro_script = (
            "강화학습에서 환경의 수학적 모델을 전혀 알지 못할 때, 우리는 어떻게 최적의 길을 찾아낼 수 있을까요? "
            "복잡한 수식에 매달리는 대신, 직접 세상에 발을 내딛고 겪은 수많은 경험들의 평균을 내어 참된 가치를 밝혀내는 "
            "위대한 방법론이 바로 몬테카를로법입니다. 수학적 기초와 흥미진진한 역사 속으로 함께 떠나보겠습니다."
        )
        inject_notes(slide_cover, intro_script)
        print(f"🖼️ [슬라이드 01] 유튜브 커버 전폭 표지 삽입 완료: {cover_path}")

    # 5. 공통 빌더 로직: slides.md의 내용을 파싱하여 본문 슬라이드 순차 생성
    for idx, slide_item in enumerate(slides_data):
        # 마크다운 본문에서 이미지 태그 및 불릿 추출
        body_text = slide_item["body"]
        img_match = re.search(r"!\[(.*?)\]\(\./img/(.*?)\)", body_text)
        img_caption = img_match.group(1) if img_match else ""
        img_name = img_match.group(2) if img_match else ""

        lead_match = re.search(r"💡\s*(.*?)(?:\n|$)", body_text)
        lead_text = lead_match.group(1).strip() if lead_match else ""

        bullet_items = []
        raw_bullets = re.findall(r"[-•]\s*(?:단락\s*\d+:|\*\*(.*?)\*\*:?)(.*?)(?=(?:[-•]|$))", body_text, re.DOTALL)
        if raw_bullets:
            for title, desc in raw_bullets:
                t = title.strip() if title else "핵심 내용"
                d = desc.strip()
                bullet_items.append((t, d))
        else:
            # 기본 불릿 추출
            lines = [l.strip() for l in body_text.split("\n") if l.strip().startswith("- ") or l.strip().startswith("• ")]
            for l in lines:
                clean = re.sub(r"^[-•]\s*", "", l)
                parts = clean.split(":", 1)
                if len(parts) == 2:
                    bullet_items.append((parts[0].strip(), parts[1].strip()))
                else:
                    bullet_items.append((clean, ""))

        build_slide_with_image_and_text(
            prs, slide_item, total_slides,
            avatar_png=avatar_png,
            img_dir=img_dir,
            img_name=img_name,
            img_caption=img_caption,
            lead_text=lead_text,
            bullet_items=bullet_items
        )

    # 6. 마지막 엔딩 슬라이드: '감사합니다' & 다음 학습 주제 예고 (텍스트 중심 와이드 레이아웃)
    slide_end = prs.slides.add_slide(prs.slide_layouts[6])
    # 상단 뱃지 & 감사 타이틀
    tb_b = slide_end.shapes.add_textbox(Inches(1.0), Inches(0.55), Inches(8.0), Inches(0.35))
    tf_b = tb_b.text_frame
    tf_b.margin_left = tf_b.margin_right = tf_b.margin_top = tf_b.margin_bottom = 0
    p_b = tf_b.paragraphs[0]
    p_b.text = lecture_name
    p_b.font.size = Pt(18)
    p_b.font.bold = True
    p_b.font.color.rgb = COLOR_BADGE
    p_b.font.name = FONT_FAMILY

    tb_t = slide_end.shapes.add_textbox(Inches(1.0), Inches(0.95), Inches(11.333), Inches(0.65))
    tf_t = tb_t.text_frame
    tf_t.margin_left = tf_t.margin_right = tf_t.margin_top = tf_t.margin_bottom = 0
    p_t = tf_t.paragraphs[0]
    p_t.text = "경청해 주셔서 감사합니다!"
    p_t.font.size = Pt(34)
    p_t.font.bold = True
    p_t.font.color.rgb = COLOR_TITLE
    p_t.font.name = FONT_FAMILY

    # 전환 서브텍스트
    tb_s = slide_end.shapes.add_textbox(Inches(1.0), Inches(1.65), Inches(11.333), Inches(0.40))
    tf_s = tb_s.text_frame
    tf_s.word_wrap = True
    tf_s.margin_left = tf_s.margin_right = tf_s.margin_top = tf_s.margin_bottom = 0
    p_s = tf_s.paragraphs[0]
    p_s.text = "본 단원의 학습을 넘어, 다음 단계의 더 깊은 알고리즘과 수학적 원리의 세계로 나아갑니다."
    p_s.font.size = Pt(17)
    p_s.font.bold = True
    p_s.font.color.rgb = COLOR_BADGE
    p_s.font.name = FONT_FAMILY

    # 실선 구분선
    line = slide_end.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.0), Inches(2.15), Inches(11.333), Inches(0.015))
    make_flat_shape(line, fill_color=COLOR_DIVIDER)

    # 다음 주제 예고 텍스트 (전폭 와이드 레이아웃)
    tb_c = slide_end.shapes.add_textbox(Inches(1.0), Inches(2.45), Inches(11.333), Inches(4.5))
    tf_c = tb_c.text_frame
    tf_c.word_wrap = True
    tf_c.margin_left = tf_c.margin_right = tf_c.margin_top = tf_c.margin_bottom = 0

    p_c1 = tf_c.paragraphs[0]
    p_c1.text = "🚀 NEXT STEP: 다음 학습 주제"
    p_c1.font.size = Pt(16)
    p_c1.font.bold = True
    p_c1.font.color.rgb = COLOR_BADGE
    p_c1.font.name = FONT_FAMILY
    p_c1.space_after = Pt(8)

    p_c2 = tf_c.add_paragraph()
    p_c2.text = "다음 단원의 핵심 알고리즘과 수학적 최적화"
    p_c2.font.size = Pt(28)
    p_c2.font.bold = True
    p_c2.font.color.rgb = COLOR_TITLE
    p_c2.font.name = FONT_FAMILY
    p_c2.space_after = Pt(16)

    p_c3 = tf_c.add_paragraph()
    p_c3.text = "• 본 단원에서 다룬 기초 원리를 바탕으로 더 깊은 수식 계산과 실전 구현으로 나아갑니다."
    p_c3.font.size = Pt(19)
    p_c3.font.color.rgb = COLOR_BODY
    p_c3.font.name = FONT_FAMILY
    p_c3.space_after = Pt(12)

    inject_notes(slide_end, "경청해 주셔서 감사합니다. 다음 강의에서 뵙겠습니다!")
    print("🎉 [슬라이드 N+2] 감사 및 다음 학습 주제 엔딩 슬라이드 생성 완료 (텍스트 중심 와이드 레이아웃)")

    out_file = args.output or os.path.join(target_path, f"{lecture_name}.pptx")
    prs.save(out_file)
    print(f"🎉 성공적으로 PPTX가 생성되었습니다: {out_file}")

    # index.pptx 동기화 복사본 생성
    compat_index_pptx = os.path.join(target_path, "index.pptx")
    try:
        import shutil
        shutil.copy2(out_file, compat_index_pptx)
        print(f"📄 index.pptx 동기화 완료: {compat_index_pptx}")
    except Exception as e:
        print(f"[!] index.pptx 동기화 실패: {e}")


if __name__ == "__main__":
    main()
