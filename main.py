import tkinter as tk
import os
from pet import RootPet
from clavier import start_keyboard_listener, check_typing_pause

# petit launcher pour root
def main():
    root = tk.Tk()
    root.title("Professeur Root")
    
    # fenetre transparente sans bordures
    root.overrideredirect(True)
    root.wm_attributes("-topmost", True)
    
    # hack classique pour la transparence sous windows
    trans_color = "#000001"
    root.wm_attributes("-transparentcolor", trans_color)
    root.config(bg=trans_color)

    # instance de root sur l'ecran
    pet = RootPet(root)
    start_keyboard_listener(pet.on_error_detected)

    # boucle pour checker si l'user s'arrete d'ecrire
    def loop():
        check_typing_pause()
        root.after(200, loop)

    pet.update_animation()
    loop()
    root.mainloop()

if __name__ == "__main__":
    main()
