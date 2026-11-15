"""Math & LaTeX Cleaner for PowerPoint Presentations and TTS Lecture Narration.

Provides dual-mode normalization:
1. clean_slide_math(text: str) -> str:
   Transforms LaTeX syntax, mathematical notations, and Greek codes into
   clean, professional Unicode typography for visual PowerPoint slides.
   Ensures 0 raw LaTeX commands (e.g. \\varepsilon, \\frac, $, ₩) remain on screen.

2. clean_notes_math(text: str) -> str:
   Translates mathematical notation, Greek letters, RL variables, and equations
   into natural, fluent Korean spoken language (구술형 한국어 독음) so that
   any Text-To-Speech (TTS) engine narrates the lecture seamlessly without pronouncing
   raw symbols or English command names.
"""

import re
from typing import Dict, Match

# Map of LaTeX / Won-escaped Greek letters to clean Unicode characters for slides
GREEK_TO_UNICODE: Dict[str, str] = {
    "varepsilon": "ε",
    "epsilon": "ε",
    "vareps": "ε",
    "alpha": "α",
    "beta": "β",
    "gamma": "γ",
    "delta": "δ",
    "theta": "θ",
    "vartheta": "θ",
    "lambda": "λ",
    "mu": "μ",
    "pi": "π",
    "varpi": "π",
    "rho": "ρ",
    "varrho": "ρ",
    "sigma": "σ",
    "tau": "τ",
    "phi": "φ",
    "varphi": "φ",
    "omega": "ω",
    "eta": "η",
    "zeta": "ζ",
    "xi": "ξ",
    "chi": "χ",
    "psi": "ψ",
    "nabla": "∇",
    "partial": "∂",
    "Delta": "Δ",
    "Gamma": "Γ",
    "Theta": "Θ",
    "Lambda": "Λ",
    "Sigma": "Σ",
    "Phi": "Φ",
    "Psi": "Ψ",
    "Omega": "Ω",
}

# Number to Korean phonetic reading for percentages and small numbers
KOREAN_NUM_MAP = {
    "0": "영",
    "1": "일",
    "2": "이",
    "3": "삼",
    "4": "사",
    "5": "오",
    "6": "육",
    "7": "칠",
    "8": "팔",
    "9": "구",
    "10": "십",
    "20": "이십",
    "30": "삼십",
    "40": "사십",
    "50": "오십",
    "60": "육십",
    "70": "칠십",
    "80": "팔십",
    "90": "구십",
    "100": "백",
}


def _int_to_korean(num: int) -> str:
    """Convert integer (0~999) to Sino-Korean pronunciation."""
    if num == 0:
        return "영"
    if num == 100:
        return "백"
    if str(num) in KOREAN_NUM_MAP:
        return KOREAN_NUM_MAP[str(num)]

    res = ""
    if num >= 100:
        hundreds = num // 100
        num %= 100
        if hundreds == 1:
            res += "백"
        else:
            res += f"{KOREAN_NUM_MAP.get(str(hundreds), '')}백"

    if num >= 10:
        tens = num // 10
        num %= 10
        if tens == 1:
            res += "십"
        else:
            res += f"{KOREAN_NUM_MAP.get(str(tens), '')}십"

    if num > 0:
        res += KOREAN_NUM_MAP.get(str(num), "")

    return res


def number_to_korean_percentage(match: Match) -> str:
    """Convert '10%' -> '십 퍼센트', '5%' -> '오 퍼센트', '92.5%' -> '구십이 점 오 퍼센트'."""
    val = match.group(1)
    if val in KOREAN_NUM_MAP:
        return f"{KOREAN_NUM_MAP[val]} 퍼센트"
    try:
        if "." in val:
            parts = val.split(".")
            int_part = int(parts[0])
            dec_part = parts[1]
            int_str = _int_to_korean(int_part)
            dec_str = " ".join(KOREAN_NUM_MAP.get(c, c) for c in dec_part)
            return f"{int_str} 점 {dec_str} 퍼센트"
        int_val = int(val)
        return f"{_int_to_korean(int_val)} 퍼센트"
    except Exception:
        return f"{val} 퍼센트"


