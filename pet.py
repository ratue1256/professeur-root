import os
import time
import random
import ctypes
from ctypes import wintypes
import tkinter as tk
from PIL import Image, ImageTk
from pynput import keyboard
from clavier import lock_input, unlock_input

# Controleur pour la frappe simulee
simulated_kb = keyboard.Controller()

# Structure Win32 pour recuperer la position du curseur texte (Caret)
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

# Recuperation des dimensions du bureau virtuel (support multi-ecrans)
# 76 = SM_XVIRTUALSCREEN, 77 = SM_YVIRTUALSCREEN, 78 = SM_CXVIRTUALSCREEN, 79 = SM_CYVIRTUALSCREEN
VIRT_SCREEN_X = ctypes.windll.user32.GetSystemMetrics(76)
VIRT_SCREEN_Y = ctypes.windll.user32.GetSystemMetrics(77)
VIRT_SCREEN_W = ctypes.windll.user32.GetSystemMetrics(78)
VIRT_SCREEN_H = ctypes.windll.user32.GetSystemMetrics(79)

def fetch_active_input_coordinates():
    # 1. Tentative d'obtention de la position exacte du caret dans l'application active
    try:
        thread_info = GUITHREADINFO(cbSize=ctypes.sizeof(GUITHREADINFO))
        if ctypes.windll.user32.GetGUIThreadInfo(0, ctypes.byref(thread_info)):
            if thread_info.hwndCaret:
                caret_pt = wintypes.POINT(thread_info.rcCaret.left, thread_info.rcCaret.top)
                ctypes.windll.user32.ClientToScreen(thread_info.hwndCaret, ctypes.byref(caret_pt))
                if caret_pt.x > -2000 and caret_pt.y > VIRT_SCREEN_Y:
                    return caret_pt.x, caret_pt.y
                    
            # 2. Si le caret n'est pas expose (ex: Electron / Chrome), on utilise la fenetre avec le focus
            if thread_info.hwndFocus:
                focus_rect = wintypes.RECT()
                ctypes.windll.user32.GetWindowRect(thread_info.hwndFocus, ctypes.byref(focus_rect))
                center_x = (focus_rect.left + focus_rect.right) // 2
                center_y = (focus_rect.top + focus_rect.bottom) // 2
                return center_x, center_y
                
        # 3. Fallback sur la fenetre au premier plan
        active_hwnd = ctypes.windll.user32.GetForegroundWindow()
        if active_hwnd:
            win_rect = wintypes.RECT()
            ctypes.windll.user32.GetWindowRect(active_hwnd, ctypes.byref(win_rect))
            if win_rect.right > win_rect.left and win_rect.bottom > win_rect.top:
                return (win_rect.left + win_rect.right) // 2, (win_rect.top + win_rect.bottom) // 2
    except (OSError, ValueError):
        pass

    # 4. Dernier recours : position de la souris
    mouse_pt = wintypes.POINT()
    ctypes.windll.user32.GetCursorPos(ctypes.byref(mouse_pt))
    return mouse_pt.x, mouse_pt.y


