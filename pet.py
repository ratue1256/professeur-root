import os
import time
import random
import ctypes
from ctypes import wintypes
import tkinter as tk
from PIL import Image, ImageTk
from pynput import keyboard
from clavier import lock_input, unlock_input

sim_kb = keyboard.Controller()

# struct win32 pour choper la pos du curseur de texte
class GUITHREADINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("hwndActive", wintypes.HWND),
        ("hwndFocus", wintypes.HWND),
        ("hwndCapture", wintypes.HWND),
        ("hwndMenuOwner", wintypes.HWND),
        ("hwndMoveSize", wintypes.HWND),
        ("hwndCaret", wintypes.HWND),
        ("rcCaret", wintypes.RECT)
    ]

# metrics multi-ecran windows (76=x, 77=y, 78=w, 79=h)
SCREEN_X = ctypes.windll.user32.GetSystemMetrics(76)
SCREEN_Y = ctypes.windll.user32.GetSystemMetrics(77)
SCREEN_W = ctypes.windll.user32.GetSystemMetrics(78)
SCREEN_H = ctypes.windll.user32.GetSystemMetrics(79)

def get_target_coords():
    # 1. tente de choper le caret exact
    try:
        g = GUITHREADINFO(cbSize=ctypes.sizeof(GUITHREADINFO))
        if ctypes.windll.user32.GetGUIThreadInfo(0, ctypes.byref(g)):
            if g.hwndCaret:
                pt = wintypes.POINT(g.rcCaret.left, g.rcCaret.top)
                ctypes.windll.user32.ClientToScreen(g.hwndCaret, ctypes.byref(pt))
                if pt.x > -2000 and pt.y > SCREEN_Y:
                    return pt.x, pt.y
                    
            # 2. fenetre avec le focus si app electron / chromium
            if g.hwndFocus:
                r = wintypes.RECT()
                ctypes.windll.user32.GetWindowRect(g.hwndFocus, ctypes.byref(r))
                return (r.left + r.right) // 2, (r.top + r.bottom) // 2
                
        # 3. fenetre foreground classique
        top_hwnd = ctypes.windll.user32.GetForegroundWindow()
        if top_hwnd:
            r = wintypes.RECT()
            ctypes.windll.user32.GetWindowRect(top_hwnd, ctypes.byref(r))
            if r.right > r.left and r.bottom > r.top:
                return (r.left + r.right) // 2, (r.top + r.bottom) // 2
    except Exception:
        pass

    # 4. fallback basique sur la souris
    pt = wintypes.POINT()
    ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
    return pt.x, pt.y