def decimal_to_korean(match: Match) -> str:
    """Convert small decimal numbers like 0.1 -> 영 점 일, 0.01 -> 영 점 영일, 0.9 -> 영 점 구."""
    val = match.group(0)
    try:
        parts = val.split(".")
        int_part = KOREAN_NUM_MAP.get(parts[0], parts[0])
        dec_str = "".join(KOREAN_NUM_MAP.get(c, c) for c in parts[1])
        return f"{int_part} 점 {dec_str}"
    except Exception:
        return val


def clean_slide_math(text: str) -> str:
    """Transform LaTeX math markup into clear, beautiful Unicode typography for slides.

    Examples:
        '강제로 \\varepsilon(10%)의 무작위 탐색' -> '강제로 ε(10%)의 무작위 탐색'
        '$\\rho = \\frac{\\pi(a|s)}{b(a|s)}$' -> 'ρ = π(a|s) / b(a|s)'
        '할인율 $\\gamma = 0.9$' -> '할인율 γ = 0.9'
    """
    if not text:
        return ""

    t = text

    # 0. Fix ASCII control characters caused by faulty escape decoding
    t = t.replace("\x07", "\\a").replace("\x08", "\\b")
    t = t.replace("\x0b", "\\v").replace("\x0c", "\\f")
    t = re.sub(r"₩([a-zA-Z]+)", r"\\\1", t)

    # 1. LaTeX Greek symbols to Unicode (longer names first)
    for cmd in sorted(GREEK_TO_UNICODE.keys(), key=len, reverse=True):
        t = re.sub(rf"\\{cmd}\b", GREEK_TO_UNICODE[cmd], t)

    # 2. Fractions: \frac{A}{B} -> A / B or (A) / (B)
    while "\\frac" in t:
        idx = t.find("\\frac")
        open1 = t.find("{", idx)
        if open1 == -1:
            break
        depth, pos1 = 1, open1 + 1
        while pos1 < len(t) and depth > 0:
            if t[pos1] == "{":
                depth += 1
            elif t[pos1] == "}":
                depth -= 1
            pos1 += 1
        close1 = pos1 - 1
        num = t[open1 + 1 : close1].strip()

        open2 = t.find("{", close1)
        if open2 == -1:
            break
        depth, pos2 = 1, open2 + 1
        while pos2 < len(t) and depth > 0:
            if t[pos2] == "{":
                depth += 1
            elif t[pos2] == "}":
                depth -= 1
            pos2 += 1
        close2 = pos2 - 1
        den = t[open2 + 1 : close2].strip()

        t = t[:idx] + f"{num} / {den}" + t[close2 + 1 :]

    # 3. Square roots: \sqrt{x} -> √(x)
    t = re.sub(r"\\sqrt\{([^{}]+)\}", r"√(\1)", t)

    # 4. Operators and relation symbols
    t = re.sub(r"\\leftarrow|\\gets", "←", t)
    t = re.sub(r"\\rightarrow|\\to", "→", t)
    t = re.sub(r"\\leftrightarrow", "↔", t)
    t = re.sub(r"\\approx", "≈", t)
    t = re.sub(r"\\neq", "≠", t)
    t = re.sub(r"\\leq|\\le", "≤", t)
    t = re.sub(r"\\geq|\\ge", "≥", t)
    t = re.sub(r"\\times", "×", t)
    t = re.sub(r"\\cdot", "·", t)
    t = re.sub(r"\\sum\b", "∑", t)
    t = re.sub(r"\\prod\b", "∏", t)
    t = re.sub(r"\\infty\b", "∞", t)
    t = re.sub(r"\\pm\b", "±", t)
    t = re.sub(r"\\in\b", "∈", t)
    t = re.sub(r"\\notin\b", "∉", t)

    # 5. Text formatting wrappers inside formulas
    t = re.sub(r"\\(text|mathbf|mathit|mathrm|bm|operatorname)\{([^{}]+)\}", r"\2", t)
    t = re.sub(r"\\mathbb\{E\}", "E", t)
    t = re.sub(r"\\mathbb\{R\}", "ℝ", t)
    t = re.sub(r"\\max\b", "max", t)
    t = re.sub(r"\\min\b", "min", t)
    t = re.sub(r"\\argmax|\\arg\\max", "argmax", t)

    # 6. Common superscripts
    t = re.sub(r"\^2\b|\^\{2\}", "²", t)
    t = re.sub(r"\^3\b|\^\{3\}", "³", t)
    t = re.sub(r"\^T\b|\^\{T\}", "ᵀ", t)
    t = re.sub(r"\^\*|\^\{\*\}", "*", t)

    # 7. Strip dollar delimiters ($ ... $ or $$ ... $$)
    t = re.sub(r"\$\$(.*?)\$\$", r"\1", t, flags=re.DOTALL)
    t = re.sub(r"\$(.*?)\$", r"\1", t)

    # 8. Clean any remaining raw LaTeX backslashes attached to word identifiers
    t = re.sub(r"\\([a-zA-Z]+)", r"\1", t)
    t = t.replace("\\", "")

    return t.strip()