class RootPet:
    def __init__(self, tk_root):
        self.root_window = tk_root
        self.sprite_size = 90
        self.window_w = 340
        self.window_h = 140
        self.ground_y = VIRT_SCREEN_Y + VIRT_SCREEN_H - self.window_h - 60
        
        # Position initiale au sol
        self.pos_x = VIRT_SCREEN_X + random.randint(200, max(300, VIRT_SCREEN_W - 400))
        self.pos_y = self.ground_y
        self.walk_direction = 1  # 1 = droite, -1 = gauche
        self.current_state = "walking"
        
        # Cibles de deplacement
        self.target_x = self.pos_x
        self.target_y = self.pos_y
        self.memo_caret_x = self.pos_x
        self.memo_caret_y = self.pos_y
        
        self.active_typo_data = None
        self.offscreen_exit_x = 0
        self.frame_index = 0
        
        self.right_frames = []
        self.left_frames = []
        self.load_all_sprites()
        
        # Affichage du texte blanc flottant (phrase originale puis corrigee)
        self.text_label = tk.Label(
            self.root_window,
            text="",
            fg="#ffffff",
            bg="#000001",
            font=("Segoe UI", 11, "bold")
        )
        self.text_label.pack(side="top", pady=(0, 2))
        
        # Sprite de Root
        self.sprite_label = tk.Label(self.root_window, bg="#000001", bd=0)
        self.sprite_label.pack(side="top")
        
        # Drag and drop manuel a la souris
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.sprite_label.bind("<Button-1>", self.on_drag_start)
        self.sprite_label.bind("<B1-Motion>", self.on_drag_motion)

    def load_all_sprites(self):
        assets_dir = os.path.join(os.path.dirname(__file__), "asset")
        for i in range(1, 9):
            sprite_path = os.path.join(assets_dir, f"Root{i}.png")
            if os.path.exists(sprite_path):
                img = Image.open(sprite_path).convert("RGBA")
                # Decoupage du cadrage pour centrer le personnage
                crop_box = (200, 0, 1800, 2000)
                img = img.crop(crop_box)
                img = img.resize((self.sprite_size, self.sprite_size), Image.Resampling.LANCZOS)
                
                # Fond de transparence
                bg_plate = Image.new("RGBA", img.size, (0, 0, 1, 255))
                img_right = Image.alpha_composite(bg_plate, img)
                img_left = Image.alpha_composite(bg_plate, img.transpose(Image.FLIP_LEFT_RIGHT))
                
                self.right_frames.append(ImageTk.PhotoImage(img_right))
                self.left_frames.append(ImageTk.PhotoImage(img_left))

    def on_error_detected(self, error_payload):
        # Ne declenche que si Root est en train de se balader
        if self.current_state not in ("walking", "idle_pause"):
            return
            
        lock_input()
        self.active_typo_data = error_payload
        caret_x, caret_y = fetch_active_input_coordinates()
        
        # Calcul de la position cible au dessus du texte
        self.memo_caret_x = min(max(VIRT_SCREEN_X + 20, caret_x - (self.window_w // 2)), VIRT_SCREEN_X + VIRT_SCREEN_W - self.window_w - 20)
        self.memo_caret_y = min(max(VIRT_SCREEN_Y + 40, caret_y - self.sprite_size - 20), self.ground_y)
        
        self.target_x = self.memo_caret_x
        self.target_y = self.memo_caret_y
        self.walk_direction = 1 if self.target_x > self.pos_x else -1
        self.current_state = "sprinting_to_caret"

    def update_animation(self):
        walk_speed = 3
        sprint_speed = 32
        
        if self.current_state == "walking":
            self.pos_x += self.walk_direction * walk_speed
            # Rebond sur les bords d'ecran
            if self.pos_x >= VIRT_SCREEN_X + VIRT_SCREEN_W - self.window_w - 20:
                self.walk_direction = -1
            elif self.pos_x <= VIRT_SCREEN_X + 20:
                self.walk_direction = 1
                
            # Descente progressive vers le sol si Root etait en hauteur
            if self.pos_y < self.ground_y:
                self.pos_y += min(4, self.ground_y - self.pos_y)
            elif self.pos_y > self.ground_y:
                self.pos_y = self.ground_y
                
            # Pause aleatoire de temps en temps
            if random.random() < 0.012:
                self.current_state = "idle_pause"
                self.root_window.after(1200, self.resume_walking)
                
        elif self.current_state == "sprinting_to_caret":
            delta_x = self.target_x - self.pos_x
            delta_y = self.target_y - self.pos_y
            dist = (delta_x**2 + delta_y**2) ** 0.5
            self.walk_direction = 1 if delta_x >= 0 else -1
            
            if dist > 30:
                self.pos_x += (delta_x / dist) * sprint_speed
                self.pos_y += (delta_y / dist) * sprint_speed
            else:
                self.pos_x = self.target_x
                self.pos_y = self.target_y
                
                # Effacement automatique du texte errone avec Backspace
                nb_chars = len(self.active_typo_data["original_text"])
                for _ in range(nb_chars):
                    simulated_kb.press(keyboard.Key.backspace)
                    simulated_kb.release(keyboard.Key.backspace)
                    time.sleep(0.01)
                    
                # Affiche le texte vole et fuit hors de l'ecran
                self.text_label.config(text=f"{self.active_typo_data['original_text']}", fg="#ffffff")
                self.offscreen_exit_x = VIRT_SCREEN_X - 200 if self.pos_x < (VIRT_SCREEN_X + VIRT_SCREEN_W / 2) else VIRT_SCREEN_X + VIRT_SCREEN_W + 100
                self.current_state = "escaping_offscreen"
                
        elif self.current_state == "escaping_offscreen":
            delta_x = self.offscreen_exit_x - self.pos_x
            self.walk_direction = 1 if delta_x >= 0 else -1
            
            if abs(delta_x) > 35:
                self.pos_x += self.walk_direction * sprint_speed
            else:
                self.pos_x = self.offscreen_exit_x
                self.current_state = "hidden"
                self.root_window.after(400, self.prepare_corrected_return)
                
        elif self.current_state == "returning_with_fix":
            delta_x = self.memo_caret_x - self.pos_x
            delta_y = self.memo_caret_y - self.pos_y
            dist = (delta_x**2 + delta_y**2) ** 0.5
            self.walk_direction = 1 if delta_x >= 0 else -1
            
            if dist > 30:
                self.pos_x += (delta_x / dist) * sprint_speed
                self.pos_y += (delta_y / dist) * sprint_speed
            else:
                self.pos_x = self.memo_caret_x
                self.pos_y = self.memo_caret_y
                self.current_state = "depositing_text"
                
                # Saisie du texte corrige
                clean_text = self.active_typo_data["corrected_text"] + " "
                simulated_kb.type(clean_text)
                
                self.text_label.config(text=f"{self.active_typo_data['corrected_text']}", fg="#ffffff")
                self.root_window.after(1200, self.finish_cycle)
                
        # Securite des coordonnees Y
        if self.current_state not in ("escaping_offscreen", "hidden"):
            self.pos_y = min(max(VIRT_SCREEN_Y + 30, self.pos_y), self.ground_y)
            
        # Application de la geometrie
        self.root_window.geometry(f"{self.window_w}x{self.window_h}+{int(self.pos_x)}+{int(self.pos_y)}")
        
        # Selection de la frame d'animation
        frames = self.right_frames if self.walk_direction == 1 else self.left_frames
        if frames:
            self.frame_index = (self.frame_index + 1) % len(frames)
            self.sprite_label.config(image=frames[self.frame_index])
            
        frame_delay = 35 if self.current_state in ("sprinting_to_caret", "escaping_offscreen", "returning_with_fix") else 110
        self.root_window.after(frame_delay, self.update_animation)

    def prepare_corrected_return(self):
        if self.active_typo_data:
            self.text_label.config(text=f"{self.active_typo_data['corrected_text']}", fg="#ffffff")
            self.current_state = "returning_with_fix"

    def finish_cycle(self):
        self.text_label.config(text="")
        self.active_typo_data = None
        self.current_state = "walking"
        unlock_input()

    def resume_walking(self):
        if self.current_state == "idle_pause":
            self.walk_direction = random.choice([1, -1])
            self.current_state = "walking"

    def on_drag_start(self, event):
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        if self.current_state == "walking":
            self.current_state = "idle_pause"

    def on_drag_motion(self, event):
        self.pos_x += (event.x - self.drag_start_x)
        self.pos_y += (event.y - self.drag_start_y)
        self.root_window.geometry(f"{self.window_w}x{self.window_h}+{int(self.pos_x)}+{int(self.pos_y)}")
