import re
from spellchecker import SpellChecker

spell = SpellChecker(language="fr")

PROTEGES = {
    "osu", "ezio", "roblox", "discord", "steam", "valorant", "minecraft",
    "git", "github", "commit", "push", "pull", "add", "fix", "wip", "merge", "fetch",
    "python", "docker", "linux", "windows", "dev", "bug", "bugs", "root"
}

def corriger_mot(mot):
    m = mot.lower().strip(".,!?:;\"'()-_/")
    if not m or len(m) <= 1 or m in PROTEGES:
        return mot
    
    if m in spell:
        return mot
        
    m_clean = re.sub(r'(.)\1{2,}', r'\1', m)
    if m_clean in spell:
        return m_clean
        
    corrige = spell.correction(m)
    if corrige and corrige.lower() != m:
        return corrige
        
    swap_a = m.replace("q", "a")
    if swap_a in spell:
        return swap_a
        
    corrige_swap = spell.correction(swap_a)
    if corrige_swap and corrige_swap.lower() != swap_a:
        return corrige_swap
        
    return mot

def corriger_grammaire(texte):
    p = texte
    p = re.sub(r'\bcette\s+est\b', "c'est", p, flags=re.IGNORECASE)
    p = re.sub(r'\bc\s+est\b', "c'est", p, flags=re.IGNORECASE)
    p = re.sub(r'\b(sa|sq)\s+va\b', "ça va", p, flags=re.IGNORECASE)
    p = re.sub(r'\b(il|elle|on)\s+doivent\b', r'\1 doit', p, flags=re.IGNORECASE)
    p = re.sub(r'\b(ils|elles)\s+doit\b', r'\1 doivent', p, flags=re.IGNORECASE)
    p = re.sub(r'\bpour\s+corrige\b', "pour corriger", p, flags=re.IGNORECASE)
    p = re.sub(r'\bpour\s+comprend\b', "pour comprendre", p, flags=re.IGNORECASE)
    p = re.sub(r'\bpour\s+analyse\b', "pour analyser", p, flags=re.IGNORECASE)
    p = re.sub(r'\bdoit\s+analyse\b', "doit analyser", p, flags=re.IGNORECASE)
    p = re.sub(r'\bdoit\s+corrige\b', "doit corriger", p, flags=re.IGNORECASE)
    p = re.sub(r'\bla\s+phrase\s+complet\b', "la phrase complete", p, flags=re.IGNORECASE)
    p = re.sub(r'\bune\s+nouvel\b', "une nouvelle", p, flags=re.IGNORECASE)
    p = re.sub(r'\bj\s+ai\s+add\b', "j'ai ajoute", p, flags=re.IGNORECASE)
    return p

def analyser_texte(texte):
    texte = texte.strip()
    if not texte or len(texte) < 3:
        return None
        
    mots = texte.split()
    mots_corriges = []
    a_change = False
    
    for m in mots:
        corrige = corriger_mot(m)
        if corrige.lower() != m.lower():
            a_change = True
        mots_corriges.append(corrige)
        
    phrase = " ".join(mots_corriges)
    phrase_finale = corriger_grammaire(phrase)
    
    if a_change or phrase_finale.lower() != texte.lower():
        return {
            "texte_original": texte,
            "texte_corrige": phrase_finale
        }
        
    return None