class RootPet:
    def __init__(self, win):
        self.win = win
        self.sprite_dim = 90
        self.w_width = 340
        self.w_height = 140
        self.ground = SCREEN_Y + SCREEN_H - self.w_height - 60
        
        # spawn aleatoire sur la largeur de l'ecran
        self.x = SCREEN_X + random.randint(200, max(300, SCREEN_W - 400))
        self.y = self.ground
        self.dir = 1
        self.state = "walk"
        
        self.target_x = self.x
        self.target_y = self.y
        self.saved_caret_x = self.x
        self.saved_caret_y = self.y
        
        self.cur_typo = None
        self.exit_x = 0
        self.anim_idx = 0
        
        self.frames_r = []
        self.frames_l = []
        self._load_sprites()
        
        # label texte pour le message au dessus de root
        self.lbl_txt = tk.Label(
            self.win,
            text="",
            fg="#ffffff",
            bg="#000001",
            font=("Segoe UI", 11, "bold")
        )
        self.lbl_txt.pack(side="top", pady=(0, 2))
        
        self.lbl_sprite = tk.Label(self.win, bg="#000001", bd=0)
        self.lbl_sprite.pack(side="top")
        
        # deplacement a la souris
        self._drag_x = 0
        self._drag_y = 0
        self.lbl_sprite.bind("<Button-1>", self._start_drag)
        self.lbl_sprite.bind("<B1-Motion>", self._do_drag)

    def _load_sprites(self):
        base_dir = os.path.join(os.path.dirname(__file__), "asset")
        for i in range(1, 9):
            p = os.path.join(base_dir, f"Root{i}.png")
            if os.path.exists(p):
                im = Image.open(p).convert("RGBA")
                # cadrage pour centrer root
                im = im.crop((200, 0, 1800, 2000))
                im = im.resize((self.sprite_dim, self.sprite_dim), Image.Resampling.LANCZOS)
                
                # fond transparent pour le rendu tkinter
                bg = Image.new("RGBA", im.size, (0, 0, 1, 255))
                im_r = Image.alpha_composite(bg, im)
                im_l = Image.alpha_composite(bg, im.transpose(Image.FLIP_LEFT_RIGHT))
                
                self.frames_r.append(ImageTk.PhotoImage(im_r))
                self.frames_l.append(ImageTk.PhotoImage(im_l))

    def on_error_detected(self, typo_info):
        if self.state not in ("walk", "idle"):
            return
            
        lock_input()
        self.cur_typo = typo_info
        cx, cy = get_target_coords()
        
        # positionne root juste au dessus du champ de saisie
        self.saved_caret_x = min(max(SCREEN_X + 20, cx - (self.w_width // 2)), SCREEN_X + SCREEN_W - self.w_width - 20)
        self.saved_caret_y = min(max(SCREEN_Y + 40, cy - self.sprite_dim - 20), self.ground)
        
        self.target_x = self.saved_caret_x
        self.target_y = self.saved_caret_y
        self.dir = 1 if self.target_x > self.x else -1
        self.state = "sprint"

    def update_animation(self):
        v_walk = 3
        v_sprint = 32
        
        if self.state == "walk":
            self.x += self.dir * v_walk
            if self.x >= SCREEN_X + SCREEN_W - self.w_width - 20:
                self.dir = -1
            elif self.x <= SCREEN_X + 20:
                self.dir = 1
                
            # revient au sol si pose en hauteur
            if self.y < self.ground:
                self.y += min(4, self.ground - self.y)
            elif self.y > self.ground:
                self.y = self.ground
                
            if random.random() < 0.012:
                self.state = "idle"
                self.win.after(1200, self._resume_walk)
                
        elif self.state == "sprint":
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            dist = (dx**2 + dy**2) ** 0.5
            self.dir = 1 if dx >= 0 else -1
            
            if dist > 30:
                self.x += (dx / dist) * v_sprint
                self.y += (dy / dist) * v_sprint
            else:
                self.x = self.target_x
                self.y = self.target_y
                
                # efface le texte tape
                n = len(self.cur_typo["original_text"])
                for _ in range(n):
                    sim_kb.press(keyboard.Key.backspace)
                    sim_kb.release(keyboard.Key.backspace)
                    time.sleep(0.01)
                    
                self.lbl_txt.config(text=f"{self.cur_typo['original_text']}", fg="#ffffff")
                self.exit_x = SCREEN_X - 200 if self.x < (SCREEN_X + SCREEN_W / 2) else SCREEN_X + SCREEN_W + 100
                self.state = "flee"
                
        elif self.state == "flee":
            dx = self.exit_x - self.x
            self.dir = 1 if dx >= 0 else -1
            
            if abs(dx) > 35:
                self.x += self.dir * v_sprint
            else:
                self.x = self.exit_x
                self.state = "hidden"
                self.win.after(400, self._prep_return)
                
        elif self.state == "return":
            dx = self.saved_caret_x - self.x
            dy = self.saved_caret_y - self.y
            dist = (dx**2 + dy**2) ** 0.5
            self.dir = 1 if dx >= 0 else -1
            
            if dist > 30:
                self.x += (dx / dist) * v_sprint
                self.y += (dy / dist) * v_sprint
            else:
                self.x = self.saved_caret_x
                self.y = self.saved_caret_y
                self.state = "drop"
                
                # retape la phrase corrigee
                clean = self.cur_typo["corrected_text"] + " "
                sim_kb.type(clean)
                
                self.lbl_txt.config(text=f"{self.cur_typo['corrected_text']}", fg="#ffffff")
                self.win.after(1200, self._finish_cycle)
                
        if self.state not in ("flee", "hidden"):
            self.y = min(max(SCREEN_Y + 30, self.y), self.ground)
            
        self.win.geometry(f"{self.w_width}x{self.w_height}+{int(self.x)}+{int(self.y)}")
        
        frames = self.frames_r if self.dir == 1 else self.frames_l
        if frames:
            self.anim_idx = (self.anim_idx + 1) % len(frames)
            self.lbl_sprite.config(image=frames[self.anim_idx])
            
        dt = 35 if self.state in ("sprint", "flee", "return") else 110
        self.win.after(dt, self.update_animation)

    def _prep_return(self):
        if self.cur_typo:
            self.lbl_txt.config(text=f"{self.cur_typo['corrected_text']}", fg="#ffffff")
            self.state = "return"

    def _finish_cycle(self):
        self.lbl_txt.config(text="")
        self.cur_typo = None
        self.state = "walk"
        unlock_input()

    def _resume_walk(self):
        if self.state == "idle":
            self.dir = random.choice([1, -1])
            self.state = "walk"

    def _start_drag(self, e):
        self._drag_x = e.x
        self._drag_y = e.y
        if self.state == "walk":
            self.state = "idle"

    def _do_drag(self, e):
        self.x += (e.x - self._drag_x)
        self.y += (e.y - self._drag_y)
        self.win.geometry(f"{self.w_width}x{self.w_height}+{int(self.x)}+{int(self.y)}")
