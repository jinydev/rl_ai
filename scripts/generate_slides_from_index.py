#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
강화학습 교재 index.md -> slides.md 고품질 자동 생성기
가이드라인: guides/SLIDES_CONVERSION_GUIDE.md
"""

import os
import re
import sys
from pathlib import Path

def clean_text_for_script(text):
    text = re.sub(r'[*_#`$]', '', text)
    text = re.sub(r'\[.*?\]\(.*?\)', '', text)
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def parse_chapter_to_slides(chapter_path: str):
    chapter_dir = Path(chapter_path).resolve()
    index_md = chapter_dir / "index.md"
    if not index_md.exists():
        print(f"[-] {index_md} 파일이 없습니다.")
        return False

    raw = index_md.read_text(encoding='utf-8')
    
    # 챕터 대분류명
    m_title = re.search(r"^title:\s*[\"']?(.*?)[\"']?\s*$", raw, re.MULTILINE)
    chapter_title = m_title.group(1) if m_title else chapter_dir.name.replace("_", " ")

    # YAML 프론트매터 제거
    text = re.sub(r"^---\s*\n.*?\n---\s*\n", "", raw, flags=re.DOTALL).strip()

    # 이미지 패턴 추출
    img_pattern = re.compile(r"(!\[(.*?)\]\((?:\./)?img/([^)]+)\)\s*(?:\*\*([^*]+)\*\*)?)")
    matches = list(img_pattern.finditer(text))
    print(f"[*] {chapter_title}: 총 {len(matches)}개 이미지 감지됨")

    slides = []
    current_h1 = chapter_title
    current_h2 = ""
    current_h3 = ""
    current_h4 = ""

    last_pos = 0

    for idx, m in enumerate(matches):
        start_pos = m.start()
        end_pos = m.end()

        # 이전 이미지 끝부터 현재 이미지까지의 텍스트
        chunk_before = text[last_pos:start_pos].strip()

        # 다음 이미지 시작 전까지의 텍스트 (캡션 이후 텍스트)
        next_start = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        chunk_after = text[end_pos:next_start].strip()

        # 헤더 업데이트
        headers = re.findall(r"^(#{1,4})\s+(.+)$", chunk_before, flags=re.MULTILINE)
        for h_level, h_text in headers:
            h_text = h_text.strip()
            if len(h_level) == 1:
                current_h1 = h_text
            elif len(h_level) == 2:
                current_h2 = h_text
            elif len(h_level) == 3:
                current_h3 = h_text
            elif len(h_level) == 4:
                current_h4 = h_text

        # 소제목 결정
        slide_topic = current_h4 if current_h4 else (current_h3 if current_h3 else (current_h2 if current_h2 else chapter_title))
        slide_topic = re.sub(r"^#+\s*", "", slide_topic).strip()

        img_alt = m.group(2).strip()
        img_file = m.group(3).strip()
        caption_full = m.group(4).strip() if m.group(4) else img_alt

        # 본문 및 설명 분석
        combined_text = f"{chunk_before}\n\n{chunk_after}".strip()
        
        # 1~2문장 리드 설명문 추출
        lead_sentences = []
        for line in chunk_before.split("\n"):
            line = line.strip()
            if line and not line.startswith("#") and not line.startswith("---") and not line.startswith(">") and not line.startswith("!"):
                lead_sentences.append(line)
                if len(" ".join(lead_sentences)) > 80:
                    break
        lead_text = " ".join(lead_sentences).strip()
        if not lead_text:
            lead_text = f"{slide_topic}의 핵심 원리와 동작 메커니즘을 시각적 도식과 함께 체계적으로 분석합니다."

        # 불릿 포인트 추출 (최대 3~4개)
        bullets = []
        # 1. 기존 불릿 탐색
        found_bullets = re.findall(r"^[-*•]\s+(.+)$", combined_text, flags=re.MULTILINE)
        for b in found_bullets[:3]:
            clean_b = re.sub(r"^단락\s*\d+:\s*", "", b).strip()
            if clean_b and len(clean_b) > 8:
                bullets.append(clean_b)

        # 2. 대화 블록에서 핵심 문장 추출
        if len(bullets) < 2:
            dialogue_quotes = re.findall(r"^>\s*[\"']?([👧🐱🐶👨‍🏫].*?)[\"']?$", combined_text, flags=re.MULTILINE)
            for q in dialogue_quotes[:2]:
                q_clean = clean_text_for_script(q)
                if len(q_clean) > 15:
                    bullets.append(q_clean[:80])

        # 3. 주요 설명 문단에서 보충
        if len(bullets) < 2:
            for p in combined_text.split("\n\n"):
                p_clean = clean_text_for_script(p)
                if len(p_clean) > 25 and not p_clean.startswith("그림") and not p_clean.startswith("---"):
                    bullets.append(p_clean[:75])
                    if len(bullets) >= 2:
                        break

        # 기본 불릿 보강
        if not bullets:
            bullets.append(f"{slide_topic}의 수학적 정의와 기초 개념 이해")
            bullets.append(f"시각화 도식을 통한 직관적 원리 및 메커니즘 파악")

        # 핵심 인사이트 (💡)
        insight_match = re.search(r"💡\s*(.+?)(?:\n|$)", combined_text)
        if insight_match:
            insight_text = clean_text_for_script(insight_match.group(1))
        else:
            insight_text = f"{slide_topic}은(는) 몬테카를로 학습의 안정성과 수렴성을 보장하는 핵심 요소입니다."

        # 강의 스크립트 작성 (200~320자 내외 구어체, 금지어 배제)
        # segment 내부의 교수님 직강/대화가 있으면 우선 활용
        # 인용구 블록(>) 전체 수집
        raw_quotes = []
        for line in combined_text.splitlines():
            line_str = line.strip()
            if line_str.startswith(">"):
                clean_q_line = re.sub(r"^>\s*", "", line_str)
                clean_q_line = re.sub(r"^[👨‍🏫🐱👧🐶].*?:\s*", "", clean_q_line)
                clean_q_line = clean_text_for_script(clean_q_line)
                if clean_q_line and len(clean_q_line) > 5:
                    raw_quotes.append(clean_q_line)

        quote_text = " ".join(raw_quotes)

        if len(quote_text) >= 150:
            script_body = quote_text[:315]
        else:
            first_b = clean_text_for_script(bullets[0]) if bullets else f"{slide_topic}의 기본 원리"
            second_b = clean_text_for_script(bullets[1]) if len(bullets) > 1 else ""
            third_b = f" {quote_text}" if quote_text else ""
            script_body = (
                f"{slide_topic}에 대해 함께 살펴보겠습니다. "
                f"{lead_text} "
                f"화면의 도식을 보시면 {first_b}. "
                f"{second_b}.{third_b} "
                f"이처럼 {insight_text}"
            )

        # 스크립트 정제 (금지어 제거 및 길이 조절)
        script_body = clean_text_for_script(script_body)
        script_body = re.sub(r'이번\s*슬라이드[는에서]*', '화면을 보시면', script_body)
        script_body = re.sub(r'다음\s*슬라이드[는에서]*', '이어서', script_body)
        script_body = re.sub(r'슬라이드', '화면', script_body)
        script_body = re.sub(r'안녕하세요[!,\s]*', '', script_body)
        script_body = re.sub(r'감사합니다[!,\s]*', '', script_body)
        
        # 180~320자 길이 최적화
        if len(script_body) > 320:
            script_body = script_body[:315] + "..."
        elif len(script_body) < 180:
            script_body += f" 이러한 수학적 원리와 수렴성을 정확히 이해하면 복잡한 환경에서도 안정적으로 최적 가치와 정책을 찾아낼 수 있습니다."

        # 슬라이드 마크다운 조립
        slide_md = f"# {chapter_title}\n"
        slide_md += f"## {slide_topic}\n\n"
        slide_md += f"{lead_text}\n\n"
        slide_md += f"![{img_alt}](./img/{img_file})\n"
        slide_md += f"**그림** {caption_full}\n\n"
        for b in bullets:
            slide_md += f"- {b}\n"
        slide_md += f"- 💡 **핵심 인사이트**: {insight_text}\n\n"
        slide_md += f'> "{script_body}"\n'

        slides.append(slide_md)
        last_pos = end_pos

    # slides.md 파일 쓰기
    slides_content = "\n---\n\n".join(slides)
    slides_file = chapter_dir / "slides.md"
    slides_file.write_text(slides_content, encoding='utf-8')
    print(f"[+] {slides_file} 생성 완료: 총 {len(slides)}개 슬라이드")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python generate_slides_from_index.py <chapter_dir>")
        sys.exit(1)
    parse_chapter_to_slides(sys.argv[1])
