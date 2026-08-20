import tkinter as tk
from pet import RootPet
from clavier import start_keyboard_listener, check_typing_pause

# Point d'entree du pet pour le hackathon
def main():
    root_window = tk.Tk()
    
    # Configuration de la fenetre overlay transparente
    # Note: le transparentcolor marche bien sur Win10/11 avec la couleur #000001
    root_window.overrideredirect(True)
    root_window.wm_attributes("-topmost", True)
    bg_color = "#000001"
    root_window.wm_attributes("-transparentcolor", bg_color)
    root_window.config(bg=bg_color)

    # Initialisation du pet et du hook clavier
    pet = RootPet(root_window)
    start_keyboard_listener(on_typo_callback=pet.on_error_detected)

    # Boucle de verification pour le debounce de frappe (~300ms)
    def update_loop():
        check_typing_pause()
        root_window.after(300, update_loop)

    # Lancement des boucles
    pet.update_animation()
    update_loop()
    root_window.mainloop()

if __name__ == "__main__":
    main()
