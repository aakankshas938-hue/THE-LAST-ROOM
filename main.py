"""
THE LAST ROOM — A Cinematic 2D Horror Survival Game.
Features: 3D Human Character, Fixed Replay UI, Realistic Story Paper, Jumpscare.

Install:  pip install pygame numpy
Run:      python the_last_room.py
"""
import pygame
import numpy as np
import math, random, sys, os, json
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, List, Tuple, Dict

# ============================================================
# CONFIG
# ============================================================
SEED = 1337
random.seed(SEED); np.random.seed(SEED)

W, H = 1024, 640
TILE = 40
FPS = 60
DT_CAP = 1/30
SAVE_FILE = "savegame.json"

THEMES = [
    {"name": "Haunted House", "wall": (75, 60, 65), "floor": (40, 30, 35)},
    {"name": "Mirror Room", "wall": (90, 90, 100), "floor": (50, 50, 60)},
    {"name": "Abandoned Hospital","wall": (70, 80, 75), "floor": (45, 55, 50)},
    {"name": "Underground Lab", "wall": (60, 70, 80), "floor": (35, 45, 55)},
    {"name": "Fog Village", "wall": (55, 50, 40), "floor": (30, 25, 20)},
    {"name": "Haunted Circus", "wall": (85, 50, 55), "floor": (50, 35, 35)},
    {"name": "Abandoned School", "wall": (65, 55, 45), "floor": (40, 35, 25)},
    {"name": "Frozen Base", "wall": (80, 90, 100), "floor": (50, 60, 70)},
    {"name": "Ancient Castle", "wall": (50, 45, 40), "floor": (25, 20, 15)},
    {"name": "Nightmare World", "wall": (40, 30, 40), "floor": (20, 15, 20)}
]

C_BG = (6, 5, 10); C_TEXT = (222, 212, 198); C_DIM = (130, 120, 110)
C_BLOOD = (120, 20, 20); C_KEY = (232, 192, 72); C_HP = (210, 60, 65); C_FEAR = (200, 36, 70)

LEVELS_DATA = [
    {"name": "THE ARRIVAL", "theme": 0, "clue": "Photograph: 4 people stand in front of the manor. Written on the back: 'Five of us entered.'"},
    {"name": "THE BASEMENT", "theme": 0, "clue": "Old Audio Tape: 'He is still inside.'"},
    {"name": "THE CHILDREN'S ROOM", "theme": 0, "clue": "A child's drawing of the mansion and a dark room. Written in crayon: 'DON'T OPEN THE LAST ROOM.'"},
    {"name": "THE MIRROR ROOM", "theme": 1, "clue": "The mirror reflects the mansion from Level 1. Something is different."},
    {"name": "THE ENDLESS CORRIDOR", "theme": 1, "clue": "A door is found. Carved into it: 'ROOM 05'"},
    {"name": "BLOOD HALL", "theme": 2, "clue": "A painting hides a key. The painting's eyes follow you."},
    {"name": "THE HAUNTED LIBRARY", "theme": 2, "clue": "Diary Page: 'He forgot everything after the seventh night.'"},
    {"name": "THE OLD CHAPEL", "theme": 2, "clue": "Symbols match the bell. The bell keeper is awake."},
    {"name": "THE GRAVEYARD", "theme": 2, "clue": "A grave bears your name. The date of death is tomorrow."},
    {"name": "THE HOSPITAL", "theme": 2, "clue": "Audio Log: 'You finally remembered.'"},
    {"name": "HOSPITAL BASEMENT", "theme": 3, "clue": "Generator logs: 'Subject 0 contained below.'"},
    {"name": "BROKEN ELEVATOR", "theme": 3, "clue": "You see yourself standing in the corridor as the doors close."},
    {"name": "SECRET LAB", "theme": 3, "clue": "Keycard Access: PROJECT LAST ROOM"},
    {"name": "THE MUTATION", "theme": 3, "clue": "Computer Log: 'Subject escaped. Hunt mode activated.'"},
    {"name": "ABANDONED SUBWAY", "theme": 4, "clue": "The train arrives. Every seat has a photo of you."},
    {"name": "GHOST TRAIN", "theme": 4, "clue": "Conductor's Manual: 'The train only goes to the Mansion.'"},
    {"name": "DARK FOREST", "theme": 4, "clue": "Compass spins wildly. Someone is watching from the trees."},
    {"name": "ABANDONED CAMP", "theme": 4, "clue": "Radio Transmission: 'Don't trust the person with you.'"},
    {"name": "FOREST CABIN", "theme": 4, "clue": "Old Diary: 'The fifth person was never human.'"},
    {"name": "THE FOG VILLAGE", "theme": 4, "clue": "House Wall: 'WELCOME HOME.'"},
    {"name": "HAUNTED HOTEL", "theme": 5, "clue": "Room 13 Ledger: Your name is checked in. For 50 years."},
    {"name": "HOTEL BASEMENT", "theme": 5, "clue": "Footsteps in the dark. No shadow casting them."},
    {"name": "ABANDONED THEATER", "theme": 5, "clue": "Actor's Mask: It fits perfectly on your face."},
    {"name": "HAUNTED CIRCUS", "theme": 5, "clue": "Carousel Controls: The music never stops."},
    {"name": "THE FUNHOUSE", "theme": 5, "clue": "Reality distorts. The walls are breathing."},
    {"name": "ABANDONED SCHOOL", "theme": 6, "clue": "Blackboard: 'WHERE WERE YOU?'"},
    {"name": "SCHOOL BASEMENT", "theme": 6, "clue": "Records: You were a student here. You never left."},
    {"name": "OLD FACTORY", "theme": 7, "clue": "Machine Logs: 'Production: Memories.'"},
    {"name": "MACHINE ROOM", "theme": 7, "clue": "The monster was trapped in the gears. Now it's free."},
    {"name": "COMPUTER FACILITY", "theme": 7, "clue": "File Recovered: SUBJECT: PLAYER. STATUS: MEMORY ERASED."},
    {"name": "SECURITY CENTER", "theme": 7, "clue": "Camera 07: You are standing in the room. But you aren't."},
    {"name": "EMPTY OFFICE", "theme": 7, "clue": "Employee Badge: Your face. Your name. 'The Mimic'."},
    {"name": "ROOFTOP", "theme": 8, "clue": "Lightning strikes. The monster is only visible in the flash."},
    {"name": "UNDERGROUND BUNKER", "theme": 8, "clue": "Blast Door Codes: 'SEAL THE PAST'"},
    {"name": "SECRET FACILITY", "theme": 8, "clue": "Quarantine Zone: 'Infection rate 100%'"},
    {"name": "FROZEN BASE", "theme": 8, "clue": "Ice Core Sample: 'They are still awake in the ice.'"},
    {"name": "ABANDONED SHIP", "theme": 9, "clue": "Engine Room: Something massive is under the hull."},
    {"name": "ENGINE ROOM", "theme": 9, "clue": "Captain's Log: 'Water rising. We never left.'"},
    {"name": "FOG ISLAND", "theme": 9, "clue": "Lighthouse Beam: The island is empty. But someone calls your name."},
    {"name": "ANCIENT CASTLE", "theme": 9, "clue": "Black Crown: Touching it floods your mind with memories."},
    {"name": "CASTLE DUNGEON", "theme": 9, "clue": "Prisoner: 'You are the reason we are trapped here.'"},
    {"name": "BURNING MANSION", "theme": 0, "clue": "Map: This is Level 1. It's burning down."},
    {"name": "UNDERGROUND RUINS", "theme": 9, "clue": "Ancient Seal: 'The Buried God stirs.'"},
    {"name": "THE ANCIENT TEMPLE", "theme": 9, "clue": "Key: 'ROOM 50'"},
    {"name": "SHADOW WORLD", "theme": 1, "clue": "Your shadow detaches. It moves on its own."},
    {"name": "NIGHTMARE WORLD", "theme": 1, "clue": "Childhood memories merge with the mansion."},
    {"name": "REALITY BREAK", "theme": 1, "clue": "Doors disappear. Rooms duplicate. You meet yourself."},
    {"name": "THE ENTITY'S HOUSE", "theme": 0, "clue": "Reveal: The Entity isn't here to kill you. It wants you to remember."},
    {"name": "THE LAST ROOM", "theme": 0, "clue": "A chair. A photograph. The truth is complete."},
    {"name": "FINAL NIGHT", "theme": 0, "clue": "The Final Confrontation. The Loop Ends."}
]

def clamp(v, a, b): return a if v < a else b if v > b else v
def lerp(a, b, t): return a + (b - a) * t
def ease_out(t): return 1 - (1 - t) ** 3

