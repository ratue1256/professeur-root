import os
import re
import difflib
import unicodedata

dossier = os.path.dirname(__file__)
chemin_dico = os.path.join(dossier, "dico_fr.txt")

DICO_TOTAL = set()
DICO_PAR_LEN = {}

if os.path.exists(chemin_dico):
    with open(chemin_dico, "r", encoding="utf-8") as f:
        brut = set([w.strip().lower() for w in f if w.strip()])
        sans_acc = set(["".join(c for c in unicodedata.normalize('NFD', w) if unicodedata.category(c) != 'Mn') for w in brut])
        DICO_TOTAL = brut | sans_acc
        
        for w in DICO_TOTAL:
            l = len(w)
            if l not in DICO_PAR_LEN:
                DICO_PAR_LEN[l] = []
            DICO_PAR_LEN[l].append(w)

PROTEGES = {
    "osu", "ezio", "roblox", "discord", "steam", "valorant", "minecraft",
    "git", "github", "commit", "push", "pull", "add", "fix", "wip", "merge", "fetch",
    "python", "docker", "linux", "windows", "dev", "bug", "bugs", "root",
    "complete", "completer", "joue", "jouer", "jeu", "partie", "con", "conne",
    "chiant", "merde", "jsp", "osef", "tkt", "bg", "frero", "pote", "truc",
    "style", "grave", "relou", "chelou", "zarbi", "wesh", "jpp", "mdr"
}

FAUTES_COURANTES = {
    "sqlut": "salut", "salu": "salut", "slt": "salut", "bjr": "bonjour", "bsr": "bonsoir",
    "commennnt": "comment", "coment": "comment", "cmnt": "comment", "commnt": "comment",
    "sqcvat": "ca va", "sqcva": "ca va", "sqva": "ca va", "cava": "ca va",
    "bouvle": "boucle", "puseh": "push", "ortogorfaf": "orthographe",
    "ortografe": "orthographe", "ortographe": "orthographe",
    "prbleme": "probleme", "problm": "probleme", "bcp": "beaucoup",
    "stp": "s'il te plait", "svp": "s'il vous plait", "frr": "frero"
}

COMMITS_NULS = ["fix", "wip", "test", "update", "patch", "a", "bug", "modifs", "rien", "yo"]

def corriger_mot(mot):
    m = mot.lower().strip(".,!?:;\"'()-_/")
    if not m or len(m) <= 1:
        return mot
    if m in PROTEGES or mot.lower() in PROTEGES:
        return mot
    if m in FAUTES_COURANTES:
        return FAUTES_COURANTES[m]
        
    m_clean = re.sub(r'(.)\1{2,}', r'\1', m)
    if m_clean in FAUTES_COURANTES:
        return FAUTES_COURANTES[m_clean]
    if m_clean in DICO_TOTAL or m_clean in PROTEGES:
        return m_clean
        
    m_double = re.sub(r'(.)\1{2,}', r'\1\1', m)
    if m_double in FAUTES_COURANTES:
        return FAUTES_COURANTES[m_double]
    if m_double in DICO_TOTAL or m_double in PROTEGES:
        return m_double
        
    if m in DICO_TOTAL:
        return mot
        
    swap_a = m.replace("q", "a")
    if swap_a in DICO_TOTAL or swap_a in PROTEGES:
        return swap_a
    if swap_a in FAUTES_COURANTES:
        return FAUTES_COURANTES[swap_a]
        
    # recherche automatique dans le dictionnaire francais
    l = len(m)
    candidats = []
    for dl in (-1, 0, 1):
        if l + dl in DICO_PAR_LEN:
            candidats.extend(DICO_PAR_LEN[l + dl])
            
    if candidats and len(m) >= 3:
        proches = difflib.get_close_matches(m, candidats, n=1, cutoff=0.75)
        if proches:
            return proches[0]
            
    return mot

def corriger_grammaire_phrase(texte):
    p = texte
    p = re.sub(r'\bcette\s+est\b', "c'est", p, flags=re.IGNORECASE)
    p = re.sub(r'\bc\s+est\b', "c'est", p, flags=re.IGNORECASE)
    p = re.sub(r'\b(sa|sq)\s+va\b', "ça va", p, flags=re.IGNORECASE)
    p = re.sub(r'\b(sa|sq)\s+marche\b', "ça marche", p, flags=re.IGNORECASE)
    
    # accords sujet-verbe
    p = re.sub(r'\b(il|elle|on)\s+doivent\b', r'\1 doit', p, flags=re.IGNORECASE)
    p = re.sub(r'\b(ils|elles)\s+doit\b', r'\1 doivent', p, flags=re.IGNORECASE)
    p = re.sub(r'\b(il|elle|on)\s+peuvent\b', r'\1 peut', p, flags=re.IGNORECASE)
    p = re.sub(r'\b(ils|elles)\s+peut\b', r'\1 peuvent', p, flags=re.IGNORECASE)
    p = re.sub(r'\b(il|elle|on)\s+savent\b', r'\1 sait', p, flags=re.IGNORECASE)
    p = re.sub(r'\b(ils|elles)\s+sait\b', r'\1 savent', p, flags=re.IGNORECASE)
    p = re.sub(r'\b(il|elle|on)\s+veulent\b', r'\1 veut', p, flags=re.IGNORECASE)
    p = re.sub(r'\b(ils|elles)\s+veut\b', r'\1 veulent', p, flags=re.IGNORECASE)
    
    # infinitifs apres prepositions
    p = re.sub(r'\bpour\s+corrige\b', "pour corriger", p, flags=re.IGNORECASE)
    p = re.sub(r'\bpour\s+comprend\b', "pour comprendre", p, flags=re.IGNORECASE)
    p = re.sub(r'\bpour\s+analyse\b', "pour analyser", p, flags=re.IGNORECASE)
    p = re.sub(r'\bdoit\s+analyse\b', "doit analyser", p, flags=re.IGNORECASE)
    p = re.sub(r'\bdoit\s+corrige\b', "doit corriger", p, flags=re.IGNORECASE)
    p = re.sub(r'\bdoit\s+comprend\b', "doit comprendre", p, flags=re.IGNORECASE)
    
    # accords genre / nombre
    p = re.sub(r'\bla\s+phrase\s+complet\b', "la phrase complete", p, flags=re.IGNORECASE)
    p = re.sub(r'\bune\s+nouvel\b', "une nouvelle", p, flags=re.IGNORECASE)
    p = re.sub(r'\bnouvel\s+boucle\b', "nouvelle boucle", p, flags=re.IGNORECASE)
    
    # dev
    p = re.sub(r'\bj\s+ai\s+add\b', "j'ai ajoute", p, flags=re.IGNORECASE)
    p = re.sub(r'\bj\s+ai\s+fix\b', "j'ai corrige", p, flags=re.IGNORECASE)
    
    return p

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
        
    phrase_intermediaire = " ".join(mots_corriges)
    phrase_finale = corriger_grammaire_phrase(phrase_intermediaire)
    
    if a_change or phrase_finale.lower() != texte.lower():
        return {
            "texte_original": texte,
            "texte_corrige": phrase_finale
        }
        
    return None
