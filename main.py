import os
import math
import random
import json
import time
import cv2
import numpy as np
import pygame
import cvzone
from cvzone.HandTrackingModule import HandDetector

# -------------------------
# Configuration & Utilities
# -------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, "Game Images")
SOUNDS_DIR = os.path.join(BASE_DIR, "Game Music")
HIGHSCORE_FILE = os.path.join(BASE_DIR, "highscore.json")

def find_camera_index(max_idx=3):
    for i in range(max_idx + 1):
        cap = cv2.VideoCapture(i)
        if cap is None or not cap.isOpened():
            if cap:
                cap.release()
            continue
        cap.release()
        return i
    return 0

def safe_load_image(path, fallback_size=(50, 50)):
    """Return image as BGRA (with alpha). If missing, return colored placeholder BGRA."""
    if not os.path.exists(path):
        w, h = fallback_size
        placeholder = np.zeros((h, w, 4), dtype=np.uint8)
        # create visible placeholder (light gray with full alpha)
        placeholder[..., :3] = 200
        placeholder[..., 3] = 255
        print(f"[WARNING] Image not found: {path} -> using placeholder")
        return placeholder
    img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if img is None:
        w, h = fallback_size
        placeholder = np.zeros((h, w, 4), dtype=np.uint8)
        placeholder[..., :3] = 200
        placeholder[..., 3] = 255
        print(f"[WARNING] Failed to read image: {path} -> using placeholder")
        return placeholder
    # If image has no alpha (3 channels), convert to BGRA
    if img.ndim == 3 and img.shape[2] == 3:
        b, g, r = cv2.split(img)
        a = np.full(b.shape, 255, dtype=b.dtype)
        img = cv2.merge((b, g, r, a))
    elif img.ndim == 2:
        # grayscale -> convert to BGRA
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGRA)
    return img

def safe_load_sound(path):
    if not os.path.exists(path):
        print(f"[WARNING] Sound not found: {path}")
        return None
    try:
        return pygame.mixer.Sound(path)
    except Exception as e:
        print(f"[WARNING] Failed to load sound {path}: {e}")
        return None

def load_highscore():
    try:
        with open(HIGHSCORE_FILE, "r") as f:
            return json.load(f).get("highScore", 0)
    except Exception:
        return 0

def save_highscore(score):
    try:
        with open(HIGHSCORE_FILE, "w") as f:
            json.dump({"highScore": score}, f)
    except Exception as e:
        print("[WARNING] Could not save highscore:", e)

# -------------------------
# Initialize pygame, camera
# -------------------------
pygame.init()
try:
    pygame.mixer.init()
except Exception as e:
    print("[WARNING] pygame.mixer init failed:", e)


cap = cv2.VideoCapture(0)       #  0 : default cam ; 1 : secondary cam
cap.set(3, 1280)
cap.set(4, 720)

detector = HandDetector(detectionCon=0.8, maxHands=1)

# -------------------------
# Load assets (safe)
# -------------------------
FOOD_PATH_DEFAULT = os.path.join(IMAGES_DIR, "donut.png")
WALL_PATH_DEFAULT = os.path.join(IMAGES_DIR, "wall.png")
BACKGROUND_MUSIC_PATH = os.path.join(SOUNDS_DIR, "background.wav")

# Sounds
eat_sound = safe_load_sound(os.path.join(SOUNDS_DIR, "eat.wav"))
game_over_sound = safe_load_sound(os.path.join(SOUNDS_DIR, "game_over.wav"))
menu_hover_sound = safe_load_sound(os.path.join(SOUNDS_DIR, "menu_hover.mp3"))
menu_select_sound = safe_load_sound(os.path.join(SOUNDS_DIR, "menu_select.wav"))

# Music
if os.path.exists(BACKGROUND_MUSIC_PATH):
    try:
        pygame.mixer.music.load(BACKGROUND_MUSIC_PATH)
    except Exception as e:
        print("[WARNING] Could not load background music:", e)
else:
    print("[WARNING] Background music file missing.")