# ============================================================
# SOUND MANAGER
# ============================================================
class SoundManager:
    def __init__(self):
        try:
            pygame.mixer.pre_init(44100, -16, 2, 512)
            pygame.mixer.init()
            self.ok = True
        except pygame.error:
            self.ok = False
        self.sr = 44100
        self.muted = False
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.channels: Dict[str, pygame.mixer.Channel] = {}
        if self.ok: self._build()

    def _mk(self, samples, vol=1.0):
        if not self.ok: return None
        samples = np.clip(samples * vol, -1, 1)
        stereo = np.column_stack([samples, samples])
        return pygame.sndarray.make_sound((stereo * 32767).astype(np.int16))

    def _env(self, n, attack=0.01, release=0.3):
        a = int(self.sr * attack); r = int(self.sr * release)
        e = np.ones(n)
        if a > 0: e[:a] = np.linspace(0, 1, a)
        if r > 0 and r < n: e[-r:] = np.linspace(1, 0, r)
        return e

    def _build(self):
        sr = self.sr
        def heartbeat():
            n = int(sr * 1.1); t = np.arange(n)/sr
            s = np.zeros(n)
            for off in (0.0, 0.22):
                seg = np.exp(-((t - off - 0.02) * 18)**2) * np.sin(2*np.pi*55*(t-off))
                s += seg * 0.8
            return s * 0.6
        self.sounds['heartbeat'] = self._mk(heartbeat())

        def footstep():
            n = int(sr * 0.12); t = np.arange(n)/sr
            noise = np.random.uniform(-1, 1, n)
            noise = np.convolve(noise, np.ones(8)/8, mode='same')
            env = np.exp(-t * 28)
            return (noise * 0.7 + np.sin(2*np.pi*90*t) * 0.3) * env
        self.sounds['footstep'] = self._mk(footstep(), 0.5)

        def creak():
            n = int(sr * 1.2); t = np.arange(n)/sr
            f = 220 + 380 * np.sin(t * 6) + 60 * np.random.uniform(-1,1,n)
            phase = np.cumsum(2*np.pi*f/sr)
            return np.sin(phase) * self._env(n, 0.05, 1.0) * 0.5
        self.sounds['creak'] = self._mk(creak(), 0.6)

        def whisper():
            n = int(sr * 1.6); t = np.arange(n)/sr
            noise = np.random.uniform(-1, 1, n)
            noise = np.convolve(noise, np.array([1,-1,0,0,1,-1]), mode='same')
            am = (0.5 + 0.5*np.sin(2*np.pi*7*t))
            return noise * am * self._env(n, 0.2, 1.2) * 0.6
        self.sounds['whisper'] = self._mk(whisper(), 0.45)

        def ambient():
            n = int(sr * 6.0); t = np.arange(n)/sr
            s = (np.sin(2*np.pi*55*t) * 0.3 + np.sin(2*np.pi*82.5*t) * 0.2)
            wind = np.convolve(np.random.uniform(-1,1,n), np.ones(200)/200, mode='same') * 0.15
            return (s + wind) * 0.5
        self.sounds['ambient'] = self._mk(ambient(), 0.35)

        def jumpscare():
            n = int(sr * 1.4); t = np.arange(n)/sr
            noise = np.random.uniform(-1, 1, n) * 0.8
            screech = np.sin(2*np.pi*880*t + 8*np.sin(2*np.pi*30*t)) * 0.5
            env = np.exp(-t * 2.4); env[:int(sr*0.005)] = np.linspace(0,1,int(sr*0.005))
            return (noise + screech) * env
        self.sounds['jumpscare'] = self._mk(jumpscare(), 0.9)

        def pickup():
            n = int(sr * 0.5); t = np.arange(n)/sr
            return (np.sin(2*np.pi*880*t)*0.4 + np.sin(2*np.pi*1320*t)*0.3) * np.exp(-t * 6)
        self.sounds['pickup'] = self._mk(pickup(), 0.5)

        def moan():
            n = int(sr * 1.6); t = np.arange(n)/sr
            f = 180 + 40*np.sin(2*np.pi*2*t)
            phase = np.cumsum(2*np.pi*f/sr)
            return (np.sin(phase) + np.sin(2*np.pi*6*t) * 0.2) * self._env(n, 0.3, 1.0) * 0.5
        self.sounds['moan'] = self._mk(moan(), 0.5)

        def click():
            n = int(sr * 0.08); t = np.arange(n)/sr
            return np.sin(2*np.pi*660*t) * np.exp(-t*30) * 0.4
        self.sounds['click'] = self._mk(click(), 0.4)

        def locked():
            n = int(sr * 0.25); t = np.arange(n)/sr
            return np.sin(2*np.pi*180*t) * 0.5 * np.exp(-t*15) + np.random.uniform(-1,1,n)*0.2*np.exp(-t*20)
        self.sounds['locked'] = self._mk(locked(), 0.5)

    def play(self, name, vol=1.0, loop=False):
        if not self.ok or self.muted: return
        s = self.sounds.get(name)
        if s is None: return
        s.set_volume(vol)
        if loop:
            ch = self.channels.get(name)
            if ch is None or not ch.get_busy():
                ch = pygame.mixer.find_channel()
                if ch: ch.play(s, loops=-1); self.channels[name] = ch
        else: s.play()

    def stop_all(self):
        if self.ok: pygame.mixer.stop()
        self.channels.clear()

