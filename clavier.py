import time
from pynput import keyboard
from ia import check_sentence_errors

# simule le clavier pour virer la faute et retaper
kb_sim = keyboard.Controller()

# stocke ce que le mec ecrit
buf = ""
last_t = 0.0
on_typo = None
locked = False

# touches a ignorer sinon le buffer se remplit de merde
IGNORE_KEYS = {
    keyboard.Key.shift, keyboard.Key.shift_r,
    keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r,
    keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r,
    keyboard.Key.cmd, keyboard.Key.cmd_l, keyboard.Key.cmd_r,
    keyboard.Key.caps_lock, keyboard.Key.tab
}

def lock_input():
    global locked
    locked = True

def unlock_input():
    global locked
    locked = False

def handle_press(k):
    global buf, last_t, locked
    
    # si root est en train de courir ou effacer on bloque la frappe
    if locked:
        return
        
    if k in IGNORE_KEYS:
        return

    try:
        if hasattr(k, "char") and k.char:
            buf += k.char
            last_t = time.time()
            # fin de phrase direct on check
            if k.char in (".", "!", "?", "\n"):
                eval_buffer(force=True)
        elif k == keyboard.Key.space:
            buf += " "
            last_t = time.time()
            # si la phrase devient bcp trop longue on coupe un peu
            if len(buf) > 150:
                buf = " ".join(buf.split()[-6:])
        elif k == keyboard.Key.enter:
            eval_buffer(force=True)
        elif k == keyboard.Key.backspace:
            buf = buf[:-1] if buf else ""
            last_t = time.time()
    except Exception:
        # pynput throw des erreurs random sur certaines touches
        pass

def eval_buffer(force=False):
    global buf
    txt = buf.strip()
    
    # check si y a une faute
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
    # si le mec s arrete 0.8s on check sa phrase
    if not locked and len(buf.strip()) >= 3:
        if (time.time() - last_t) > 0.8:
            eval_buffer(force=False)

def start_keyboard_listener(callback):
    global on_typo
    on_typo = callback
    # listener en arriere plan
    listener = keyboard.Listener(on_press=handle_press)
    listener.daemon = True
    listener.start()
