#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
마크다운(index.md) 기반 16:9 와이드스크린 100% 편집 가능한 네이티브 텍스트, 
외부 JSON(lecture_scripts.json) 기반 교수님 심층 실전 강의 대본(슬라이드 노트),
텍스트 중심의 명확한 강의 정보 전달, 50대 교수님 AI TTS 오디오 삽입 PPTX 자동 생성기 (v10.0)

핵심 슬라이드 구성 및 디자인 규칙:
  1. 기본 글꼴: 모든 슬라이드 텍스트의 기본 글꼴은 'Noto Sans KR'로 통일 (DrawingML East Asian ea 태그 포함)
  2. 슬라이드 좌측 상단 (1행): 강의 챕터 대분류명 (16pt, Sky Blue #0284C7, Bold, Noto Sans KR)
  3. 슬라이드 좌측 상단 (2행): 해당 슬라이드 핵심 설명 주제/소단원 제목 (25~32pt, Dark Navy #0F172A, Bold, Noto Sans KR)
  4. 슬라이드 우측 상단: 슬라이드 페이지 번호 (예: 01 / 66, 13.5pt, Slate Gray #64748B, Bold, Noto Sans KR)
  5. 교수님 강의 오디오 버튼: 슬라이드 번호 하단에 단일 플레이 버튼 ([🎙️ 강의 듣기]) 배치
  6. 구분선: 32pt 제목 하단에 음영/그라데이션 없는 순수 1.5pt 회색 실선 (#E2E8F0) 배치
  7. 슬라이드 우측 하단: 실제 OBS/웹캠 카메라 원형에 일치시킨 30% 회색 아바타 영역 (Left: 790pt, Top: 370pt, 160x160pt, 외곽선 없음, 👤 아바타 영역)
  8. 대화 + 이미지 슬라이드 레이아웃 (2-Column):
     - 좌측 영역: 일러스트레이션 이미지 + 하단 그림 캡션 (너비 440pt)
     - 우측 영역: 대화 음성 플레이어 바 + 캐릭터(도로시, 지니, 토토) 대화 카드 (너비 420pt)
     - 대화 텍스트 색상 분리:
       * 👧 도로시 (Dorothy): 코랄 로즈 (#E11D48)
       * 🐱 지니 (Jiny): 로열 블루 (#1D4ED8)
       * 🐶 토토 (Toto): 에메랄드 그린 (#059669)
     - [재생] 버튼 위치에 파워포인트 표준 미디어(msoMedia) 오디오 파일 자동 임베딩
  9. 일반 설명 슬라이드 레이아웃 (텍스트 중심 와이드 레이아웃):
     - 카드형 SVG 생성을 배제하고 슬라이드 전폭(Left: 40pt, Width: 730pt, Height: 410pt)을 활용하여 강의 정보 전달
     - 100% 편집 가능한 네이티브 파워포인트 텍스트 상자 구성
     - 텍스트 서식: 13~16.5pt 본문(반응형), 18~20pt 중앙정렬 수식, 12.5~15.5pt 콜아웃, 12.5~16pt 리스트
     - 우하단 아바타 영역(Left: 790pt)과 20pt 안전 간격 유지로 겹침 원천 차단
  10. 강의 스크립트 및 슬라이드 노트:
     - 외부 JSON 파일 (lecture_scripts.json)에서 슬라이드별 대본 로드
     - 슬라이드 내용보다 최소 15% 이상 길고 상세한 50대 남성 명교수님 심층 실전 강의 대본을 슬라이드 노트에 삽입
  11. 출력 파일명:
     - <강의챕터폴더명>.pptx (예: 6_4_행동_가치_함수_Q_함수와_벨만_방정식.pptx) 우선 생성
     - index.pptx 호환 복사본 자동 동기화
"""

import sys
import os
import re
import io
import json
import shutil
import argparse
import asyncio
from pathlib import Path

try:
    import pptx
    from pptx import Presentation
    from pptx.util import Pt, Inches
    from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
    from pptx.dml.color import RGBColor
    from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
    from pptx.oxml import parse_xml
    from pptx.oxml.ns import nsdecls
except ImportError:
    print("[오류] python-pptx 라이브러리가 필요합니다. 'pip install python-pptx'를 실행하세요.")
    sys.exit(1)

try:
    from PIL import Image
except ImportError:
    print("[오류] Pillow 라이브러리가 필요합니다. 'pip install pillow'를 실행하세요.")
    sys.exit(1)

# 외부 생성기 모듈 불러오기
try:
    from scratch.generate_lecture_assets import PROF_SCRIPTS, generate_svg_diagram
except ImportError:
    PROF_SCRIPTS = {}
    def generate_svg_diagram(s_num, topic, svg_p, png_p): pass

# 16:9 와이드스크린 슬라이드 규격
SLIDE_W = 960.0
SLIDE_H = 540.0

# 기본 표준 글꼴
FONT_FAMILY = "Noto Sans KR"


def set_font_run(run, name=FONT_FAMILY, size=None, bold=None, color=None, italic=None):
    """Run에 글꼴(Noto Sans KR 영문/한글 typeface) 및 서식을 지정합니다."""
    if name:
        run.font.name = name
        try:
            rPr = run._r.get_or_add_rPr()
            ea = rPr.find('{http://schemas.openxmlformats.org/drawingml/2006/main}ea')
            if ea is None:
                rPr.append(parse_xml(f'<a:ea {nsdecls("a")} typeface="{name}"/>'))
            else:
                ea.set('typeface', name)
        except Exception:
            pass
    if size is not None:
        run.font.size = Pt(size)
    if bold is not None:
        run.font.bold = bold
    if italic is not None:
        run.font.italic = italic
    if color is not None:
        run.font.color.rgb = color


def set_font_paragraph(p, name=FONT_FAMILY, size=None, bold=None, color=None):
    """Paragraph 기본 서식에 글꼴(Noto Sans KR)을 지정합니다."""
    if name:
        p.font.name = name
        try:
            pPr = p._p.get_or_add_pPr()
            defRPr = pPr.get_or_add_defRPr()
            ea = defRPr.find('{http://schemas.openxmlformats.org/drawingml/2006/main}ea')
            if ea is None:
                defRPr.append(parse_xml(f'<a:ea {nsdecls("a")} typeface="{name}"/>'))
            else:
                ea.set('typeface', name)
        except Exception:
            pass
    if size is not None:
        p.font.size = Pt(size)
    if bold is not None:
        p.font.bold = bold
    if color is not None:
        p.font.color.rgb = color


def extract_balanced_braces(s: str, start_idx: int):
    """주어진 시작 인덱스의 '{'에 대응하는 닫는 '}'의 인덱스와 내부 내용을 반환합니다."""
    if start_idx >= len(s) or s[start_idx] != '{':
        return None, None
    depth = 0
    for i in range(start_idx, len(s)):
        if s[i] == '{':
            depth += 1
        elif s[i] == '}':
            depth -= 1
            if depth == 0:
                return i, s[start_idx + 1:i]
    return None, None


def replace_balanced_command(text: str, cmd: str, repl_func) -> str:
    """\\frac{a}{b} 등 중첩 중괄호를 가진 LaTeX 명령어를 안전하게 변환합니다."""
    res = []
    i = 0
    cmd_len = len(cmd)
    while i < len(text):
        if text[i:i+cmd_len] == cmd:
            next_idx = i + cmd_len
            while next_idx < len(text) and text[next_idx] in ' \t':
                next_idx += 1
            if next_idx < len(text) and text[next_idx] == '{':
                end1, arg1 = extract_balanced_braces(text, next_idx)
                if end1 is not None:
                    next_idx2 = end1 + 1
                    while next_idx2 < len(text) and text[next_idx2] in ' \t':
                        next_idx2 += 1
                    if next_idx2 < len(text) and text[next_idx2] == '{':
                        end2, arg2 = extract_balanced_braces(text, next_idx2)
                        if end2 is not None:
                            res.append(repl_func(arg1, arg2))
                            i = end2 + 1
                            continue
        res.append(text[i])
        i += 1
    return "".join(res)


import html

def clean_inline_html(text: str) -> str:
    """HTML 태그 및 HTML 엔티티를 가독성 높은 유니코드 기호로 변환합니다."""
    # 1. 최적 별표 첨자 (*, &ast;) 우선 변환: v*, q*, π*, μ*
    text = re.sub(r'<sub>\s*(?:&ast;|\*|\\ast)\s*</sub>', '*', text, flags=re.IGNORECASE)
    
    # 2. 일반 sub / sup 태그 변환
    text = re.sub(r'<sub>(.*?)</sub>', r'_\1', text, flags=re.IGNORECASE)
    text = re.sub(r'<sup>(.*?)</sup>', r'^\1', text, flags=re.IGNORECASE)
    text = re.sub(r'<[^>]+>', '', text)
    
    # 3. HTML 엔티티 변환
    entity_map = {
        '&pi;': 'π', '&ast;': '*', '&gamma;': 'γ', '&sum;': '∑',
        '&mu;': 'μ', '&alpha;': 'α', '&beta;': 'β', '&theta;': 'θ',
        '&lambda;': 'λ', '&sigma;': 'σ', '&delta;': 'δ', '&Delta;': 'Δ',
        '&le;': '≤', '&ge;': '≥', '&times;': '×', '&divide;': '÷',
        '&rarr;': '→', '&larr;': '←', '&middot;': '·', '&infin;': '∞',
        '&forall;': '∀', '&exist;': '∃', '&isin;': '∈', '&notin;': '∉',
        '&ne;': '≠', '&approx;': '≈', '&amp;': '&', '&lt;': '<', '&gt;': '>'
    }
    for ent, val in entity_map.items():
        text = text.replace(ent, val)
    text = html.unescape(text)
    
    # _* 기호를 깔끔한 * 기호로 정규화 (예: π_* -> π*, v_* -> v*, q_* -> q*)
    text = re.sub(r'([vVqQπμβa-zA-Z])_\*', r'\1*', text)
    
    return text


def clean_math_text(math_str: str) -> str:
    """LaTeX 수식 기호를 가독성 높은 유니코드 수식 텍스트로 변환합니다."""
    s = clean_inline_html(math_str.strip())
    s = re.sub(r'^\${1,2}', '', s)
    s = re.sub(r'\${1,2}$', '', s)
    s = s.strip()

    # LaTeX 환경 제거
    s = re.sub(r'\\begin\{(?:cases|matrix|bmatrix|pmatrix)\}', '{ ', s)
    s = re.sub(r'\\end\{(?:cases|matrix|bmatrix|pmatrix)\}', ' }', s)
    s = re.sub(r'\\begin\{(?:align\*?|aligned|equation\*?|gather\*?|split)\}', '', s)
    s = re.sub(r'\\end\{(?:align\*?|aligned|equation\*?|gather\*?|split)\}', '', s)
    s = re.sub(r'\\operatorname\{argmax\}', 'argmax', s)
    s = re.sub(r'\\operatorname\{argmin\}', 'argmin', s)
    s = re.sub(r'\\operatorname\{([^}]+)\}', r'\1', s)
    s = re.sub(r'\\qquad\s*', '   ', s)
    s = re.sub(r'\\quad\s*', '  ', s)
    s = re.sub(r'\\tag\{.*?\}', '', s)

    # 괄호 및 바 정리
    s = re.sub(r'\\left\s*\\\{', '{', s)
    s = re.sub(r'\\right\s*\\\}', '}', s)
    s = re.sub(r'\\left\s*\[', '[', s)
    s = re.sub(r'\\right\s*\]', ']', s)
    s = re.sub(r'\\left\s*\(', '(', s)
    s = re.sub(r'\\right\s*\)', ')', s)
    s = re.sub(r'\\left\s*\.', '', s)
    s = re.sub(r'\\right\s*\.', '', s)
    s = re.sub(r'\\left[\[\(\{\|\.]', '', s)
    s = re.sub(r'\\right[\]\)\}\|\.]', '', s)
    s = re.sub(r'\\mathbf\{([^}]+)\}', r'\1', s)
    s = re.sub(r'\\mathrm\{([^}]+)\}', r'\1', s)
    s = re.sub(r'\\text\{([^}]+)\}', r'\1', s)

    # 조건부 바 및 연산자
    s = re.sub(r'\\mid\b', ' | ', s)
    s = re.sub(r'\\vert\b', ' | ', s)
    s = re.sub(r'\\\|', ' | ', s)

    # 분수 변환
    s = replace_balanced_command(s, r'\frac', lambda num, den: f"({num.strip()}/{den.strip()})")
    s = replace_balanced_command(s, r'\dfrac', lambda num, den: f"({num.strip()}/{den.strip()})")

    # max 및 argmax
    s = re.sub(r'\\max(?![a-zA-Z])', 'max', s)
    s = re.sub(r'\\arg\s*\\max(?![a-zA-Z])', 'argmax', s)
    s = re.sub(r'\\min(?![a-zA-Z])', 'min', s)

    # 시그마 및 그리스 문자 (단어 경계 없이 _ 앞에서도 매칭)
    s = re.sub(r'\\Sigma(?![a-zA-Z])', '∑', s)
    s = re.sub(r'\\sum(?![a-zA-Z])', '∑', s)
    
    greek_map = {
        r'\pi': 'π', r'\gamma': 'γ', r'\alpha': 'α', r'\beta': 'β',
        r'\theta': 'θ', r'\lambda': 'λ', r'\mu': 'μ', r'\sigma': 'σ',
        r'\epsilon': 'ε', r'\delta': 'δ', r'\Delta': 'Δ',
        r'\prod': '∏', r'\infty': '∞',
        r'\leq': '≤', r'\geq': '≥', r'\neq': '≠', r'\approx': '≈',
        r'\cdot': '·', r'\times': '×', r'\in': '∈', r'\notin': '∉',
        r'\rightarrow': '→', r'\to': '→', r'\leftarrow': '←',
        r'\mathbb{E}': 'E', r'\mathbb{P}': 'P', r'\mathbb{R}': 'R',
    }
    for k, v in greek_map.items():
        s = re.sub(re.escape(k) + r'(?![a-zA-Z])', v, s)

    # 첨자 처리
    s = re.sub(r'_\{([^}]+)\}', r'_\1', s)
    s = re.sub(r'\^\{([^}]+)\}', r'^\1', s)
    s = re.sub(r'([vVqQπμβa-zA-Z])_\*', r'\1*', s)

    # 불필요한 공백 및 역슬래시 정리
    s = re.sub(r'\\([,;:! ])', ' ', s)
    s = re.sub(r'\\\\', '\n', s)
    s = re.sub(r'&', '', s)
    s = re.sub(r'\\', '', s)
    s = re.sub(r'[ \t]+', ' ', s)

    return s.strip()


def normalize_markdown_inlines(text: str) -> str:
    """중첩된 마크다운 볼드/이탤릭 (*, **), 인라인 코드 및 HTML 태그를 정규화합니다."""
    text = clean_inline_html(text)
    # **`code`** 형태를 **code**로 정규화
    text = re.sub(r'\*\*`([^`]+)`\*\*', r'**\1**', text)
    # ** 안에서 *s*, *a* 처럼 변수 강조용으로 쓰인 단독 이탤릭 제거
    def clean_nested_bold(m):
        inner = m.group(1)
        inner = re.sub(r'(?<![vVqQπμβa-zA-Z])\*([a-zA-Z0-9_\']+)\*', r'\1', inner)
        inner = re.sub(r'`([^`]+)`', r'\1', inner)
        return f"**{inner}**"
    text = re.sub(r'\*\*(.+?)\*\*', clean_nested_bold, text)
    return text


def parse_inline_runs(text: str):
    """
    텍스트 내의 **볼드**, *이탤릭/강조*, `코드`, $인라인수식$을 파싱하여 토큰 리스트로 반환합니다.
    """
    norm_text = normalize_markdown_inlines(text)
    pattern = re.compile(
        r'(\*\*.+?\*\*|\*[a-zA-Z0-9가-힣_\']+\*|`[^`]+`|\$[^$\n]+\$)'
    )
    tokens = []
    last_idx = 0
    for m in pattern.finditer(norm_text):
        if m.start() > last_idx:
            tokens.append((norm_text[last_idx:m.start()], 'normal'))
        raw = m.group(0)
        if raw.startswith('**') and raw.endswith('**') and len(raw) >= 4:
            tokens.append((raw[2:-2], 'bold'))
        elif raw.startswith('*') and raw.endswith('*') and len(raw) >= 2:
            tokens.append((raw[1:-1], 'bold'))  # *강조* 볼드로 깔끔하게 렌더링
        elif raw.startswith('`') and raw.endswith('`') and len(raw) >= 2:
            tokens.append((raw[1:-1], 'code'))
        elif raw.startswith('$') and raw.endswith('$') and len(raw) >= 2:
            tokens.append((clean_math_text(raw[1:-1]), 'math'))
        last_idx = m.end()
    if last_idx < len(norm_text):
        tokens.append((norm_text[last_idx:], 'normal'))
    return tokens


def add_formatted_paragraph(tf, raw_text: str, is_bullet=False, bullet_prefix="• ", font_size=16.5, space_after=12, line_spacing=1.38):
    """텍스트 프레임에 인라인 서식(볼드/수식/컬러)이 적용된 문단을 추가합니다 (Noto Sans KR 기본 적용)."""
    p = tf.add_paragraph() if len(tf.paragraphs[0].text) > 0 else tf.paragraphs[0]
    p.line_spacing = line_spacing
    p.space_after = Pt(space_after)
    set_font_paragraph(p, name=FONT_FAMILY, size=font_size)
    
    if is_bullet:
        p.margin_left = Pt(16)
        r_b = p.add_run()
        r_b.text = bullet_prefix
        set_font_run(r_b, name=FONT_FAMILY, size=font_size, bold=True, color=RGBColor(2, 132, 199))
        
    runs = parse_inline_runs(raw_text)
    for txt, style in runs:
        if not txt:
            continue
        r = p.add_run()
        r.text = txt
        if style == 'bold':
            set_font_run(r, name=FONT_FAMILY, size=font_size, bold=True, color=RGBColor(2, 132, 199))  # Sky Blue
        elif style in ('italic', 'math'):
            set_font_run(r, name=FONT_FAMILY, size=font_size, bold=True, color=RGBColor(15, 23, 42))   # Dark Navy
        elif style == 'code':
            set_font_run(r, name=FONT_FAMILY, size=font_size, bold=True, color=RGBColor(194, 65, 12))  # Amber
        else:
            set_font_run(r, name=FONT_FAMILY, size=font_size, bold=False, color=RGBColor(30, 41, 59))  # Slate 800


def add_slide_chrome(slide, chapter_title: str, topic_title: str, slide_num: int, total_slides: int, prof_audio_path: Path = None):
    """
    슬라이드 공통 헤더, 실선 구분바, 페이지 번호, 교수님 오디오 재생 버튼, 외곽선 없는 원형 아바타 영역을 생성합니다.
    (모든 요소 Noto Sans KR 적용)
    """
    # 1. 1행: 강의 챕터 대분류명 (16pt, Sky Blue #0284C7, Bold)
    tx_cat = slide.shapes.add_textbox(Pt(40), Pt(14), Pt(700), Pt(22))
    tf_cat = tx_cat.text_frame
    tf_cat.word_wrap = True
    tf_cat.margin_left = tf_cat.margin_top = tf_cat.margin_right = tf_cat.margin_bottom = 0
    p_cat = tf_cat.paragraphs[0]
    p_cat.text = clean_inline_html(chapter_title)
    set_font_paragraph(p_cat, name=FONT_FAMILY, size=16, bold=True, color=RGBColor(2, 132, 199))

    # 2. 2행: 슬라이드 설명 주제 제목 (동적 폰트 크기, Dark Navy #0F172A, Bold)
    clean_topic = clean_inline_html(topic_title)
    clean_topic = re.sub(r'[*_#`$]', '', clean_topic).strip()
    
    if len(clean_topic) > 38:
        t_size = 18.0
    elif len(clean_topic) > 26:
        t_size = 21.0
    elif len(clean_topic) > 16:
        t_size = 25.0
    else:
        t_size = 28.0

    tx_topic = slide.shapes.add_textbox(Pt(40), Pt(40), Pt(760), Pt(42))
    tf_topic = tx_topic.text_frame
    tf_topic.word_wrap = True
    tf_topic.margin_left = tf_topic.margin_top = tf_topic.margin_right = tf_topic.margin_bottom = 0
    p_topic = tf_topic.paragraphs[0]
    p_topic.text = clean_topic
    set_font_paragraph(p_topic, name=FONT_FAMILY, size=t_size, bold=True, color=RGBColor(15, 23, 42))

    # 3. 우측 상단: 슬라이드 번호 (13.5pt, Slate Gray #64748B, Bold)
    tx_page = slide.shapes.add_textbox(Pt(760), Pt(15), Pt(160), Pt(22))
    tf_page = tx_page.text_frame
    tf_page.margin_left = tf_page.margin_top = tf_page.margin_right = tf_page.margin_bottom = 0
    p_page = tf_page.paragraphs[0]
    p_page.text = f"{slide_num:02d} / {total_slides:02d}"
    p_page.alignment = PP_ALIGN.RIGHT
    set_font_paragraph(p_page, name=FONT_FAMILY, size=13.5, bold=True, color=RGBColor(100, 116, 139))

    # 4. 슬라이드 번호 하단: 🎙️ 교수님 강의 단일 버튼 (Top: 44pt)
    if prof_audio_path and prof_audio_path.exists():
        btn_prof = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Pt(812), Pt(44), Pt(108), Pt(28)
        )
        btn_prof.fill.solid()
        btn_prof.fill.fore_color.rgb = RGBColor(2, 132, 199)
        btn_prof.line.fill.background()
        tf_prof = btn_prof.text_frame
        tf_prof.vertical_anchor = MSO_ANCHOR.MIDDLE
        p_prof = tf_prof.paragraphs[0]
        p_prof.text = "🎙️ 강의 듣기"
        p_prof.alignment = PP_ALIGN.CENTER
        set_font_paragraph(p_prof, name=FONT_FAMILY, size=10.5, bold=True, color=RGBColor(255, 255, 255))

        # 오디오 무비 임베딩
        slide.shapes.add_movie(
            str(prof_audio_path),
            left=Pt(812), top=Pt(44), width=Pt(28), height=Pt(28),
            mime_type='audio/mp3'
        )

    # 5. 헤더 하단 회색 실선 구분바 (1.5pt 순수 실선, 음영 없음)
    connector = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Pt(40), Pt(88), Pt(920), Pt(88))
    connector.line.color.rgb = RGBColor(226, 232, 240)
    connector.line.width = Pt(1.5)
    spPr = connector.element.spPr
    effectLst = spPr.find('{http://schemas.openxmlformats.org/drawingml/2006/main}effectLst')
    if effectLst is not None:
        spPr.remove(effectLst)
    spPr.append(parse_xml(f'<a:effectLst {nsdecls("a")}/>'))

    # 6. 우측 하단: 원형 아바타 영역 (Left: 790pt, Top: 370pt, 160x160pt, 외곽선 없음)
    avatar = slide.shapes.add_shape(
        MSO_SHAPE.OVAL,
        Pt(790), Pt(370), Pt(160), Pt(160)
    )
    avatar.fill.solid()
    avatar.fill.fore_color.rgb = RGBColor(226, 232, 240)
    avatar.line.fill.background()
    
    spPr_av = avatar.element.spPr
    eff_av = spPr_av.find('{http://schemas.openxmlformats.org/drawingml/2006/main}effectLst')
    if eff_av is not None:
        spPr_av.remove(eff_av)
    spPr_av.append(parse_xml(f'<a:effectLst {nsdecls("a")}/>'))

    tf_av = avatar.text_frame
    tf_av.vertical_anchor = MSO_ANCHOR.MIDDLE
    p_av = tf_av.paragraphs[0]
    p_av.text = "👤 아바타 영역"
    p_av.alignment = PP_ALIGN.CENTER
    set_font_paragraph(p_av, name=FONT_FAMILY, size=11, bold=True, color=RGBColor(148, 163, 184))


def build_dialogue_slide(slide, chapter_title: str, topic_title: str, slide_num: int, total_slides: int,
                         img_path: Path, caption_text: str, audio_path: Path, quotes: list, script_text: str = "", prof_audio_path: Path = None):
    """
    대화 + 이미지 2열 레이아웃 슬라이드 생성 및 슬라이드 노트(대본) 삽입 (Noto Sans KR 적용)
    """
    add_slide_chrome(slide, chapter_title, topic_title, slide_num, total_slides, prof_audio_path)

    # 슬라이드 노트 (교수님 심층 강의 대본)
    if script_text:
        slide.notes_slide.notes_text_frame.text = script_text

    # 1. 좌측 영역: 이미지 및 캡션 (폭 440pt)
    if img_path and img_path.exists():
        actual_img = img_path
        if actual_img.suffix.lower() == '.svg':
            png_candidate = actual_img.with_suffix('.png')
            if not png_candidate.exists():
                try:
                    from svglib.svglib import svg2rlg
                    from reportlab.graphics import renderPM
                    drawing = svg2rlg(str(actual_img))
                    if drawing:
                        renderPM.drawToFile(drawing, str(png_candidate), fmt="PNG")
                except Exception as e:
                    print(f"[!] SVG 변환 실패 ({actual_img}): {e}")
            if png_candidate.exists():
                actual_img = png_candidate

        try:
            with Image.open(actual_img) as im:
                iw, ih = im.size
            max_iw = 440.0
            max_ih = 330.0
            scale = min(max_iw / iw, max_ih / ih, 1.0)
            pw = iw * scale
            ph = ih * scale
            pleft = 40.0 + (max_iw - pw) / 2.0
            ptop = 105.0 + (max_ih - ph) / 2.0
            slide.shapes.add_picture(str(actual_img), Pt(pleft), Pt(ptop), width=Pt(pw), height=Pt(ph))
        except Exception as e:
            print(f"[!] 이미지 로드 실패 ({actual_img}): {e}")

        if caption_text:
            clean_cap = clean_inline_html(re.sub(r'[*_#`]', '', caption_text).strip())
            tx_cap = slide.shapes.add_textbox(Pt(40), Pt(445), Pt(440), Pt(65))
            tf_cap = tx_cap.text_frame
            tf_cap.word_wrap = True
            tf_cap.margin_left = tf_cap.margin_top = tf_cap.margin_right = tf_cap.margin_bottom = 0
            p_cap = tf_cap.paragraphs[0]
            p_cap.text = clean_cap
            p_cap.alignment = PP_ALIGN.CENTER
            set_font_paragraph(p_cap, name=FONT_FAMILY, size=11, bold=False, color=RGBColor(71, 85, 105))

    # 2. 우측 영역: 대화 플레이어 바 (폭 420pt)
    player_box = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Pt(500), Pt(105), Pt(420), Pt(44)
    )
    player_box.fill.solid()
    player_box.fill.fore_color.rgb = RGBColor(248, 250, 252)
    player_box.line.color.rgb = RGBColor(2, 132, 199)
    player_box.line.width = Pt(1.5)
    try:
        sp = player_box.element.spPr
        ef = sp.find('{http://schemas.openxmlformats.org/drawingml/2006/main}effectLst')
        if ef is not None:
            sp.remove(ef)
        sp.append(parse_xml(f'<a:effectLst {nsdecls("a")}/>'))
    except Exception:
        pass

    tf_p = player_box.text_frame
    tf_p.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf_p.margin_left = Pt(14)
    tf_p.margin_right = Pt(155)
    p_p = tf_p.paragraphs[0]
    p_p.text = "🎧 대화 음성 듣기 (도로시, 지니, 토토)"
    p_p.alignment = PP_ALIGN.LEFT
    set_font_paragraph(p_p, name=FONT_FAMILY, size=11.5, bold=True, color=RGBColor(3, 105, 161))

    # 재생 버튼
    btn_play = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Pt(770), Pt(112), Pt(68), Pt(30)
    )
    btn_play.fill.solid()
    btn_play.fill.fore_color.rgb = RGBColor(2, 132, 199)
    btn_play.line.fill.background()
    try:
        sp_bp = btn_play.element.spPr
        ef_bp = sp_bp.find('{http://schemas.openxmlformats.org/drawingml/2006/main}effectLst')
        if ef_bp is not None:
            sp_bp.remove(ef_bp)
        sp_bp.append(parse_xml(f'<a:effectLst {nsdecls("a")}/>'))
    except Exception:
        pass
    tf_btn = btn_play.text_frame
    tf_btn.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf_btn.margin_left = Pt(22)
    p_btn = tf_btn.paragraphs[0]
    p_btn.text = "재생"
    p_btn.alignment = PP_ALIGN.CENTER
    set_font_paragraph(p_btn, name=FONT_FAMILY, size=11, bold=True, color=RGBColor(255, 255, 255))

    # 정지 버튼
    btn_stop = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Pt(844), Pt(112), Pt(66), Pt(30)
    )
    btn_stop.fill.solid()
    btn_stop.fill.fore_color.rgb = RGBColor(226, 232, 240)
    btn_stop.line.fill.background()
    try:
        sp_bs = btn_stop.element.spPr
        ef_bs = sp_bs.find('{http://schemas.openxmlformats.org/drawingml/2006/main}effectLst')
        if ef_bs is not None:
            sp_bs.remove(ef_bs)
        sp_bs.append(parse_xml(f'<a:effectLst {nsdecls("a")}/>'))
    except Exception:
        pass
    tf_stop = btn_stop.text_frame
    tf_stop.vertical_anchor = MSO_ANCHOR.MIDDLE
    p_stop = tf_stop.paragraphs[0]
    p_stop.text = "⏹ 정지"
    p_stop.alignment = PP_ALIGN.CENTER
    set_font_paragraph(p_stop, name=FONT_FAMILY, size=11, bold=True, color=RGBColor(71, 85, 105))

    # 대화 오디오 임베딩
    if audio_path and audio_path.exists():
        slide.shapes.add_movie(
            str(audio_path),
            left=Pt(774), top=Pt(115), width=Pt(24), height=Pt(24),
            mime_type='audio/mp3'
        )

    # 3. 우측 영역: 캐릭터 대화 카드
    tx_q = slide.shapes.add_textbox(Pt(500), Pt(158), Pt(420), Pt(200))
    tf_q = tx_q.text_frame
    tf_q.word_wrap = True
    tf_q.margin_left = tf_q.margin_top = tf_q.margin_right = tf_q.margin_bottom = 0
    
    for q_i, q_text in enumerate(quotes):
        p = tf_q.paragraphs[0] if q_i == 0 else tf_q.add_paragraph()
        p.space_after = Pt(12)
        p.line_spacing = 1.35
        clean_q = clean_inline_html(q_text)
        clean_q = re.sub(r'[*_#`]', '', clean_q).strip()
        clean_q = re.sub(r'\$\\?([a-zA-Z]+)\$', r'\1', clean_q)
        clean_q = clean_q.replace(r'\max', 'max').replace(r'\pi', 'π').replace(r'\gamma', 'γ')
        p.text = clean_q
        
        # 발화자별 색상 구분
        if re.search(r'도로시\s*:', clean_q):
            set_font_paragraph(p, name=FONT_FAMILY, size=13, bold=False, color=RGBColor(225, 29, 72))  # Coral Rose
        elif re.search(r'지니\s*:', clean_q):
            set_font_paragraph(p, name=FONT_FAMILY, size=13, bold=False, color=RGBColor(29, 78, 216))  # Royal Blue
        elif re.search(r'토토\s*:', clean_q):
            set_font_paragraph(p, name=FONT_FAMILY, size=13, bold=False, color=RGBColor(5, 150, 105))  # Emerald Green
        else:
            set_font_paragraph(p, name=FONT_FAMILY, size=13, bold=False, color=RGBColor(30, 41, 59))


def build_native_explanation_slide(slide, chapter_title: str, topic_title: str, slide_num: int, total_slides: int,
                                   content_md: str, svg_img_path: Path = None, prof_audio_path: Path = None, script_text: str = ""):
    """
    일반 설명 슬라이드를 2열 레이아웃(좌측: 대형 SVG 개념 다이어그램, 우측: 100% 편집 가능한 네이티브 텍스트)으로 생성합니다.
    (모든 텍스트 Noto Sans KR 적용)
    """
    add_slide_chrome(slide, chapter_title, topic_title, slide_num, total_slides, prof_audio_path)

    # 슬라이드 노트 (교수님 심층 강의 대본)
    if script_text:
        slide.notes_slide.notes_text_frame.text = script_text

    has_svg = svg_img_path and svg_img_path.exists()

    # 1. 좌측 영역: 대형 SVG/PNG 개념 다이어그램 (폭 440pt, 높이 380pt)
    if has_svg:
        with Image.open(svg_img_path) as im:
            iw, ih = im.size
        max_w = 440.0
        max_h = 380.0
        scale = min(max_w / iw, max_h / ih, 1.0)
        dw = iw * scale
        dh = ih * scale
        dleft = 40.0 + (max_w - dw) / 2.0
        dtop = 105.0 + (max_h - dh) / 2.0
        slide.shapes.add_picture(str(svg_img_path), Pt(dleft), Pt(dtop), width=Pt(dw), height=Pt(dh))

    # 2. 우측/전체 영역: 100% 편집 가능한 네이티브 텍스트 상자
    tx_left = 500 if has_svg else 40
    tx_width = 420 if has_svg else 730
    tx_height = 255 if has_svg else 410

    lines = content_md.strip().split('\n')
    tx_box = slide.shapes.add_textbox(Pt(tx_left), Pt(105), Pt(tx_width), Pt(tx_height))
    tf = tx_box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

    total_chars = sum(len(l.strip()) for l in lines if l.strip())
    non_empty_lines = [l for l in lines if l.strip() and l.strip() != '---']
    
    if total_chars > 350 or len(non_empty_lines) >= 6:
        base_font_sz = 13.0
        bullet_font_sz = 12.5
        base_space_after = 4
        base_line_spacing = 1.22
        note_font_sz = 12.5
    elif total_chars > 220 or len(non_empty_lines) >= 4:
        base_font_sz = 14.5
        bullet_font_sz = 14.0
        base_space_after = 7
        base_line_spacing = 1.30
        note_font_sz = 14.0
    else:
        base_font_sz = 16.5
        bullet_font_sz = 16.0
        base_space_after = 12
        base_line_spacing = 1.38
        note_font_sz = 15.5
    
    in_math = False
    math_buf = []
    in_note = False
    note_buf = []
    in_caution = False
    caution_buf = []
    
    for line in lines:
        raw_l = line.strip()
        if not raw_l or raw_l == '---':
            continue
            
        # 수식 블록 ($$ ... $$)
        if raw_l.startswith('$$') and raw_l.endswith('$$') and len(raw_l) > 2:
            eq_text = clean_math_text(raw_l)
            for eq_line in eq_text.split('\n'):
                if not eq_line.strip(): continue
                p_m = tf.add_paragraph() if len(tf.paragraphs[0].text) > 0 else tf.paragraphs[0]
                p_m.alignment = PP_ALIGN.CENTER
                p_m.space_before = Pt(6)
                p_m.space_after = Pt(8)
                r_m = p_m.add_run()
                r_m.text = eq_line.strip()
                eq_sz = 18 if len(eq_line) > 42 else 20
                set_font_run(r_m, name=FONT_FAMILY, size=eq_sz, bold=True, color=RGBColor(15, 23, 42))
            continue
            
        if raw_l == '$$':
            if in_math:
                in_math = False
                eq_text = clean_math_text('\n'.join(math_buf))
                math_buf.clear()
                for eq_line in eq_text.split('\n'):
                    if not eq_line.strip(): continue
                    p_m = tf.add_paragraph() if len(tf.paragraphs[0].text) > 0 else tf.paragraphs[0]
                    p_m.alignment = PP_ALIGN.CENTER
                    p_m.space_before = Pt(6)
                    p_m.space_after = Pt(8)
                    r_m = p_m.add_run()
                    r_m.text = eq_line.strip()
                    eq_sz = 18 if len(eq_line) > 42 else 20
                    set_font_run(r_m, name=FONT_FAMILY, size=eq_sz, bold=True, color=RGBColor(15, 23, 42))
            else:
                in_math = True
            continue

        if raw_l.startswith('$$') and not raw_l.endswith('$$'):
            in_math = True
            math_buf.append(raw_l[2:].strip())
            continue

        if in_math and raw_l.endswith('$$'):
            in_math = False
            math_buf.append(raw_l[:-2].strip())
            eq_text = clean_math_text('\n'.join(math_buf))
            math_buf.clear()
            for eq_line in eq_text.split('\n'):
                if not eq_line.strip(): continue
                p_m = tf.add_paragraph() if len(tf.paragraphs[0].text) > 0 else tf.paragraphs[0]
                p_m.alignment = PP_ALIGN.CENTER
                p_m.space_before = Pt(6)
                p_m.space_after = Pt(8)
                r_m = p_m.add_run()
                r_m.text = eq_line.strip()
                eq_sz = 18 if len(eq_line) > 42 else 20
                set_font_run(r_m, name=FONT_FAMILY, size=eq_sz, bold=True, color=RGBColor(15, 23, 42))
            continue
            
        if in_math:
            math_buf.append(raw_l)
            continue
            
        # NOTE / CAUTION 콜아웃
        if raw_l.startswith('> NOTE_') or (in_note and raw_l.startswith('>')):
            clean_l = re.sub(r'^>\s*(NOTE_)?', '', raw_l).strip()
            in_note = True
            note_buf.append(clean_l)
            continue
        elif in_note:
            in_note = False
            raw_note = " ".join(note_buf)
            note_buf.clear()
            p_n = tf.add_paragraph() if len(tf.paragraphs[0].text) > 0 else tf.paragraphs[0]
            p_n.space_before = Pt(6)
            p_n.space_after = Pt(base_space_after)
            p_n.line_spacing = base_line_spacing
            
            r_np = p_n.add_run()
            r_np.text = "💡 핵심 요약: "
            set_font_run(r_np, name=FONT_FAMILY, size=note_font_sz, bold=True, color=RGBColor(3, 105, 161))
            
            note_runs = parse_inline_runs(raw_note)
            for txt, style in note_runs:
                if not txt: continue
                r = p_n.add_run()
                r.text = txt
                set_font_run(r, name=FONT_FAMILY, size=note_font_sz, bold=(style == 'bold'), color=RGBColor(3, 105, 161))
            
        if raw_l.startswith('> CAUTION_') or (in_caution and raw_l.startswith('>')):
            clean_l = re.sub(r'^>\s*(CAUTION_)?', '', raw_l).strip()
            in_caution = True
            caution_buf.append(clean_l)
            continue
        elif in_caution:
            in_caution = False
            raw_caution = " ".join(caution_buf)
            caution_buf.clear()
            p_c = tf.add_paragraph() if len(tf.paragraphs[0].text) > 0 else tf.paragraphs[0]
            p_c.space_before = Pt(6)
            p_c.space_after = Pt(base_space_after)
            p_c.line_spacing = base_line_spacing
            
            r_cp = p_c.add_run()
            r_cp.text = "⚠️ 주의: "
            set_font_run(r_cp, name=FONT_FAMILY, size=note_font_sz, bold=True, color=RGBColor(190, 18, 60))
            
            caution_runs = parse_inline_runs(raw_caution)
            for txt, style in caution_runs:
                if not txt: continue
                r = p_c.add_run()
                r.text = txt
                set_font_run(r, name=FONT_FAMILY, size=note_font_sz, bold=(style == 'bold'), color=RGBColor(190, 18, 60))
            
        # 마크다운 이미지 구문 제외
        if raw_l.startswith('![') and raw_l.endswith(')'):
            continue

        # 마크다운 표(Table) 처리
        if raw_l.startswith('|') and raw_l.endswith('|'):
            cells = [c.strip() for c in raw_l.strip('|').split('|')]
            if all(re.match(r'^:?-+:?$', c) for c in cells if c):
                continue
            if len(cells) >= 2:
                if len(cells) >= 3 and cells[2]:
                    table_item = f"**{cells[0]}**: {cells[1]} ({cells[2]})"
                else:
                    table_item = f"**{cells[0]}**: {cells[1]}"
                add_formatted_paragraph(tf, table_item, is_bullet=True, bullet_prefix="• ", font_size=bullet_font_sz, space_after=base_space_after, line_spacing=base_line_spacing)
            continue

        # 리스트 항목
        if raw_l.startswith('*   ') or raw_l.startswith('- ') or raw_l.startswith('* '):
            item_text = re.sub(r'^(\*\s+|\-\s+|\*\s+)', '', raw_l).strip()
            add_formatted_paragraph(tf, item_text, is_bullet=True, bullet_prefix="• ", font_size=bullet_font_sz, space_after=base_space_after, line_spacing=base_line_spacing)
            continue
            
        if re.match(r'^\d+\.\s+', raw_l):
            num_m = re.match(r'^(\d+\.\s+)(.*)$', raw_l)
            prefix = num_m.group(1)
            item_text = num_m.group(2)
            add_formatted_paragraph(tf, item_text, is_bullet=True, bullet_prefix=prefix, font_size=bullet_font_sz, space_after=base_space_after, line_spacing=base_line_spacing)
            continue
            
        # 일반 문단
        add_formatted_paragraph(tf, raw_l, is_bullet=False, font_size=base_font_sz, space_after=base_space_after, line_spacing=base_line_spacing)

    if in_note and note_buf:
        raw_note = " ".join(note_buf)
        note_buf.clear()
        p_n = tf.add_paragraph() if len(tf.paragraphs[0].text) > 0 else tf.paragraphs[0]
        p_n.space_before = Pt(6)
        p_n.space_after = Pt(base_space_after)
        p_n.line_spacing = base_line_spacing
        r_np = p_n.add_run()
        r_np.text = "💡 핵심 요약: "
        set_font_run(r_np, name=FONT_FAMILY, size=note_font_sz, bold=True, color=RGBColor(3, 105, 161))
        note_runs = parse_inline_runs(raw_note)
        for txt, style in note_runs:
            if not txt: continue
            r = p_n.add_run()
            r.text = txt
            set_font_run(r, name=FONT_FAMILY, size=note_font_sz, bold=(style == 'bold'), color=RGBColor(3, 105, 161))

    if in_caution and caution_buf:
        raw_caution = " ".join(caution_buf)
        caution_buf.clear()
        p_c = tf.add_paragraph() if len(tf.paragraphs[0].text) > 0 else tf.paragraphs[0]
        p_c.space_before = Pt(6)
        p_c.space_after = Pt(base_space_after)
        p_c.line_spacing = base_line_spacing
        r_cp = p_c.add_run()
        r_cp.text = "⚠️ 주의: "
        set_font_run(r_cp, name=FONT_FAMILY, size=note_font_sz, bold=True, color=RGBColor(190, 18, 60))
        caution_runs = parse_inline_runs(raw_caution)
        for txt, style in caution_runs:
            if not txt: continue
            r = p_c.add_run()
            r.text = txt
            set_font_run(r, name=FONT_FAMILY, size=note_font_sz, bold=(style == 'bold'), color=RGBColor(190, 18, 60))


def clean_prof_script(text: str) -> str:
    """강의 스크립트에서 '학생 여러분', 'N번 슬라이드', '슬라이드' 등의 어색한 표현을 자연스러운 강의 구어로 정제합니다."""
    text = re.sub(r'학생\s*여러분[!,~]?', '여러분,', text)
    text = re.sub(r'자,\s*(\d+)\s*번\s*슬라이드(에서는|에서|의|를|에|는|가|도)?', '자, 이번에는', text)
    text = re.sub(r'(\d+)\s*번\s*슬라이드(에서는|에서|의|를|에|는|가|도)?', '이번에는', text)
    text = re.sub(r'이번\s*슬라이드(에서는|에서|의|를|에|는|가|도)?', '이번에는', text)
    text = re.sub(r'이\s*슬라이드(에서는|에서|의|를|에|는|가|도)?', '여기서', text)
    text = re.sub(r'다음\s*슬라이드(에서는|에서|의|를|에|는|가|도)?', '이어서', text)
    text = re.sub(r'슬라이드(에서는|에서|의|를|에|는|가|도)?', '화면', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def get_prof_lecture_script(slide_num: int, topic: str, item: dict, loaded_scripts: dict = None) -> str:
    """슬라이드별 자연스러운 50대 교수님 실전 강의 대본을 외부 JSON 또는 생성기에서 가져옵니다."""
    clean_topic = re.sub(r'[*_#`]', '', topic).strip()

    # 1. 외부 JSON에서 로드된 대본 우선 확인
    if loaded_scripts:
        str_key = str(slide_num)
        if str_key in loaded_scripts:
            val = loaded_scripts[str_key]
            if isinstance(val, dict) and 'script' in val:
                return clean_prof_script(val['script'])
            elif isinstance(val, str):
                return clean_prof_script(val)
        if slide_num in loaded_scripts:
            val = loaded_scripts[slide_num]
            if isinstance(val, dict) and 'script' in val:
                return clean_prof_script(val['script'])
            elif isinstance(val, str):
                return clean_prof_script(val)

    # 2. 내장 PROF_SCRIPTS 확인
    if slide_num in PROF_SCRIPTS:
        return clean_prof_script(PROF_SCRIPTS[slide_num])
    
    # 3. 대화 슬라이드 기본값
    if item['type'] == 'dialogue':
        dialogue_brief = " ".join([re.sub(r'[*_#`]', '', q) for q in item.get('quotes', [])[:2]])
        return clean_prof_script(f"이번에는 도로시와 지니의 대화를 살펴보겠습니다. {dialogue_brief}")
    else:
        # 설명 슬라이드 자동 요약 대본
        content_lines = [l.strip() for l in item.get('content', '').split('\n') if l.strip() and not l.startswith('#') and not l.startswith('---')]
        first_summary = content_lines[0] if content_lines else ""
        first_summary = re.sub(r'[*_#`$]', '', first_summary)
        return clean_prof_script(f"이번에는 {clean_topic}에 대해 함께 살펴보겠습니다. {first_summary}")


def convert_chapter_to_pptx(chapter_dir: Path, output_pptx: Path = None) -> bool:
    """
    지정된 챕터 폴더의 index.md, audio/, img/, lecture_scripts.json을 분석하여 
    Noto Sans KR 글꼴 기반 100% 편집 가능한 16:9 와이드스크린 PPTX를 생성합니다.
    """
    chapter_dir = Path(chapter_dir).resolve()
    md_path = chapter_dir / "index.md"
    if not md_path.exists():
        print(f"[-] {chapter_dir} 폴더에 index.md 파일이 없습니다.")
        return False

    folder_name = chapter_dir.name
    primary_output_pptx = chapter_dir / f"{folder_name}.pptx" if output_pptx is None else Path(output_pptx).resolve()
    compat_index_pptx = chapter_dir / "index.pptx"

    img_dir = chapter_dir / "img"
    audio_dir = chapter_dir / "audio"
    json_path = chapter_dir / "lecture_scripts.json"

    img_dir.mkdir(parents=True, exist_ok=True)
    audio_dir.mkdir(parents=True, exist_ok=True)

    # 외부 강의 대본 JSON 로드
    loaded_scripts = {}
    if json_path.exists():
        try:
            j_data = json.loads(json_path.read_text(encoding='utf-8'))
            loaded_scripts = j_data.get('slides', {})
            print(f"[*] 외부 강의 스크립트 JSON 로드 완료: {len(loaded_scripts)}개 슬라이드 대본")
        except Exception as e:
            print(f"[!] JSON 로드 오류 ({e}), 기본 대본을 사용합니다.")

    raw_text = md_path.read_text(encoding='utf-8')

    # 1. 챕터 대분류명 추출
    m_title = re.search(r'^title:\s*[\"\']?(.*?)[\"\']?\s*$', raw_text, re.MULTILINE)
    chapter_title = m_title.group(1) if m_title else chapter_dir.name.replace('_', ' ')
    print(f"[*] 챕터 분류명: {chapter_title}")

    # 2. YAML 프론트매터 제거
    text = re.sub(r'^---\s*\n.*?\n---\s*\n', '', raw_text, flags=re.DOTALL).strip()

    # 3. 대화 패턴 추출 및 시맨틱 슬라이드 청킹
    dlg_pattern = re.compile(
        r'(<div class=["\']dialogue-audio-player["\'][\s\S]*?<audio\s+src=["\']\./?audio/([^"\']+)["\'][\s\S]*?</div>\s*'
        r'((?:>\s*[^\n]+\n*)+)\s*'
        r'!\[(.*?)\]\(\./?img/([^)]+)\)\s*'
        r'(?:\*\*([^*]+)\*\*)?)',
        re.MULTILINE
    )

    matches = list(dlg_pattern.finditer(text))
    print(f"[*] 감지된 캐릭터 대화 씬 수: {len(matches)}개")

    slides_data = []
    last_pos = 0
    current_h3 = chapter_title
    current_h4 = ""

    def add_explanation_chunk(txt, top_title):
        clean = txt.strip()
        if not clean:
            return
        paras = [p.strip() for p in clean.split('\n\n') if p.strip()]
        cur_buf = []
        cur_len = 0
        for p in paras:
            p_len = len(p)
            if cur_len + p_len > 450 and cur_buf:
                slides_data.append({
                    'type': 'explanation',
                    'topic': top_title,
                    'content': '\n\n'.join(cur_buf)
                })
                cur_buf = [p]
                cur_len = p_len
            else:
                cur_buf.append(p)
                cur_len += p_len
        if cur_buf:
            slides_data.append({
                'type': 'explanation',
                'topic': top_title,
                'content': '\n\n'.join(cur_buf)
            })

    for m in matches:
        start_pos = m.start()
        end_pos = m.end()
        
        between_text = text[last_pos:start_pos].strip()
        if between_text:
            h_splits = re.split(r'^(?:#{1,4})\s+(.+)$', between_text, flags=re.MULTILINE)
            if h_splits[0].strip():
                clean_chunk = re.sub(r'---', '', h_splits[0]).strip()
                clean_chunk = re.sub(r'^#\s+\d+[\.\d+]*.*?\n', '', clean_chunk).strip()
                if clean_chunk:
                    add_explanation_chunk(clean_chunk, current_h4 if current_h4 else current_h3)
            for i in range(1, len(h_splits), 2):
                h_title = h_splits[i].strip()
                if h_title.startswith("06."):
                    current_h3 = h_title
                    current_h4 = ""
                else:
                    current_h4 = h_title
                chunk = re.sub(r'---', '', h_splits[i+1]).strip()
                if chunk:
                    add_explanation_chunk(chunk, current_h4 if current_h4 else current_h3)
                    
        # 대화 블록
        audio = m.group(2)
        quotes_raw = m.group(3)
        img_src = m.group(5)
        caption = m.group(6) or ""
        quotes = [re.sub(r'^>\s*', '', q).strip() for q in quotes_raw.strip().split('\n') if q.strip() and q.strip() != '>']
        
        dlg_topic = f"{current_h4 if current_h4 else current_h3} - 대화 및 핵심 정리"
        slides_data.append({
            'type': 'dialogue',
            'topic': dlg_topic,
            'audio': audio,
            'quotes': quotes,
            'img': img_src,
            'caption': caption
        })
        last_pos = end_pos

    # 잔여 설명 텍스트
    rem_text = text[last_pos:].strip()
    if rem_text:
        h_splits = re.split(r'^(?:#{1,4})\s+(.+)$', rem_text, flags=re.MULTILINE)
        if h_splits[0].strip():
            add_explanation_chunk(h_splits[0].strip(), current_h4 if current_h4 else current_h3)
        for i in range(1, len(h_splits), 2):
            h_title = h_splits[i].strip()
            chunk = re.sub(r'---', '', h_splits[i+1]).strip()
            if chunk:
                add_explanation_chunk(chunk, h_title)

    total_slides = len(slides_data)
    print(f"[*] 총 {total_slides}개 16:9 슬라이드 생성 시작 (기본 글꼴: {FONT_FAMILY}, 교수님 음성 TTS & SVG 다이어그램 포함)...")

    prs = Presentation()
    prs.slide_width = Pt(SLIDE_W)
    prs.slide_height = Pt(SLIDE_H)
    blank_layout = prs.slide_layouts[6]

    embedded_audio_count = 0

    for s_idx, item in enumerate(slides_data):
        slide_num = s_idx + 1
        slide = prs.slides.add_slide(blank_layout)
        topic = item['topic']
        script_text = get_prof_lecture_script(slide_num, topic, item, loaded_scripts)
        prof_audio_path = audio_dir / f"prof_lecture_slide_{slide_num:02d}.mp3"

        if item['type'] == 'dialogue':
            img_path = img_dir / item['img']
            aud_path = audio_dir / item['audio']
            
            build_dialogue_slide(
                slide, chapter_title, topic, slide_num, total_slides,
                img_path, item['caption'], aud_path, item['quotes'], script_text, prof_audio_path
            )
            if aud_path.exists():
                embedded_audio_count += 1

        else:
            # 설명 슬라이드: 카드형 SVG를 생성하지 않고 100% 편집 가능한 텍스트 중심 와이드 레이아웃 적용
            build_native_explanation_slide(
                slide, chapter_title, topic, slide_num, total_slides,
                item['content'], None, prof_audio_path, script_text
            )
            if prof_audio_path.exists():
                embedded_audio_count += 1

    # PPTX 저장
    try:
        prs.save(str(primary_output_pptx))
        print(f"\n[+] 변환 성공: {primary_output_pptx} (총 {len(prs.slides)} 슬라이드, {embedded_audio_count}개 오디오 임베딩 완료)\n", flush=True)
    except PermissionError:
        print(f"[!] 파일이 다른 프로그램(PowerPoint 등)에서 열려있어 저장이 차단되었습니다. 프로세스를 종료하고 재시도합니다.")
        os.system("powershell -Command \"Stop-Process -Name POWERPNT -Force -ErrorAction SilentlyContinue\"")
        prs.save(str(primary_output_pptx))
        print(f"[+] 재시도 성공: {primary_output_pptx}")

    # index.pptx 동기화
    try:
        shutil.copy2(primary_output_pptx, compat_index_pptx)
        print(f"[+] 호환 복사본 동기화 완료: {compat_index_pptx}\n")
    except Exception as e:
        print(f"[!] index.pptx 복사 실패: {e}")

    return True


def main():
    parser = argparse.ArgumentParser(description="마크다운 폴더를 16:9 Noto Sans KR 교수님 강의 PPTX로 변환합니다.")
    parser.add_argument("chapter_dir", nargs="?", default=r"c:\dev\sites\강화학습2\src\06_벨만_방정식\6_4_행동_가치_함수_Q_함수와_벨만_방정식",
                        help="변환할 강의 챕터 폴더 경로")
    parser.add_argument("-o", "--output", default=None, help="출력 PPTX 파일 경로")
    args = parser.parse_args()

    success = convert_chapter_to_pptx(Path(args.chapter_dir), args.output)
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
