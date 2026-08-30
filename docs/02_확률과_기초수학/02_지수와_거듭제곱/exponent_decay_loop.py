# exponent_decay_loop.py
# 매 단계마다 이전 가치를 감쇄(decay)시키는 코드

def main():
    discount_factor = 0.9
    value = 100.0

    print("--- 지수적 감쇄 루프 실습 시작 ---")
    for step in range(4):
        print(f"{step}단계 가치: {value:.1f}")
        value = value * discount_factor  # 매 루프마다 0.9가 누적 곱해짐

if __name__ == "__main__":
    main()
