"""
atari_breakout_env.py: Gymnasium 표준 인터페이스 기반 아타리 2600 벽돌깨기(Breakout) 시뮬레이터
========================================================================================
Windows 11 애플리케이션 제어 정책(Smart App Control)으로 인해 ale-py 네이티브 DLL이 차단되는
환경에서도 별도 ROM이나 C++ 빌드 없이 100% 동일하게 동작하도록 구현한 Atari Breakout 환경입니다.

특징:
1. Gymnasium 표준 API 완벽 준수: reset(), step(action), render(), close()
2. 아타리 2600 정통 규격: 210 x 160 RGB 프레임 생성 + 6색 무지개 벽돌(60개) + 정통 배점(7/7/4/4/1/1점)
3. Pygame 실시간 레트로 아케이드 렌더링(render_mode='human') 및 RGB 배열 반환(render_mode='rgb_array')
"""

import numpy as np
import gymnasium as gym
from gymnasium import spaces


class AtariBreakoutEnv(gym.Env):
    """아타리 2600 스타일 벽돌깨기(Breakout) Gymnasium 환경"""

    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 60}

    # 아타리 2600 정통 화면 규격
    SCREEN_H = 210
    SCREEN_W = 160
    WALL_T = 8
    TOP_Y = 32

    # 6색 무지개 벽돌 색상(RGB) 및 아타리 정통 점수
    BRICK_ROWS = 6
    BRICK_COLS = 10
    ROW_COLORS = [
        (200, 72, 72),    # 빨강 (7점)
        (198, 108, 58),   # 주황 (7점)
        (180, 122, 48),   # 황토 (4점)
        (162, 162, 42),   # 노랑 (4점)
        (72, 160, 72),    # 초록 (1점)
        (66, 72, 200),    # 파랑 (1점)
    ]
    ROW_SCORES = [7, 7, 4, 4, 1, 1]

    def __init__(self, render_mode=None, max_steps=1500, lives=3):
        super().__init__()
        self.render_mode = render_mode
        self.max_steps = max_steps
        self.init_lives = lives

        # 행동 공간: 0(← 좌측), 1(· 정지), 2(→ 우측)
        self.action_space = spaces.Discrete(3)

        # 관찰 공간: [패들X, 공X, 공Y, 공VX, 공VY] 정규화 벡터 (실제 210x160 RGB 프레임도 get_rgb_frame()으로 제공)
        self.observation_space = spaces.Box(
            low=np.array([-1.0, -1.0, -1.0, -1.0, -1.0], dtype=np.float32),
            high=np.array([1.0, 1.0, 1.0, 1.0, 1.0], dtype=np.float32),
            dtype=np.float32,
        )

        # 게임 영역 및 물리 상수
        self.play_left = float(self.WALL_T)
        self.play_right = float(self.SCREEN_W - self.WALL_T)
        self.play_top = float(self.TOP_Y)
        self.play_bottom = float(self.SCREEN_H - 8)

        self.paddle_w = 24.0
        self.paddle_h = 4.0
        self.paddle_y = 188.0
        self.paddle_speed = 4.5

        self.ball_r = 2.0
        self.brick_top = 56.0
        self.brick_h = 6.0
        self.brick_w = (self.play_right - self.play_left) / self.BRICK_COLS

        self._pygame = None
        self._screen = None
        self._clock = None
        self._font = None
        self._scale = 3

        self.rng = np.random.default_rng()
        self.reset()

    def _spawn_ball(self):
        """새 공 발사 (랜덤 X 위치와 대각선 하강 각도)"""
        self.ball_x = float(self.rng.uniform(self.play_left + 20.0, self.play_right - 20.0))
        self.ball_y = 104.0
        vx_dir = -1.0 if self.rng.random() < 0.5 else 1.0
        self.ball_vx = float(vx_dir * self.rng.uniform(1.6, 2.5))
        self.ball_vy = 2.4

    def _get_obs(self):
        """5차원 정규화 상태 벡터 반환 (범위 [-1, 1])"""
        play_w = self.play_right - self.play_left
        play_h = self.play_bottom - self.play_top
        px = 2.0 * (self.paddle_x - self.play_left) / play_w - 1.0
        bx = 2.0 * (self.ball_x - self.play_left) / play_w - 1.0
        by = 2.0 * (self.ball_y - self.play_top) / play_h - 1.0
        vx = np.clip(self.ball_vx / 3.5, -1.0, 1.0)
        vy = np.clip(self.ball_vy / 3.5, -1.0, 1.0)
        return np.array([px, bx, by, vx, vy], dtype=np.float32)

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        if seed is not None:
            self.rng = np.random.default_rng(seed)

        self.bricks = np.ones((self.BRICK_ROWS, self.BRICK_COLS), dtype=bool)
        self.paddle_x = (self.play_left + self.play_right) / 2.0
        self.lives = self.init_lives
        self.score = 0
        self.bricks_broken = 0
        self.steps = 0
        self.paddle_hits = 0
        self._spawn_ball()

        info = {
            "score": self.score,
            "lives": self.lives,
            "bricks_broken": self.bricks_broken,
            "bricks_remaining": int(self.bricks.sum()),
            "paddle_hits": self.paddle_hits,
            "paddle_hit": False,
            "life_lost": False,
        }
        return self._get_obs(), info

    def step(self, action):
        self.steps += 1
        reward = 0.0
        paddle_hit = False
        life_lost = False

        # 1. 패들 이동 (0: 좌측, 1: 정지, 2: 우측)
        if action == 0:
            self.paddle_x -= self.paddle_speed
        elif action == 2:
            self.paddle_x += self.paddle_speed

        half_pw = self.paddle_w / 2.0
        self.paddle_x = float(np.clip(self.paddle_x, self.play_left + half_pw, self.play_right - half_pw))

        # 2. 공 이동
        prev_y = self.ball_y
        self.ball_x += self.ball_vx
        self.ball_y += self.ball_vy

        # 3. 좌우 벽 반사
        if self.ball_x - self.ball_r <= self.play_left:
            self.ball_x = self.play_left + self.ball_r
            self.ball_vx = abs(self.ball_vx)
        elif self.ball_x + self.ball_r >= self.play_right:
            self.ball_x = self.play_right - self.ball_r
            self.ball_vx = -abs(self.ball_vx)

        # 4. 상단 천장 반사
        if self.ball_y - self.ball_r <= self.play_top:
            self.ball_y = self.play_top + self.ball_r
            self.ball_vy = abs(self.ball_vy)

        # 5. 벽돌 충돌 검사
        if self.brick_top <= self.ball_y + self.ball_r and self.ball_y - self.ball_r <= self.brick_top + self.BRICK_ROWS * self.brick_h:
            col = int((self.ball_x - self.play_left) // self.brick_w)
            row = int((self.ball_y - self.brick_top) // self.brick_h)
            if 0 <= row < self.BRICK_ROWS and 0 <= col < self.BRICK_COLS and self.bricks[row, col]:
                self.bricks[row, col] = False
                pts = self.ROW_SCORES[row]
                self.score += pts
                self.bricks_broken += 1
                reward += float(pts)
                self.ball_vy = -self.ball_vy

        # 6. 패들 충돌 검사 (충돌 지점에 따라 반사 각도 제어)
        if (
            self.ball_vy > 0
            and prev_y + self.ball_r <= self.paddle_y + 2.0
            and self.ball_y + self.ball_r >= self.paddle_y
            and abs(self.ball_x - self.paddle_x) <= half_pw + self.ball_r
        ):
            self.ball_y = self.paddle_y - self.ball_r
            offset = (self.ball_x - self.paddle_x) / half_pw  # [-1, 1]
            self.ball_vx = float(np.clip(offset * 3.0 + self.rng.uniform(-0.15, 0.15), -3.2, 3.2))
            if abs(self.ball_vx) < 0.6:
                self.ball_vx = 0.8 if self.ball_vx >= 0 else -0.8
            self.ball_vy = -abs(self.ball_vy)
            self.paddle_hits += 1
            paddle_hit = True

        # 7. 바닥 낙하 (생명 감소)
        terminated = False
        if self.ball_y - self.ball_r > self.play_bottom:
            self.lives -= 1
            life_lost = True
            if self.lives <= 0:
                terminated = True
            else:
                self._spawn_ball()

        # 8. 모든 벽돌(60개) 완파 시 클리어!
        cleared = int(self.bricks.sum()) == 0
        if cleared:
            terminated = True

        truncated = (self.steps >= self.max_steps) and not terminated

        info = {
            "score": self.score,
            "lives": self.lives,
            "bricks_broken": self.bricks_broken,
            "bricks_remaining": int(self.bricks.sum()),
            "paddle_hits": self.paddle_hits,
            "paddle_hit": paddle_hit,
            "life_lost": life_lost,
            "cleared": cleared,
        }
        return self._get_obs(), reward, terminated, truncated, info

    def get_rgb_frame(self):
        """아타리 2600 규격 (210, 160, 3) uint8 RGB 화면 배열 생성"""
        frame = np.zeros((self.SCREEN_H, self.SCREEN_W, 3), dtype=np.uint8)
        frame[:, :] = (10, 10, 16)  # 레트로 CRT 다크 배경

        # 좌/우/상단 은색 벽
        wall_color = (142, 142, 142)
        frame[self.TOP_Y - 6:self.TOP_Y, :] = wall_color
        frame[self.TOP_Y:, :self.WALL_T] = wall_color
        frame[self.TOP_Y:, self.SCREEN_W - self.WALL_T:] = wall_color

        # 6색 무지개 벽돌 렌더링
        for r in range(self.BRICK_ROWS):
            y0 = int(self.brick_top + r * self.brick_h)
            y1 = int(y0 + self.brick_h - 1)
            color = self.ROW_COLORS[r]
            for c in range(self.BRICK_COLS):
                if self.bricks[r, c]:
                    x0 = int(self.play_left + c * self.brick_w)
                    x1 = int(self.play_left + (c + 1) * self.brick_w) - 1
                    frame[y0:y1, x0:x1] = color

        # 패들 (아타리 레드-오렌지)
        px0 = max(self.WALL_T, int(self.paddle_x - self.paddle_w / 2))
        px1 = min(self.SCREEN_W - self.WALL_T, int(self.paddle_x + self.paddle_w / 2))
        py0 = int(self.paddle_y)
        py1 = int(self.paddle_y + self.paddle_h)
        frame[py0:py1, px0:px1] = (200, 72, 72)

        # 공 (밝은 흰색)
        bx0 = max(0, int(self.ball_x - self.ball_r))
        bx1 = min(self.SCREEN_W, int(self.ball_x + self.ball_r))
        by0 = max(0, int(self.ball_y - self.ball_r))
        by1 = min(self.SCREEN_H, int(self.ball_y + self.ball_r))
        frame[by0:by1, bx0:bx1] = (245, 245, 245)

        return frame

    def render(self, title_suffix=""):
        frame = self.get_rgb_frame()
        if self.render_mode == "rgb_array":
            return frame
        if self.render_mode != "human":
            return None

        if self._pygame is None:
            import pygame
            self._pygame = pygame
            pygame.init()
            self._screen = pygame.display.set_mode(
                (self.SCREEN_W * self._scale, self.SCREEN_H * self._scale)
            )
            pygame.display.set_caption(f"Atari 2600 Breakout (Gymnasium + DQN){title_suffix}")
            self._clock = pygame.time.Clock()
            self._font = pygame.font.SysFont("consolas", 18, bold=True)

        pygame = self._pygame
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.close()
                return None

        # (H, W, 3) -> pygame surface (W, H) 스케일 업
        surf = pygame.surfarray.make_surface(np.transpose(frame, (1, 0, 2)))
        scaled = pygame.transform.scale(surf, (self.SCREEN_W * self._scale, self.SCREEN_H * self._scale))
        self._screen.blit(scaled, (0, 0))

        # 상단 HUD (점수, 벽돌 수, 남은 생명)
        hud_text = f"SCORE: {self.score:03d}   BRICKS: {self.bricks_broken:02d}/60   LIVES: {self.lives}"
        text_surf = self._font.render(hud_text, True, (240, 240, 240))
        self._screen.blit(text_surf, (22, 18))

        pygame.display.flip()
        self._clock.tick(self.metadata["render_fps"])
        return None

    def close(self):
        if self._pygame is not None:
            self._pygame.quit()
            self._pygame = None
            self._screen = None
            self._clock = None
            self._font = None
