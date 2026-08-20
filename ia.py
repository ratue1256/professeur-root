import re
from spellchecker import SpellChecker

spell = SpellChecker(language="fr")

PROTEGES = {
    "osu", "ezio", "roblox", "discord", "steam", "valorant", "minecraft",
    "git", "github", "commit", "push", "pull", "add", "fix", "wip", "merge", "fetch",
    "python", "docker", "linux", "windows", "dev", "bug", "bugs", "root"
}

def analyser_texte(texte):
    texte = texte.strip()
    if not texte or len(texte) < 3:
        return None

    p = texte
    
    # fautes de frappe et expressions courantes
    p = re.sub(r'\bsqlut\b', "salut", p, flags=re.IGNORECASE)
    p = re.sub(r'\b(je\s+)?mapple\b', "je m'appelle", p, flags=re.IGNORECASE)
    p = re.sub(r'\bcommennnt\b', "comment", p, flags=re.IGNORECASE)
    p = re.sub(r'\bsqcvat\b', "ca va", p, flags=re.IGNORECASE)
    p = re.sub(r'\bj\s+ai\s+add\b', "j'ai ajoute", p, flags=re.IGNORECASE)
    p = re.sub(r'\bj\s+ai\s+fix\b', "j'ai corrige", p, flags=re.IGNORECASE)
    p = re.sub(r'\bcette\s+est\b', "c'est", p, flags=re.IGNORECASE)
    p = re.sub(r'\bc\s+est\b', "c'est", p, flags=re.IGNORECASE)
    p = re.sub(r'\b(sa|sq)\s+va\b', "ça va", p, flags=re.IGNORECASE)
    
    # conjugaison et accords
    p = re.sub(r'\b(il|elle|on)\s+doivent\b', r'\1 doit', p, flags=re.IGNORECASE)
    p = re.sub(r'\b(ils|elles)\s+doit\b', r'\1 doivent', p, flags=re.IGNORECASE)
    p = re.sub(r'\bpour\s+corrige\b', "pour corriger", p, flags=re.IGNORECASE)
    p = re.sub(r'\bpour\s+comprend\b', "pour comprendre", p, flags=re.IGNORECASE)
    p = re.sub(r'\bpour\s+analyse\b', "pour analyser", p, flags=re.IGNORECASE)
    p = re.sub(r'\bdoit\s+analyse\b', "doit analyser", p, flags=re.IGNORECASE)
    p = re.sub(r'\bla\s+phrase\s+complet\b', "la phrase complete", p, flags=re.IGNORECASE)
    p = re.sub(r'\bune\s+nouvel\b', "une nouvelle", p, flags=re.IGNORECASE)
    p = re.sub(r'\bnouvel\s+boucle\b', "nouvelle boucle", p, flags=re.IGNORECASE)
    
    mots = p.split()
    mots_c = []
    for m in mots:
        clean = m.lower().strip(".,!?:;\"()-_/")
        if "'" in clean or clean in PROTEGES or clean in spell or len(clean) <= 2:
            mots_c.append(m)
        else:
            cor = spell.correction(clean)
            if cor and len(clean) >= 4:
                mots_c.append(cor)
            else:
                mots_c.append(m)
                
    resultat = " ".join(mots_c)
    
    if resultat.lower() != texte.lower():
        return {
            "texte_original": texte,
            "texte_corrige": resultat
        }
        
    return None
