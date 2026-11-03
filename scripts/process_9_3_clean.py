#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Process 9.3 index.md into clean lossless slides.md with high-quality domain lecture scripts.
"""

import re
from pathlib import Path

SOURCE_INDEX = Path("/Users/hojin9/dev/jinysite/강화학습3/src/09_몬테카를로법/9_3_몬테카를로법_구현/index.md")
TARGET_SLIDES = Path("/Users/hojin9/dev/jinysite/강화학습3/src/09_몬테카를로법/9_3_몬테카를로법_구현/slides.md")

DOM_SCRIPTS = [
    # 0: Intro overview
    "파이썬 코드로 몬테카를로 정책 평가 알고리즘을 한 줄씩 구현하는 실습 단원입니다. 환경 클래스와 에이전트 클래스가 step 메서드와 경험 메모리를 통해 어떻게 대화하는지 전체 아키텍처를 파악해 봅니다.",
    # 1: Pipeline roadmap
    "환경에 행동을 전달하는 env.step부터 에이전트의 배낭에 경험을 채우는 add, 에피소드 완주 판정, 그리고 마지막 eval의 역방향 가치 정산까지 이어지는 4단계 파이프라인의 유기적 흐름을 짚어봅니다.",
    # 2: 3x4 GridWorld interaction interface
    "3x4 그리드월드를 모델 프리 관점에서 바라봅니다. 과거에는 전이 행렬과 보상 공식을 모두 알고 풀었지만, 이제는 환경 내부 수식을 전혀 건네주지 않고 오직 상호작용 인터페이스만으로 해결합니다.",
    # 3: Known environment comparison
    "동적 프로그래밍에서는 미로의 완전한 지도를 들고 시작했습니다. 컴퓨터 메모리에 모든 확률과 보상이 투명하게 공개되어 있어 현장을 밟아보지 않고도 펜으로 가치를 계산할 수 있었습니다.",
    # 4: Unknown environment comparison
    "반면 몬테카를로법에서는 지도를 전혀 주지 않습니다. 에이전트는 안개 자욱한 미로 속에서 오직 지팡이로 바닥을 두드리며 다음 위치와 즉각 보상을 직접 확인하는 방식으로만 정보를 얻습니다.",
    # 5: step() method principle
    "GridWorld 클래스의 가장 중요한 메서드인 step의 인터페이스입니다. 에이전트가 행동 번호를 매개변수로 건네면 환경은 내부 물리 법칙에 따라 이동을 수행하고 결과를 반환합니다.",
    # 6: step() example code
    "step 메서드를 실제로 호출해보는 간결한 파이썬 예제 코드입니다. (2, 0) 상태에서 '위(0)'로 이동했을 때 반환되는 3개의 결과 튜플을 출력하여 확인합니다.",
    # 7: step() terminal output
    "터미널 출력 결과를 시각화한 모습입니다. next_state는 (1, 0), reward는 0.0, 그리고 에피소드가 끝나지 않았음을 뜻하는 done은 False로 깔끔하게 반환됩니다.",
    # 8: step() parameters
    "step 메서드의 매개변수인 action 정수값의 의미입니다. 상, 하, 좌, 우 4방향을 각각 0, 1, 2, 3으로 매핑하여 환경에 전달함으로써 물리 엔진이 동작하도록 만듭니다.",
    # 9: 3 return values breakdown
    "반환되는 3개의 핵심 데이터인 다음 상태 s', 즉각 보상 r, 완주 여부 플래그 done을 상세히 분해합니다. 이 세 가지 정보만으로 에이전트는 세상을 완전히 학습해 나갈 수 있습니다.",
    # 10: code math correspondence
    "파이썬 코드 변수와 수학 기호의 1:1 대응표입니다. next_state는 s_{t+1}, reward는 R_{t+1}, done은 종료 판정 조건식과 완벽히 일치하여 이론과 코드가 하나로 연결됩니다.",
    # 11: step memory packaging
    "step 메서드의 반환값을 에이전트의 경험 배낭인 memory 리스트에 (state, action, reward) 튜플 형태로 체계적으로 패키징하여 차곡차곡 적재하는 메모리 구조도입니다.",
    # 12: interaction loop circular structure
    "에이전트와 환경이 턴을 주고받는 4단계 순환 라이프사이클입니다. 행동 결정, 행동 실행, 경험 저장, 완주 판정의 4개 스텝이 매 에피소드마다 톱니바퀴처럼 맞물려 회전합니다.",
    # 13: 4 lifecycle steps detail
    "순환 라이프사이클의 세부 단계 설명입니다. 도로시가 정책 나침반을 보고 행동을 고르면 환경 콘솔에 전달되고, 반환된 경험을 배낭에 넣은 뒤 골 도착 시 eval을 호출합니다.",
    # 14: stochastic ice gridworld note
    "만약 80% 전진에 20% 미끄러짐이 있는 확률적 빙판길 환경이라도 에이전트의 코드는 단 한 줄도 바뀔 필요가 없습니다. 환경 모델을 몰라도 경험의 평균이 참 가치에 도달하기 때문입니다.",
    # 15: env.reset() start position
    "새로운 에피소드를 시작할 때마다 에이전트를 출발점 좌표인 (2, 0)으로 안전하게 되돌려놓는 env.reset() 메서드의 역할과 초기화 메커니즘을 설명합니다.",
    # 16: RandomAgent class architecture
    "본격적으로 몬테카를로 정책 평가를 담당하는 파이썬 클래스 RandomAgent를 설계합니다. 상하좌우 네 방향으로 25%씩 무작위로 걷는 에이전트의 속성과 동작을 정의합니다.",
    # 17: class init & defaultdict magic
    "RandomAgent의 __init__ 생성자와 defaultdict의 활용법입니다. 아직 가보지 않은 미지의 상태를 만나더라도 KeyError 없이 기본값을 즉시 생성해 주는 파이썬의 강력한 도구입니다.",
    # 18: init attributes detail
    "__init__에서 정의되는 핵심 속성들입니다. 감가율 gamma 0.9, 행동 개수 4개, 균등 정책 pi, 상태 가치 테이블 V, 방문 카운트 cnts, 그리고 경험 배낭 memory를 초기화합니다.",
    # 19: defaultdict vs general dict comparison
    "일반 딕셔너리를 쓸 때 발생하는 KeyError 예외 처리의 번거로움과, defaultdict(lambda: 0)을 썼을 때 코드 5줄이 단 1줄로 우아하게 단축되는 가독성 혁신을 비교합니다.",
    # 20: general dict problems code
    "일반 dict를 썼을 때 if s not in V로 매번 검사해야 하는 지저분한 방어 코드와 defaultdict의 간결한 자동 초기화 코드를 실제 구현 예시로 대조해 봅니다.",
    # 21: get_action() analysis
    "현재 상태 state에서 정책 딕셔너리를 참조하여 np.random.choice로 행동을 무작위 추출하는 get_action 메서드의 통계적 샘플링 원리를 설명합니다.",
    # 22: add, reset, eval methods intro
    "RandomAgent의 핵심 삼총사 메서드인 add, reset, eval의 시그니처와 구현 코드를 한눈에 조망합니다. 경험을 담고, 비우고, 가치를 정산하는 핵심 로직입니다.",
    # 23: add method memory packaging
    "한 걸음 걸을 때마다 state, action, reward를 묶어 self.memory.append로 배낭에 밀어 넣는 add 메서드의 구체적인 메모리 스택 구조를 살펴봅니다.",
    # 24: final memory data structure
    "에피소드가 끝났을 때 self.memory에 최종적으로 담겨 있는 튜플 리스트의 실제 구조입니다. 이동 궤적이 순서대로 보존되어 역방향 정산의 완벽한 입력이 됩니다.",
    # 25: why goal state not saved
    "마지막 골 지점 S_4는 왜 memory에 저장하지 않을까요? 골은 게임이 끝나는 곳으로 더 이상의 다음 행동이나 미래 보상이 존재하지 않아 V(s) 정의상 가치가 0이기 때문입니다.",
    # 26: eval() method backward accumulation
    "몬테카를로 평가의 심장인 eval 메서드입니다. reversed(self.memory)를 통해 골부터 출발지까지 거슬러 올라가며 G = r + gamma * G 점화식으로 증분 평균을 갱신합니다.",
    # 27: Hojin professor code lecture
    "이호진 교수님이 실제 파이썬 코드를 칠판에 띄우고 eval의 역순 순회 원리를 열정적으로 해설합니다. 뒤에서부터 정산할 때 모든 중복이 사라지는 경이로움을 강조합니다.",
    # 28: reversed evaluation chalkboard
    "칠판에 도식화된 역방향 가치 정산 비유입니다. 골에서 출발지로 거슬러 올라가며 가치 바구니에 보상을 담고, n분의 1 가중치로 가치 함수 카드를 갱신하는 원리입니다.",
    # 29: episode path tracking example
    "실제 에이전트가 3걸음 만에 골에 도달한 구체적인 좌표 경로 예시를 추적합니다. (2,0)에서 출발해 (1,0), (0,0)을 거쳐 골 (0,1)에 들어갔을 때의 보상 시퀀스입니다.",
    # 30: 3-step concrete path trace
    "이동 경로의 구체적인 스텝별 좌표와 보상입니다. 첫 걸음 0점, 두 번째 걸음 0점, 세 번째 골 도달 시 +1.0점을 획득했을 때의 데이터 궤적을 확인합니다.",
    # 31: eval reversed loop execution
    "G를 0으로 초기화한 뒤 골 직전 상태부터 거꾸로 계산을 수행합니다. S_2의 수익 1.0, S_1의 수익 0.9, S_0의 수익 0.81이 눈 깜짝할 사이에 유도되는 과정입니다.",
    # 32: incremental average update
    "수익 G가 계산되면 해당 상태의 방문 횟수를 1 늘리고, 기존 가치와의 오차(G - V)에 1/n을 곱해 점진적으로 더해주는 증분 평균 갱신 수식의 동작 원리입니다.",
    # 33: incremental update equivalence
    "이 코드가 9.1절에서 수학적으로 증명했던 V_n = V_{n-1} + (1/n)(G_n - V_{n-1}) 공식과 완벽히 일치함을 확인하며, 수학 이론이 파이썬 코드로 온전히 구현됨을 보여줍니다.",
    # 34: full execution script
    "RandomAgent와 GridWorld를 결합하여 1,000회의 에피소드를 실제로 돌려보는 전체 실행 스크립트입니다. 간결한 20줄 안팎의 코드로 완전한 정책 평가가 실행됩니다.",
    # 35: loop step by step analysis
    "실행 루프의 4단계를 코드 단위로 해부합니다. 매 에피소드 reset, while not done 내부의 get_action과 step, add, 그리고 에피소드 종료 후 eval 호출까지 일목요연합니다.",
    # 36: result value function heatmap
    "1,000회 에피소드 학습 후 출력된 3x4 그리드월드의 가치 함수 히트맵입니다. 골인 (0,3) 주변의 칸들이 높은 가치를 보이고, 함정 근처나 먼 곳은 낮은 가치를 띱니다.",
    # 37: random policy state coverage
    "출발점은 (2,0) 하나였지만 무작위 정책 덕분에 에이전트가 미로 전체를 골고루 누비며 모든 상태의 가치 카드를 빠짐없이 성공적으로 수렴시킬 수 있었음을 설명합니다.",
    # 38: deterministic policy caution
    "만약 정책이 한 방향으로만 가는 결정적 정책이었다면 가보지 못한 상태의 가치는 영원히 0으로 남았을 것입니다. 몬테카를로법에서 충분한 탐험이 왜 필수적인지 짚어봅니다.",
    # 39: MC vs DP comparison intro
    "몬테카를로법으로 구한 가치 히트맵과 4장에서 동적 프로그래밍으로 구한 참 가치 함수를 직접 대조해 봅니다. 두 결과가 소수점 단위까지 거의 일치함을 시각적으로 확인합니다.",
    # 40: MC vs DP comprehensive table
    "DP와 MC의 핵심 비교 표입니다. 환경 모델 필요 여부, 부트스트래핑 사용 여부, 계산 복잡도, 현실 적용 가능성 등 모든 측면에서 두 접근법의 장단점을 명확히 정리합니다.",
    # 41: summary 3 pillars of MC implementation
    "몬테카를로 구현의 3대 핵심 기둥인 step 인터페이스, defaultdict와 memory 배낭, 역방향 eval 증분 갱신의 전체 조감도를 한눈에 요약합니다.",
    # 42: pillar 1, 2, 3 details
    "구현 3대 기둥의 세부 요약입니다. 블랙박스 상호작용 인터페이스, O(1) 메모리 관리, 그리고 O(T) 선형 시간 역방향 증분 갱신이 결합되어 실전 알고리즘을 완성합니다.",
    # 43: Hojin professor direct lecture note
    "단 3줄의 점화식과 역방향 루프만으로 미지의 환경 가치를 밝혀내는 몬테카를로 코드의 극적인 간결함과 아름다움을 강조하는 이호진 교수님의 직강 메시지입니다.",
    # 44: Genie celebration note
    "복잡한 행렬 연산 없이 파이썬의 기본 자료구조만으로 완벽한 인공지능 에이전트를 완성해 낸 도로시와 학습자들을 축하하며 다음 9.4장 정책 제어로의 진입을 안내합니다."
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
    
    current_h1 = "09.3 몬테카를로법 구현"
    current_h2 = "09.3 몬테카를로법 구현"
    
    slides = []
    
    for i, sec in enumerate(sections):
        lines = sec.split('\n')
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
        if h3_match and (current_h2 == "09.3 몬테카를로법 구현" or "09.3." not in current_h2):
            slide_h2 = f"09.3 {h3_match.group(1).strip()}"
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

