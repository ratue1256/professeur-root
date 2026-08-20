import tkinter as tk
from pet import RootPet
from clavier import start_keyboard_listener, check_typing_pause

# lanceur de Root pour le hackathon
def main():
    root = tk.Tk()
    
    # fenetre transparente sans bordure par dessus toutes les apps
    root.overrideredirect(True)
    root.wm_attributes("-topmost", True)
    root.wm_attributes("-transparentcolor", "#000001")
    root.config(bg="#000001")

    # init pet + ecoute clavier
    companion = RootPet(root)
    start_keyboard_listener(companion.on_error_detected)

    # boucle pour checker si la personne a fini de taper
    def poll_kb():
        check_typing_pause()
        root.after(250, poll_kb)

    companion.update_animation()
    poll_kb()
    root.mainloop()

if __name__ == "__main__":
    main()
