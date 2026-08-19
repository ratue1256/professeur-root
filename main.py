import tkinter as tk
from pet import RootPet
from clavier import initialiser_clavier, verifier_pause

def main():
    fenetre = tk.Tk()
    fenetre.overrideredirect(True)
    fenetre.wm_attributes("-topmost", True)
    couleur_transparente = "#000001"
    fenetre.wm_attributes("-transparentcolor", couleur_transparente)
    fenetre.configure(bg=couleur_transparente)
    
    root_pet = RootPet(fenetre)
    initialiser_clavier(root_pet.declencher_faute)
    
    print("[+] Professeur Root est en route sur ta faute ou la mienne")
    
    def loop_check():
        verifier_pause()
        fenetre.after(300, loop_check)
        
    root_pet.actualiser()
    loop_check()
    fenetre.mainloop()

if __name__ == "__main__":
    main()