def clean_notes_math(text: str) -> str:
    """Translate formulas, Greek symbols, and RL expressions into natural spoken Korean phonetics.

    Ensures TTS engines pronounce equations accurately and smoothly as a human lecturer would.
    """
    if not text:
        return ""

    t = text

    # 0. Fix ASCII control characters caused by faulty escape decoding
    t = t.replace("\x07", "\\a").replace("\x08", "\\b")
    t = t.replace("\x0b", "\\v").replace("\x0c", "\\f")
    t = re.sub(r"₩([a-zA-Z]+)", r"\\\1", t)

    # 1. Clean markdown headers, bold, code wrappers
    t = re.sub(r"^\s*>\s*", "", t)  # strip leading blockquote marker
    t = re.sub(r"\*\*", "", t)
    t = re.sub(r"\*", "", t)
    t = re.sub(r"`", "", t)
    t = re.sub(r"\[(식\s*[0-9\.]+)\]", r"\1", t)
    t = re.sub(r"\[(그림\s*[0-9\.]+)\]", r"\1", t)

    # 2. High-priority composite phrases: e.g. \varepsilon(10%) -> 탐색 확률 입실론 십 퍼센트
    t = re.sub(
        r"(?:\\?varepsilon|\\?epsilon|\\?vareps|ε|ϵ)\s*\(\s*(\d+(?:\.\d+)?)\s*%\s*\)",
        lambda m: f"탐색 확률 입실론 {number_to_korean_percentage(m)}",
        t,
    )
    t = re.sub(
        r"(?:\\?varepsilon|\\?epsilon|\\?vareps|ε|ϵ)\s*\(([^)]+)\)",
        r"탐색 확률 입실론 \1",
        t,
    )

    # 3. Percentages in general: (10%) -> 십 퍼센트, 10% -> 십 퍼센트
    t = re.sub(r"\(\s*(\d+(?:\.\d+)?)\s*%\s*\)", lambda m: f" {number_to_korean_percentage(m)}", t)
    t = re.sub(r"(\d+(?:\.\d+)?)\s*%", number_to_korean_percentage, t)

    # 4. Fractions: \frac{A}{B} -> B 분의 A
    while "\\frac" in t or "frac{" in t:
        idx = t.find("\\frac")
        if idx == -1:
            idx = t.find("frac{")
        open1 = t.find("{", idx)
        if open1 == -1:
            break
        depth, pos1 = 1, open1 + 1
        while pos1 < len(t) and depth > 0:
            if t[pos1] == "{":
                depth += 1
            elif t[pos1] == "}":
                depth -= 1
            pos1 += 1
        close1 = pos1 - 1
        num = t[open1 + 1 : close1].strip()

        open2 = t.find("{", close1)
        if open2 == -1:
            break
        depth, pos2 = 1, open2 + 1
        while pos2 < len(t) and depth > 0:
            if t[pos2] == "{":
                depth += 1
            elif t[pos2] == "}":
                depth -= 1
            pos2 += 1
        close2 = pos2 - 1
        den = t[open2 + 1 : close2].strip()

        t = t[:idx] + f" {den} 분의 {num} " + t[close2 + 1 :]

    # 5. Composite RL functions & equations
    # Q and V functions
    t = re.sub(r"\bq_π\(s,\s*a\)|\bq_\\?pi\(s,\s*a\)", "큐 파이 에스 에이", t)
    t = re.sub(r"\bq_π\(s\',\s*a\'\)|\bq_\\?pi\(s\',\s*a\'\)", "큐 파이 에스 프라임 에이 프라임", t)
    t = re.sub(r"\bv_π\(s\)|\bv_\\?pi\(s\)", "브이 파이 에스", t)
    t = re.sub(r"\bv_π\(s\'\)|\bv_\\?pi\(s\'\)", "브이 파이 에스 프라임", t)
    t = re.sub(r"\bq_\*\(s,\s*a\)", "큐 스타 에스 에이", t)
    t = re.sub(r"\bv_\*\(s\)", "브이 스타 에스", t)

    t = re.sub(r"\bQ\(s,\s*a\)", "큐 에스 에이", t)
    t = re.sub(r"\bQ\(s\',\s*a\'\)", "큐 에스 프라임 에이 프라임", t)
    t = re.sub(r"\bQ\(S_\{t\+1\},\s*A_\{t\+1\}\)|\bQ\(S_t\+1,\s*A_t\+1\)", "큐 오브 에스티 플러스 원 에이티 플러스 원", t)
    t = re.sub(r"\bQ\(S_t,\s*A_t\)", "큐 오브 에스티 에이티", t)
    t = re.sub(r"\bV\(s\)", "브이 에스", t)
    t = re.sub(r"\bV\(s\'\)", "브이 에스 프라임", t)
    t = re.sub(r"\bV\(S_\{t\+1\}\)|\bV\(S_t\+1\)", "브이 오브 에스티 플러스 원", t)
    t = re.sub(r"\bV\(S_t\)", "브이 오브 에스티", t)

    # Transition probability & Policies
    t = re.sub(r"p\(s\'\s*\|\s*s,\s*a\)", "피 에스 프라임 기븐 에스 에이", t)
    t = re.sub(r"p\(s\'\s*\|\s*s\)", "피 에스 프라임 기븐 에스", t)
    t = re.sub(r"(?:π|\\?pi)\(a\'\s*\|\s*s\'\)", "파이 에이 프라임 기븐 에스 프라임", t)
    t = re.sub(r"(?:π|\\?pi)\(a\s*\|\s*s\)", "파이 에이 기븐 에스", t)
    t = re.sub(r"b\(a\'\s*\|\s*s\'\)", "비 에이 프라임 기븐 에스 프라임", t)
    t = re.sub(r"b\(a\s*\|\s*s\)", "비 에이 기븐 에스", t)
    t = re.sub(r"r\(s,\s*a,\s*s\'\)", "알 에스 에이 에스 프라임", t)
    t = re.sub(r"r\(s,\s*a\)", "알 에스 에이", t)

    # Summations
    t = re.sub(r"(?:\\sum|∑)_\{s\'\}|(?:\\sum|∑)_\{s'\}|(?:\\sum|∑)_s\'|(?:\\sum|∑)_s'", "시그마 에스 프라임,", t)
    t = re.sub(r"(?:\\sum|∑)_\{a\'\}|(?:\\sum|∑)_\{a'\}|(?:\\sum|∑)_a\'|(?:\\sum|∑)_a'", "시그마 에이 프라임,", t)
    t = re.sub(r"(?:\\sum|∑)_\{s\}|(?:\\sum|∑)_s", "시그마 에스,", t)
    t = re.sub(r"(?:\\sum|∑)_\{a\}|(?:\\sum|∑)_a", "시그마 에이,", t)
    t = re.sub(r"\\sum\b|∑", "시그마 합 ", t)

    # Subscripts with time t
    t = re.sub(r"\bR_\{t\+1\}|\bR_t\+1", "알 티 플러스 일", t)
    t = re.sub(r"\bS_\{t\+1\}|\bS_t\+1", "에스 티 플러스 일", t)
    t = re.sub(r"\bA_\{t\+1\}|\bA_t\+1", "에이 티 플러스 일", t)
    t = re.sub(r"\bG_t\b|G_t", "수익 지 티", t)
    t = re.sub(r"\bS_t\b|S_t", "에스 티", t)
    t = re.sub(r"\bA_t\b|A_t", "에이 티", t)
    t = re.sub(r"\bR_t\b|R_t", "알 티", t)
    t = re.sub(r"\bdelta_t\b|δ_t|델타_t", "시간차 오차 델타 티", t)

    # Primed variables
    t = re.sub(r"\bs\'|\bs’", "에스 프라임", t)
    t = re.sub(r"\ba\'|\ba’", "에이 프라임", t)

    # Greek letters with appropriate particles
    t = re.sub(r"\\?varepsilon|\\?epsilon|\\?vareps|\bepsilon\b|ε|ϵ", "입실론", t)
    t = re.sub(r"\\?gamma|\bgamma\b|γ", "감마", t)
    t = re.sub(r"\\?pi|\bpi\b|π", "파이", t)
    t = re.sub(r"\\?rho|\brho\b|ρ", "로", t)
    t = re.sub(r"\\?alpha|\balpha\b|α", "알파", t)
    t = re.sub(r"\\?theta|\btheta\b|θ", "세타", t)
    t = re.sub(r"\\?lambda|\blambda\b|λ", "람다", t)
    t = re.sub(r"\\?sigma|\bsigma\b|σ", "시그마", t)
    t = re.sub(r"\\?delta|\bdelta\b|δ", "델타", t)
    t = re.sub(r"\\?mu|\bmu\b|μ", "뮤", t)
    t = re.sub(r"\\?tau|\btau\b|τ", "타우", t)
    t = re.sub(r"\\?eta|\beta\b|η", "에타", t)
    t = re.sub(r"\\?phi|\bphi\b|φ", "파이", t)
    t = re.sub(r"\\?omega|\bomega\b|ω", "오메가", t)
    t = re.sub(r"\\?nabla|∇", "그래디언트", t)
    t = re.sub(r"\\?partial|∂", "편미분", t)

    # Math operators and expectations
    t = re.sub(r"\\mathbb\{E\}|E\[", "기댓값 이 대괄호 ", t)
    t = re.sub(r"\\argmax|\\arg\\max|\bargmax\b", "아그맥스 ", t)
    t = re.sub(r"\\max_a|\bmax_a\b", "맥스 에이 ", t)
    t = re.sub(r"\\max\b", "최댓값 맥스 ", t)
    t = re.sub(r"\\min\b", "최솟값 민 ", t)

    # RL programming and algorithm terms
    t = re.sub(r"ε-탐욕|입실론-탐욕|\\epsilon-greedy", "입실론 탐욕", t)
    t = re.sub(r"TD\(0\)", "티디 제로", t)
    t = re.sub(r"\bTD\b", "티디", t)
    t = re.sub(r"\bMC\b", "엠씨", t)
    t = re.sub(r"\bDP\b", "디피", t)
    t = re.sub(r"\bSARSA\b", "살사", t)
    t = re.sub(r"Q-러닝|Q-Learning|\bQLearning\b", "큐러닝", t)
    t = re.sub(r"\bDQN\b", "디큐엔", t)
    t = re.sub(r"SarsaOffPolicyAgent", "살사 오프 정책 에이전트", t)
    t = re.sub(r"SarsaAgent", "살사 에이전트", t)
    t = re.sub(r"TdAgent", "티디 에이전트", t)
    t = re.sub(r"QLearningAgentSimple", "큐러닝 에이전트 심플", t)
    t = re.sub(r"QLearningAgentStep1", "큐러닝 에이전트 스텝 원", t)
    t = re.sub(r"QLearningAgent", "큐러닝 에이전트", t)
    t = re.sub(r"GridWorld", "그리드월드", t)
    t = re.sub(r"defaultdict", "디폴트딕트", t)
    t = re.sub(r"\bdeque\b", "디큐", t)
    t = re.sub(r"maxlen", "맥스렌", t)
    t = re.sub(r"get_action", "겟 액션 메서드", t)
    t = re.sub(r"greedy_probs", "그리디 프랍스 함수", t)
    t = re.sub(r"\bupdate\b", "업데이트 메서드", t)
    t = re.sub(r"\breset\b", "리셋 메서드", t)
    t = re.sub(r"\beval\b", "이밸 메서드", t)
    t = re.sub(r"\bstep\b", "스텝 메서드", t)
    t = re.sub(r"\bdone\b", "던 플래그", t)
    t = re.sub(r"self\.pi", "셀프 닷 파이", t)
    t = re.sub(r"self\.b", "셀프 닷 비", t)
    t = re.sub(r"self\.Q", "셀프 닷 큐", t)
    t = re.sub(r"self\.V", "셀프 닷 브이", t)
    t = re.sub(r"self\.memory", "셀프 닷 메모리", t)
    t = re.sub(r"self\.gamma", "셀프 닷 감마", t)
    t = re.sub(r"self\.alpha", "셀프 닷 알파", t)
    t = re.sub(r"self\.epsilon", "셀프 닷 입실론", t)
    t = re.sub(r"next_state", "넥스트 스테이트", t)
    t = re.sub(r"next_action", "넥스트 액션", t)
    t = re.sub(r"next_q_max", "넥스트 큐 맥스", t)
    t = re.sub(r"next_q", "넥스트 큐", t)
    t = re.sub(r"\btarget\b", "타겟", t)

    # Relations and arrows
    t = re.sub(r"\\leftarrow|\\gets|←", "로 갱신", t)
    t = re.sub(r"\\rightarrow|\\to|→", "에서", t)
    t = re.sub(r"\\approx|≈", " 약 ", t)
    t = re.sub(r"\\neq|≠", " 다르다 ", t)
    t = re.sub(r"\\leq|\\le|≤", " 이하 ", t)
    t = re.sub(r"\\geq|\\ge|≥", " 이상 ", t)

    # Convert small decimals like 0.1, 0.01, 0.9 when following math terms
    t = re.sub(r"(?<=[=:\s])(0\.\d+)", decimal_to_korean, t)

    # Equals in formula context (avoid changing Korean sentences without formulas)
    t = re.sub(r"\s*=\s*", "는 ", t)
    # Fix particle agreement: e.g. 입실론는 -> 입실론은
    t = t.replace("입실론는", "입실론은")

    # Math plus / multiply in formula context
    t = re.sub(r"\s*\+\s*", " 더하기 ", t)
    t = re.sub(r"\s*[×·]\s*|\\times|\\cdot", " 곱하기 ", t)

    # Strip dollar signs
    t = re.sub(r"\$\$|\$", "", t)

    # Clean double spaces, brackets, remaining backslashes
    t = re.sub(r"\\[a-zA-Z]+", "", t)
    t = re.sub(r"[{}\[\]]", " ", t)
    t = re.sub(r"\s+", " ", t)

    return t.strip()
