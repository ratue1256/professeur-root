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

# struct win32 un peu chiante pour chopper la pos du caret texte
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

# metrics multi ecran sous windows (76=x, 77=y, 78=w, 79=h)
VIRT_X = ctypes.windll.user32.GetSystemMetrics(76)
VIRT_Y = ctypes.windll.user32.GetSystemMetrics(77)
VIRT_W = ctypes.windll.user32.GetSystemMetrics(78)
VIRT_H = ctypes.windll.user32.GetSystemMetrics(79)

def get_text_caret_pos():
    # 1. essaye de chopper le curseur texte
    try:
        info = GUITHREADINFO(cbSize=ctypes.sizeof(GUITHREADINFO))
        if ctypes.windll.user32.GetGUIThreadInfo(0, ctypes.byref(info)):
            if info.hwndCaret:
                pt = wintypes.POINT(info.rcCaret.left, info.rcCaret.top)
                ctypes.windll.user32.ClientToScreen(info.hwndCaret, ctypes.byref(pt))
                if pt.x > -2000 and pt.y > VIRT_Y:
                    return pt.x, pt.y
                    
            # 2. fenetre avec le focus (discord chrome etc)
            if info.hwndFocus:
                rect = wintypes.RECT()
                ctypes.windll.user32.GetWindowRect(info.hwndFocus, ctypes.byref(rect))
                return (rect.left + rect.right) // 2, (rect.top + rect.bottom) // 2
                
        # 3. fenetre active
        active = ctypes.windll.user32.GetForegroundWindow()
        if active:
            rect = wintypes.RECT()
            ctypes.windll.user32.GetWindowRect(active, ctypes.byref(rect))
            if rect.right > rect.left and rect.bottom > rect.top:
                return (rect.left + rect.right) // 2, (rect.top + rect.bottom) // 2
    except Exception:
        pass

    # 4. si tout foire on prend la souris
    pt = wintypes.POINT()
    ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
    return pt.x, pt.y


