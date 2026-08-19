import time
from pynput import keyboard
from ia import analyser_texte

clavier_simule = keyboard.Controller()
buffer_phrase = ""
dernier_temps = 0
callback_faute = None
bloquer_saisie = False

def bloquer():
    global bloquer_saisie
    bloquer_saisie = True

def debloquer():
    global bloquer_saisie
    bloquer_saisie = False

def initialiser_clavier(callback):
    global callback_faute
    callback_faute = callback
    listener = keyboard.Listener(on_press=touche_pressee)
    listener.daemon = True
    listener.start()

def touche_pressee(key):
    global buffer_phrase, dernier_temps, bloquer_saisie
    if bloquer_saisie:
        return
        
    try:
        if hasattr(key, "char") and key.char:
            buffer_phrase += key.char
            dernier_temps = time.time()
            if len(buffer_phrase) > 120:
                buffer_phrase = " ".join(buffer_phrase.split()[-4:])
        elif key == keyboard.Key.space:
            buffer_phrase += " "
            dernier_temps = time.time()
        elif key == keyboard.Key.enter:
            verifier_et_nettoyer()
        elif key == keyboard.Key.backspace:
            buffer_phrase = buffer_phrase[:-1]
    except Exception:
        pass

def verifier_et_nettoyer():
    global buffer_phrase
    phrase = buffer_phrase.strip()
    if phrase and len(phrase) >= 3:
        res = analyser_texte(phrase)
        if res and callback_faute:
            buffer_phrase = ""
            callback_faute(res)
        elif not res:
            mots = phrase.split()
            buffer_phrase = mots[-1] if mots else ""

def verifier_pause():
    global buffer_phrase, dernier_temps, bloquer_saisie
    if not bloquer_saisie and buffer_phrase.strip() and time.time() - dernier_temps > 1.2:
        verifier_et_nettoyer()
