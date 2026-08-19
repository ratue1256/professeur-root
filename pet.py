import os
import time
import random
import ctypes
from ctypes import wintypes
import tkinter as tk
from PIL import Image, ImageTk
from pynput import keyboard

clavier_simule = keyboard.Controller()

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

def get_exact_typing_pos():
    try:
        gui = GUITHREADINFO(cbSize=ctypes.sizeof(GUITHREADINFO))
        if ctypes.windll.user32.GetGUIThreadInfo(0, ctypes.byref(gui)) and gui.hwndCaret:
            pt = wintypes.POINT(gui.rcCaret.left, gui.rcCaret.top)
            ctypes.windll.user32.ClientToScreen(gui.hwndCaret, ctypes.byref(pt))
            if pt.x > -1000 and pt.y > -500:
                return pt.x, pt.y
    except Exception:
        pass
        
    pt = wintypes.POINT()
    ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
    return pt.x, pt.y

virt_x = ctypes.windll.user32.GetSystemMetrics(76)
virt_y = ctypes.windll.user32.GetSystemMetrics(77)
virt_w = ctypes.windll.user32.GetSystemMetrics(78)
virt_h = ctypes.windll.user32.GetSystemMetrics(79)

class RootPet:
    def __init__(self, fenetre):
        self.fenetre = fenetre
        self.taille_sprite = 90
        self.largeur_fen = 340
        self.hauteur_fen = 140
        
        self.pos_x = virt_x + random.randint(200, max(300, virt_w - 400))
        self.pos_y = virt_y + virt_h - self.taille_sprite - 80
        self.direction = 1
        self.etat = "marche"
        
        self.cible_x = self.pos_x
        self.cible_y = self.pos_y
        self.souris_memo_x = self.pos_x
        self.souris_memo_y = self.pos_y
        
        self.faute_en_cours = None
        self.bord_sortie_x = 0
        self.num_frame = 0
        
        self.frames_droite = []
        self.frames_gauche = []
        self.charger_sprites()
        
        # texte blanc pur sans fond et sans couleur verte
        self.label_texte = tk.Label(
            self.fenetre,
            text="",
            fg="#ffffff",
            bg="#000001",
            font=("Segoe UI", 11, "bold")
        )
        self.label_texte.pack(side="top", pady=(0, 2))
        
        self.label_root = tk.Label(self.fenetre, bg="#000001", bd=0)
        self.label_root.pack(side="top")
        
        self.drag_x = 0
        self.drag_y = 0
        self.label_root.bind("<Button-1>", self.debut_glisser)
        self.label_root.bind("<B1-Motion>", self.glisser)

    def charger_sprites(self):
        dossier = os.path.join(os.path.dirname(__file__), "asset")
        for i in range(1, 9):
            chemin = os.path.join(dossier, f"Root{i}.png")
            if os.path.exists(chemin):
                img = Image.open(chemin).convert("RGBA")
                bbox = (200, 0, 1800, 2000)
                img = img.crop(bbox)
                img = img.resize((self.taille_sprite, self.taille_sprite), Image.Resampling.LANCZOS)
                
                bg = Image.new("RGBA", img.size, (0, 0, 1, 255))
                img_d = Image.alpha_composite(bg, img)
                img_g = Image.alpha_composite(bg, img.transpose(Image.FLIP_LEFT_RIGHT))
                
                self.frames_droite.append(ImageTk.PhotoImage(img_d))
                self.frames_gauche.append(ImageTk.PhotoImage(img_g))

    def declencher_faute(self, faute_info):
        if self.etat not in ("marche", "pause"):
            return
            
        self.faute_en_cours = faute_info
        sx, sy = get_exact_typing_pos()
        
        self.souris_memo_x = min(max(virt_x + 20, sx - (self.largeur_fen // 2)), virt_x + virt_w - self.largeur_fen - 20)
        self.souris_memo_y = min(max(virt_y + 20, sy - self.taille_sprite - 20), virt_y + virt_h - self.hauteur_fen - 50)
        
        self.cible_x = self.souris_memo_x
        self.cible_y = self.souris_memo_y
        self.direction = 1 if self.cible_x > self.pos_x else -1
        self.etat = "cours_vers_souris"

    def actualiser(self):
        v_marche = 3
        v_sprint = 20
        
        if self.etat == "marche":
            self.pos_x += self.direction * v_marche
            if self.pos_x >= virt_x + virt_w - self.largeur_fen - 20:
                self.direction = -1
            elif self.pos_x <= virt_x + 20:
                self.direction = 1
                
            if random.random() < 0.012:
                self.etat = "pause"
                self.fenetre.after(1200, self.reprendre_marche)
                
        elif self.etat == "cours_vers_souris":
            dx = self.cible_x - self.pos_x
            dy = self.cible_y - self.pos_y
            dist = (dx**2 + dy**2) ** 0.5
            self.direction = 1 if dx >= 0 else -1
            
            if dist > 22:
                self.pos_x += (dx / dist) * v_sprint
                self.pos_y += (dy / dist) * v_sprint
            else:
                # arrive sur place : efface la phrase
                self.pos_x = self.cible_x
                self.pos_y = self.cible_y
                
                nb = len(self.faute_en_cours["texte_original"]) + 1
                for _ in range(nb):
                    clavier_simule.press(keyboard.Key.backspace)
                    clavier_simule.release(keyboard.Key.backspace)
                    time.sleep(0.01)
                    
                # affiche le texte vole en blanc au-dessus de root
                self.label_texte.configure(text=f"{self.faute_en_cours['texte_original']}", fg="#ffffff")
                self.bord_sortie_x = virt_x - 200 if self.pos_x < (virt_x + virt_w / 2) else virt_x + virt_w + 100
                self.etat = "fuite_hors_ecran"
                
        elif self.etat == "fuite_hors_ecran":
            dx = self.bord_sortie_x - self.pos_x
            self.direction = 1 if dx >= 0 else -1
            
            if abs(dx) > 25:
                self.pos_x += self.direction * v_sprint
            else:
                self.pos_x = self.bord_sortie_x
                self.etat = "cache"
                self.fenetre.after(600, self.retour_corrige)
                
        elif self.etat == "retour_corrige":
            dx = self.souris_memo_x - self.pos_x
            dy = self.souris_memo_y - self.pos_y
            dist = (dx**2 + dy**2) ** 0.5
            self.direction = 1 if dx >= 0 else -1
            
            if dist > 22:
                self.pos_x += (dx / dist) * v_sprint
                self.pos_y += (dy / dist) * v_sprint
            else:
                self.pos_x = self.souris_memo_x
                self.pos_y = self.souris_memo_y
                self.etat = "depose"
                
                # retape la phrase corrigee
                texte_propre = self.faute_en_cours["texte_corrige"] + " "
                clavier_simule.type(texte_propre)
                
                # texte reste blanc au-dessus de sa tete
                self.label_texte.configure(text=f"{self.faute_en_cours['texte_corrige']}", fg="#ffffff")
                self.fenetre.after(1600, self.finir_remise)
                
        self.fenetre.geometry(f"{self.largeur_fen}x{self.hauteur_fen}+{int(self.pos_x)}+{int(self.pos_y)}")
        
        frames = self.frames_droite if self.direction == 1 else self.frames_gauche
        if frames:
            self.num_frame = (self.num_frame + 1) % len(frames)
            self.label_root.configure(image=frames[self.num_frame])
            
        delai = 65 if "cours" in self.etat or "fuite" in self.etat or "retour" in self.etat else 110
        self.fenetre.after(delai, self.actualiser)

    def retour_corrige(self):
        if self.faute_en_cours:
            self.label_texte.configure(text=f"{self.faute_en_cours['texte_corrige']}", fg="#ffffff")
            self.etat = "retour_corrige"

    def finir_remise(self):
        self.label_texte.configure(text="")
        self.faute_en_cours = None
        self.etat = "marche"

    def reprendre_marche(self):
        if self.etat == "pause":
            self.direction = random.choice([1, -1])
            self.etat = "marche"

    def debut_glisser(self, event):
        self.drag_x = event.x
        self.drag_y = event.y
        if self.etat == "marche":
            self.etat = "pause"

    def glisser(self, event):
        self.pos_x += (event.x - self.drag_x)
        self.pos_y += (event.y - self.drag_y)
        self.fenetre.geometry(f"{self.largeur_fen}x{self.hauteur_fen}+{int(self.pos_x)}+{int(self.pos_y)}")