# -------------------------
# Menu class
# -------------------------
class Menu:
    def __init__(self):
        self.state = "main"
        self.main_options = ["Play", "Levels", "Settings", "Quit"]
        self.settings_options = ["Background Music: ON", "Game Sound Effects: ON", "Back"]
        self.level_options = [f"Level {i+1}" for i in range(6)]
        self.selected_index = 0
        self.background_music_enabled = True
        self.game_sound_enabled = True
        self.last_hover_index = -1
        self.last_selection_time = 0
        self.selected_level = 1

    def draw(self, img):
        if self.state == "main":
            options = self.main_options
        elif self.state == "settings":
            options = self.settings_options
        else:
            options = self.level_options

        for i, option in enumerate(options):
            color = (0, 255, 0) if i == self.selected_index else (255, 255, 255)
            y_pos = 300 + i * 100 if self.state != "levels" else 200 + i * 80
            scale = 3 if self.state != "levels" else 2
            cvzone.putTextRect(img, option, [500 if self.state != "levels" else 400, y_pos],
                               scale=scale, thickness=3, offset=20,
                               colorR=color, colorT=(0, 0, 0))
        return img

    def update_selection(self, hand_pos, img_w, img_h):
        if not hand_pos:
            return
        y_pos = hand_pos[1]
        if self.state == "levels":
            idx = int((y_pos - 150) // 80)
        else:
            idx = int((y_pos - 250) // 100)
        idx = max(0, min(len(self.level_options) - 1, idx)) if self.state == "levels" else max(0, min(len(self.main_options) - 1, idx))
        # Map to current options length
        if self.state == "main":
            idx = max(0, min(len(self.main_options) - 1, idx))
        elif self.state == "settings":
            idx = max(0, min(len(self.settings_options) - 1, idx))
        else:
            idx = max(0, min(len(self.level_options) - 1, idx))

        if self.selected_index != idx:
            self.selected_index = idx
            if self.state == "main" and self.game_sound_enabled and menu_hover_sound:
                try:
                    menu_hover_channel.play(menu_hover_sound)
                except Exception:
                    pass

    def handle_selection(self):
        if self.state == "main":
            selected = self.main_options[self.selected_index]
            if selected == "Play":
                if self.game_sound_enabled and menu_select_sound:
                    try: menu_select_sound.play()
                    except: pass
                return "start_game"
            elif selected == "Levels":
                self.state = "levels"
                self.selected_index = 0
                if self.game_sound_enabled and menu_select_sound:
                    try: menu_select_sound.play()
                    except: pass
            elif selected == "Settings":
                self.state = "settings"
                self.selected_index = 0
                if self.game_sound_enabled and menu_select_sound:
                    try: menu_select_sound.play()
                    except: pass
            elif selected == "Quit":
                return "quit"

        elif self.state == "settings":
            option = self.settings_options[self.selected_index]
            if option.startswith("Background Music"):
                self.background_music_enabled = not self.background_music_enabled
                self.settings_options[0] = f"Background Music: {'ON' if self.background_music_enabled else 'OFF'}"
                if not self.background_music_enabled:
                    try: pygame.mixer.music.pause()
                    except: pass
                else:
                    try: pygame.mixer.music.unpause()
                    except: pass
                if self.game_sound_enabled and menu_select_sound:
                    try: menu_select_sound.play()
                    except: pass
            elif option.startswith("Game Sound Effects"):
                self.game_sound_enabled = not self.game_sound_enabled
                self.settings_options[1] = f"Game Sound Effects: {'ON' if self.game_sound_enabled else 'OFF'}"
                if self.game_sound_enabled and menu_select_sound:
                    try: menu_select_sound.play()
                    except: pass
            elif option == "Back":
                self.state = "main"
                self.selected_index = 0
                if self.game_sound_enabled and menu_select_sound:
                    try: menu_select_sound.play()
                    except: pass

        elif self.state == "levels":
            # set selected level and return to main
            self.selected_level = self.selected_index + 1
            self.state = "main"
            self.selected_index = 0
            if self.game_sound_enabled and menu_select_sound:
                try: menu_select_sound.play()
                except: pass
            return "start_game"

        return "menu"

# -------------------------
# Snake game class (robust)
# -------------------------
class SnakeGameClass:
    def __init__(self, pathFood, level=1):
        self.level = level
        self.points = []
        self.lengths = []
        self.currentLength = 0
        self.allowedLength = 150
        self.previousHead = (0, 0)
        self.smoothedHead = None

        # Safe load images (BGRA)
        self.imgFood = safe_load_image(pathFood, fallback_size=(40,40))
        self.hFood, self.wFood = self.imgFood.shape[0], self.imgFood.shape[1]

        self.imgWall = safe_load_image(WALL_PATH_DEFAULT, fallback_size=(80,80))
        self.hWall, self.wWall = self.imgWall.shape[0], self.imgWall.shape[1]

        self.permanent_walls = []
        self.generate_permanent_walls()

        self.obstacles = []
        self.obstacleTimers = {}
        self.foodPoint = (0, 0)
        self.randomFoodLocation()

        self.score = 0
        self.highScore = load_highscore()
        self.gameOver = False
        self.gameOverTime = None
        self.speedFactor = 1.0

        self.lastMovementTime = time.time()
        self.startTime = time.time()

    def generate_permanent_walls(self):
        self.permanent_walls = []
        num_walls = min(self.level * 2, 12)
        tries = 0
        while len(self.permanent_walls) < num_walls and tries < num_walls * 20:
            tries += 1
            x = random.randint(200, 1000)
            y = random.randint(200, 600)
            new_rect = (x, y, x + self.wWall, y + self.hWall)
            valid = True
            for wx, wy in self.permanent_walls:
                existing_rect = (wx, wy, wx + self.wWall, wy + self.hWall)
                if self.rectangles_overlap(new_rect, existing_rect):
                    valid = False
                    break
            if valid:
                self.permanent_walls.append((x, y))

    def loadHighScore(self):
        return load_highscore()

    def saveHighScore(self):
        save_highscore(self.highScore)

    def rectangles_overlap(self, rect1, rect2):
        if rect1[2] <= rect2[0] or rect2[2] <= rect1[0]:
            return False
        if rect1[3] <= rect2[1] or rect2[3] <= rect1[1]:
            return False
        return True

    def randomFoodLocation(self):
        tries = 0
        while True:
            tries += 1
            x = random.randint(100, 1000)
            y = random.randint(100, 600)
            food_rect = (x - self.wFood // 2, y - self.hFood // 2, x + self.wFood // 2, y + self.hFood // 2)
            overlap = False
            for ox, oy in self.permanent_walls + self.obstacles:
                wall_rect = (ox, oy, ox + self.wWall, oy + self.hWall)
                if self.rectangles_overlap(food_rect, wall_rect):
                    overlap = True
                    break
            if not overlap:
                self.foodPoint = (x, y)
                return
            if tries > 100:
                # place anyway to avoid infinite loop
                self.foodPoint = (x, y)
                return

    def spawnObstacle(self):
        if len(self.obstacles) >= 3:
            return
        tries = 0
        while True:
            tries += 1
            x = random.randint(200, 1000)
            y = random.randint(200, 600)
            wall_rect = (x, y, x + self.wWall, y + self.hWall)
            food_rect = (self.foodPoint[0] - self.wFood // 2, self.foodPoint[1] - self.hFood // 2,
                         self.foodPoint[0] + self.wFood // 2, self.foodPoint[1] + self.hFood // 2)
            valid = True
            for ox, oy in self.permanent_walls:
                existing_rect = (ox, oy, ox + self.wWall, oy + self.hWall)
                if self.rectangles_overlap(wall_rect, existing_rect):
                    valid = False
                    break
            if valid and not self.rectangles_overlap(wall_rect, food_rect):
                self.obstacles.append((x, y))
                self.obstacleTimers[(x, y)] = time.time() + random.randint(5, 10)
                return
            if tries > 200:
                return

    def removeOldObstacles(self):
        current_time = time.time()
        self.obstacles = [obs for obs in self.obstacles if self.obstacleTimers.get(obs, 0) > current_time]
        self.obstacleTimers = {obs: timer for obs, timer in self.obstacleTimers.items() if timer > current_time}

    def resetGame(self):
        if self.score > self.highScore:
            self.highScore = self.score
            self.saveHighScore()
        # reinitialize most vars but preserve level
        self.points = []
        self.lengths = []
        self.currentLength = 0
        self.allowedLength = 150
        self.previousHead = (0, 0)
        self.score = 0
        self.gameOver = False
        self.speedFactor = 1.0
        self.obstacles = []
        self.obstacleTimers = {}
        self.generate_permanent_walls()
        self.randomFoodLocation()
        self.gameOverTime = None
        self.lastMovementTime = time.time()
        self.startTime = time.time()
        self.smoothedHead = None

    def update(self, imgMain, currentHead):
        currentTime = time.time()
        # smoothing
        if self.smoothedHead is None:
            self.smoothedHead = tuple(currentHead)
        else:
            self.smoothedHead = (int(0.8 * self.smoothedHead[0] + 0.2 * currentHead[0]),
                                 int(0.8 * self.smoothedHead[1] + 0.2 * currentHead[1]))
        cx, cy = self.smoothedHead
        invincible = (currentTime - self.startTime) < 5

        # Game over display & restart logic
        if self.gameOver:
            cvzone.putTextRect(imgMain, "Game Over", [400, 300], scale=5, thickness=6, offset=20,
                               colorR=(0, 0, 255), colorT=(255, 255, 255))
            cvzone.putTextRect(imgMain, f'Your Score: {self.score}', [450, 380], scale=2, thickness=2)
            cvzone.putTextRect(imgMain, f'High Score: {self.highScore}', [450, 420], scale=2, thickness=2)
            if self.gameOverTime is None:
                self.gameOverTime = currentTime
            if currentTime - self.gameOverTime > 3:
                self.resetGame()
            return imgMain

        # track movement inactivity (keep original idea)
        px, py = self.previousHead
        if not invincible and self.previousHead != (0, 0):
            movementDistance = math.hypot(cx - self.previousHead[0], cy - self.previousHead[1])
            if movementDistance >= 10:
                self.lastMovementTime = currentTime
            elif currentTime - self.lastMovementTime > 2:
                if menu.game_sound_enabled and game_over_sound:
                    try: game_over_sound.play()
                    except: pass
                self.gameOver = True
                self.gameOverTime = currentTime
                return imgMain

        # append points & lengths
        self.points.append([cx, cy])
        distance = math.hypot(cx - px, cy - py) * self.speedFactor
        self.lengths.append(distance)
        self.currentLength += distance
        self.previousHead = (cx, cy)

        # trim tail if too long
        if self.currentLength > self.allowedLength and self.lengths:
            for i, length in enumerate(list(self.lengths)):
                self.currentLength -= length
                self.lengths.pop(0)
                self.points.pop(0)
                if self.currentLength < self.allowedLength:
                    break

        # food collision
        rx, ry = self.foodPoint
        if rx - self.wFood // 2 < cx < rx + self.wFood // 2 and ry - self.hFood // 2 < cy < ry + self.hFood // 2:
            self.randomFoodLocation()
            self.allowedLength += 25
            self.score += 1
            self.speedFactor += 0.02
            if menu.game_sound_enabled and eat_sound:
                try: eat_sound.play()
                except: pass
            if random.random() > 0.5:
                self.spawnObstacle()

        self.removeOldObstacles()

        # draw snake body
        if len(self.points) >= 2:
            for i in range(1, len(self.points)):
                try:
                    cv2.line(imgMain, tuple(self.points[i - 1]), tuple(self.points[i]), (0, 0, 255), 20)
                except Exception:
                    pass
        if self.points:
            try:
                cv2.circle(imgMain, tuple(self.points[-1]), 20, (0, 255, 0), cv2.FILLED)
            except Exception:
                pass

        # overlay food/walls safely
        try:
            imgMain = cvzone.overlayPNG(imgMain, self.imgFood, (rx - self.wFood // 2, ry - self.hFood // 2))
        except Exception:
            pass

        cvzone.putTextRect(imgMain, f'Score: {self.score}', [50, 50], scale=2, thickness=2, offset=5)
        cvzone.putTextRect(imgMain, f'High Score: {self.highScore}', [50, 100], scale=2, thickness=2, offset=5)
        cvzone.putTextRect(imgMain, f'Level: {self.level}', [50, 150], scale=2, thickness=2, offset=5)

        # draw permanent walls
        for ox, oy in self.permanent_walls:
            try:
                imgMain = cvzone.overlayPNG(imgMain, self.imgWall, (ox, oy))
            except Exception:
                pass

        # draw dynamic obstacles
        for ox, oy in self.obstacles:
            try:
                imgMain = cvzone.overlayPNG(imgMain, self.imgWall, (ox, oy))
            except Exception:
                pass

        # collision checks
        if not invincible:
            # snake collision with walls
            for ox, oy in self.permanent_walls:
                if ox < cx < ox + self.wWall and oy < cy < oy + self.hWall:
                    if menu.game_sound_enabled and game_over_sound:
                        try: game_over_sound.play()
                        except: pass
                    self.gameOver = True
                    self.gameOverTime = currentTime
                    return imgMain
            for ox, oy in self.obstacles:
                if ox < cx < ox + self.wWall and oy < cy < oy + self.hWall:
                    if menu.game_sound_enabled and game_over_sound:
                        try: game_over_sound.play()
                        except: pass
                    self.gameOver = True
                    self.gameOverTime = currentTime
                    return imgMain

            # self-collision using polygon test if enough points
            pts = None
            if len(self.points) > 3:
                try:
                    pts_arr = np.array(self.points[:-2], dtype=np.int32).reshape((-1, 1, 2))
                    if pts_arr.size > 0:
                        minDist = cv2.pointPolygonTest(pts_arr, (cx, cy), True)
                        if self.score >= 7 and -1 <= minDist <= 1:
                            if menu.game_sound_enabled and game_over_sound:
                                try: game_over_sound.play()
                                except: pass
                            self.gameOver = True
                            self.gameOverTime = currentTime
                            return imgMain
                except Exception:
                    pass

        return imgMain

# -------------------------
# Game initialization
# -------------------------
menu = Menu()
game_state = "menu"
selection_cooldown = 0.5
last_select_time = 0
fist_cooldown_time = 1.0
last_fist_time = 0
current_game = None

# prepare menu hover channel
menu_hover_channel = pygame.mixer.Channel(1)

# -------------------------
# Main loop
# -------------------------
while True:
    success, img = cap.read()
    if not success:
        print("[ERROR] Camera read failed.")
        break
    img = cv2.flip(img, 1)
    hands, img = detector.findHands(img, flipType=False)
    current_time = time.time()

    if game_state == "menu":
        # pause bg music here; only unpause when game starts
        try:
            pygame.mixer.music.pause()
        except Exception:
            pass

        if hands:
            hand = hands[0]
            lmList = hand['lmList']
            index_tip = lmList[8][0:2]
            thumb_tip = lmList[4][0:2]
            menu.update_selection(index_tip, img.shape[1], img.shape[0])
            distance = math.hypot(index_tip[0] - thumb_tip[0], index_tip[1] - thumb_tip[1])
            if distance < 30 and (current_time - menu.last_selection_time) > selection_cooldown:
                menu.last_selection_time = current_time
                result = menu.handle_selection()
                if result == "start_game":
                    # construct food path depending on selected level (you can tweak)
                    food_path = FOOD_PATH_DEFAULT
                    current_game = SnakeGameClass(food_path, menu.selected_level)
                    game_state = "game"
                    # play background music loop if enabled
                    if menu.background_music_enabled:
                        try:
                            pygame.mixer.music.play(-1)
                        except Exception:
                            pass
                elif result == "quit":
                    break

        img = menu.draw(img)

    elif game_state == "game":
        # stop menu hover sounds
        try:
            menu_hover_channel.stop()
        except Exception:
            pass

        if hands:
            hand = hands[0]
            lmList = hand['lmList']
            fingers = detector.fingersUp(hand)

            # fist gesture: back to menu
            if sum(fingers) == 0 and (current_time - last_fist_time) > fist_cooldown_time:
                game_state = "menu"
                current_game = None
                try: pygame.mixer.music.pause()
                except: pass
                last_fist_time = current_time
                if menu.game_sound_enabled and menu_select_sound:
                    try: menu_select_sound.play()
                    except: pass
                continue

            pointIndex = lmList[8][0:2]
            if current_game:
                img = current_game.update(img, pointIndex)
        else:
            cvzone.putTextRect(img, "Paused - Show hand to continue", [300, 300], scale=3, thickness=3, offset=20)

    cv2.imshow("HOLOSNAKE", img)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break

# cleanup
try:
    pygame.mixer.music.stop()
except:
    pass
cap.release()
cv2.destroyAllWindows()