class RootPet:
    def __init__(self, tk_window):
        self.win = tk_window
        self.sprite_size = 90
        self.win_w = 340
        self.win_h = 140
        self.floor_y = VIRT_Y + VIRT_H - self.win_h - 60
        
        # spawn root au sol direct
        self.x = VIRT_X + random.randint(200, max(300, VIRT_W - 400))
        self.y = self.floor_y
        self.dir = 1
        self.state = "walk"
        
        self.target_x = self.x
        self.target_y = self.y
        self.caret_x = self.x
        self.caret_y = self.y
        
        self.typo_data = None
        self.flee_x = 0
        self.frame_num = 0
        
        self.frames_r = []
        self.frames_l = []
        self.load_sprites()
        
        # label texte pour le message au dessus de root
        self.txt_label = tk.Label(
            self.win,
            text="",
            fg="#ffffff",
            bg="#000001",
            font=("Segoe UI", 11, "bold")
        )
        self.txt_label.pack(side="top", pady=(0, 2))
        
        self.sprite_label = tk.Label(self.win, bg="#000001", bd=0)
        self.sprite_label.pack(side="top")
        
        # drag and drop a la souris
        self.drag_x = 0
        self.drag_y = 0
        self.sprite_label.bind("<Button-1>", self.start_drag)
        self.sprite_label.bind("<B1-Motion>", self.do_drag)

    def load_sprites(self):
        asset_folder = os.path.join(os.path.dirname(__file__), "asset")
        for i in range(1, 9):
            img_path = os.path.join(asset_folder, f"Root{i}.png")
            if os.path.exists(img_path):
                img = Image.open(img_path).convert("RGBA")
                # crop pour centrer root
                img = img.crop((200, 0, 1800, 2000))
                img = img.resize((self.sprite_size, self.sprite_size), Image.Resampling.LANCZOS)
                
                # fond transparent pour tkinter (#000001)
                bg = Image.new("RGBA", img.size, (0, 0, 1, 255))
                img_r = Image.alpha_composite(bg, img)
                img_l = Image.alpha_composite(bg, img.transpose(Image.FLIP_LEFT_RIGHT))
                
                self.frames_r.append(ImageTk.PhotoImage(img_r))
                self.frames_l.append(ImageTk.PhotoImage(img_l))

    def on_error_detected(self, typo):
        if self.state not in ("walk", "idle"):
            return
            
        lock_input()
        self.typo_data = typo
        cx, cy = get_text_caret_pos()
        
        # se place pile au dessus du texte
        self.caret_x = min(max(VIRT_X + 20, cx - (self.win_w // 2)), VIRT_X + VIRT_W - self.win_w - 20)
        self.caret_y = min(max(VIRT_Y + 40, cy - self.sprite_size - 20), self.floor_y)
        
        self.target_x = self.caret_x
        self.target_y = self.caret_y
        self.dir = 1 if self.target_x > self.x else -1
        self.state = "sprint"

    def update_animation(self):
        speed_walk = 3
        speed_sprint = 32
        
        if self.state == "walk":
            self.x += self.dir * speed_walk
            if self.x >= VIRT_X + VIRT_W - self.win_w - 20:
                self.dir = -1
            elif self.x <= VIRT_X + 20:
                self.dir = 1
                
            # redescend au sol si il est en l air
            if self.y < self.floor_y:
                self.y += min(4, self.floor_y - self.y)
            elif self.y > self.floor_y:
                self.y = self.floor_y
                
            if random.random() < 0.012:
                self.state = "idle"
                self.win.after(1200, self.resume_walk)
                
        elif self.state == "sprint":
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            dist = (dx**2 + dy**2) ** 0.5
            self.dir = 1 if dx >= 0 else -1
            
            if dist > 30:
                self.x += (dx / dist) * speed_sprint
                self.y += (dy / dist) * speed_sprint
            else:
                self.x = self.target_x
                self.y = self.target_y
                
                # efface les lettres tapees avec backspace
                count = len(self.typo_data["original_text"])
                for _ in range(count):
                    sim_kb.press(keyboard.Key.backspace)
                    sim_kb.release(keyboard.Key.backspace)
                    time.sleep(0.01)
                    
                self.txt_label.config(text=f"{self.typo_data['original_text']}", fg="#ffffff")
                self.flee_x = VIRT_X - 200 if self.x < (VIRT_X + VIRT_W / 2) else VIRT_X + VIRT_W + 100
                self.state = "flee"
                
        elif self.state == "flee":
            dx = self.flee_x - self.x
            self.dir = 1 if dx >= 0 else -1
            
            if abs(dx) > 35:
                self.x += self.dir * speed_sprint
            else:
                self.x = self.flee_x
                self.state = "hidden"
                self.win.after(400, self.prep_return)
                
        elif self.state == "return":
            dx = self.caret_x - self.x
            dy = self.caret_y - self.y
            dist = (dx**2 + dy**2) ** 0.5
            self.dir = 1 if dx >= 0 else -1
            
            if dist > 30:
                self.x += (dx / dist) * speed_sprint
                self.y += (dy / dist) * speed_sprint
            else:
                self.x = self.caret_x
                self.y = self.caret_y
                self.state = "drop"
                
                # retape le texte propre
                fixed_text = self.typo_data["corrected_text"] + " "
                sim_kb.type(fixed_text)
                
                self.txt_label.config(text=f"{self.typo_data['corrected_text']}", fg="#ffffff")
                self.win.after(1200, self.finish_cycle)
                
        if self.state not in ("flee", "hidden"):
            self.y = min(max(VIRT_Y + 30, self.y), self.floor_y)
            
        self.win.geometry(f"{self.win_w}x{self.win_h}+{int(self.x)}+{int(self.y)}")
        
        frames = self.frames_r if self.dir == 1 else self.frames_l
        if frames:
            self.frame_num = (self.frame_num + 1) % len(frames)
            self.sprite_label.config(image=frames[self.frame_num])
            
        delay = 35 if self.state in ("sprint", "flee", "return") else 110
        self.win.after(delay, self.update_animation)

    def prep_return(self):
        if self.typo_data:
            self.txt_label.config(text=f"{self.typo_data['corrected_text']}", fg="#ffffff")
            self.state = "return"

    def finish_cycle(self):
        self.txt_label.config(text="")
        self.typo_data = None
        self.state = "walk"
        unlock_input()

    def resume_walk(self):
        if self.state == "idle":
            self.dir = random.choice([1, -1])
            self.state = "walk"

    def start_drag(self, e):
        self.drag_x = e.x
        self.drag_y = e.y
        if self.state == "walk":
            self.state = "idle"

    def do_drag(self, e):
        self.x += (e.x - self.drag_x)
        self.y += (e.y - self.drag_y)
        self.win.geometry(f"{self.win_w}x{self.win_h}+{int(self.x)}+{int(self.y)}")
