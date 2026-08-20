import time
import os
from pynput import keyboard
from ia import check_sentence_errors

# Controleur pynput pour la simulation de frappe
key_controller = keyboard.Controller()

# Buffer de texte pour accumuler la phrase courante
current_buffer = ""
last_keystroke_ts = 0.0
on_error_found = None
is_input_locked = False

def lock_input():
    global is_input_locked
    is_input_locked = True

def unlock_input():
    global is_input_locked
    is_input_locked = False

def start_keyboard_listener(on_typo_callback):
    global on_error_found
    on_error_found = on_typo_callback
    
    # Listener global en daemon thread
    listener = keyboard.Listener(on_press=handle_key_press)
    listener.daemon = True
    listener.start()

def handle_key_press(key):
    global current_buffer, last_keystroke_ts, is_input_locked
    
    # Bloque les touches utilisateurs pendant que Root efface / retape
    if is_input_locked:
        return
        
    try:
        if hasattr(key, "char") and key.char:
            current_buffer += key.char
            last_keystroke_ts = time.time()
            # Si ponctuation de fin de phrase, on analyse direct
            if key.char in (".", "!", "?"):
                process_buffer(force_reset=True)
        elif key == keyboard.Key.space:
            current_buffer += " "
            last_keystroke_ts = time.time()
        elif key == keyboard.Key.enter:
            # Sur Entree, verifie avant de valider
            process_buffer(force_reset=True)
        elif key == keyboard.Key.backspace:
            if current_buffer:
                current_buffer = current_buffer[:-1]
    except (AttributeError, TypeError):
        pass

def process_buffer(force_reset=False):
    global current_buffer
    raw_text = current_buffer.strip()
    
    # On n'analyse que si on a au moins 3 caracteres
    if raw_text and len(raw_text) >= 3:
        correction_result = check_sentence_errors(raw_text)
        if correction_result and on_error_found:
            lock_input()
            current_buffer = ""
            on_error_found(correction_result)
        elif force_reset:
            current_buffer = ""

def check_typing_pause():
    global current_buffer, last_keystroke_ts, is_input_locked
    # Si l'utilisateur s'arrete d'ecrire pendant ~900ms, on analyse
    if not is_input_locked and current_buffer.strip():
        if time.time() - last_keystroke_ts > 0.9:
            process_buffer(force_reset=False)
