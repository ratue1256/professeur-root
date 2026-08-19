import os
import re
import difflib
import random
import threading

ia_prete = False
modele_camembert = None

# dictionnaire de mots francais et dev
VOCAB_FR = [
    "j", "t", "l", "c", "d", "n", "s", "m", "qu", "ai", "as", "a", "ont", "est", "es", "suis",
    "sommes", "etes", "sont", "un", "une", "des", "le", "la", "les", "du", "de", "ce",
    "cet", "cette", "ces", "mon", "ton", "son", "mes", "tes", "ses", "notre", "votre",
    "leur", "leurs", "je", "tu", "il", "elle", "on", "nous", "vous", "ils", "elles",
    "salut", "bonjour", "bonsoir", "comment", "ca", "va", "bien", "oui", "non", "merci",
    "quoi", "qui", "quand", "pourquoi", "parce", "dans", "avec", "sans", "pour", "sur",
    "sous", "chez", "faire", "fait", "vais", "veux", "peux", "doit", "doivent", "peut",
    "peuvent", "sait", "savent", "pote", "frero", "chose", "temps", "style", "vraiment",
    "faute", "fautes", "phrase", "phrases", "propre", "tout", "tous", "toute", "toutes",
    "alors", "donc", "mais", "trop", "tres", "plus", "moins", "nouvel", "nouveau",
    "nouvelle", "pile", "endroit", "chercher", "comprend", "comprendre", "contexte",
    "conjugaison", "corriger", "corrige", "complete", "complet", "analyser", "analyse",
    "smart", "intelligent", "vite", "rapide", "marche", "roule", "boucle", "fichier",
    "fichiers", "fonction", "variable", "variables", "commit", "commits", "push", "pull",
    "branche", "branches", "serveur", "code", "coder", "ecrire", "ecrit", "ajouter",
    "ajoute", "supprimer", "installer", "modele", "python", "terminal", "github",
    "hackathon", "erreur", "erreurs", "orthographe", "programme", "script", "test",
    "tests", "valider", "projet", "clavier", "ecran", "vitesse", "docker", "linux",
    "windows", "bug", "bugs", "add", "fix", "git", "diff", "merge", "fetch"
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

def phonetique(mot):
    m = mot.lower()
    m = re.sub(r'ph', 'f', m)
    m = re.sub(r'qu', 'k', m)
    m = re.sub(r'c([eiy])', r's\1', m)
    m = re.sub(r'c([aou])', r'k\1', m)
    m = re.sub(r'ss', 's', m)
    m = re.sub(r'(.)\1+', r'\1', m)
    return m

def nettoyer(mot):
    return re.sub(r'(.)\1{2,}', r'\1', mot.lower().strip(".,!?:;\"()-_/"))

def corriger_grammaire_contexte(phrase):
    # regles grammaticales et de contexte sur toute la phrase
    p = phrase
    
    # 1. homophones et confusions classiques
    p = re.sub(r'\bcette\s+est\b', "c'est", p, flags=re.IGNORECASE)
    p = re.sub(r'\bc\s+est\b', "c'est", p, flags=re.IGNORECASE)
    p = re.sub(r'\bse\s+est\b', "c'est", p, flags=re.IGNORECASE)
    p = re.sub(r'\b(sa|sq)\s+va\b', "ça va", p, flags=re.IGNORECASE)
    p = re.sub(r'\b(sa|sq)\s+marche\b', "ça marche", p, flags=re.IGNORECASE)
    p = re.sub(r'\b(il|elle|on)\s+doivent\b', r'\1 doit', p, flags=re.IGNORECASE)
    p = re.sub(r'\b(ils|elles)\s+doit\b', r'\1 doivent', p, flags=re.IGNORECASE)
    p = re.sub(r'\b(il|elle|on)\s+peuvent\b', r'\1 peut', p, flags=re.IGNORECASE)
    p = re.sub(r'\b(ils|elles)\s+peut\b', r'\1 peuvent', p, flags=re.IGNORECASE)
    
    # 2. infinitif apres preposition (pour/de/a + verbe)
    p = re.sub(r'\bpour\s+corrige\b', "pour corriger", p, flags=re.IGNORECASE)
    p = re.sub(r'\bpour\s+comprend\b', "pour comprendre", p, flags=re.IGNORECASE)
    p = re.sub(r'\bpour\s+analyse\b', "pour analyser", p, flags=re.IGNORECASE)
    p = re.sub(r'\bdoit\s+analyse\b', "doit analyser", p, flags=re.IGNORECASE)
    p = re.sub(r'\bdoit\s+corrige\b', "doit corriger", p, flags=re.IGNORECASE)
    
    # 3. accords feminins / masculins
    p = re.sub(r'\bla\s+phrase\s+complet\b', "la phrase complete", p, flags=re.IGNORECASE)
    p = re.sub(r'\bun\s+nouvelle\b', "un nouveau", p, flags=re.IGNORECASE)
    p = re.sub(r'\bune\s+nouvel\b', "une nouvelle", p, flags=re.IGNORECASE)
    p = re.sub(r'\bnouvel\s+boucle\b', "nouvelle boucle", p, flags=re.IGNORECASE)
    
    # 4. franglais dev
    p = re.sub(r'\bj\s+ai\s+add\b', "j'ai ajoute", p, flags=re.IGNORECASE)
    p = re.sub(r'\bj\s+ai\s+fix\b', "j'ai corrige", p, flags=re.IGNORECASE)
    p = re.sub(r'\bj\s+ai\s+push\b', "j'ai push", p, flags=re.IGNORECASE)
    
    return p

def corriger_mot(mot, phrase_complete=""):
    propre = nettoyer(mot)
    if not propre or len(propre) <= 1 or "'" in propre:
        return mot
        
    if propre in VOCAB_FR:
        return propre
        
    swap_a = propre.replace("q", "a")
    if swap_a in VOCAB_FR:
        return swap_a
    if "sq" in propre and propre in ("sqva", "sqcva", "sqcvat", "sqcv"):
        return "ca va"
        
    # IA CamemBERT contextuelle si active
    if ia_prete and modele_camembert and phrase_complete:
        try:
            masque = phrase_complete.replace(mot, "<mask>", 1)
            preds = modele_camembert(masque)
            if isinstance(preds, list) and len(preds) > 0:
                candidat_ia = preds[0]["token_str"].strip().lower()
                if len(candidat_ia) >= 2 and difflib.SequenceMatcher(None, propre, candidat_ia).ratio() > 0.45:
                    return candidat_ia
        except Exception:
            pass
            
    proches = difflib.get_close_matches(propre, VOCAB_FR, n=1, cutoff=0.55)
    if proches:
        return proches[0]
        
    proches_swap = difflib.get_close_matches(swap_a, VOCAB_FR, n=1, cutoff=0.55)
    if proches_swap:
        return proches_swap[0]
        
    p_propre = phonetique(propre)
    candidats = sorted(VOCAB_FR, key=lambda v: difflib.SequenceMatcher(None, p_propre, phonetique(v)).ratio(), reverse=True)
    if candidats and difflib.SequenceMatcher(None, p_propre, phonetique(candidats[0])).ratio() > 0.65:
        return candidats[0]
        
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
        
    # 1. passe mot par mot
    mots_corriges = []
    a_change = False
    for m in mots:
        corrige = corriger_mot(m, phrase_complete=texte)
        if corrige.lower() != m.lower():
            a_change = True
        mots_corriges.append(corrige)
        
    phrase_intermediaire = " ".join(mots_corriges)
    
    # 2. passe contextuelle et grammaticale sur toute la phrase
    phrase_finale = corriger_grammaire_contexte(phrase_intermediaire)
    
    if a_change or phrase_finale.lower() != texte.lower():
        return {
            "texte_original": texte,
            "texte_corrige": phrase_finale
        }
        
    return None
