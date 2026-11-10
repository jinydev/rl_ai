import os
import shutil
from PIL import Image, ImageDraw, ImageFont, ImageFilter

base_dir = '/Users/hojin9/dev/jinysite/강화학습3/src/10_TD법/10_5_분포_모델과_샘플_모델'
assets_dir = os.path.join(base_dir, 'assets')
output_path = os.path.join(base_dir, '10_5_분포_모델과_샘플_모델.png')
youtube_path = os.path.join(base_dir, 'youtube_cover.png')

canvas_w, canvas_h = 1376, 768
canvas = Image.new('RGBA', (canvas_w, canvas_h), (255, 255, 255, 255))

font_path = '/System/Library/AssetsV2/com_apple_MobileAsset_Font8/7a0b5c0f3c1d41c4c52a33343496c9c65ad52c50.asset/AssetData/NanumGothic.ttc'
if not os.path.exists(font_path):
    font_path = '/System/Library/Fonts/AppleSDGothicNeo.ttc'

badge_font = ImageFont.truetype(font_path, 22, index=1 if 'Nanum' in font_path else 0)
title_font = ImageFont.truetype(font_path, 52, index=1 if 'Nanum' in font_path else 0) # 44pt에 대응
sub_font = ImageFont.truetype(font_path, 24, index=0)   # 20pt에 대응
author_font = ImageFont.truetype(font_path, 20, index=0)

draw = ImageDraw.Draw(canvas)

# 1. 뱃지 (파란 #1A73E8 알약 모양, 흰 글씨)
badge_text = 'PART 10 · 강화학습 이론'
badge_x, badge_y = 80, 100
badge_padding_x, badge_padding_y = 22, 10
bbox = badge_font.getbbox(badge_text)
bw = bbox[2] - bbox[0] + badge_padding_x * 2
bh = bbox[3] - bbox[1] + badge_padding_y * 2
draw.rounded_rectangle([badge_x, badge_y, badge_x + bw, badge_y + bh], radius=bh//2, fill=(26, 115, 232, 255))
draw.text((badge_x + badge_padding_x, badge_y + badge_padding_y - 2), badge_text, font=badge_font, fill=(255, 255, 255, 255))

# 2. 메인 타이틀 (44pt 볼드, #111827)
title_x, title_y = 80, 180
draw.text((title_x, title_y), '10.5 분포 모델과 샘플 모델:\n에이전트의 초경량화', font=title_font, fill=(17, 24, 39, 255), spacing=14)

# 3. 부제목 (20pt 회색, #6B7280)
sub_x, sub_y = 80, 350
sub_text = '전체 확률 계산의 무거운 동적 계획법에서\n단일 경험 샘플링의 초경량화로 도약하는\n환경 모델의 본질과 패러다임 전환'
draw.text((sub_x, sub_y), sub_text, font=sub_font, fill=(107, 114, 128, 255), spacing=10)

# 4. 강사 정보 (#374151)
auth_x, auth_y = 80, 500
draw.text((auth_x, auth_y), '강의: 이호진 교수 · 조교 지니와 도로시 탐험대', font=author_font, fill=(55, 65, 81, 255))

# 5. 우측 캐릭터 (같은 바닥선 y=615에 정렬하여 나란히 배치)
ground_y = 615

assets_spec = [
    ('asset_01_jiny_scholar.png', 245, 640, ground_y - 245),
    ('asset_02_dorothy_stepping.png', 410, 785, ground_y - 410),
    ('asset_03_toto_running.png', 205, 940, ground_y - 205),
    ('asset_04_prof_hojin.png', 510, 1085, ground_y - 510),
]

for filename, target_h, target_x, target_y in assets_spec:
    img_path = os.path.join(assets_dir, filename)
    if os.path.exists(img_path):
        asset = Image.open(img_path).convert('RGBA')
        aspect = asset.width / asset.height
        target_w = int(target_h * aspect)
        resized = asset.resize((target_w, target_h), Image.Resampling.LANCZOS)
        
        shadow = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
        s_draw = ImageDraw.Draw(shadow)
        foot_y = ground_y - 6
        s_cx = target_x + target_w // 2
        s_rx = target_w // 3
        s_ry = 12
        s_draw.ellipse([s_cx - s_rx, foot_y - s_ry, s_cx + s_rx, foot_y + s_ry], fill=(0, 0, 0, 45))
        shadow = shadow.filter(ImageFilter.GaussianBlur(8))
        canvas.alpha_composite(shadow)
        
        canvas.paste(resized, (target_x, target_y), resized)

canvas.convert('RGB').save(output_path, 'PNG')
shutil.copyfile(output_path, youtube_path)
print(f'Successfully composed cover image: {output_path} ({canvas.size})')

