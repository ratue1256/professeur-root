import time
import os
from pynput import keyboard
from ia import analyser_texte

# simule les touches pour effacer et reecrire
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
    # evite que l utilisateur tape pendant que root reecrit
    if bloquer_saisie:
        return
        
    try:
        if hasattr(key, "char") and key.char:
            buffer_phrase += key.char
            dernier_temps = time.time()
            if key.char in (".", "!", "?"):
                verifier_et_nettoyer(forcer_reset=True)
        elif key == keyboard.Key.space:
            buffer_phrase += " "
            dernier_temps = time.time()
        elif key == keyboard.Key.enter:
            verifier_et_nettoyer(forcer_reset=True)
        elif key == keyboard.Key.backspace:
            buffer_phrase = buffer_phrase[:-1]
    except Exception:
        pass

def verifier_et_nettoyer(forcer_reset=False):
    global buffer_phrase
    phrase = buffer_phrase.strip()
    if phrase and len(phrase) >= 3:
        res = analyser_texte(phrase)
        if res and callback_faute:
            bloquer()
            buffer_phrase = ""
            callback_faute(res)
        elif forcer_reset:
            buffer_phrase = ""

def verifier_pause():
    global buffer_phrase, dernier_temps, bloquer_saisie
    # declenche si la personne s arrete d ecrire
    if not bloquer_saisie and buffer_phrase.strip() and time.time() - dernier_temps > 0.9:
        verifier_et_nettoyer(forcer_reset=False)
