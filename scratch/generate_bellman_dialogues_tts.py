import asyncio
import os
import re
import shutil
import edge_tts

BASE_DIR = "/Users/hojin9/dev/jinysite/강화학습"
TEMP_DIR = "/tmp/tts_bellman_gen"

os.makedirs(TEMP_DIR, exist_ok=True)

# Voice profiles as defined in audio.md
VOICES = {
    'dorothy': {'voice': 'ko-KR-SunHiNeural', 'pitch': '+22Hz', 'rate': '+3%'},
    'jiny': {'voice': 'ko-KR-InJoonNeural', 'pitch': '+2Hz', 'rate': '+0%'},
    'toto': {'voice': 'ko-KR-SunHiNeural', 'pitch': '+38Hz', 'rate': '+8%'},
}

SECTIONS = [
    {
        'id': '6_4',
        'md_path': os.path.join(BASE_DIR, "src/06_벨만_방정식/6_4_행동_가치_함수_Q_함수와_벨만_방정식/index.md"),
        'src_audio': os.path.join(BASE_DIR, "src/06_벨만_방정식/6_4_행동_가치_함수_Q_함수와_벨만_방정식/audio"),
        'docs_audio': os.path.join(BASE_DIR, "docs/06_벨만_방정식/6_4_행동_가치_함수_Q_함수와_벨만_방정식/audio"),
    },
    {
        'id': '6_5',
        'md_path': os.path.join(BASE_DIR, "src/06_벨만_방정식/6_5_벨만_최적_방정식/index.md"),
        'src_audio': os.path.join(BASE_DIR, "src/06_벨만_방정식/6_5_벨만_최적_방정식/audio"),
        'docs_audio': os.path.join(BASE_DIR, "docs/06_벨만_방정식/6_5_벨만_최적_방정식/audio"),
    },
    {
        'id': '6_6',
        'md_path': os.path.join(BASE_DIR, "src/06_벨만_방정식/6_6_벨만_최적_방정식의_예/index.md"),
        'src_audio': os.path.join(BASE_DIR, "src/06_벨만_방정식/6_6_벨만_최적_방정식의_예/audio"),
        'docs_audio': os.path.join(BASE_DIR, "docs/06_벨만_방정식/6_6_벨만_최적_방정식의_예/audio"),
    },
    {
        'id': '6_7',
        'md_path': os.path.join(BASE_DIR, "src/06_벨만_방정식/6_7_정리/index.md"),
        'src_audio': os.path.join(BASE_DIR, "src/06_벨만_방정식/6_7_정리/audio"),
        'docs_audio': os.path.join(BASE_DIR, "docs/06_벨만_방정식/6_7_정리/audio"),
    },
]

def preprocess_text(text: str) -> str:
    # Remove markdown & quotes
    text = re.sub(r"[\"'\`\*]", "", text)
    # LaTeX / math replacements
    replacements = [
        (r"\$v_\*\(s\)\$", "브이 스타 에스"),
        (r"\$v_\*\(s'\)\$", "브이 스타 에스 프라임"),
        (r"\$q_\*\(s,\s*a\)\$", "큐 스타 에스 에이"),
        (r"\$q_\*\(s',\s*a'\)\$", "큐 스타 에스 프라임 에이 프라임"),
        (r"\$v_\*\(s_1\)\$", "브이 스타 에스 원"),
        (r"\$v_\*\(s_2\)\$", "브이 스타 에스 투"),
        (r"\$v_\*\(s_3\)\$", "브이 스타 에스 쓰리"),
        (r"\$v_\*\(s_4\)\$", "브이 스타 에스 포"),
        (r"\$v_\\pi\(s\)\$", "브이 파이 에스"),
        (r"\$v_\\pi\(s'\)\$", "브이 파이 에스 프라임"),
        (r"\$q_\\pi\(s,\s*a\)\$", "큐 파이 에스 에이"),
        (r"\$q_\\pi\(s',\s*a'\)\$", "큐 파이 에스 프라임 에이 프라임"),
        (r"\$v_\*\$", "브이 스타"),
        (r"\$q_\*\$", "큐 스타"),
        (r"v_\*", "브이 스타"),
        (r"q_\*", "큐 스타"),
        (r"\$\\pi_\*\$", "최적 정책 파이 스타"),
        (r"\$\\pi_\*\(a\s*\|\s*s\)\$", "최적 정책 파이 스타"),
        (r"\$\\pi_\*\(a'\s*\|\s*s'\)\$", "최적 정책 파이 스타"),
        (r"\$\\pi\$", "파이"),
        (r"\$\\mu_\*\(s\)\$", "결정적 최적 정책 뮤 스타"),
        (r"\$\\mu_\*\$", "뮤 스타"),
        (r"\$\\max_\{a'\}\$", "맥스 에이 프라임"),
        (r"\$\\max_a\$", "맥스 에이"),
        (r"\$\\max_\{a\}\$", "맥스 에이"),
        (r"\$\\max_\\pi\$", "맥스 파이"),
        (r"\$\\max_\{\\pi\}\$", "맥스 파이"),
        (r"\$\\max\$", "맥스"),
        (r"\\max", "맥스"),
        (r"\$\\argmax\$", "아그맥스"),
        (r"argmax", "아그맥스"),
        (r"\$\\sum_\{a,\s*s'\}\$", "시그마 에이 에스 프라임"),
        (r"\$\\sum_\{s'\}\$", "시그마 에스 프라임"),
        (r"\$\\sum_a\$", "시그마 에이"),
        (r"\$\\sum_\{a'\}\$", "시그마 에이 프라임"),
        (r"\$\\sum\$", "시그마"),
        (r"\$\\gamma\$", "감마"),
        (r"\$s'\$", "에스 프라임"),
        (r"\$a'\$", "에이 프라임"),
        (r"\$s_1\$", "에스 원"),
        (r"\$s_2\$", "에스 투"),
        (r"\$s_3\$", "에스 쓰리"),
        (r"\$s_4\$", "에스 포"),
        (r"\$a_1\$", "에이 원"),
        (r"\$a_2\$", "에이 투"),
        (r"\$a_3\$", "에이 쓰리"),
        (r"\$a_4\$", "에이 포"),
        (r"\(s,\s*a\)", "에스 에이"),
        (r"\(s',\s*a'\)", "에스 프라임 에이 프라임"),
        (r"\$s\$", "에스"),
        (r"\$a\$", "에이"),
        (r"\$r\$", "알"),
        (r"\$p\$", "피"),
        (r"\$q\$", "큐"),
        (r"\$v\$", "브이"),
        (r"Q-러닝", "큐러닝"),
        (r"Q 러닝", "큐러닝"),
        (r"Q-Learning", "큐러닝"),
        (r"DQN", "디큐엔"),
        (r"MDP", "엠디피"),
        (r"DP", "디피"),
        (r"Q 함수", "큐 함수"),
        (r"V 함수", "브이 함수"),
        (r"Q값", "큐값"),
        (r"V값", "브이값"),
        (r"-2\.0점", "마이너스 이 점 영 점"),
        (r"\+4\.0점", "플러스 사 점 영 점"),
        (r"0\.0점", "영 점 영 점"),
        (r"-2점", "마이너스 이 점"),
        (r"4점", "사 점"),
        (r"0점", "영 점"),
        (r"100%", "백 퍼센트"),
        (r"50%", "오십 퍼센트"),
        (r"0%", "영 퍼센트"),
        (r"2 × 2", "이 곱하기 이"),
        (r"2×2", "이 곱하기 이"),
    ]
    for pat, rep in replacements:
        text = re.sub(pat, rep, text)
    # Clean any leftover $ signs, backslashes, emojis
    text = re.sub(r"[\$\\👧🐱🐶]", "", text)
    return text.strip()

