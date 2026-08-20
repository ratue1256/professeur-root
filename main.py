import tkinter as tk
from pet import RootPet
from clavier import start_keyboard_listener, check_typing_pause

# lance le pet root
def main():
    root = tk.Tk()
    root.title("Professeur Root")
    
    # fenetre transparente
    root.overrideredirect(True)
    root.wm_attributes("-topmost", True)
    
    # 000001 = noir presque pur rendu transparent par tkinter
    trans_color = "#000001"
    root.wm_attributes("-transparentcolor", trans_color)
    root.config(bg=trans_color)

    # pet + listener clavier
    pet = RootPet(root)
    start_keyboard_listener(pet.on_error_detected)

    # loop pour voir si le mec a fini sa phrase
    def loop():
        check_typing_pause()
        root.after(200, loop)

    pet.update_animation()
    loop()
    root.mainloop()

if __name__ == "__main__":
    main()
