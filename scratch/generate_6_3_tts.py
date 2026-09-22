import asyncio
import os
import shutil
import edge_tts

OUTPUT_DIR = "/Users/hojin9/dev/jinysite/강화학습/src/06_벨만_방정식/6_3_벨만_방정식의_예/audio"
DOCS_DIR = "/Users/hojin9/dev/jinysite/강화학습/docs/06_벨만_방정식/6_3_벨만_방정식의_예/audio"
TEMP_DIR = "/tmp/tts_temp_6_3"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(DOCS_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

VOICES = {
    'dorothy': {'voice': 'ko-KR-SunHiNeural', 'pitch': '+22Hz', 'rate': '+3%'},
    'jiny': {'voice': 'ko-KR-InJoonNeural', 'pitch': '+2Hz', 'rate': '+0%'},
}

def preprocess_text(text: str) -> str:
    # Remove markdown formatting
    text = text.replace("**", "").replace("*", "").replace("`", "")
    text = text.replace('"', '').replace("'", "")
    # Math symbols to natural Korean
    text = text.replace("v_π(L1)", "브이 파이 엘원")
    text = text.replace("v_π(L2)", "브이 파이 엘투")
    text = text.replace("v_π(s)", "브이 파이 에스")
    text = text.replace("v_π(s')", "브이 파이 에스 프라임")
    text = text.replace("v(L1)", "브이 엘원")
    text = text.replace("v(L2)", "브이 엘투")
    text = text.replace("L1", "엘원")
    text = text.replace("L2", "엘투")
    text = text.replace("f(s, a)", "에프 에스 에이")
    text = text.replace("s'", "에스 프라임")
    text = text.replace("γ", "감마")
    text = text.replace("π", "파이")
    text = text.replace("Σ", "시그마")
    text = text.replace("0.55", "영 점 오오")
    text = text.replace("0.45", "영 점 사오")
    text = text.replace("0.9", "영 점 구")
    text = text.replace("0.5", "영 점 오")
    text = text.replace("-2.25", "마이너스 이 점 이오")
    text = text.replace("-2.75", "마이너스 이 점 칠오")
    text = text.replace("-1", "마이너스 일")
    text = text.replace("+1", "플러스 일")
    return text

SCENES = [
    # Scene 1: Introduction
    (1, [
        ("dorothy", "지니! 지난번에 유도한 벨만 방정식으로 진짜 상태 가치를 구할 수 있는 거야?"),
        ("jiny", "그럼 도로시! 벨만 방정식은 미지수가 들어있는 연립방정식이라서, 대수학 마법으로 정확한 수치를 척척 풀어낼 수 있단다!")
    ]),
    # Scene 2: Bellman power
    (2, [
        ("dorothy", "벨만 방정식의 위력을 직접 눈으로 확인해보고 싶어!"),
        ("jiny", "좋아! 복잡한 미래의 무한한 길을 단 두 개의 깔끔한 연립방정식으로 압축하는 마법을 보여줄게!")
    ]),
    # Scene 3: Grid World Intro
    (3, [
        ("dorothy", "엘원과 엘투, 딱 두 칸짜리 격자 세상이네? 룰은 어떻게 돼?"),
        ("jiny", "벽에 쾅 부딪히면 벌점 마이너스 일점이고, 탐스러운 사과를 따먹으면 보너스 플러스 일점이야! 사과는 먹어도 계속 새로 열린단다!")
    ]),
    # Scene 4: Random Policy
    (4, [
        ("dorothy", "여기서 내가 왼쪽이나 오른쪽으로 반반의 확률로 걸어간다는 거지?"),
        ("jiny", "맞아! 반반, 즉 오십 퍼센트 확률로 왼쪽이나 오른쪽을 고르는 무작위 정책을 따르는 거야!")
    ]),
    # Scene 5: L1 Infinite Return
    (5, [
        ("dorothy", "엘원에서 출발해서 영원히 움직이면 받을 수 있는 기대 수익은 어떻게 계산할까?"),
        ("jiny", "앞으로 무한히 계속해서 받을 미래 보상들의 총합인데, 끝없이 이어져서 직접 더하기는 불가능해 보여!")
    ]),
    # Scene 6: Backup Tree
    (6, [
        ("dorothy", "우와, 백업 다이어그램을 그려보니까 가지가 끝도 없이 퍼져나가네!"),
        ("jiny", "한 걸음 걸을 때마다 두 갈래씩 영원히 뻗어나가니까, 나무처럼 거대해지는 무한 분기란다!")
    ]),
    # Scene 7: Infinite to Finite
    (7, [
        ("dorothy", "다람쥐 쳇바퀴처럼 끝없는 무한 계산의 굴레에서 어떻게 빠져나오지?"),
        ("jiny", "바로 벨만 방정식이라는 마법 열쇠를 쓰면, 무한한 미래가 단 하나의 징검다리 점화식으로 쏙 정리된단다!")
    ]),
    # Scene 8: Double Sum Split
    (8, [
        ("dorothy", "벨만 방정식의 시그마 기호가 행동과 다음 상태 둘 다 더하고 있네?"),
        ("jiny", "맞아! 행동에 대한 합과 다음 상태에 대한 합을 둘로 똑 떨어지게 분리하면 단계별로 계산하기 아주 쉬워져!")
    ]),
    # Scene 9: Deterministic Transition
    (9, [
        ("dorothy", "이번 격자 세상은 발을 헛디딜 확률 없이, 내가 걸어간 칸으로 정확히 이동하지?"),
        ("jiny", "빙고! 바람이나 미끄러짐이 없는 결정적 전이라서, 다음 상태가 백 퍼센트 확실하게 정해진단다!")
    ]),
    # Scene 10: Transition Function f
    (10, [
        ("dorothy", "다음 칸이 백 퍼센트 확실하다면, 전이 확률은 어떻게 바뀌어?"),
        ("jiny", "도착할 한 곳의 확률만 일이고, 나머지 다른 곳으로 갈 확률은 몽땅 영이 된단다!")
    ]),
    # Scene 11: Sum Disappearing
    (11, [
        ("dorothy", "확률이 영인 항들을 지우니까 다음 상태 시그마 기호가 통째로 사라졌어!"),
        ("jiny", "그렇지! 오직 확실한 한 칸만 남으니, 복잡했던 상태 합산 기호가 마법처럼 펑 하고 사라진 거야!")
    ]),
    # Scene 12: Simplified Bellman Equation
    (12, [
        ("dorothy", "결정적 환경의 벨만 방정식 식 육 점 팔이 이렇게나 간단해지다니!"),
        ("jiny", "각 행동을 고를 확률에, 그때 얻는 즉각 보상과 다음 상태 가치만 쏙 곱해서 더해주면 끝이란다!")
    ]),
    # Scene 13: L1 Backup Diagram
    (13, [
        ("dorothy", "이제 엘원의 백업 다이어그램을 보면서 수식을 조립해볼까?"),
        ("jiny", "좋아! 엘원에서는 왼쪽으로 벽을 들이받는 길과, 오른쪽으로 사과를 향해 가는 딱 두 갈래 길만 보면 돼!")
    ]),
    # Scene 14: L1 Left Action
    (14, [
        ("dorothy", "엘원에서 왼쪽으로 가면 벽에 쿵 부딪혀서 제자리 엘원에 남고 감점 마이너스 일이네!"),
        ("jiny", "맞아, 오십 퍼센트 확률에 보상 마이너스 일 더하기 할인율 영 점 구 곱하기 브이 엘원을 묶어주면 돼!")
    ]),
    # Scene 15: L1 Right Action
    (15, [
        ("dorothy", "오른쪽으로 가면 엘투로 넘어가면서 달콤한 사과 보너스 플러스 일을 받네!"),
        ("jiny", "정답이야! 오십 퍼센트 확률에 보상 일 더하기 할인율 영 점 구 곱하기 브이 엘투를 곱해주면 되지!")
    ]),
    # Scene 16: L1 Equation Complete
    (16, [
        ("dorothy", "두 가지 행동을 더해서 정리하니까, 마이너스 영 점 오오 브이 엘원 더하기 영 점 사오 브이 엘투는 영이 됐어!"),
        ("jiny", "훌륭해 도로시! 미지수가 두 개인 멋진 첫 번째 일차방정식 식 육 점 구가 완성되었어!")
    ]),
    # Scene 17: L2 Backup Diagram
    (17, [
        ("dorothy", "이번에는 엘투 칸에 서 있을 때의 백업 다이어그램을 볼 차례야!"),
        ("jiny", "엘투에서도 똑같이 왼쪽과 오른쪽, 두 갈래 행동의 기대 가치를 합쳐주면 된단다!")
    ]),
    # Scene 18: L2 Left Action
    (18, [
        ("dorothy", "엘투에서 왼쪽으로 가면 엘원으로 돌아가는데, 이때 사과가 없으니 보상은 영이네?"),
        ("jiny", "맞아! 보상은 영점이고 다음 상태는 엘원이니, 오십 퍼센트에 영 점 구 곱하기 브이 엘원을 곱하면 돼!")
    ]),
    # Scene 19: L2 Right Action
    (19, [
        ("dorothy", "엘투에서 오른쪽으로 가면 벽에 부딪혀서 제자리 엘투에 남고 감점 마이너스 일점이군!"),
        ("jiny", "그렇지! 오십 퍼센트에 마이너스 일 더하기 영 점 구 곱하기 브이 엘투를 곱해주면 오른쪽 경로 완성!")
    ]),
    # Scene 20: L2 Equation Consolidation
    (20, [
        ("dorothy", "엘투의 식도 괄호를 풀고 정리하니까, 영 점 사오 브이 엘원 빼기 영 점 오오 브이 엘투는 영 점 오가 나왔어!"),
        ("jiny", "완벽해! 이렇게 해서 두 번째 일차방정식 식 육 점 십까지 완벽하게 손에 넣었단다!")
    ]),
    # Scene 21: Simultaneous Equations Setup
    (21, [
        ("dorothy", "미지수는 브이 엘원과 브이 엘투 두 개고, 식도 딱 두 개니까 중학교 연립방정식이네!"),
        ("jiny", "맞아 도로시! 가감법이나 대입법으로 두 식을 묶어서 풀기만 하면 진짜 가치 숫자가 튀어나온단다!")
    ]),
    # Scene 22: Grid World Solve
    (22, [
        ("dorothy", "연립방정식을 계산해보니 브이 엘원은 마이너스 이 점 이오, 브이 엘투는 마이너스 이 점 칠오가 나왔어!"),
        ("jiny", "정확해! 무한히 이어지던 기대 수익이 드디어 딱 떨어지는 실수 숫자로 명쾌하게 풀려났단다!")
    ]),
    # Scene 23: Value Comparison
    (23, [
        ("dorothy", "둘 다 마이너스인 것도 신기하고, 엘원이 엘투보다 더 큰 것도 재밌어!"),
        ("jiny", "벽에 부딪히기 쉬워서 마이너스지만, 엘원 옆에는 바로 사과가 있어서 첫 판에 딸 확률이 오십 퍼센트나 되니까 더 가치 있는 거야!")
    ]),
    # Scene 24: Bellman 3-Step Summary
    (24, [
        ("dorothy", "벨만 방정식을 세우고, 정리하고, 연립방정식으로 푸는 삼단계로 모든 게 해결되는구나!"),
        ("jiny", "바로 그거야! 아무리 거대한 세상이라도 벨만 방정식을 쓰면 컴퓨터가 자동으로 모든 가치를 풀어낼 수 있단다!")
    ]),
    # Scene 25: Core Summary
    (25, [
        ("dorothy", "오늘 배운 두 칸짜리 그리드 월드 벨만 예제를 마음속에 쏙 정리해두자!"),
        ("jiny", "결정적 전이의 간소화부터 연립방정식 해법까지, 핵심 정리 목록으로 확실하게 복습해보렴!")
    ]),
]

async def generate_scene(scene_num, lines, filename):
    temp_files = []
    for idx, (role, text) in enumerate(lines):
        clean_text = preprocess_text(text)
        temp_path = os.path.join(TEMP_DIR, f"s{scene_num}_{idx}.mp3")
        prof = VOICES[role]
        comm = edge_tts.Communicate(clean_text, prof['voice'], pitch=prof['pitch'], rate=prof['rate'])
        await comm.save(temp_path)
        temp_files.append(temp_path)

    final_src_path = os.path.join(OUTPUT_DIR, filename)
    final_docs_path = os.path.join(DOCS_DIR, filename)
    
    with open(final_src_path, 'wb') as outfile:
        for tf in temp_files:
            with open(tf, 'rb') as infile:
                outfile.write(infile.read())
                
    shutil.copyfile(final_src_path, final_docs_path)
    print(f"Scene {scene_num} generated: {filename}")

async def main():
    for num, lines in SCENES:
        fname = f"dialogue_6_3_scene{num}.mp3"
        await generate_scene(num, lines, fname)
    print("All 25 TTS audio files generated successfully!")

if __name__ == "__main__":
    asyncio.run(main())
