import os
import re
import difflib
import random
import threading

ia_prete = False
modele_camembert = None

MOTS_FR = [
    "j", "t", "l", "c", "d", "n", "s", "m", "ai", "as", "a", "ont", "est", "es", "suis",
    "sommes", "etes", "sont", "un", "une", "des", "le", "la", "les", "du", "de", "ce",
    "cet", "cette", "ces", "mon", "ton", "son", "mes", "tes", "ses", "notre", "votre",
    "leur", "leurs", "je", "tu", "il", "elle", "on", "nous", "vous", "ils", "elles",
    "salut", "bonjour", "comment", "ca", "va", "bien", "oui", "non", "merci", "quoi",
    "qui", "quand", "pourquoi", "parce", "dans", "avec", "sans", "pour", "sur", "sous",
    "faire", "fait", "vais", "veux", "peux", "doit", "pote", "frero", "chose", "temps",
    "style", "vraiment", "faute", "phrase", "propre", "tout", "tous", "alors", "donc",
    "mais", "trop", "tres", "plus", "moins", "nouvel", "nouveau", "nouvelle",
    "boucle", "fichier", "fichiers", "fonction", "variable", "variables", "commit", "commits",
    "push", "pull", "branche", "branches", "serveur", "code", "coder", "ecrire", "ecrit",
    "ajouter", "supprimer", "installer", "modele", "python", "terminal", "github", "hackathon",
    "erreur", "erreurs", "orthographe", "programme", "script", "test", "tests", "valider",
    "projet", "clavier", "ecran", "vitesse", "docker", "linux", "windows", "bug", "bugs"
]

COMMITS_NULS = ["fix", "wip", "test", "update", "patch", "a", "bug", "modifs", "rien", "yo"]

def charger_ia():
    global ia_prete, modele_camembert
    try:
        import torch
        from transformers import pipeline
        device = 0 if torch.cuda.is_available() else -1
        modele_camembert = pipeline(
            "fill-mask",
            model="cmarkea/distilcamembert-base",
            tokenizer="cmarkea/distilcamembert-base",
            device=device
        )
        ia_prete = True
    except Exception:
        pass

thread = threading.Thread(target=charger_ia, daemon=True)
thread.start()

def nettoyer(mot):
    return re.sub(r'(.)\1{2,}', r'\1', mot.lower().strip(".,!?:;\"'()-_/"))

def corriger_mot(mot):
    propre = nettoyer(mot)
    if not propre or len(propre) <= 2:
        return mot
        
    if propre in MOTS_FR:
        return propre
        
    swap_a = propre.replace("q", "a")
    if swap_a in MOTS_FR:
        return swap_a
    if "sq" in propre:
        if propre in ("sqva", "sqcva", "sqcvat", "sqcv"):
            return "ca va"
            
    proches = difflib.get_close_matches(propre, MOTS_FR, n=1, cutoff=0.55)
    if proches:
        return proches[0]
        
    proches_swap = difflib.get_close_matches(swap_a, MOTS_FR, n=1, cutoff=0.55)
    if proches_swap:
        return proches_swap[0]
        
    return mot

def analyser_texte(texte):
    texte = texte.strip()
    if not texte or len(texte) < 3:
        return None
        
    mots = texte.split()
    if len(mots) == 1 and mots[0].lower() in COMMITS_NULS:
        return {
            "texte_original": texte,
            "texte_corrige": f"feat: mise a jour propre ({texte})"
        }
        
    mots_corriges = []
    a_change = False
    
    for m in mots:
        corrige = corriger_mot(m)
        if corrige.lower() != m.lower():
            a_change = True
        mots_corriges.append(corrige)
        
    phrase = " ".join(mots_corriges)
    if "j ai add" in texte.lower():
        phrase = phrase.replace("j ai add", "j'ai ajoute")
        a_change = True
    elif "j ai fix" in texte.lower():
        phrase = phrase.replace("j ai fix", "j'ai corrige")
        a_change = True
        
    if a_change:
        return {
            "texte_original": texte,
            "texte_corrige": phrase
        }
        
    return None