def parse_scenes(md_path):
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = r"<audio src=\"\./audio/([^\"]+)\"[^>]*></audio>\s*</div>\s*((?:>[^\n]*(?:\n|$))+)"
    matches = re.findall(pattern, content)
    scenes = []

    for fname, block in matches:
        lines = []
        for line in block.split("\n"):
            line = line.strip()
            if not line or not line.startswith(">"):
                continue
            line = line[1:].strip()
            speaker = None
            text = ""
            if "**도로시**:" in line or "**도로시** :" in line:
                speaker = "dorothy"
                text = line.split("**:", 1)[-1].strip() if "**:" in line else line.split("** :", 1)[-1].strip()
            elif "**지니**:" in line or "**지니** :" in line:
                speaker = "jiny"
                text = line.split("**:", 1)[-1].strip() if "**:" in line else line.split("** :", 1)[-1].strip()
            elif "**토토**:" in line or "**토토** :" in line:
                speaker = "toto"
                text = line.split("**:", 1)[-1].strip() if "**:" in line else line.split("** :", 1)[-1].strip()
            
            if speaker and text:
                lines.append((speaker, text))
        scenes.append((fname, lines))
    return scenes

async def generate_single_scene(sec_id, fname, lines, src_dir, docs_dir):
    temp_files = []
    for idx, (speaker, raw_text) in enumerate(lines):
        clean_text = preprocess_text(raw_text)
        temp_file = os.path.join(TEMP_DIR, f"{sec_id}_{fname}_{idx}.mp3")
        prof = VOICES[speaker]
        comm = edge_tts.Communicate(clean_text, prof['voice'], pitch=prof['pitch'], rate=prof['rate'])
        await comm.save(temp_file)
        temp_files.append(temp_file)

    src_file = os.path.join(src_dir, fname)
    docs_file = os.path.join(docs_dir, fname)

    with open(src_file, 'wb') as outfile:
        for tf in temp_files:
            with open(tf, 'rb') as infile:
                outfile.write(infile.read())

    shutil.copyfile(src_file, docs_file)
    print(f"[{sec_id}] Successfully generated: {fname} ({len(lines)} utterances, {os.path.getsize(src_file)} bytes)")

async def process_section(sec):
    sec_id = sec['id']
    md_path = sec['md_path']
    src_dir = sec['src_audio']
    docs_dir = sec['docs_audio']

    os.makedirs(src_dir, exist_ok=True)
    os.makedirs(docs_dir, exist_ok=True)

    scenes = parse_scenes(md_path)
    print(f"\n==========================================")
    print(f"Processing Section {sec_id}: {len(scenes)} scenes found in {os.path.basename(md_path)}")
    print(f"==========================================")

    for fname, lines in scenes:
        await generate_single_scene(sec_id, fname, lines, src_dir, docs_dir)

async def main():
    print("Starting Bellman Chapters 6.4, 6.5, 6.6, 6.7 TTS Generation...")
    for sec in SECTIONS:
        await process_section(sec)
    print("\n🎉 ALL 67 TTS DIALOGUE MP3 FILES GENERATED AND SYNCED SUCCESSFULLY! 🎉")

if __name__ == "__main__":
    asyncio.run(main())
