"""
atari_pacman_env.py: Gymnasium 표준 인터페이스 기반 아타리 2600 팩맨(Pac-Man) 시뮬레이터
========================================================================================
Windows 11 애플리케이션 제어 정책(Smart App Control)으로 인해 ale-py 네이티브 DLL이 차단되는
환경에서도 별도 ROM이나 C++ 빌드 없이 100% 동일하게 동작하도록 구현한 Atari Pac-Man 환경입니다.

특징:
1. Gymnasium 표준 API 완벽 준수: reset(), step(action), render(), close()
2. 아타리 2600 정통 규격: 210 x 160 RGB 프레임 생성 + 클래식 미로 + 쿠키(66개)·파워 쿠키(4개) + 3인 유령(Blinky/Pinky/Inky)
3. 파워 모드(Frightened Mode): 파워 쿠키 섭취 시 유령이 파랗게 변하며 역으로 포식(+200점) 가능
4. Pygame 실시간 레트로 아케이드 렌더링(render_mode='human') 및 RGB 배열 반환(render_mode='rgb_array')
"""

from collections import deque
import numpy as np
import gymnasium as gym
from gymnasium import spaces


class AtariPacmanEnv(gym.Env):
    """아타리 2600 스타일 팩맨(Pac-Man) Gymnasium 환경"""

    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 14}

    # 아타리 2600 정통 화면 규격
    SCREEN_H = 210
    SCREEN_W = 160
    TOP_HUD_H = 30
    CELL_SIZE = 13  # 13행 x 13px = 169px, 11열 x 13px = 143px
    OFFSET_X = 8
    OFFSET_Y = 34

    # 13x11 대칭 클래식 아케이드 미로 (막다른 길 0개, 총 70개 쿠키: 일반 66 + 파워 4)
    # '#': 벽, '.': 일반 쿠키(10점), 'o': 파워 쿠키(50점), 'G': 유령 집, 'P': 팩맨 시작점
    MAZE_LAYOUT = [
        "###########",
        "#o...#...o#",
        "#.##.#.##.#",
        "#.........#",
        "#.##...##.#",
        "#....#....#",
        "##.#GGG#.##",
        "#....#....#",
        "#.##...##.#",
        "#.........#",
        "#.##.#.##.#",
        "#o...P...o#",
        "###########",
    ]

    # 행동 정의: 0(↑ 위), 1(↓ 아래), 2(← 좌측), 3(→ 우측)
    DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    OPPOSITE_DIR = {0: 1, 1: 0, 2: 3, 3: 2}

    # 아케이드 정통 배점 및 파워 모드 지속 스텝
    PELLET_SCORE = 10
    POWER_SCORE = 50
    GHOST_SCORE = 200
    CLEAR_BONUS = 200
    FRIGHTENED_DURATION = 24
    GHOST_RESPAWN_COOLDOWN = 8

    # 3인 유령 스펙: (이름, RGB 색상, 시작 위치, 추적 성향)
    GHOST_SPECS = [
        ("Blinky", (228, 56, 56), (6, 4), 0.72),   # 빨강: 적극 추적형
        ("Pinky", (248, 146, 200), (6, 5), 0.58),  # 분홍: 매복/선제 추적형
        ("Inky", (64, 218, 232), (6, 6), 0.35),    # 청록: 변칙 순찰형
    ]

    def __init__(self, render_mode=None, max_steps=600, lives=3):
        super().__init__()
        self.render_mode = render_mode
        self.max_steps = max_steps
        self.init_lives = lives

        self.rows = len(self.MAZE_LAYOUT)
        self.cols = len(self.MAZE_LAYOUT[0])

        # 미로 파싱 및 최단거리 테이블(BFS) 사전 계산
        self.walls = np.zeros((self.rows, self.cols), dtype=bool)
        self.init_pellets = np.zeros((self.rows, self.cols), dtype=np.int8)  # 1: 일반, 2: 파워
        self.pac_start = (11, 5)
        self.ghost_house_center = (6, 5)

        for r, line in enumerate(self.MAZE_LAYOUT):
            for c, ch in enumerate(line):
                if ch == "#":
                    self.walls[r, c] = True
                elif ch == ".":
                    self.init_pellets[r, c] = 1
                elif ch == "o":
                    self.init_pellets[r, c] = 2
                elif ch == "P":
                    self.pac_start = (r, c)

        self.total_pellets = int(np.sum(self.init_pellets > 0))
        self.dist_table = self._precompute_all_pairs_bfs()

        # 행동 공간: 0(↑ 위), 1(↓ 아래), 2(← 좌측), 3(→ 우측)
        self.action_space = spaces.Discrete(4)

        # 관찰 공간 (18차원 정규화 특징 벡터, 범위 [0, 1]):
        # [0..3]  wall_free (상하좌우 이동 가능 여부)
        # [4..7]  pellet_dir (가장 가까운 쿠키 방향 지시자)
        # [8..11] ghost_danger (각 방향 인접 칸의 활성 유령 위협도)
        # [12..15] edible_dir (파워 모드 시 가장 가까운 겁먹은 유령 방향)
        # [16]    frightened_ratio (남은 파워 모드 비율)
        # [17]    pellets_ratio (남은 쿠키 비율)
        self.observation_space = spaces.Box(
            low=np.zeros(18, dtype=np.float32),
            high=np.ones(18, dtype=np.float32),
            dtype=np.float32,
        )

        self._pygame = None
        self._screen = None
        self._clock = None
        self._font = None
        self._scale = 3

        self.rng = np.random.default_rng()
        self.reset()

    def _precompute_all_pairs_bfs(self):
        """미로 내 모든 이동 가능 칸 쌍 간의 최단 BFS 거리를 사전 계산"""
        INF = 999
        dist = np.full((self.rows, self.cols, self.rows, self.cols), INF, dtype=np.int16)
        for sr in range(self.rows):
            for sc in range(self.cols):
                if self.walls[sr, sc]:
                    continue
                dist[sr, sc, sr, sc] = 0
                q = deque([(sr, sc)])
                while q:
                    r, c = q.popleft()
                    d = dist[sr, sc, r, c]
                    for dr, dc in self.DIRS:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < self.rows and 0 <= nc < self.cols and not self.walls[nr, nc]:
                            if dist[sr, sc, nr, nc] == INF:
                                dist[sr, sc, nr, nc] = d + 1
                                q.append((nr, nc))
        return dist

    def _is_valid(self, r, c):
        return 0 <= r < self.rows and 0 <= c < self.cols and not self.walls[r, c]

    def _reset_entities(self):
        """팩맨과 유령들을 초기 위치로 배치"""
        self.pac_pos = self.pac_start
        self.pac_dir = 3  # 초기 방향: 우측
        self.frightened_timer = 0
        self.ghosts = []
        for idx, (name, color, start_pos, chase_prob) in enumerate(self.GHOST_SPECS):
            self.ghosts.append({
                "name": name,
                "color": color,
                "pos": start_pos,
                "start_pos": start_pos,
                "dir": 0,
                "chase_prob": chase_prob,
                "respawn_timer": idx * 2,  # 순차 출격
            })

    def _get_obs(self):
        """18차원 정규화 상태 벡터 생성"""
        pr, pc = self.pac_pos
        wall_free = np.zeros(4, dtype=np.float32)
        pellet_dir = np.zeros(4, dtype=np.float32)
        ghost_danger = np.ones(4, dtype=np.float32)
        edible_dir = np.zeros(4, dtype=np.float32)

        # 남은 쿠키 좌표 추출
        pellet_coords = np.argwhere(self.pellets > 0)
        active_ghost_positions = [
            g["pos"] for g in self.ghosts
            if g["respawn_timer"] == 0 and self.frightened_timer == 0
        ]
        edible_ghost_positions = [
            g["pos"] for g in self.ghosts
            if g["respawn_timer"] == 0 and self.frightened_timer > 0
        ]

        # 1. 각 방향별 이동 가능성 및 가장 가까운 쿠키/유령까지의 거리 계산
        neighbor_pellet_dists = []
        neighbor_edible_dists = []

        for d, (dr, dc) in enumerate(self.DIRS):
            nr, nc = pr + dr, pc + dc
            if not self._is_valid(nr, nc):
                wall_free[d] = 0.0
                ghost_danger[d] = 1.0
                neighbor_pellet_dists.append(999)
                neighbor_edible_dists.append(999)
                continue

            wall_free[d] = 1.0

            # 가장 가까운 쿠키까지의 거리
            if len(pellet_coords) > 0:
                dists = self.dist_table[nr, nc, pellet_coords[:, 0], pellet_coords[:, 1]]
                neighbor_pellet_dists.append(int(np.min(dists)))
            else:
                neighbor_pellet_dists.append(999)

            # 활성 유령 위협도 (거리가 가까울수록 1.0에 근접, 6칸 이상이면 0.0)
            if active_ghost_positions:
                min_gd = min(int(self.dist_table[nr, nc, gr, gc]) for gr, gc in active_ghost_positions)
                ghost_danger[d] = float(max(0.0, 1.0 - min_gd / 6.0))
            else:
                ghost_danger[d] = 0.0

            # 겁먹은 유령(포식 가능)까지의 거리
            if edible_ghost_positions:
                min_ed = min(int(self.dist_table[nr, nc, gr, gc]) for gr, gc in edible_ghost_positions)
                neighbor_edible_dists.append(min_ed)
            else:
                neighbor_edible_dists.append(999)

        # 최단 쿠키 방향 원-핫(복수 최단 경로 허용)
        min_pd = min(neighbor_pellet_dists)
        if min_pd < 999:
            for d in range(4):
                if neighbor_pellet_dists[d] == min_pd:
                    pellet_dir[d] = 1.0

        # 최단 겁먹은 유령 방향 (7칸 이내 포식 가능할 때 활성화)
        min_ed = min(neighbor_edible_dists)
        if min_ed <= 7:
            for d in range(4):
                if neighbor_edible_dists[d] == min_ed:
                    edible_dir[d] = 1.0

        frightened_ratio = float(self.frightened_timer) / float(self.FRIGHTENED_DURATION)
        pellets_remaining = int(np.sum(self.pellets > 0))
        pellets_ratio = float(pellets_remaining) / float(self.total_pellets)

        return np.concatenate([
            wall_free,
            pellet_dir,
            ghost_danger,
            edible_dir,
            np.array([frightened_ratio, pellets_ratio], dtype=np.float32),
        ]).astype(np.float32)

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        if seed is not None:
            self.rng = np.random.default_rng(seed)

        self.pellets = self.init_pellets.copy()
        self.lives = self.init_lives
        self.score = 0
        self.pellets_eaten = 0
        self.power_eaten = 0
        self.ghosts_eaten = 0
        self.steps = 0
        self._reset_entities()

        info = {
            "score": self.score,
            "lives": self.lives,
            "pellets_eaten": self.pellets_eaten,
            "pellets_remaining": int(np.sum(self.pellets > 0)),
            "total_pellets": self.total_pellets,
            "ghosts_eaten": self.ghosts_eaten,
            "pellet_eaten_now": False,
            "power_eaten_now": False,
            "ghost_eaten_now": False,
            "wall_hit": False,
            "life_lost": False,
            "cleared": False,
            "frightened": False,
        }
        return self._get_obs(), info

    def _choose_ghost_move(self, ghost):
        """유령의 다음 이동 좌표 및 방향 결정"""
        gr, gc = ghost["pos"]
        valid_moves = []
        for d, (dr, dc) in enumerate(self.DIRS):
            nr, nc = gr + dr, gc + dc
            if self._is_valid(nr, nc):
                valid_moves.append((d, nr, nc))

        if not valid_moves:
            return ghost["pos"], ghost["dir"]

        # 막다른 길이 아니면 직전 반대 방향(180도 유턴) 회피
        opp = self.OPPOSITE_DIR[ghost["dir"]]
        non_reverse = [m for m in valid_moves if m[0] != opp]
        candidates = non_reverse if non_reverse else valid_moves

        pr, pc = self.pac_pos

        if self.frightened_timer > 0:
            # 파워 모드: 팩맨에게서 멀어지려 도망 (70%) 또는 무작위 (30%)
            if self.rng.random() < 0.70:
                best_dist = max(int(self.dist_table[nr, nc, pr, pc]) for _, nr, nc in candidates)
                best = [m for m in candidates if int(self.dist_table[m[1], m[2], pr, pc]) == best_dist]
                chosen = best[int(self.rng.integers(len(best)))]
            else:
                chosen = candidates[int(self.rng.integers(len(candidates)))]
        else:
            # 일반 모드: 각 유령의 추적 성향(Blinky 0.72, Pinky 0.58, Inky 0.35)에 따라 추적
            if self.rng.random() < ghost["chase_prob"]:
                # Pinky는 팩맨의 2칸 앞 지점을 선제 타깃팅
                target_r, target_c = pr, pc
                if ghost["name"] == "Pinky":
                    dr, dc = self.DIRS[self.pac_dir]
                    for step_ahead in (2, 1):
                        tr, tc = pr + dr * step_ahead, pc + dc * step_ahead
                        if self._is_valid(tr, tc):
                            target_r, target_c = tr, tc
                            break
                best_dist = min(int(self.dist_table[nr, nc, target_r, target_c]) for _, nr, nc in candidates)
                best = [m for m in candidates if int(self.dist_table[m[1], m[2], target_r, target_c]) == best_dist]
                chosen = best[int(self.rng.integers(len(best)))]
            else:
                chosen = candidates[int(self.rng.integers(len(candidates)))]

        return (chosen[1], chosen[2]), chosen[0]

    def step(self, action):
        self.steps += 1
        reward = 0.0
        pellet_eaten_now = False
        power_eaten_now = False
        ghost_eaten_now = False
        wall_hit = False
        life_lost = False

        # 1. 팩맨 이동
        prev_pac_pos = self.pac_pos
        dr, dc = self.DIRS[int(action)]
        nr, nc = prev_pac_pos[0] + dr, prev_pac_pos[1] + dc
        if self._is_valid(nr, nc):
            self.pac_pos = (nr, nc)
            self.pac_dir = int(action)
        else:
            wall_hit = True

        # 2. 쿠키 및 파워 쿠키 섭취 검사
        pr, pc = self.pac_pos
        cell_val = int(self.pellets[pr, pc])
        if cell_val == 1:
            self.pellets[pr, pc] = 0
            self.score += self.PELLET_SCORE
            self.pellets_eaten += 1
            reward += float(self.PELLET_SCORE)
            pellet_eaten_now = True
        elif cell_val == 2:
            self.pellets[pr, pc] = 0
            self.score += self.POWER_SCORE
            self.pellets_eaten += 1
            self.power_eaten += 1
            self.frightened_timer = self.FRIGHTENED_DURATION
            reward += float(self.POWER_SCORE)
            pellet_eaten_now = True
            power_eaten_now = True

        # 3. 팩맨 이동 직후 유령 충돌 검사
        for g in self.ghosts:
            if g["respawn_timer"] > 0:
                continue
            if g["pos"] == self.pac_pos:
                if self.frightened_timer > 0:
                    # 파워 모드: 유령 포식!
                    self.score += self.GHOST_SCORE
                    self.ghosts_eaten += 1
                    reward += float(self.GHOST_SCORE)
                    ghost_eaten_now = True
                    g["pos"] = self.ghost_house_center
                    g["respawn_timer"] = self.GHOST_RESPAWN_COOLDOWN
                else:
                    life_lost = True
                    break

        # 4. 유령 이동 (아케이드 속도 밸런스: 일반 시 2/3 속도, 파워 모드 시 1/2 속도)
        if not life_lost:
            ghost_can_move = (self.steps % 2 == 0) if self.frightened_timer > 0 else (self.steps % 3 != 0)
            for g in self.ghosts:
                if g["respawn_timer"] > 0:
                    g["respawn_timer"] -= 1
                    continue
                if not ghost_can_move:
                    continue

                prev_g_pos = g["pos"]
                new_g_pos, new_g_dir = self._choose_ghost_move(g)
                g["pos"] = new_g_pos
                g["dir"] = new_g_dir

                # 동일 타일 충돌 또는 정면 교차 충돌 판정
                collided = (g["pos"] == self.pac_pos) or (
                    g["pos"] == prev_pac_pos and prev_g_pos == self.pac_pos
                )
                if collided:
                    if self.frightened_timer > 0:
                        self.score += self.GHOST_SCORE
                        self.ghosts_eaten += 1
                        reward += float(self.GHOST_SCORE)
                        ghost_eaten_now = True
                        g["pos"] = self.ghost_house_center
                        g["respawn_timer"] = self.GHOST_RESPAWN_COOLDOWN
                    else:
                        life_lost = True
                        break

        # 5. 파워 모드 타이머 감소
        if self.frightened_timer > 0:
            self.frightened_timer -= 1

        # 6. 생명 손실 및 게임 오버 판정
        terminated = False
        if life_lost:
            self.lives -= 1
            if self.lives <= 0:
                terminated = True
            else:
                self._reset_entities()

        # 7. 전체 70개 쿠키 완식 시 스테이지 클리어!
        pellets_remaining = int(np.sum(self.pellets > 0))
        cleared = pellets_remaining == 0
        if cleared:
            self.score += self.CLEAR_BONUS
            reward += float(self.CLEAR_BONUS)
            terminated = True

        truncated = (self.steps >= self.max_steps) and not terminated

        info = {
            "score": self.score,
            "lives": self.lives,
            "pellets_eaten": self.pellets_eaten,
            "pellets_remaining": pellets_remaining,
            "total_pellets": self.total_pellets,
            "ghosts_eaten": self.ghosts_eaten,
            "pellet_eaten_now": pellet_eaten_now,
            "power_eaten_now": power_eaten_now,
            "ghost_eaten_now": ghost_eaten_now,
            "wall_hit": wall_hit,
            "life_lost": life_lost,
            "cleared": cleared,
            "frightened": self.frightened_timer > 0,
        }
        return self._get_obs(), reward, terminated, truncated, info

    def _draw_circle(self, frame, cy, cx, radius, color):
        """원형 스프라이트 픽셀 렌더링"""
        r2 = radius * radius
        y0 = max(0, int(cy - radius))
        y1 = min(self.SCREEN_H, int(cy + radius) + 1)
        x0 = max(0, int(cx - radius))
        x1 = min(self.SCREEN_W, int(cx + radius) + 1)
        yy, xx = np.ogrid[y0:y1, x0:x1]
        mask = (yy - cy) ** 2 + (xx - cx) ** 2 <= r2
        frame[y0:y1, x0:x1][mask] = color

    def get_rgb_frame(self):
        """아타리 2600 규격 (210, 160, 3) uint8 RGB 화면 배열 생성"""
        frame = np.zeros((self.SCREEN_H, self.SCREEN_W, 3), dtype=np.uint8)
        frame[:, :] = (8, 8, 18)  # 레트로 CRT 다크 네이비 배경

        # 상단 HUD 구분선
        frame[self.TOP_HUD_H - 2:self.TOP_HUD_H, :] = (40, 72, 190)

        cs = self.CELL_SIZE
        ox, oy = self.OFFSET_X, self.OFFSET_Y

        # 1. 클래식 네온 블루 미로 벽 + 쿠키/파워 쿠키 렌더링
        wall_outer = (36, 76, 220)
        wall_inner = (18, 36, 115)
        pellet_color = (255, 212, 164)
        power_color = (255, 240, 180) if (self.steps % 4 < 3) else (255, 175, 90)

        for r in range(self.rows):
            y0 = oy + r * cs
            y1 = y0 + cs
            for c in range(self.cols):
                x0 = ox + c * cs
                x1 = x0 + cs
                if self.walls[r, c]:
                    frame[y0 + 1:y1 - 1, x0 + 1:x1 - 1] = wall_outer
                    frame[y0 + 3:y1 - 3, x0 + 3:x1 - 3] = wall_inner
                else:
                    cy = y0 + cs // 2
                    cx = x0 + cs // 2
                    val = int(self.pellets[r, c])
                    if val == 1:
                        frame[cy - 1:cy + 2, cx - 1:cx + 2] = pellet_color
                    elif val == 2:
                        self._draw_circle(frame, cy, cx, 3.3, power_color)

        # 2. 팩맨 렌더링 (노란색 + 이동 방향 입 벌림 애니메이션)
        pr, pc = self.pac_pos
        pcy = oy + pr * cs + cs // 2
        pcx = ox + pc * cs + cs // 2
        self._draw_circle(frame, pcy, pcx, 4.8, (255, 224, 32))

        # 짝수 스텝마다 입 벌림(Chomp!) 표현
        if self.steps % 2 == 0:
            mouth_bg = (8, 8, 18)
            for dy in range(-5, 6):
                for dx in range(-5, 6):
                    py, px = pcy + dy, pcx + dx
                    if not (0 <= py < self.SCREEN_H and 0 <= px < self.SCREEN_W):
                        continue
                    if self.pac_dir == 0 and dy < 0 and abs(dx) <= abs(dy):
                        frame[py, px] = mouth_bg
                    elif self.pac_dir == 1 and dy > 0 and abs(dx) <= abs(dy):
                        frame[py, px] = mouth_bg
                    elif self.pac_dir == 2 and dx < 0 and abs(dy) <= abs(dx):
                        frame[py, px] = mouth_bg
                    elif self.pac_dir == 3 and dx > 0 and abs(dy) <= abs(dx):
                        frame[py, px] = mouth_bg

        # 3. 3인 유령 렌더링 (몸통 + 눈동자 + 파워 모드 파란색 깜빡임)
        for g in self.ghosts:
            gr, gc = g["pos"]
            gcy = oy + gr * cs + cs // 2
            gcx = ox + gc * cs + cs // 2

            if g["respawn_timer"] > 0:
                body_color = (90, 90, 120)
            elif self.frightened_timer > 0:
                if self.frightened_timer <= 6 and self.steps % 2 == 0:
                    body_color = (235, 235, 255)  # 종료 임박 흰색 깜빡임
                else:
                    body_color = (42, 82, 238)    # 겁먹은 파란 유령
            else:
                body_color = g["color"]

            # 상단 둥근 머리 + 하단 사각 스커트
            self._draw_circle(frame, gcy - 1, gcx, 4.3, body_color)
            frame[gcy - 1:gcy + 5, gcx - 4:gcx + 5] = body_color
            # 물결 스커트 컷아웃
            frame[gcy + 4, gcx - 2] = (8, 8, 18)
            frame[gcy + 4, gcx + 2] = (8, 8, 18)

            # 눈 (흰자 + 검은 동공)
            eye_color = (255, 255, 255)
            pupil_color = (255, 190, 190) if self.frightened_timer > 0 else (20, 30, 120)
            frame[gcy - 3:gcy - 1, gcx - 3:gcx - 1] = eye_color
            frame[gcy - 3:gcy - 1, gcx + 1:gcx + 3] = eye_color
            frame[gcy - 2, gcx - 2] = pupil_color
            frame[gcy - 2, gcx + 2] = pupil_color

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
            pygame.display.set_caption(f"Atari 2600 Pac-Man (Gymnasium + DQN){title_suffix}")
            self._clock = pygame.time.Clock()
            self._font = pygame.font.SysFont("consolas", 17, bold=True)

        pygame = self._pygame
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.close()
                return None

        surf = pygame.surfarray.make_surface(np.transpose(frame, (1, 0, 2)))
        scaled = pygame.transform.scale(surf, (self.SCREEN_W * self._scale, self.SCREEN_H * self._scale))
        self._screen.blit(scaled, (0, 0))

        # 상단 HUD (점수, 쿠키, 파워 상태, 생명)
        mode_tag = f" PWR:{self.frightened_timer:02d}" if self.frightened_timer > 0 else ""
        hud_text = (
            f"SCORE:{self.score:04d}  DOTS:{self.pellets_eaten:02d}/{self.total_pellets}  "
            f"LIVES:{self.lives}{mode_tag}"
        )
        hud_color = (120, 200, 255) if self.frightened_timer > 0 else (255, 232, 88)
        text_surf = self._font.render(hud_text, True, hud_color)
        self._screen.blit(text_surf, (16, 28))

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
