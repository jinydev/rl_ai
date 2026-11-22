"""Math & LaTeX Cleaner for PowerPoint Presentations and TTS Lecture Narration.

Provides dual-mode normalization:
1. clean_slide_math(text: str) -> str:
   Transforms LaTeX syntax, mathematical notations, HTML formatting (sup/sub/b/i),
   and Markdown markers into clean, professional Unicode typography for visual PowerPoint slides.
   Ensures 0 raw LaTeX commands (e.g. \\varepsilon, \\frac, $, ₩) and 0 raw HTML/Markdown markers remain on screen.

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

SUPERSCRIPT_MAP: Dict[str, str] = {
    "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴",
    "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹",
    "+": "⁺", "-": "⁻", "=": "⁼", "(": "⁽", ")": "⁾",
    "n": "ⁿ", "i": "ⁱ", "T": "ᵀ", "N": "ᴺ", "x": "ˣ",
    "y": "ʸ", "*": "",
}

SUBSCRIPT_MAP: Dict[str, str] = {
    "0": "₀", "1": "₁", "2": "₂", "3": "₃", "4": "₄",
    "5": "₅", "6": "₆", "7": "₇", "8": "₈", "9": "₉",
    "+": "₊", "-": "₋", "=": "₌", "(": "₍", ")": "₎",
    "a": "ₐ", "e": "ₑ", "h": "ₕ", "i": "ᵢ", "j": "ⱼ",
    "k": "ₖ", "l": "ₗ", "m": "ₘ", "n": "ₙ", "o": "ₒ",
    "p": "ₚ", "r": "ᵣ", "s": "ₛ", "t": "ₜ", "u": "ᵤ",
    "v": "ᵥ", "x": "ₓ", "*": "",
}


def to_superscript(s: str) -> str:
    cleaned = s.replace("*", "").replace(" ", "")
    if all(c in SUPERSCRIPT_MAP for c in cleaned):
        return "".join(SUPERSCRIPT_MAP.get(c, c) for c in cleaned)
    return f"^{cleaned}"


def to_subscript(s: str) -> str:
    cleaned = s.replace("*", "").replace(" ", "")
    if all(c in SUBSCRIPT_MAP for c in cleaned):
        return "".join(SUBSCRIPT_MAP.get(c, c) for c in cleaned)
    return f"_{cleaned}"


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
    """Transform LaTeX math markup, HTML tags, and Markdown emphasis into clear Unicode typography for slides.

    Examples:
        '*y* = 3*x*<sup>2</sup>' -> 'y = 3x²'
        '**d*y* / d*x* = 6*x***' -> 'dy / dx = 6x'
        '`y.backward()`' -> 'y.backward()'
        '$\\rho = \\frac{\\pi(a|s)}{b(a|s)}$' -> 'ρ = π(a|s) / b(a|s)'
        '할인율 $\\gamma = 0.9$' -> '할인율 γ = 0.9'
    """
    if not text:
        return ""

    t = text

    # 0. Strip metadata div blocks like <div align="right"><b>...</b></div>
    t = re.sub(r"<div\b[^>]*>.*?</div>", "", t, flags=re.IGNORECASE | re.DOTALL)

    # 1. HTML sup / sub conversions
    t = re.sub(r"<sup\b[^>]*>(.*?)</sup>", lambda m: to_superscript(m.group(1)), t, flags=re.IGNORECASE)
    t = re.sub(r"<sub\b[^>]*>(.*?)</sub>", lambda m: to_subscript(m.group(1)), t, flags=re.IGNORECASE)

    # 2. HTML formatting tags strip: <b>, </b>, <i>, </i>, <code>, </code>, <span...>, </p>, etc.
    t = re.sub(r"</?(?:b|strong|i|em|code|span|p|br|div)\b[^>]*>", "", t, flags=re.IGNORECASE)

    # 3. Fix ASCII control characters caused by faulty escape decoding
    t = t.replace("\x07", "\\a").replace("\x08", "\\b")
    t = t.replace("\x0b", "\\v").replace("\x0c", "\\f")
    t = re.sub(r"₩([a-zA-Z]+)", r"\\\1", t)

    # 4. LaTeX Greek symbols to Unicode (longer names first)
    for cmd in sorted(GREEK_TO_UNICODE.keys(), key=len, reverse=True):
        t = re.sub(rf"\\{cmd}\b", GREEK_TO_UNICODE[cmd], t)

    # 5. Fractions: \frac{A}{B} -> A / B or (A) / (B)
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

    # 6. Square roots: \sqrt{x} -> √(x)
    t = re.sub(r"\\sqrt\{([^{}]+)\}", r"√(\1)", t)

    # 7. LaTeX Subscripts & Superscripts
    t = re.sub(r"\^\{([^{}]+)\}", lambda m: to_superscript(m.group(1)), t)
    t = re.sub(r"\^([0-9a-zA-Z*])", lambda m: to_superscript(m.group(1)), t)
    t = re.sub(r"_\{([^{}]+)\}", lambda m: to_subscript(m.group(1)), t)
    t = re.sub(r"_([0-9a-zA-Z*])", lambda m: to_subscript(m.group(1)), t)

    # 8. Operators and relation symbols
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

    # 9. Text formatting wrappers inside formulas
    t = re.sub(r"\\(text|mathbf|mathit|mathrm|bm|operatorname)\{([^{}]+)\}", r"\2", t)
    t = re.sub(r"\\mathbb\{E\}", "E", t)
    t = re.sub(r"\\mathbb\{R\}", "ℝ", t)
    t = re.sub(r"\\max\b", "max", t)
    t = re.sub(r"\\min\b", "min", t)
    t = re.sub(r"\\argmax|\\arg\\max", "argmax", t)

    # 10. Strip dollar delimiters ($ ... $ or $$ ... $$)
    t = re.sub(r"\$\$(.*?)\$\$", r"\1", t, flags=re.DOTALL)
    t = re.sub(r"\$(.*?)\$", r"\1", t)

    # 11. Inline code backticks: `code` -> code
    t = re.sub(r"`([^`\n]+)`", r"\1", t)

    # 12. Markdown Italics in math/variables: *y* -> y, *x* -> x
    t = re.sub(r"\*([a-zA-Z0-9가-힣α-ωΑ-Ω_+=/-]+)\*", r"\1", t)

    # 13. Mathematical multiplication: 3*x -> 3x
    t = re.sub(r"(\d+)\s*\*\s*([a-zA-Z])", r"\1\2", t)

    # 14. Markdown Bold: **text** -> text
    t = re.sub(r"\*\*([^*]+)\*\*", r"\1", t)
    t = re.sub(r"\*{2,}", "", t)
    t = re.sub(r"(?<!\d)\*(?!\d)", "", t)

    # 15. Clean any remaining raw LaTeX backslashes attached to word identifiers
    t = re.sub(r"\\([a-zA-Z]+)", r"\1", t)
    t = t.replace("\\", "")

    # 16. Normalize extra spaces
    t = re.sub(r"[ \t]+", " ", t)

    return t.strip()


def clean_notes_math(text: str) -> str:
    """Translate formulas, Greek symbols, and RL expressions into natural spoken Korean phonetics.

    Ensures TTS engines pronounce equations accurately and smoothly as a human lecturer would.
    """
    if not text:
        return ""

    t = text

    # Strip HTML and markdown markup first
    t = re.sub(r"<div\b[^>]*>.*?</div>", "", t, flags=re.IGNORECASE | re.DOTALL)
    t = re.sub(r"<sup\b[^>]*>(.*?)</sup>", lambda m: to_superscript(m.group(1)), t, flags=re.IGNORECASE)
    t = re.sub(r"<sub\b[^>]*>(.*?)</sub>", lambda m: to_subscript(m.group(1)), t, flags=re.IGNORECASE)
    t = re.sub(r"</?[a-zA-Z]+\b[^>]*>", "", t)
    t = re.sub(r"`([^`\n]+)`", r"\1", t)
    t = re.sub(r"\*([a-zA-Z0-9가-힣α-ωΑ-Ω_+=/-]+)\*", r"\1", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"\1", t)
    t = re.sub(r"\*{2,}", "", t)
    t = re.sub(r"(?<!\d)\*(?!\d)", "", t)

    # Numbers as Korean phonetics for chapter and section titles: e.g. "9.0.1" -> "구점영점일", "09.1" -> "구점일"
    def dotted_num_repl(m):
        raw = m.group(0)
        parts = raw.split(".")
        # If it is a decimal like 3.14 or 0.05
        if len(parts) == 2 and (len(parts[1]) > 1 or parts[0] == "0"):
            n1 = _int_to_korean(int(parts[0]))
            n2 = "".join(KOREAN_NUM_MAP.get(c, c) for c in parts[1])
            return f"{n1}점{n2}"
        # Chapter / Section numbering like 9.0, 9.0.1, 9.1.2
        korean_parts = [_int_to_korean(int(p)) for p in parts]
        return "점".join(korean_parts)
    t = re.sub(r"\b\d+(?:\.\d+)+\b", dotted_num_repl, t)

    # Specific Chapter 9 math & RL terms
    t = re.sub(r"\bQ\s*\(\s*s\s*,\s*a\s*\)", "큐 에스 에이", t)
    t = re.sub(r"\bV\s*\(\s*s\s*\)", "브이 에스", t)
    t = re.sub(r"\bG_t\b|Gₜ", "누적 수익 지 티", t)
    t = re.sub(r"\bS_t\b|Sₜ", "상태 에스 티", t)
    t = re.sub(r"\bA_t\b|Aₜ", "행동 에이 티", t)
    t = re.sub(r"\bR_t\b|Rₜ", "보상 알 티", t)
    t = re.sub(r"\b1\s*/\s*N\b", "엔 분의 일", t)
    t = re.sub(r"\bN\s*=\s*(\d+)\b", lambda m: f"엔이 {_int_to_korean(int(m.group(1)))} 번", t)
    t = re.sub(r"ε-탐욕|입실론-탐욕|입실론-그리디", "입실론 탐욕", t)
    t = re.sub(r"온-정책|온정책", "온 정책", t)
    t = re.sub(r"오프-정책|오프정책", "오프 정책", t)

    # Parenthesized duplicate English removal: e.g. "연쇄 법칙(Chain Rule)" -> "연쇄 법칙"
    t = re.sub(r"([가-힣]+)\s*\([a-zA-Z0-9\s_\-./]+\)", r"\1", t)

    # Math percentages: e.g. 10% -> 십 퍼센트
    t = re.sub(r"(\d+(?:\.\d+)?)\s*%", number_to_korean_percentage, t)

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
    t = re.sub(r"\\max_a|\bmax_a\b|maxₐ", "맥스 에이 ", t)
    t = re.sub(r"\\max\b", "최댓값 맥스 ", t)
    t = re.sub(r"\\min\b", "최솟값 민 ", t)

    # Common equations
    t = re.sub(r"\bdy\s*/\s*dx\b", "디와이 디엑스", t)

    # Clean double spaces, brackets, remaining backslashes
    t = re.sub(r"\\[a-zA-Z]+", "", t)
    t = re.sub(r"\$\$|\$", "", t)
    t = re.sub(r"[{}\[\]]", " ", t)
    t = re.sub(r"\s+", " ", t)

    return t.strip()
