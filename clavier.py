import time
from pynput import keyboard
from ia import check_sentence_errors

# listener clavier pour choper les phrases en direct
kb_ctrl = keyboard.Controller()
buf = ""
last_t = 0.0
on_typo = None
locked = False

def lock_input():
    global locked
    locked = True

def unlock_input():
    global locked
    locked = False

def handle_press(k):
    global buf, last_t, locked
    
    # si root est en train de corriger on touche a rien
    if locked:
        return
        
    try:
        # caractere normal
        if hasattr(k, "char") and k.char is not None:
            buf += k.char
            last_t = time.time()
            # fin de phrase direct
            if k.char in (".", "!", "?", "\n"):
                eval_buffer(force=True)
        elif k == keyboard.Key.space:
            buf += " "
            last_t = time.time()
        elif k == keyboard.Key.enter:
            eval_buffer(force=True)
        elif k == keyboard.Key.backspace:
            buf = buf[:-1] if len(buf) > 0 else ""
            last_t = time.time()
    except Exception:
        # pynput peut throw des trucs bizarres sur certaines touches speciales
        pass

def eval_buffer(force=False):
    global buf
    txt = buf.strip()
    
    # evite d'analyser pour 1 ou 2 lettres
    if len(txt) >= 3:
        res = check_sentence_errors(txt)
        if res and on_typo:
            lock_input()
            buf = ""
            on_typo(res)
            return
            
    if force:
        buf = ""

def check_typing_pause():
    global buf, last_t, locked
    # debounce d'environ 0.85s sans frappe pour laisser l'user reflechir
    if not locked and len(buf.strip()) >= 3:
        if (time.time() - last_t) > 0.85:
            eval_buffer(force=False)

def start_keyboard_listener(callback):
    global on_typo
    on_typo = callback
    l = keyboard.Listener(on_press=handle_press)
    l.daemon = True
    l.start()