# ============================================================
# PROCEDURAL ASSETS
# ============================================================
class Assets:
    def __init__(self):
        self.fonts = {
            'title': pygame.font.SysFont("Georgia,Times New Roman,serif", 72, bold=True),
            'h1':    pygame.font.SysFont("Georgia,serif", 40, bold=True),
            'h2':    pygame.font.SysFont("Georgia,serif", 26, bold=True),
            'body':  pygame.font.SysFont("Consolas,Courier New,monospace", 18),
            'small': pygame.font.SysFont("Consolas,Courier New,monospace", 14),
            'hud':   pygame.font.SysFont("Consolas,monospace", 16, bold=True),
        }
        self.textures: Dict[str, pygame.Surface] = {}
        self.sprites = self._gen_sprites()
        self.vignette = self._gen_vignette()
        self.current_theme = -1

    def gen_textures(self, theme_idx):
        if self.current_theme == theme_idx: return
        self.current_theme = theme_idx
        t = THEMES[theme_idx]
        wall_c = t['wall']; floor_c = t['floor']
        
        s = pygame.Surface((TILE, TILE)).convert()
        s.fill(floor_c)
        for y in range(TILE):
            shade = random.uniform(-0.1, 0.1)
            c = (int(floor_c[0]*(1+shade)), int(floor_c[1]*(1+shade)), int(floor_c[2]*(1+shade)))
            pygame.draw.line(s, c, (0, y), (TILE, y))
        for i in range(0, TILE, 10):
            pygame.draw.line(s, (max(0,floor_c[0]-20), max(0,floor_c[1]-20), max(0,floor_c[2]-20)), (0, i), (TILE, i), 1)
        self.textures['floor'] = s
        
        w = pygame.Surface((TILE, TILE)).convert()
        w.fill(wall_c)
        for y in range(0, TILE, 10):
            pygame.draw.line(w, (max(0,wall_c[0]-25), max(0,wall_c[1]-25), max(0,wall_c[2]-25)), (0, y), (TILE, y), 2)
        for y in range(0, TILE, 20):
            off = 10 if (y//20) % 2 else 0
            for x in range(off, TILE, 20):
                pygame.draw.line(w, (max(0,wall_c[0]-25), max(0,wall_c[1]-25), max(0,wall_c[2]-25)), (x, y), (x, y+10), 2)
        self.textures['wall'] = w
        
        d = pygame.Surface((TILE, TILE), pygame.SRCALPHA).convert_alpha()
        pygame.draw.rect(d, (60, 40, 35), (4, 2, TILE-8, TILE-4))
        pygame.draw.rect(d, (100, 70, 55), (4, 2, TILE-8, TILE-4), 2)
        pygame.draw.circle(d, (220, 180, 60), (TILE-10, TILE//2), 3)
        self.textures['door'] = d
        
        do = pygame.Surface((TILE, TILE), pygame.SRCALPHA).convert_alpha()
        pygame.draw.rect(do, (25, 18, 16), (4, 2, TILE-8, TILE-4))
        self.textures['door_open'] = do

    def _gen_sprites(self):
        s = {}
        size = 48 
        
        # 3D Animated Human Character
        def draw_human(surf, dir_idx, frame):
            cx, cy = size//2, size//2
            shadow = pygame.Surface((40, 20), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow, (0, 0, 0, 100), (0, 0, 40, 20))
            surf.blit(shadow, (cx-20, cy+14))
            bob = math.sin(frame * math.pi/2) * 1.5
            leg_off = math.sin(frame * math.pi/2) * 3
            leg_y = cy + 6 + bob
            pygame.draw.rect(surf, (45, 45, 55), (cx-7, leg_y, 6, 10 + leg_off), border_radius=2)
            pygame.draw.rect(surf, (45, 45, 55), (cx+1, leg_y, 6, 10 - leg_off), border_radius=2)
            pygame.draw.rect(surf, (25, 25, 30), (cx-8, leg_y + 10 + leg_off, 8, 4), border_radius=2)
            pygame.draw.rect(surf, (25, 25, 30), (cx+0, leg_y + 10 - leg_off, 8, 4), border_radius=2)
            body_rect = pygame.Rect(cx-12, cy-6+bob, 24, 20)
            pygame.draw.ellipse(surf, (60, 45, 80), body_rect)
            pygame.draw.ellipse(surf, (90, 70, 110), body_rect.inflate(-4, -12)) 
            pygame.draw.ellipse(surf, (40, 25, 60), body_rect, 2)
            head_y = cy - 14 + bob
            pygame.draw.circle(surf, (40, 25, 15), (cx, head_y), 11) 
            pygame.draw.circle(surf, (220, 180, 150), (cx, head_y), 9) 
            pygame.draw.circle(surf, (180, 140, 110), (cx+2, head_y+2), 7) 
            pygame.draw.circle(surf, (40, 25, 15), (cx, head_y-3), 9) 
            dir_vecs = [(0,-1),(1,0),(0,1),(-1,0)]
            dx, dy = dir_vecs[dir_idx]
            if dy != 1: 
                pygame.draw.circle(surf, (20, 20, 20), (cx + dx*3 - 2, head_y + dy*2 + (1 if dy==-1 else 0)), 1)
                pygame.draw.circle(surf, (20, 20, 20), (cx + dx*3 + 2, head_y + dy*2 + (1 if dy==-1 else 0)), 1)
            arm_y = cy - 2 + bob
            if dir_idx == 0: 
                pygame.draw.rect(surf, (60, 45, 80), (cx-12, arm_y, 5, 12), border_radius=2)
                pygame.draw.rect(surf, (60, 45, 80), (cx+7, arm_y, 5, 12), border_radius=2)
                pygame.draw.rect(surf, (40,40,50), (cx-2, arm_y-8, 4, 8))
            elif dir_idx == 2: 
                pygame.draw.rect(surf, (60, 45, 80), (cx-14, arm_y, 5, 12), border_radius=2)
                pygame.draw.rect(surf, (60, 45, 80), (cx+9, arm_y, 5, 12), border_radius=2)
                pygame.draw.rect(surf, (40,40,50), (cx-2, arm_y+12, 4, 8))
            elif dir_idx == 1: 
                pygame.draw.rect(surf, (60, 45, 80), (cx+4, arm_y, 12, 5), border_radius=2)
                pygame.draw.rect(surf, (40,40,50), (cx+14, arm_y-1, 8, 4))
                pygame.draw.circle(surf, (255, 255, 200), (cx+22, arm_y+1), 2)
            elif dir_idx == 3: 
                pygame.draw.rect(surf, (60, 45, 80), (cx-16, arm_y, 12, 5), border_radius=2)
                pygame.draw.rect(surf, (40,40,50), (cx-22, arm_y-1, 8, 4))
                pygame.draw.circle(surf, (255, 255, 200), (cx-22, arm_y+1), 2)

        player = []
        for d in range(4):
            row = []
            for f in range(4):
                surf = pygame.Surface((size, size), pygame.SRCALPHA).convert_alpha()
                draw_human(surf, d, f)
                row.append(surf)
            player.append(row)
        s['player'] = player

        # Ghost
        gs = 56 
        ghost_frames = []
        for f in range(8):
            surf = pygame.Surface((gs, gs), pygame.SRCALPHA).convert_alpha()
            cx, cy = gs//2, gs//2
            bob = math.sin(f * math.pi/4) * 2
            sway = math.sin(f * math.pi/4) * 1.5
            aura = pygame.Surface((gs, gs), pygame.SRCALPHA)
            pygame.draw.circle(aura, (150, 0, 0, 40), (cx, cy), 25)
            surf.blit(aura, (0, 0))
            pts = []
            for i in range(8):
                t = i / 7
                y = cy + 6 + t * 16 + bob
                x = cx + sway * (1-t) + math.sin(t*8 + f) * 2
                pts.append((x, y))
            for i in range(len(pts)-1):
                a = int(180 * (1 - i/len(pts)))
                pygame.draw.line(surf, (220, 220, 240, a), pts[i], pts[i+1], 6-i//3)
            body_r = pygame.Rect(cx-12, cy-16+bob, 24, 24)
            pygame.draw.ellipse(surf, (230, 240, 255, 220), body_r)
            pygame.draw.ellipse(surf, (255, 255, 255, 150), body_r.inflate(-6,-6))
            pygame.draw.ellipse(surf, (255, 0, 0), (cx-8, cy-8+bob, 5, 8))
            pygame.draw.ellipse(surf, (255, 0, 0), (cx+3, cy-8+bob, 5, 8))
            pygame.draw.ellipse(surf, (20, 0, 10), (cx-4, cy-1+bob, 8, 6))
            ghost_frames.append(surf)
        s['ghost'] = ghost_frames

        # Items
        c = pygame.Surface((24, 24), pygame.SRCALPHA).convert_alpha()
        pygame.draw.rect(c, (200, 180, 140), (4, 2, 16, 20))
        pygame.draw.rect(c, (140, 120, 90), (4, 2, 16, 20), 1)
        pygame.draw.line(c, (90, 70, 50), (6, 8), (18, 8), 1)
        s['clue'] = c

        bat = pygame.Surface((20, 20), pygame.SRCALPHA).convert_alpha()
        pygame.draw.rect(bat, (50, 50, 50), (4, 2, 12, 20), border_radius=3)
        pygame.draw.rect(bat, (255, 200, 0), (6, 4, 8, 16), border_radius=2)
        pygame.draw.rect(bat, (0, 255, 0), (6, 14, 8, 6), border_radius=2)
        s['battery'] = bat

        pill = pygame.Surface((20, 20), pygame.SRCALPHA).convert_alpha()
        pygame.draw.ellipse(pill, (255, 255, 255), (2, 8, 16, 8))
        pygame.draw.ellipse(pill, (200, 0, 0), (2, 8, 8, 8))
        s['pill'] = pill

        wd = pygame.Surface((TILE, TILE), pygame.SRCALPHA).convert_alpha()
        pygame.draw.rect(wd, (80, 60, 40), (2, 2, TILE-4, TILE-4))
        pygame.draw.rect(wd, (110, 80, 50), (2, 2, TILE-4, TILE-4), 2)
        pygame.draw.line(wd, (40, 25, 15), (TILE//2, 4), (TILE//2, TILE-4), 2)
        pygame.draw.circle(wd, (200, 180, 60), (TILE//2-4, TILE//2), 2)
        s['wardrobe'] = wd

        lamp = pygame.Surface((TILE, TILE), pygame.SRCALPHA).convert_alpha()
        pygame.draw.rect(lamp, (70, 55, 45), (TILE//2-3, 8, 6, 12))
        pygame.draw.circle(lamp, (255, 180, 80, 220), (TILE//2, 6), 6)
        s['lamp'] = lamp

        ex = pygame.Surface((TILE*2, TILE*2), pygame.SRCALPHA).convert_alpha()
        pygame.draw.rect(ex, (50, 35, 30), (4, 4, TILE*2-8, TILE*2-8))
        pygame.draw.rect(ex, (110, 80, 55), (4, 4, TILE*2-8, TILE*2-8), 3)
        pygame.draw.circle(ex, (220, 180, 70), (TILE*2-14, TILE), 5)
        s['exit'] = ex
        
        # Cinematic Jumpscare Face
        jf = pygame.Surface((W, H), pygame.SRCALPHA).convert_alpha()
        jf.fill((0,0,0,255))
        face_color = (210, 200, 190)
        pygame.draw.ellipse(jf, face_color, (W//2 - 250, 50, 500, 550))
        pygame.draw.ellipse(jf, (150, 140, 130), (W//2 - 200, 300, 400, 250))
        hair_color = (10, 5, 5)
        pygame.draw.ellipse(jf, hair_color, (W//2 - 300, 0, 600, 250))
        for i in range(12):
            x = W//2 - 250 + i * 40
            pygame.draw.polygon(jf, hair_color, [(x, 150), (x+20, 350), (x+40, 150)])
        pygame.draw.ellipse(jf, (0,0,0), (W//2 - 150, 200, 100, 150))
        pygame.draw.ellipse(jf, (0,0,0), (W//2 + 50, 200, 100, 150))
        pygame.draw.ellipse(jf, (150, 0, 0), (W//2 - 120, 250, 40, 50))
        pygame.draw.ellipse(jf, (150, 0, 0), (W//2 + 80, 250, 40, 50))
        pygame.draw.line(jf, (100, 0, 0), (W//2 - 50, 80), (W//2 + 50, 180), 10)
        pygame.draw.line(jf, (100, 0, 0), (W//2 - 80, 130), (W//2 + 80, 130), 10)
        pygame.draw.ellipse(jf, (0,0,0), (W//2 - 80, 400, 160, 250))
        for i in range(5):
            pygame.draw.polygon(jf, (230, 230, 220), [(W//2 - 70 + i*30, 400), (W//2 - 55 + i*30, 450), (W//2 - 40 + i*30, 400)])
            pygame.draw.polygon(jf, (230, 230, 220), [(W//2 - 70 + i*30, 650), (W//2 - 55 + i*30, 600), (W//2 - 40 + i*30, 650)])
        s['jumpscare'] = jf
        
        # Story Paper Texture
        paper = pygame.Surface((600, 400), pygame.SRCALPHA).convert_alpha()
        paper.fill((210, 180, 140, 240))
        pygame.draw.rect(paper, (100, 80, 50), (0,0,600,400), 5)
        for i in range(0, 600, 20):
            pygame.draw.polygon(paper, (210, 180, 140, 0), [(i, 0), (i+10, 20), (i+20, 0)])
            pygame.draw.polygon(paper, (210, 180, 140, 0), [(i, 400), (i+10, 380), (i+20, 400)])
        s['paper'] = paper
        
        return s

    def _gen_vignette(self):
        s = pygame.Surface((W, H), pygame.SRCALPHA).convert_alpha()
        cx, cy = W//2, H//2
        max_r = math.hypot(cx, cy)
        for y in range(0, H, 2):
            for x in range(0, W, 2):
                d = math.hypot(x-cx, y-cy) / max_r
                a = int(clamp((d - 0.6) * 350, 0, 180))
                if a > 0: s.fill((0, 0, 0, a), (x, y, 2, 2))
        return s

# ============================================================
# PARTICLES
# ============================================================
@dataclass
class Particle:
    x: float; y: float; vx: float; vy: float
    life: float; max_life: float; size: float
    color: Tuple[int,int,int]; grav: float = 0.0; fade: bool = True

class ParticleSystem:
    def __init__(self): self.parts: List[Particle] = []
    def emit(self, x, y, count=10, speed=40, life=0.6, size=3, color=(180,170,160), spread=2*math.pi, angle=0, grav=0):
        if len(color) == 3: color = (color[0], color[1], color[2])
        for _ in range(count):
            a = angle + random.uniform(-spread/2, spread/2)
            sp = speed * random.uniform(0.4, 1.0)
            l = life * random.uniform(0.7, 1.2)
            self.parts.append(Particle(x, y, math.cos(a)*sp, math.sin(a)*sp, l, l, size * random.uniform(0.7, 1.3), color, grav))
    def emit_fog(self, x, y):
        self.emit(x, y, count=1, speed=4, life=4.0, size=30, color=(110, 100, 120), spread=2*math.pi, grav=0)
    def emit_dust(self, x, y):
        self.emit(x, y, count=1, speed=2, life=4.0, size=1, color=(200, 200, 200), spread=2*math.pi, grav=-1)
    def update(self, dt):
        alive = []
        for p in self.parts:
            p.life -= dt
            if p.life <= 0: continue
            p.x += p.vx * dt; p.y += p.vy * dt; p.vy += p.grav * dt; p.vx *= 0.98
            alive.append(p)
        self.parts = alive
    def draw(self, surf, cam):
        for p in self.parts:
            t = max(0, p.life / p.max_life)
            a = clamp(int(255 * t) if p.fade else 255, 0, 255)
            sz = max(1, int(p.size * (0.5 + 0.5*t)))
            sx, sy = int(p.x - cam.x), int(p.y - cam.y)
            if -20 < sx < W+20 and -20 < sy < H+20:
                s = pygame.Surface((sz*2, sz*2), pygame.SRCALPHA)
                pygame.draw.circle(s, (*p.color, a), (sz, sz), sz)
                surf.blit(s, (sx-sz, sy-sz))

# ============================================================
# CAMERA
# ============================================================
class Camera:
    def __init__(self):
        self.x = 0.0; self.y = 0.0; self.shake_amp = 0.0; self.shake_t = 0.0; self.shake_dur = 0.0; self.ox = 0.0; self.oy = 0.0
        self.breath_t = 0.0
    def follow(self, tx, ty, dt, smoothing=6.0):
        self.x += (tx - W/2 - self.x) * min(1, smoothing * dt)
        self.y += (ty - H/2 - self.y) * min(1, smoothing * dt)
    def shake(self, amp, dur=0.4):
        if amp > self.shake_amp: self.shake_amp = amp; self.shake_dur = dur; self.shake_t = dur
    def update(self, dt, fear=0):
        self.breath_t += dt * (1.5 + fear/50)
        self.ox = math.sin(self.breath_t) * 2
        self.oy = math.cos(self.breath_t * 0.8) * 2
        if self.shake_t > 0:
            self.shake_t -= dt; t = max(0, self.shake_t / self.shake_dur); amp = self.shake_amp * t * t
            self.ox += random.uniform(-amp, amp); self.oy += random.uniform(-amp, amp)

# ============================================================
# MANSION
# ============================================================
class Door:
    def __init__(self, tx, ty, is_exit=False):
        self.x = tx * TILE + TILE/2; self.y = ty * TILE + TILE/2
        self.open = False; self.rect = pygame.Rect(tx*TILE, ty*TILE, TILE, TILE)
        self.is_exit = is_exit
    def interact(self, game):
        if self.is_exit:
            if game.player.has_clue:
                game._next_level()
            else:
                game.sound.play('locked')
                game.toast("The door is sealed. Find the clue first...", 3.0)
            return
        self.open = not self.open
        game.sound.play('creak', 0.6 if self.open else 0.4)
    def blocks(self): return not self.open

class Item:
    def __init__(self, tx, ty, kind, text=None):
        self.x = tx * TILE + TILE/2; self.y = ty * TILE + TILE/2
        self.kind = kind; self.taken = False; self.bob = random.random() * math.pi * 2
        self.text = text
    def interact(self, game):
        if self.taken: return
        self.taken = True
        game.sound.play('pickup', 0.7)
        if self.kind == 'clue':
            game.player.has_clue = True
            game.player.story_text = self.text
            game.player.notes.append(self.text)
            game.state = GameState.STORY
        elif self.kind == 'battery':
            game.player.flash_battery = 100
            game.player.flash_on = True
            game.toast("Picked up Battery. Flashlight recharged!", 3.0)
        elif self.kind == 'pill':
            game.player.fear = max(0, game.player.fear - 50)
            game.toast("Pills taken. Fear reduced.", 3.0)

class HideSpot:
    def __init__(self, tx, ty):
        self.x = tx * TILE + TILE/2; self.y = ty * TILE + TILE/2
        self.rect = pygame.Rect(tx*TILE, ty*TILE, TILE, TILE)

class Mansion:
    def __init__(self, level_num):
        self.level = level_num
        self.data = LEVELS_DATA[level_num]
        self.theme_idx = self.data['theme']
        Assets_singleton.gen_textures(self.theme_idx)
        self.theme_name = THEMES[self.theme_idx]['name']
        
        self.w, self.h = 32, 22
        self.grid = [['#' for _ in range(self.w)] for _ in range(self.h)]
        self.doors: List[Door] = []; self.items: List[Item] = []
        self.lamps: List[dict] = []; self.exit_pos = None; self.ghost_spawn = None; self.start_pos = None
        self.hide_spots: List[HideSpot] = []
        self._generate()
        self.floor_surf = self._bake_floor()

    def _generate(self):
        rooms = []
        self._carve_room(2, 2, 6, 6)
        self.start_pos = (4*TILE, 4*TILE)
        rooms.append((2, 2, 6, 6))
        
        for _ in range(8):
            for _ in range(10):
                rx, ry = random.randint(1, self.w-7), random.randint(1, self.h-7)
                rw, rh = random.randint(5, 8), random.randint(5, 8)
                if rx+rw < self.w-1 and ry+rh < self.h-1:
                    px, py, _, _ = rooms[-1]
                    self._carve_room(rx, ry, rw, rh)
                    self._carve_corridor(px+2, py+2, rx+rw//2, ry+rh//2)
                    self.doors.append(Door(px+3, py+2))
                    rooms.append((rx, ry, rw, rh))
                    break
        
        ex, ey, _, _ = rooms[-1]
        self.grid[ey+1][ex+1] = '.'
        self.doors.append(Door(ex+1, ey+1, is_exit=True))
        self.exit_pos = ((ex+1)*TILE + TILE/2, (ey+1)*TILE + TILE/2)
        
        gx, gy, _, _ = rooms[len(rooms)//2]
        self.grid[gy+1][gx+1] = '.'
        self.ghost_spawn = ((gx+1)*TILE + TILE/2, (gy+1)*TILE + TILE/2)
        
        kx, ky, kw, kh = rooms[random.randint(1, len(rooms)-2)]
        self.items.append(Item(kx + random.randint(0, kw-1), ky + random.randint(0, kh-1), 'clue', self.data['clue']))
        
        for rx, ry, rw, rh in rooms[1:]:
            if random.random() < 0.7:
                self.lamps.append({'x': (rx + random.randint(0, rw-1))*TILE + TILE/2, 'y': (ry + 1)*TILE + TILE/2, 'radius': 200, 'intensity': 1.0, 'flicker_t': random.random()*5})
            if random.random() < 0.4:
                ix, iy = rx + random.randint(0, rw-1), ry + random.randint(0, rh-1)
                if self.grid[iy][ix] == '.':
                    typ = 'battery' if random.random() < 0.6 else 'pill'
                    self.items.append(Item(ix, iy, typ))
            if random.random() < 0.5:
                hx, hy = rx + random.randint(0, rw-1), ry + random.randint(0, rh-1)
                if self.grid[hy][hx] == '.':
                    self.hide_spots.append(HideSpot(hx, hy))

    def _carve_room(self, x, y, w, h):
        for ry in range(y, y+h):
            for rx in range(x, x+w):
                if 0 <= ry < self.h and 0 <= rx < self.w: self.grid[ry][rx] = '.'

    def _carve_corridor(self, x1, y1, x2, y2):
        x, y = x1, y1
        while x != x2: self.grid[y][x] = '.'; x += 1 if x < x2 else -1
        while y != y2: self.grid[y][x] = '.'; y += 1 if y < y2 else -1

    def _bake_floor(self):
        surf = pygame.Surface((self.w*TILE, self.h*TILE)).convert()
        surf.fill(C_BG)
        for y in range(self.h):
            for x in range(self.w):
                tx, ty = x*TILE, y*TILE
                if self.grid[y][x] == '#':
                    surf.blit(Assets_singleton.textures['wall'], (tx, ty))
                    if y+1 < self.h and self.grid[y+1][x] != '#':
                        shadow = pygame.Surface((TILE, 12), pygame.SRCALPHA)
                        pygame.draw.rect(shadow, (0, 0, 0, 100), (0, 0, TILE, 12))
                        surf.blit(shadow, (tx, ty+TILE-4))
                else:
                    surf.blit(Assets_singleton.textures['floor'], (tx, ty))
        for h in self.hide_spots:
            surf.blit(Assets_singleton.sprites['wardrobe'], (h.x-TILE//2, h.y-TILE//2))
        for y in range(self.h):
            for x in range(self.w):
                if self.grid[y][x] != '#' and random.random() < 0.03:
                    pygame.draw.circle(surf, C_BLOOD, (x*TILE + random.randint(5, 35), y*TILE + random.randint(5, 35)), random.randint(4, 10))
        return surf

    def is_wall(self, tx, ty):
        if tx < 0 or ty < 0 or tx >= self.w or ty >= self.h: return True
        return self.grid[ty][tx] == '#'

    def is_solid(self, px, py, radius=14):
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if self.is_wall(int((px + ax*radius) // TILE), int((py + ay*radius) // TILE)): return True
        return False

# ============================================================
# PLAYER
# ============================================================
class Player:
    def __init__(self, x, y):
        self.x = x; self.y = y; self.r = 14; self.speed = 140; self.sprint_speed = 210
        self.dir_idx = 0; self.anim_t = 0.0; self.anim_frame = 0; self.moving = False
        self.hp = 100.0; self.fear = 0.0; self.stamina = 100.0
        self.has_clue = False; self.story_text = ""
        self.notes: List[str] = []
        self.flash_on = True; self.flash_battery = 100.0; self.flash_angle = 0.0; self.flash_range = 360
        self.hidden = False; self.noise_level = 0.0; self.invuln_t = 0.0; self.alive = True

    def take_damage(self, dmg, game):
        if self.invuln_t > 0: return
        self.hp -= dmg; self.invuln_t = 0.8
        game.camera.shake(12, 0.5); game.sound.play('jumpscare', 0.6)
        if self.hp <= 0: self.hp = 0; self.alive = False

    def update(self, dt, keys, game):
        if not self.alive: return
        self.invuln_t = max(0, self.invuln_t - dt)
        dx = (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT])
        dy = (keys[pygame.K_s] or keys[pygame.K_DOWN]) - (keys[pygame.K_w] or keys[pygame.K_UP])
        if dx and dy: dx *= 0.7071; dy *= 0.7071
        sprint = (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) and self.stamina > 0 and (dx or dy)
        speed = self.sprint_speed if sprint else self.speed
        if sprint: self.stamina = max(0, self.stamina - 30*dt)
        else: self.stamina = min(100, self.stamina + 15*dt)
        if self.hidden: speed = 0; dx = dy = 0
        
        nx = self.x + dx * speed * dt; ny = self.y + dy * speed * dt
        if not game.mansion.is_solid(nx, self.y, self.r): self.x = nx
        if not game.mansion.is_solid(self.x, ny, self.r): self.y = ny
        
        self.moving = (dx or dy) and not self.hidden
        if self.moving:
            self.anim_t += dt * (8 if sprint else 6)
            self.anim_frame = int(self.anim_t) % 4
            if abs(dx) > abs(dy): self.dir_idx = 1 if dx > 0 else 3
            else: self.dir_idx = 2 if dy > 0 else 0
            self.noise_level = 140 if sprint else 70
            if int(self.anim_t) != int(self.anim_t - dt*8): game.sound.play('footstep', 0.4 if sprint else 0.2)
        else: self.noise_level = max(0, self.noise_level - 200*dt); self.anim_frame = 0
        
        mx, my = pygame.mouse.get_pos()
        self.flash_angle = math.atan2(my + game.camera.y - game.camera.oy - self.y, mx + game.camera.x - game.camera.ox - self.x)
        if self.flash_on:
            self.flash_battery = max(0, self.flash_battery - 1.2 * dt)
            if self.flash_battery <= 0: self.flash_on = False; game.toast("Flashlight died.")
        
        light_here = game.light_at(self.x, self.y)
        if light_here < 0.2 and not self.hidden: self.fear += 4.0 * dt
        else: self.fear -= 6.0 * dt
        if game.ghost.state == 'CHASE' and game.ghost.dist_to_player < 200: self.fear += 25.0 * dt
        if self.hidden: self.fear -= 8 * dt
        self.fear = clamp(self.fear, 0, 100)
        if self.fear >= 100: self.hp -= 5 * dt; self.alive = self.hp > 0
        
        if self.fear > 50:
            interval = lerp(1.1, 0.45, (self.fear-50)/50)
            if not hasattr(self, '_hb_t'): self._hb_t = 0
            self._hb_t -= dt
            if self._hb_t <= 0:
                game.sound.play('heartbeat', clamp(0.4 + self.fear/200, 0.4, 0.9))
                self._hb_t = interval

    def draw(self, surf, cam, assets):
        sx = int(self.x - cam.x + cam.ox); sy = int(self.y - cam.y + cam.oy)
        if self.hidden:
            pygame.draw.circle(surf, (60, 50, 70, 100), (sx, sy), 8, 1)
            return
        spr = assets.sprites['player'][self.dir_idx][self.anim_frame]
        if self.invuln_t > 0 and int(self.invuln_t*20) % 2:
            spr = spr.copy(); spr.fill((180, 30, 30, 0), special_flags=pygame.BLEND_RGBA_ADD)
        surf.blit(spr, (sx - spr.get_width()//2, sy - spr.get_height()//2))

# ============================================================
# GHOST
# ============================================================
class Ghost:
    def __init__(self, x, y, level_diff):
        self.x = x; self.y = y; self.r = 14
        self.speed_patrol = 60 + level_diff * 2
        self.speed_chase = 110 + level_diff * 3
        self.speed_investigate = 80 + level_diff * 2
        self.state = 'PATROL'; self.target = (x, y)
        self.patrol_timer = 0; self.anger = 0.0; self.dist_to_player = 9999
        self.anim_t = 0.0; self.moan_t = random.uniform(4, 8)

    def _can_see(self, player, mansion):
        if player.hidden: return False
        dx = player.x - self.x; dy = player.y - self.y
        dist = math.hypot(dx, dy)
        if dist > 380: return False
        steps = int(dist / (TILE/2))
        if steps == 0: return True
        for i in range(steps):
            t = i / steps
            cx = self.x + dx * t; cy = self.y + dy * t
            if mansion.is_wall(int(cx//TILE), int(cy//TILE)): return False
        return True

    def _pick_patrol_target(self, mansion):
        for _ in range(20):
            tx = random.randint(1, mansion.w-2); ty = random.randint(1, mansion.h-2)
            if not mansion.is_wall(tx, ty):
                self.target = (tx*TILE + TILE/2, ty*TILE + TILE/2); return
        self.target = (self.x, self.y)

    def update(self, dt, player, mansion, game):
        self.anim_t += dt
        self.dist_to_player = math.hypot(player.x - self.x, player.y - self.y)
        self.moan_t -= dt
        if self.moan_t <= 0:
            self.moan_t = random.uniform(5, 12)
            if self.dist_to_player < 600:
                vol = clamp(1 - self.dist_to_player/600, 0.1, 0.8)
                game.sound.play('moan', vol)
        
        hearing_range = max(0, player.noise_level)
        if hearing_range > 0 and not player.hidden:
            d = math.hypot(player.x - self.x, player.y - self.y)
            if d < hearing_range + 80:
                if self.state != 'CHASE':
                    self.state = 'INVESTIGATE'; self.target = (player.x, player.y)
        
        can_see = self._can_see(player, mansion)
        if can_see and self.dist_to_player < 380:
            if self.state != 'CHASE':
                if self.dist_to_player < 150:
                    game.camera.shake(10, 0.6); game.sound.play('jumpscare', 0.6)
                self.state = 'CHASE'
            self.anger = 0; self.target = (player.x, player.y)
        else:
            self.anger += dt
            if self.state == 'CHASE' and self.anger > 4:
                self.state = 'INVESTIGATE'; self.target = (player.x, player.y)
            elif self.state == 'INVESTIGATE' and self.anger > 6:
                self.state = 'PATROL'; self._pick_patrol_target(mansion)

        if self.state == 'PATROL':
            self.patrol_timer -= dt
            d = math.hypot(self.target[0]-self.x, self.target[1]-self.y)
            if d < 10 or self.patrol_timer <= 0:
                self._pick_patrol_target(mansion); self.patrol_timer = random.uniform(4, 8)
            speed = self.speed_patrol
        elif self.state == 'INVESTIGATE':
            speed = self.speed_investigate
            d = math.hypot(self.target[0]-self.x, self.target[1]-self.y)
            if d < 20:
                self.state = 'PATROL'; self._pick_patrol_target(mansion)
        else:
            speed = self.speed_chase

        dx = self.target[0] - self.x; dy = self.target[1] - self.y
        d = math.hypot(dx, dy)
        if d > 1:
            nx = self.x + dx/d * speed * dt; ny = self.y + dy/d * speed * dt
            if not mansion.is_solid(nx, self.y, self.r): self.x = nx
            if not mansion.is_solid(self.x, ny, self.r): self.y = ny
            if self.state == 'PATROL' and self.x == nx and self.y == ny:
                self._pick_patrol_target(mansion)
        
        if self.dist_to_player < 28 and not player.hidden and player.invuln_t <= 0:
            player.take_damage(50, game)
            self.x -= dx/d * 20; self.y -= dy/d * 20
            self._pick_patrol_target(mansion); self.state = 'PATROL'

    def draw(self, surf, cam, assets):
        sx = int(self.x - cam.x + cam.ox); sy = int(self.y - cam.y + cam.oy)
        aura_color = (180, 0, 0, 60) if self.state == 'CHASE' else (100, 100, 150, 40)
        aura_surf = pygame.Surface((100, 100), pygame.SRCALPHA)
        pygame.draw.circle(aura_surf, aura_color, (50, 50), 40)
        surf.blit(aura_surf, (sx-50, sy-50))
        frame = assets.sprites['ghost'][int(self.anim_t * 8) % 8]
        wobble = 1.0 + 0.05 * math.sin(self.anim_t * 6)
        if abs(wobble - 1) > 0.01:
            frame = pygame.transform.scale(frame, (int(frame.get_width()*wobble), frame.get_height()))
        surf.blit(frame, (sx - frame.get_width()//2, sy - frame.get_height()//2))

# ============================================================
# GAME STATES
# ============================================================
class GameState(Enum):
    MENU = auto(); PLAYING = auto(); PAUSED = auto()
    GAME_OVER = auto(); VICTORY = auto(); STORY = auto(); JOURNAL = auto()

# ============================================================
# GAME MANAGER
# ============================================================
Assets_singleton: Assets = None

class GameManager:
    def __init__(self, screen):
        self.screen = screen
        self.state = GameState.MENU
        self.fade_dir = 0; self.fade_alpha = 0.0; self.fade_callback = None
        self.sound = SoundManager(); self.particles = ParticleSystem(); self.camera = Camera()
        self.mansion: Optional[Mansion] = None; self.player: Optional[Player] = None; self.ghost: Optional[Ghost] = None
        self.current_level = 0
        self.toast_msg = ""; self.toast_t = 0.0
        self.menu_t = 0.0; self.end_t = 0.0; self.flicker_global = 0.0; self.hallucination_t = 0.0; self.thunder_t = random.uniform(8, 20)
        self.door_event_t = random.uniform(10, 20); self.dust_t = 0.0
        self.menu_flicker_t = 0.0; self.menu_shadow_t = 5.0
        self.buttons: List[dict] = []; self.end_buttons: List[dict] = []
        self.jumpscare_t = 0.0
        self._build_menu()
        self._init_run()

    def save_game(self):
        if self.player:
            with open(SAVE_FILE, "w") as f:
                json.dump({"level": self.current_level, "notes": self.player.notes}, f)

    def load_game(self) -> bool:
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, "r") as f:
                    data = json.load(f)
                    self.current_level = data.get("level", 0)
                    return True
            except:
                pass
        return False

    def fade_to(self, callback, dur=0.6):
        self.fade_dir = 1; self.fade_alpha = 0; self.fade_dur = dur; self.fade_callback = callback

    def _update_fade(self, dt):
        if self.fade_dir == 1:
            self.fade_alpha = min(255, self.fade_alpha + 255/self.fade_dur * dt)
            if self.fade_alpha >= 255:
                if self.fade_callback: self.fade_callback()
                self.fade_dir = -1
        elif self.fade_dir == -1:
            self.fade_alpha = max(0, self.fade_alpha - 255/self.fade_dur * dt)
            if self.fade_alpha <= 0: self.fade_dir = 0

    def _init_run(self):
        self.current_level = 0
        self.load_game() 
        self._load_level()
        self.sound.stop_all()
        self.sound.play('ambient', loop=True)

    def _load_level(self):
        if self.current_level >= 50: self.current_level = 0
        self.mansion = Mansion(self.current_level)
        sx, sy = self.mansion.start_pos
        self.player = Player(sx, sy)
        gx, gy = self.mansion.ghost_spawn
        self.ghost = Ghost(gx, gy, self.current_level)
        self.particles = ParticleSystem(); self.camera = Camera()
        self.camera.x = sx - W/2; self.camera.y = sy - H/2
        
        if self.current_level == 0: self.toast_msg = "WASD to Move. Mouse to aim. Find the Clue."
        elif self.current_level == 1: self.toast_msg = "Flashlight drains. Find Batteries (Yellow). Press F to toggle."
        elif self.current_level == 2: self.toast_msg = "Ghost is near! Find Wardrobe and press H to Hide!"
        elif self.current_level == 3: self.toast_msg = "Fear high? Find Pills (Red/White). Press TAB to read Journal."
        else: self.toast_msg = f"Chapter {self.current_level + 1}: {self.mansion.data['name']}"
        self.toast_t = 5.0

    def _restart_level(self):
        self._load_level()
        self.state = GameState.PLAYING
        self.fade_to(None, 0.4)

    def start_game(self):
        self.current_level = 0
        self.load_game()
        self._load_level()
        self.state = GameState.PLAYING
        self.fade_to(None, 0.4)

    def new_game(self):
        self.current_level = 0
        if os.path.exists(SAVE_FILE): os.remove(SAVE_FILE)
        self._load_level()
        self.state = GameState.PLAYING
        self.fade_to(None, 0.4)

    def toast(self, msg, dur=3.0):
        self.toast_msg = msg; self.toast_t = dur

    def light_at(self, x, y):
        total = 0.25
        if self.player.flash_on and self.player.flash_battery > 0:
            dx = x - self.player.x; dy = y - self.player.y
            d = math.hypot(dx, dy)
            if d < self.player.flash_range:
                ang = math.atan2(dy, dx)
                diff = (ang - self.player.flash_angle + math.pi) % (2*math.pi) - math.pi
                if abs(diff) < math.pi/3: total += (1 - d/self.player.flash_range) * 1.5
        for l in self.mansion.lamps:
            d = math.hypot(x - l['x'], y - l['y'])
            if d < l['radius']: total += (1 - d/l['radius']) * l['intensity'] * 1.2
        return clamp(total, 0, 1.5)

    def handle_event(self, ev):
        if ev.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_m:
                self.sound.muted = not self.sound.muted
                self.toast(f"Audio {'muted' if self.sound.muted else 'on'}")
            if self.state == GameState.MENU:
                if ev.key in (pygame.K_RETURN, pygame.K_SPACE): self.fade_to(self.start_game)
                elif ev.key == pygame.K_ESCAPE: pygame.quit(); sys.exit()
            elif self.state == GameState.STORY:
                if ev.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_e): self.state = GameState.PLAYING
            elif self.state == GameState.JOURNAL:
                if ev.key in (pygame.K_TAB, pygame.K_ESCAPE): self.state = GameState.PLAYING
            elif self.state == GameState.PLAYING:
                if ev.key in (pygame.K_ESCAPE, pygame.K_p): self.state = GameState.PAUSED
                elif ev.key == pygame.K_e: self._interact()
                elif ev.key == pygame.K_TAB: self.state = GameState.JOURNAL
                elif ev.key == pygame.K_f:
                    if self.player.flash_battery > 0:
                        self.player.flash_on = not self.player.flash_on
                        self.sound.play('click', 0.3)
                elif ev.key == pygame.K_h: self._toggle_hide()
            elif self.state == GameState.PAUSED:
                if ev.key in (pygame.K_ESCAPE, pygame.K_p): self.state = GameState.PLAYING
                elif ev.key == pygame.K_q: self.fade_to(lambda: (setattr(self, 'state', GameState.MENU), self._build_menu()))
            elif self.state in (GameState.GAME_OVER, GameState.VICTORY):
                if ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if self.state == GameState.GAME_OVER: self.fade_to(self._restart_level)
                    else: self.fade_to(self.new_game)
                elif ev.key == pygame.K_ESCAPE: self.fade_to(lambda: (setattr(self, 'state', GameState.MENU), self._build_menu()))
                
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if self.state == GameState.MENU:
                for b in self.buttons:
                    if b['rect'].collidepoint(ev.pos):
                        self.sound.play('click', 0.5); b['action']()
            elif self.state == GameState.PAUSED:
                for b in self.pause_buttons:
                    if b['rect'].collidepoint(ev.pos):
                        self.sound.play('click', 0.5); b['action']()
            elif self.state in (GameState.GAME_OVER, GameState.VICTORY) and self.jumpscare_t <= 0:
                for b in self.end_buttons:
                    if b['rect'].collidepoint(ev.pos):
                        self.sound.play('click', 0.5); b['action']()
            elif self.state == GameState.PLAYING:
                self._check_touch_controls(ev.pos)

    def _check_touch_controls(self, pos):
        mx, my = pos
        if pygame.Rect(20, H-140, 60, 60).collidepoint(mx, my): self.player.x -= 20
        elif pygame.Rect(100, H-140, 60, 60).collidepoint(mx, my): self.player.x += 20
        elif pygame.Rect(60, H-180, 60, 60).collidepoint(mx, my): self.player.y -= 20
        elif pygame.Rect(60, H-100, 60, 60).collidepoint(mx, my): self.player.y += 20
        elif pygame.Rect(W-80, H-100, 60, 60).collidepoint(mx, my): self._interact()
        elif pygame.Rect(W-160, H-100, 60, 60).collidepoint(mx, my): self._toggle_hide()
        elif pygame.Rect(W-240, H-100, 60, 60).collidepoint(mx, my): 
            if self.player.flash_battery > 0:
                self.player.flash_on = not self.player.flash_on
                self.sound.play('click', 0.3)

    def _toggle_hide(self):
        p = self.player
        if p.hidden:
            p.hidden = False
            self.toast("You step out of the shadows.", 2.0)
        else:
            for h in self.mansion.hide_spots:
                if math.hypot(h.x - p.x, h.y - p.y) < 40:
                    p.hidden = True
                    p.x, p.y = h.x, h.y
                    self.toast("Hiding. Press H to come out.", 2.0)
                    return

    def _interact(self):
        p = self.player
        best = None; best_d = 40
        for d in self.mansion.doors:
            dist = math.hypot(d.x - p.x, d.y - p.y)
            if dist < best_d: best = ('door', d); best_d = dist
        for it in self.mansion.items:
            if it.taken: continue
            dist = math.hypot(it.x - p.x, it.y - p.y)
            if dist < best_d: best = ('item', it); best_d = dist
        
        if best:
            kind, obj = best
            if kind == 'door': obj.interact(self)
            elif kind == 'item': obj.interact(self)

    def _next_level(self):
        self.current_level += 1
        self.save_game()
        if self.current_level >= 50:
            if os.path.exists(SAVE_FILE): os.remove(SAVE_FILE)
            self.fade_to(self._win)
        else:
            self.sound.play('pickup', 0.8)
            self.fade_to(self._load_level)

    def _build_end_buttons(self):
        self.end_buttons = []
        if self.state == GameState.GAME_OVER:
            actions = [("RETRY LEVEL", lambda: self.fade_to(self._restart_level)), ("MAIN MENU", lambda: self.fade_to(lambda: (setattr(self, 'state', GameState.MENU), self._build_menu())))]
        else:
            actions = [("PLAY AGAIN", lambda: self.fade_to(self.new_game)), ("MAIN MENU", lambda: self.fade_to(lambda: (setattr(self, 'state', GameState.MENU), self._build_menu())))]
        cx, cy = W//2, H//2
        for i, (label, action) in enumerate(actions):
            r = pygame.Rect(0, 0, 300, 60); r.center = (cx, cy + 80 + i * 75)
            self.end_buttons.append({'rect': r, 'label': label, 'action': action, 'hover': 0})

    def _win(self):
        self.state = GameState.VICTORY
        self.end_t = 0
        self.sound.stop_all()
        self.sound.play('pickup', 0.8)
        self._build_end_buttons()

    def _lose(self):
        self.state = GameState.GAME_OVER
        self.end_t = 0
        self.sound.stop_all()
        self.sound.play('jumpscare', 0.9)
        self.camera.shake(20, 1.0)
        self.jumpscare_t = 1.5
        self._build_end_buttons()

    def update(self, dt, keys):
        self.menu_t += dt
        self._update_fade(dt)
        if self.jumpscare_t > 0: self.jumpscare_t -= dt
        
        if self.state == GameState.PLAYING:
            self.player.update(dt, keys, self)
            self.ghost.update(dt, self.player, self.mansion, self)
            if not self.player.alive: self.fade_to(self._lose)
            
            self.door_event_t -= dt
            if self.door_event_t <= 0:
                self.door_event_t = random.uniform(15, 30)
                if self.mansion.doors:
                    d = random.choice(self.mansion.doors)
                    if not d.is_exit and d.open:
                        d.open = False
                        self.sound.play('creak', 0.8)
                        self.toast("A door slammed shut somewhere...", 2.0)
            
            if self.player.fear > 70:
                self.hallucination_t += dt
                if self.hallucination_t > 5:
                    self.hallucination_t = 0
                    self.particles.emit(self.player.x + random.uniform(-100,100), self.player.y + random.uniform(-100,100), count=5, speed=10, life=1.0, size=20, color=(200,210,230), spread=2*math.pi)
                    self.sound.play('whisper', 0.5)
            
            self.thunder_t -= dt
            if self.thunder_t <= 0:
                self.thunder_t = random.uniform(15, 35)
                self.sound.play('thunder', 0.5); self.flicker_global = 1.0
            self.flicker_global = max(0, self.flicker_global - dt*2)
            
            for l in self.mansion.lamps:
                l['flicker_t'] += dt
                if random.random() < dt * 1.5: l['intensity'] = random.uniform(0.4, 1.0)
                else: l['intensity'] = lerp(l['intensity'], 1.0, dt * 4)
                
            self.camera.follow(self.player.x, self.player.y, dt, 4.5)
            self.camera.update(dt, self.player.fear)
            if self.toast_t > 0: self.toast_t -= dt
            self.particles.update(dt)
            if random.random() < dt * 2:
                self.particles.emit_fog(self.camera.x + random.uniform(0, W), self.camera.y + random.uniform(0, H))
            
            self.dust_t -= dt
            if self.dust_t <= 0:
                self.dust_t = 0.02
                self.particles.emit_dust(self.player.x + random.uniform(-150, 150), self.player.y + random.uniform(-150, 150))
                
        elif self.state in (GameState.GAME_OVER, GameState.VICTORY):
            self.end_t += dt; self.camera.update(dt); self.particles.update(dt)
        elif self.state == GameState.MENU:
            self.particles.update(dt)
            if random.random() < dt * 1.5: self.particles.emit_fog(random.uniform(0, W), random.uniform(0, H))
            self.menu_flicker_t -= dt
            if self.menu_flicker_t <= 0: self.menu_flicker_t = random.uniform(0.1, 0.5)
            self.menu_shadow_t -= dt
            if self.menu_shadow_t <= 0:
                self.menu_shadow_t = random.uniform(5, 12)
                self.menu_flicker_t = 0.05

    def _build_menu(self):
        self.buttons = []
        cx, cy = W//2, H//2
        has_save = os.path.exists(SAVE_FILE)
        if has_save:
            actions = [("CONTINUE", lambda: self.fade_to(self.start_game)), ("NEW GAME", lambda: self.fade_to(self.new_game)), ("QUIT", lambda: (pygame.quit(), sys.exit()))]
        else:
            actions = [("PLAY", lambda: self.fade_to(self.start_game)), ("QUIT", lambda: (pygame.quit(), sys.exit()))]
        for i, (label, action) in enumerate(actions):
            r = pygame.Rect(0, 0, 300, 60); r.center = (cx, cy + 40 + i * 75)
            self.buttons.append({'rect': r, 'label': label, 'action': action, 'hover': 0})
        self.pause_buttons = []
        for i, (label, action) in enumerate([("RESUME", lambda: setattr(self, 'state', GameState.PLAYING)), ("QUIT TO MENU", lambda: self.fade_to(lambda: (setattr(self, 'state', GameState.MENU), self._build_menu())))]):
            r = pygame.Rect(0, 0, 300, 60); r.center = (cx, cy + 30 + i * 75)
            self.pause_buttons.append({'rect': r, 'label': label, 'action': action, 'hover': 0})

    def _hover_update(self, btns):
        mp = pygame.mouse.get_pos()
        for b in btns:
            b['hover'] = lerp(b['hover'], 1.0 if b['rect'].collidepoint(mp) else 0.0, 0.18)

    def _draw_button(self, b):
        r = b['rect'].copy().inflate(int(10*b['hover']), int(5*b['hover']))
        bg = pygame.Surface(r.size, pygame.SRCALPHA)
        # Black background, White border
        pygame.draw.rect(bg, (0, 0, 0, 220), bg.get_rect(), border_radius=8)
        border_color = (255, 255, 255) if b['hover'] < 0.5 else (200, 30, 40)
        pygame.draw.rect(bg, border_color, bg.get_rect(), 3, border_radius=8)
        self.screen.blit(bg, r.topleft)
        txt_color = (255, 255, 255) if b['hover'] < 0.5 else (200, 30, 40)
        txt = Assets_singleton.fonts['h2'].render(b['label'], True, txt_color)
        self.screen.blit(txt, (r.centerx - txt.get_width()//2, r.centery - txt.get_height()//2))

    def draw(self):
        if self.state == GameState.MENU:
            self._draw_menu()
        else:
            self._draw_game()
            if self.state == GameState.STORY: self._draw_story()
            elif self.state == GameState.JOURNAL: self._draw_journal()
            elif self.state == GameState.PAUSED: self._draw_pause()
            elif self.state == GameState.GAME_OVER: self._draw_gameover()
            elif self.state == GameState.VICTORY: self._draw_victory()
        if self.fade_alpha > 0:
            s = pygame.Surface((W, H)); s.fill((0, 0, 0)); s.set_alpha(int(self.fade_alpha))
            self.screen.blit(s, (0, 0))
            
        if self.jumpscare_t > 0:
            self.screen.blit(Assets_singleton.sprites['jumpscare'], (0, 0))

    def _draw_menu(self):
        t = self.menu_t
        flicker = 1.0
        if self.menu_flicker_t < 0.1: flicker = random.uniform(0.2, 0.8)
        for y in range(0, H, 4):
            c = lerp(0.05, 0.15, y/H) * flicker
            pygame.draw.rect(self.screen, (int(20*c), int(15*c), int(30*c)), (0, y, W, 4))
        cx, cy = W//2, 50
        pygame.draw.line(self.screen, (40, 30, 30), (cx, 0), (cx + math.sin(t)*10, cy), 4)
        for i in range(5):
            lx = cx - 40 + i*20 + math.sin(t)*5
            pygame.draw.circle(self.screen, (255, 200, 100), (int(lx), cy), 6)
            pygame.draw.circle(self.screen, (255, 240, 180), (int(lx), cy), 3)
        if self.menu_shadow_t < 1.0:
            alpha = int(255 * (1 - self.menu_shadow_t))
            shadow = pygame.Surface((100, 200), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow, (0,0,0,alpha), (0, 0, 100, 200))
            self.screen.blit(shadow, (W//2 - 50, H//2 - 100))
        self.particles.draw(self.screen, Camera())
        title = Assets_singleton.fonts['title'].render("THE LAST ROOM", True, (200, 30, 40))
        sh = Assets_singleton.fonts['title'].render("THE LAST ROOM", True, (0,0,0))
        self.screen.blit(sh, (W//2 - title.get_width()//2 + 3, 120 + 3))
        self.screen.blit(title, (W//2 - title.get_width()//2, 120))
        sub_alpha = int(180 + 60 * math.sin(t * 2))
        sub = Assets_singleton.fonts['h2'].render("— Some doors should never be opened —", True, (180, 160, 140))
        sub.set_alpha(sub_alpha)
        self.screen.blit(sub, (W//2 - sub.get_width()//2, 200))
        self._hover_update(self.buttons)
        for b in self.buttons: self._draw_button(b)

    def _draw_game(self):
        cam = self.camera
        self.screen.blit(self.mansion.floor_surf, (-cam.x + cam.ox, -cam.y + cam.oy))
        for d in self.mansion.doors:
            sx = int(d.x - cam.x + cam.ox); sy = int(d.y - cam.y + cam.oy)
            if -TILE < sx < W+TILE and -TILE < sy < H+TILE:
                tex = Assets_singleton.textures['door_open'] if d.open else Assets_singleton.textures['door']
                if d.is_exit: tex = Assets_singleton.sprites['exit']
                self.screen.blit(tex, (sx - tex.get_width()//2, sy - tex.get_height()//2))
        for it in self.mansion.items:
            if it.taken: continue
            it.bob += 1/60
            sx = int(it.x - cam.x + cam.ox); sy = int(it.y - cam.y + cam.oy + math.sin(it.bob)*2)
            if -20 < sx < W+20:
                spr = Assets_singleton.sprites.get(it.kind, Assets_singleton.sprites['clue'])
                self.screen.blit(spr, (sx - spr.get_width()//2, sy - spr.get_height()//2))
        self.particles.draw(self.screen, cam)
        self.ghost.draw(self.screen, cam, Assets_singleton)
        self.player.draw(self.screen, cam, Assets_singleton)
        for l in self.mansion.lamps:
            sx = int(l['x'] - cam.x + cam.ox); sy = int(l['y'] - cam.y + cam.oy)
            if -TILE < sx < W+TILE: self.screen.blit(Assets_singleton.sprites['lamp'], (sx - TILE//2, sy - TILE//2))
        self._draw_lighting()
        self._draw_hud()
        self._draw_objective_marker()
        if self.toast_t > 0: self._draw_toast()
        self._draw_fear_overlay()
        self.screen.blit(Assets_singleton.vignette, (0, 0))
        self._draw_touch_ui()

    def _draw_touch_ui(self):
        pygame.draw.rect(self.screen, (255,255,255,50), (20, H-140, 60, 60), border_radius=8)
        pygame.draw.rect(self.screen, (255,255,255,50), (100, H-140, 60, 60), border_radius=8)
        pygame.draw.rect(self.screen, (255,255,255,50), (60, H-180, 60, 60), border_radius=8)
        pygame.draw.rect(self.screen, (255,255,255,50), (60, H-100, 60, 60), border_radius=8)
        pygame.draw.rect(self.screen, (255,255,255,50), (W-80, H-100, 60, 60), border_radius=8)
        txt = Assets_singleton.fonts['hud'].render("E", True, C_TEXT)
        self.screen.blit(txt, (W-60, H-85))
        pygame.draw.rect(self.screen, (255,255,255,50), (W-160, H-100, 60, 60), border_radius=8)
        txt = Assets_singleton.fonts['hud'].render("H", True, C_TEXT)
        self.screen.blit(txt, (W-140, H-85))
        pygame.draw.rect(self.screen, (255,255,255,50), (W-240, H-100, 60, 60), border_radius=8)
        txt = Assets_singleton.fonts['hud'].render("F", True, C_TEXT)
        self.screen.blit(txt, (W-220, H-85))

    def _draw_objective_marker(self):
        p = self.player
        if not p.has_clue:
            target = next((it for it in self.mansion.items if not it.taken), None)
            color = (200, 180, 100)
        else:
            target = None
            for d in self.mansion.doors:
                if d.is_exit: target = d; break
            color = (100, 200, 120)
        if target:
            dx = target.x - p.x; dy = target.y - p.y
            dist = math.hypot(dx, dy)
            if dist > 150:
                angle = math.atan2(dy, dx)
                sx = int(p.x - self.camera.x + self.camera.ox + math.cos(angle) * 40)
                sy = int(p.y - self.camera.y + self.camera.oy + math.sin(angle) * 40)
                pts = [(sx + math.cos(angle)*15, sy + math.sin(angle)*15), (sx + math.cos(angle + 2.5)*10, sy + math.sin(angle + 2.5)*10), (sx + math.cos(angle - 2.5)*10, sy + math.sin(angle - 2.5)*10)]
                pygame.draw.polygon(self.screen, color, pts)

    def _draw_lighting(self):
        dark = pygame.Surface((W, H), pygame.SRCALPHA)
        dark.fill((0, 0, 0, 150))
        p = self.player
        psx = int(p.x - self.camera.x + self.camera.ox); psy = int(p.y - self.camera.y + self.camera.oy)
        amb_r = 90
        for r in range(amb_r, 0, -3):
            a = int(150 * (1 - r/amb_r)**1.5)
            pygame.draw.circle(dark, (0, 0, 0, max(0, 150 - a)), (psx, psy), r)
        if p.flash_on and p.flash_battery > 0:
            flicker = 1.0
            if self.ghost.dist_to_player < 200 and self.ghost.state == 'CHASE':
                flicker = random.uniform(0.3, 1.0)
            self._blit_flashlight(dark, psx, psy, p.flash_angle, p.flash_range * flicker)
        for l in self.mansion.lamps:
            sx = int(l['x'] - self.camera.x + self.camera.ox); sy = int(l['y'] - self.camera.y + self.camera.oy)
            if -200 < sx < W+200 and -200 < sy < H+200:
                r = int(l['radius'] * l['intensity'])
                if r > 0:
                    for rr in range(r, 0, -6):
                        a = int(150 * (1 - rr/r) * l['intensity'])
                        pygame.draw.circle(dark, (0, 0, 0, max(0, 150 - a)), (sx, sy), rr)
        self.screen.blit(dark, (0, 0))

    def _blit_flashlight(self, dark, sx, sy, angle, rng):
        cone = pygame.Surface((W, H), pygame.SRCALPHA)
        pts = [(sx, sy)]; steps = 24; spread = math.pi / 3.5
        for i in range(steps + 1):
            a = angle - spread + (2*spread) * i / steps
            pts.append((sx + math.cos(a)*rng, sy + math.sin(a)*rng))
        pygame.draw.polygon(cone, (0, 0, 0, 255), pts)
        for k in range(6, 0, -1):
            r = int(rng * k/6); pts2 = [(sx, sy)]
            for i in range(steps + 1):
                a = angle - spread + (2*spread) * i / steps
                pts2.append((sx + math.cos(a)*r, sy + math.sin(a)*r))
            pygame.draw.polygon(cone, (0, 0, 0, 40), pts2)
        dark.blit(cone, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)

    def _draw_hud(self):
        p = self.player
        x, y = 20, 20
        pygame.draw.rect(self.screen, (30, 15, 18), (x-2, y-2, 204, 24), border_radius=4)
        pygame.draw.rect(self.screen, (60, 20, 25), (x, y, 200, 20), border_radius=3)
        pygame.draw.rect(self.screen, C_HP, (x, y, int(200 * p.hp/100), 20), border_radius=3)
        pygame.draw.rect(self.screen, (90, 30, 35), (x, y, 200, 20), 2, border_radius=3)
        self.screen.blit(Assets_singleton.fonts['hud'].render(f"HP {int(p.hp)}", True, C_TEXT), (x + 6, y + 2))
        
        y2 = y + 28
        pygame.draw.rect(self.screen, (30, 15, 25), (x-2, y2-2, 204, 24), border_radius=4)
        pygame.draw.rect(self.screen, (50, 20, 35), (x, y2, 200, 20), border_radius=3)
        pygame.draw.rect(self.screen, C_FEAR if p.fear < 80 else (255, 80, 80), (x, y2, int(200 * p.fear/100), 20), border_radius=3)
        pygame.draw.rect(self.screen, (90, 30, 50), (x, y2, 200, 20), 2, border_radius=3)
        self.screen.blit(Assets_singleton.fonts['hud'].render(f"FEAR {int(p.fear)}", True, C_TEXT), (x + 6, y2 + 2))
        
        y3 = y2 + 28
        pygame.draw.rect(self.screen, (30, 25, 15), (x-2, y3-2, 204, 14), border_radius=2)
        pygame.draw.rect(self.screen, (50, 40, 20), (x, y3, 200, 10), border_radius=2)
        pygame.draw.rect(self.screen, (255, 200, 0) if p.flash_on else (100, 100, 100), (x, y3, int(200 * p.flash_battery/100), 10), border_radius=2)
        self.screen.blit(Assets_singleton.fonts['small'].render(f"FLASHLIGHT {int(p.flash_battery)}%", True, C_DIM), (x, y3 + 12))
        
        obj_txt = "OBJECTIVE: Find the Clue" if not p.has_clue else "OBJECTIVE: Reach the Exit"
        obj_col = (200, 180, 100) if not p.has_clue else (100, 200, 120)
        t = Assets_singleton.fonts['hud'].render(obj_txt, True, obj_col)
        self.screen.blit(t, (W//2 - t.get_width()//2, 20))
        
        if self.ghost.state == 'CHASE' and self.ghost.dist_to_player < 300:
            warn = Assets_singleton.fonts['h2'].render("RUN", True, (255, 60, 70))
            warn.set_alpha(int(180 + 60*math.sin(self.menu_t*12)))
            self.screen.blit(warn, (W//2 - warn.get_width()//2, 80))

    def _draw_toast(self):
        t = Assets_singleton.fonts['body'].render(self.toast_msg, True, C_TEXT)
        a = int(255 * min(1, self.toast_t))
        t.set_alpha(a)
        r = t.get_rect(center=(W//2, 60))
        bg = pygame.Surface((r.w+24, r.h+10), pygame.SRCALPHA)
        bg.fill((0, 0, 0, min(180, a)))
        self.screen.blit(bg, (r.x-12, r.y-5))
        self.screen.blit(t, r)

    def _draw_fear_overlay(self):
        f = self.player.fear
        if f < 30: return
        a = int(80 * (f - 30)/70)
        if self.ghost.state == 'CHASE': a = min(180, a + 60)
        pulse = math.sin(self.menu_t * (4 + f/15))
        a = clamp(int(a + 20 * pulse), 0, 200)
        s = pygame.Surface((W, H), pygame.SRCALPHA)
        s.fill((120, 10, 20, a))
        self.screen.blit(s, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        if f > 70:
            shake = math.sin(self.menu_t * 20) * 3
            layer = self.screen.copy()
            layer.set_alpha(int(80 * (f-70)/30))
            self.screen.blit(layer, (shake, 0))

    def _draw_story(self):
        s = pygame.Surface((W, H), pygame.SRCALPHA)
        s.fill((0, 0, 0, 210))
        self.screen.blit(s, (0, 0))
        
        # Draw Paper Texture
        paper = Assets_singleton.sprites['paper']
        self.screen.blit(paper, (W//2 - 300, H//2 - 200))
        
        title = Assets_singleton.fonts['h1'].render("CLUE FOUND", True, (80, 50, 20))
        self.screen.blit(title, (W//2 - title.get_width()//2, H//2 - 160))
        
        words = self.player.story_text.split()
        lines = []; line = ""
        for w in words:
            test = (line + " " + w).strip()
            if Assets_singleton.fonts['body'].size(test)[0] > 500:
                lines.append(line); line = w
            else: line = test
        if line: lines.append(line)
        
        y = H//2 - 80
        for line in lines:
            t = Assets_singleton.fonts['body'].render(line, True, (40, 20, 10))
            self.screen.blit(t, (W//2 - t.get_width()//2, y)); y += 24
            
        h = Assets_singleton.fonts['small'].render("Press E to continue", True, (100, 80, 50))
        self.screen.blit(h, (W//2 - h.get_width()//2, H//2 + 150))

    def _draw_journal(self):
        s = pygame.Surface((W, H), pygame.SRCALPHA)
        s.fill((0, 0, 0, 210))
        self.screen.blit(s, (0, 0))
        title = Assets_singleton.fonts['h1'].render("JOURNAL", True, (200, 180, 140))
        self.screen.blit(title, (W//2 - title.get_width()//2, 40))
        y = 100
        for i, note in enumerate(self.player.notes):
            txt = Assets_singleton.fonts['body'].render(f"Clue {i+1}: {note}", True, C_TEXT)
            self.screen.blit(txt, (50, y)); y += 30
        h = Assets_singleton.fonts['small'].render("Press TAB to close", True, C_DIM)
        self.screen.blit(h, (W//2 - h.get_width()//2, H - 40))

    def _draw_pause(self):
        s = pygame.Surface((W, H), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        self.screen.blit(s, (0, 0))
        title = Assets_singleton.fonts['h1'].render("PAUSED", True, C_TEXT)
        self.screen.blit(title, (W//2 - title.get_width()//2, H//2 - 140))
        self._hover_update(self.pause_buttons)
        for b in self.pause_buttons: self._draw_button(b)

    def _draw_gameover(self):
        a = int(min(220, self.end_t * 300))
        s = pygame.Surface((W, H)); s.fill((0, 0, 0)); s.set_alpha(a)
        self.screen.blit(s, (0, 0))
        title_y = lerp(-100, H//2 - 120, ease_out(min(1, self.end_t/0.6)))
        title = Assets_singleton.fonts['title'].render("YOU DIED", True, (200, 30, 35))
        self.screen.blit(title, (W//2 - title.get_width()//2, title_y))
        # Only show buttons if jumpscare is over
        if self.end_t > 1.4 and self.jumpscare_t <= 0:
            self._hover_update(self.end_buttons)
            for b in self.end_buttons: self._draw_button(b)

    def _draw_victory(self):
        a = int(min(200, self.end_t * 250))
        s = pygame.Surface((W, H)); s.fill((10, 8, 4)); s.set_alpha(a)
        self.screen.blit(s, (0, 0))
        title_y = lerp(-100, H//2 - 120, ease_out(min(1, self.end_t/0.7)))
        title = Assets_singleton.fonts['title'].render("YOU ESCAPED", True, (220, 200, 140))
        self.screen.blit(title, (W//2 - title.get_width()//2, title_y))
        if self.end_t > 1.5:
            self._hover_update(self.end_buttons)
            for b in self.end_buttons: self._draw_button(b)

# ============================================================
# MAIN
# ============================================================
def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H), pygame.SCALED, vsync=1)
    pygame.display.set_caption("THE LAST ROOM")
    pygame.mouse.set_visible(True)
    global Assets_singleton
    Assets_singleton = Assets()
    clock = pygame.time.Clock()
    game = GameManager(screen)
    running = True
    while running:
        dt = min(clock.tick(FPS) / 1000.0, DT_CAP)
        keys = pygame.key.get_pressed()
        for ev in pygame.event.get():
            game.handle_event(ev)
        game.update(dt, keys)
        game.draw()
        pygame.display.flip()
    pygame.quit()

if __name__ == "__main__":
    main()