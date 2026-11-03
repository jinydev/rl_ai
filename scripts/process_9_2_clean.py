#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Process 9.2 index.md into clean lossless slides.md with high-quality domain lecture scripts.
"""

import re
from pathlib import Path

SOURCE_INDEX = Path("/Users/hojin9/dev/jinysite/강화학습3/src/09_몬테카를로법/9_2_몬테카를로법으로_정책_평가하기/index.md")
TARGET_SLIDES = Path("/Users/hojin9/dev/jinysite/강화학습3/src/09_몬테카를로법/9_2_몬테카를로법으로_정책_평가하기/slides.md")

DOM_SCRIPTS = [
    # 0: Intro overview
    "주어진 정책 파이를 따랐을 때 각 상태에서 기대할 수 있는 장기 보상의 합인 가치 함수를 근사하는 정책 평가의 핵심 개념을 소개합니다. 환경 모델을 모르는 상태에서 오직 에피소드 시뮬레이션 경험만으로 참 가치에 도달하는 여정이 시작됩니다.",
    # 1: Stepping stones intro
    "징검다리를 건너 끝까지 도달하는 에피소드 경험을 축적하여 각 발판의 기대 가치를 완성해 가는 과정입니다. 에이전트가 완주할 때마다 얻은 누적 보상을 바탕으로 각 위치의 잠재적 가치 카드가 하나씩 정밀하게 채워집니다.",
    # 2: Experience sampling
    "복잡한 전이 확률 수식이나 보상 함수를 펼쳐놓지 않고도, 실제 환경 속에서 주사위를 굴리듯 수집한 표본 데이터의 산술 평균만으로 참 기댓값을 찾아내는 몬테카를로법의 본질적인 통계적 발상을 설명합니다.",
    # 3: Why fits RL blackbox
    "현실의 강화학습 환경은 다음 상태와 보상이 어떻게 주어질지 알 수 없는 완전한 블랙박스입니다. 몬테카를로법은 시스템 내부 방정식을 전혀 요구하지 않으므로, 미지의 현실 세계 문제에 가장 직관적이면서도 완벽하게 부합합니다.",
    # 4: Ground truth accuracy
    "에이전트가 환경에 직접 부딪혀 얻은 실제 누적 수익 샘플 G들을 충분히 모아 평균을 내면, 큰 수의 법칙에 의해 참 가치 함수에 수학적으로 완벽하게 수렴하게 됩니다. 경험의 누적이 곧 정확한 평가로 이어지는 메커니즘입니다.",
    # 5: Fixed policy evaluation
    "정책 평가 단계에서는 에이전트의 행동 지침인 정책 파이가 고정되어 있습니다. 이 고정된 지침에 따라 환경 속을 탐색했을 때 각 상태가 에이전트에게 얼마나 유리하고 안전한 곳인지 객관적인 점수를 매기는 것이 목표입니다.",
    # 6: Value function formula
    "상태 가치 함수 v_pi(s)의 수학적 정의를 살펴봅니다. 특정 상태 s에서 출발하여 고정 정책 파이를 따랐을 때 미래에 받게 될 감가 누적 보상들의 총합인 G_t의 조건부 기댓값으로 엄밀하게 정의됩니다.",
    # 7: Symbol breakdown
    "가치 함수 정의식에 등장하는 네 가지 핵심 기호의 역할을 분해합니다. 정책 파이, 기대수익 G_t, 출발 상태 s 조건, 그리고 확률적 조건부 기댓값 E가 결합되어 미래 보상의 기대 총량을 수학적으로 완성합니다.",
    # 8: MC approximation free running
    "복잡한 적분이나 무한 급수를 계산할 필요 없이, 에이전트가 정책에 맞춰 환경 속을 자유롭게 뛰어다니며 에피소드를 완주하게 합니다. 실제 주행 경험이 곧 적분을 대신하는 표본 데이터가 됩니다.",
    # 9: Episode finish & return token
    "출발 상태에서 시작하여 종결 상태에 도달할 때까지 얻은 모든 즉각 보상들을 할인율에 따라 합산하면 하나의 완결된 누적 수익 샘플 G를 손에 쥐게 됩니다. 이 수익 토큰이 가치 평가의 기초 원자재가 됩니다.",
    # 10: Sample averaging formula
    "동일한 상태에서 출발하여 얻은 n개의 실제 수익 샘플들을 모두 더해 n으로 나누는 산술 평균 공식입니다. 표본 수가 늘어날수록 평균 오차는 0으로 수렴하여 참 가치 함수를 빈틈없이 복원해 냅니다.",
    # 11: Hojin professor finish
    "에피소드를 성공적으로 완주하고 출발선으로 돌아온 에이전트를 격려하는 모습입니다. 끝까지 달려가 최종 결과를 확인해야만 비로소 에피소드의 가치를 정산할 수 있는 몬테카를로의 고유한 특성을 보여줍니다.",
    # 12: Episodic task caution
    "몬테카를로 정책 평가는 반드시 끝이 정해져 있는 일회성 에피소드 과제에서만 적용할 수 있습니다. 무한히 끝나지 않는 지속적 과제에서는 최종 수익 G_t를 확정할 수 없으므로 주의 깊은 문제 정의가 요구됩니다.",
    # 13: 2-episode toy example
    "이해를 돕기 위해 에이전트가 상태 s에서 출발하여 딱 2번의 에피소드를 수행하는 구체적인 수치 예시를 다룹니다. 첫 번째 시도와 두 번째 시도의 수익이 어떻게 누적 평균되는지 직관적으로 확인해 봅시다.",
    # 14: Step by step calculation
    "첫 번째 에피소드에서 1점을 얻고 두 번째 에피소드에서 5점을 얻었을 때, 표본 평균은 (1+5)/2인 3.0으로 갱신됩니다. 아주 적은 시도만으로도 참 가치에 한 걸음씩 다가가는 평균의 안정성을 보여줍니다.",
    # 15: 1-hit multi-state harvest
    "하나의 출발 상태만 고집할 필요 없이, 단 한 번의 에피소드 완주만으로 지나쳐 온 모든 상태의 가치를 한꺼번에 수확하는 몬테카를로법의 놀라운 효율적 혁신인 1타 다피 원리를 소개합니다.",
    # 16: Inefficient reset limits
    "각 상태마다 에이전트를 강제로 리셋시켜 개별적으로 출발시키는 방식은 엄청난 환경 초기화 비용과 연산 낭비를 초래합니다. 환경의 자연스러운 흐름을 끊는 비효율적인 접근의 한계를 짚어봅니다.",
    # 17: Single path multi harvest math
    "하나의 이동 경로 A -> B -> C -> 골에서 A의 수익, B의 수익, C의 수익을 수식으로 동시에 전개해 봅니다. 각 상태 이후에 등장하는 보상들의 꼬리 부분이 완벽하게 공유된다는 놀라운 구조적 특징이 드러납니다.",
    # 18: Train journey analogy
    "서울에서 출발해 대전과 대구를 거쳐 부산으로 가는 기차 여행의 비유입니다. 서울 승객, 대전 승객, 대구 승객 모두 각자의 탑승 시점부터 종착역까지의 남은 여정 만족도를 자연스럽게 정산할 수 있는 원리와 같습니다.",
    # 19: All states triumph
    "단 한 번의 완주로 경로 상의 모든 상태 카드를 풍성하게 채워 넣는 성취의 순간입니다. 에이전트가 다양한 경로를 자유롭게 탐험하기만 하면 미로 전체의 가치 지도가 고르게 완성됩니다.",
    # 20: Backward return redundancy
    "각 상태의 수익을 처음부터 순서대로 계산하면 뒷부분의 보상 덧셈이 계속 반복되어 심각한 연산 중복이 발생합니다. 컴퓨터가 불필요하게 덧셈을 되풀이하는 비효율성을 시각적으로 확인합니다.",
    # 21: Recurrence pattern discovery
    "수식을 자세히 뜯어보면 G_A는 바로 다음 상태의 수익 G_B에 할인율 감마를 곱하고 즉각 보상 R_0를 더한 것과 같다는 점화식 규칙이 도출됩니다. 과거의 계산을 재활용하는 다이내믹 프로그래밍의 정수입니다.",
    # 22: 3-step backward settlement
    "골 지점 직전의 C부터 B, A로 거슬러 올라가며 단 세 번의 점화식 덧셈만으로 모든 수익을 정산하는 단계별 메커니즘입니다. 중복 연산이 순식간에 사라지는 마법 같은 최적화입니다.",
    # 23: Backward recurrence formula
    "임의의 시점 t에 대해 G_t = R_t + 감마 * G_{t+1}로 정의되는 아름다운 재귀 점화식입니다. 최종 종료 시점에서는 G_T = 0으로 시작하여 역방향으로 완벽하게 전파됩니다.",
    # 24: Hojin blackboard lecture
    "이호진 교수님이 역방향 징검다리 칠판을 통해 점화식의 직관적 물리 의미를 명쾌하게 설명합니다. 끝에 도달하여 결말을 안 뒤에야 각 순간의 진정한 기여도를 거꾸로 정확히 평가할 수 있습니다.",
    # 25: Backward accumulation flowchart
    "종료 지점에서 시작 지점을 향해 보상들을 감가율과 결합하며 누적해 내려오는 데이터 파이프라인의 완성된 순서도입니다. 하드웨어 메모리와 캐시 친화적인 알고리즘 구조를 보여줍니다.",
    # 26: Complexity O(T^2) vs O(T)
    "정방향 계산 시 에피소드 길이 T에 대해 O(T^2)의 2차 시간 복잡도가 소요되지만, 역방향 재귀 정산을 적용하면 O(T)의 선형 시간으로 비약적인 속도 개선이 이루어집니다.",
    # 27: Backward step settlement
    "골에서 출발지를 향해 거꾸로 거슬러 올라가는 실제 연산 흐름을 시각화했습니다. 에피소드가 수백 걸음으로 길어져도 곱셈과 덧셈 한 쌍만으로 각 상태의 수익이 즉시 정산됩니다.",
    # 28: Python reversed memory
    "파이썬 코드에서 에이전트의 경험 리스트를 reversed(memory)로 뒤집어 for 루프를 순회하는 핵심 구현 원리입니다. 단 3줄의 파이썬 코드로 O(T) 역방향 점화식을 구현할 수 있습니다.",
    # 29: Summary core takeaways
    "몬테카를로 정책 평가를 떠받치는 3대 핵심 기둥인 표본 평균, 단일 경로 다중 수확, 역방향 재귀 정산의 전체 조감도를 한눈에 정리합니다.",
    # 30: Pillar 1 Return averaging
    "제1기둥인 경험 수익 표본 평균입니다. 환경의 전이 확률을 전혀 몰라도 에이전트가 직접 겪은 에피소드들의 누적 보상 평균만으로 상태의 참 가치를 정밀하게 근사합니다.",
    # 31: Pillar 2 Multi-state harvesting
    "제2기둥인 단일 경로 다중 상태 수확입니다. 상태마다 따로 리셋할 필요 없이 단 한 번의 여정에서 밟고 지나간 모든 상태의 수익 데이터를 동시에 획득하여 학습 속도를 극대화합니다.",
    # 32: Pillar 3 Backward recursion
    "제3기둥인 초고속 역방향 재귀 정산입니다. 점화식 G_t = R_t + 감마 * G_{t+1}을 통해 O(T)의 선형 시간에 에피소드 전체의 수익을 누수 없이 정산해 냅니다.",
    # 33: Hojin mentor note
    "끝까지 도달해 본 자만이 과거의 모든 순간에 올바른 가치를 매길 수 있다는 강화학습의 철학적 통찰입니다. 미지의 세계에서도 직접 부딪히고 뒤돌아 정산할 때 최적의 길을 발견하게 됩니다.",
    # 34: Genie preview note
    "이론적 원리를 완벽하게 마스터한 도로시와 학습자들을 응원하며, 다음 9.3절에서 파이썬과 그리드월드를 결합하여 실제 코드로 구현해 볼 흥미진진한 실습을 예고합니다."
]

def clean_prompts(text: str) -> str:
    # Remove generation prompt tags like (1:1 순백색), (16:9 와이드), etc.
    text = re.sub(r'\s*\([0-9]+:[0-9]+[^\)]*\)', '', text)
    text = re.sub(r'\(1:1\s*순백색[^\)]*\)', '', text)
    text = re.sub(r'\(16:9\s*와이드[^\)]*\)', '', text)
    text = re.sub(r'\(순백색\s*배경[^\)]*\)', '', text)
    return text

def main():
    content = SOURCE_INDEX.read_text(encoding='utf-8')
    raw_sections = content.split('\n---\n')
    
    # Filter out frontmatter and empty sections
    sections = []
    for s in raw_sections:
        s_clean = s.strip()
        if not s_clean:
            continue
        if s_clean.startswith('---') or s_clean.startswith('layout:'):
            continue
        sections.append(s_clean)
        
    print(f"Total valid sections: {len(sections)}")
    
    current_h1 = "09.2 몬테카를로법으로 정책 평가하기"
    current_h2 = "09.2 몬테카를로법으로 정책 평가하기"
    
    slides = []
    
    for i, sec in enumerate(sections):
        lines = sec.split('\n')
        # Check if first few lines contain # or ##
        h1_match = None
        h2_match = None
        cleaned_lines = []
        
        for l in lines:
            if l.startswith('# '):
                current_h1 = l[2:].strip()
                continue
            elif l.startswith('## '):
                current_h2 = l[3:].strip()
                continue
            cleaned_lines.append(l)
            
        sec_body = '\n'.join(cleaned_lines).strip()
        sec_body = clean_prompts(sec_body)
        
        # Derive h2 if it's still default or has ###
        h3_match = re.search(r'^###\s+(.+)$', sec_body, re.MULTILINE)
        if h3_match and (current_h2 == "09.2 몬테카를로법으로 정책 평가하기" or "09.2." not in current_h2):
            slide_h2 = f"09.2 {h3_match.group(1).strip()}"
        else:
            slide_h2 = current_h2
            
        script = DOM_SCRIPTS[i] if i < len(DOM_SCRIPTS) else DOM_SCRIPTS[-1]
        
        slide_md = f"# {current_h1}\n## {slide_h2}\n\n{sec_body}\n\n> \"{script}\""
        slides.append(slide_md)
        
    final_output = '\n\n---\n\n'.join(slides) + '\n'
    TARGET_SLIDES.write_text(final_output, encoding='utf-8')
    print(f"Successfully wrote {len(slides)} slides to {TARGET_SLIDES}")

if __name__ == '__main__':
    main()

