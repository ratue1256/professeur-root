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
    p = re.sub(r'\bsqlut\b', "salut", p, flags=re.IGNORECASE)
    p = re.sub(r'\b(je\s+)?mapple\b', "je m'appelle", p, flags=re.IGNORECASE)
    p = re.sub(r'\b(je\s+)?m\s+appele\b', "je m'appelle", p, flags=re.IGNORECASE)
    p = re.sub(r'\bcommennnt\b', "comment", p, flags=re.IGNORECASE)
    p = re.sub(r'\bsqcvat\b', "ca va", p, flags=re.IGNORECASE)
    p = re.sub(r'\bj\s+ai\s+add\b', "j'ai ajoute", p, flags=re.IGNORECASE)
    p = re.sub(r'\bj\s+ai\s+fix\b', "j'ai corrige", p, flags=re.IGNORECASE)
    p = re.sub(r'\bj\s+ai\s+push\b', "j'ai push", p, flags=re.IGNORECASE)
    p = re.sub(r'\bcette\s+est\b', "c'est", p, flags=re.IGNORECASE)
    p = re.sub(r'\bc\s+est\b', "c'est", p, flags=re.IGNORECASE)
    p = re.sub(r'\b(sa|sq)\s+va\b', "ça va", p, flags=re.IGNORECASE)
    p = re.sub(r'\b(sa|sq)\s+marche\b', "ça marche", p, flags=re.IGNORECASE)
    
    p = re.sub(r'\b(il|elle|on)\s+doivent\b', r'\1 doit', p, flags=re.IGNORECASE)
    p = re.sub(r'\b(ils|elles)\s+doit\b', r'\1 doivent', p, flags=re.IGNORECASE)
    p = re.sub(r'\b(il|elle|on)\s+peuvent\b', r'\1 peut', p, flags=re.IGNORECASE)
    p = re.sub(r'\b(ils|elles)\s+peut\b', r'\1 peuvent', p, flags=re.IGNORECASE)
    p = re.sub(r'\b(il|elle|on)\s+savent\b', r'\1 sait', p, flags=re.IGNORECASE)
    p = re.sub(r'\b(ils|elles)\s+sait\b', r'\1 savent', p, flags=re.IGNORECASE)
    p = re.sub(r'\b(il|elle|on)\s+veulent\b', r'\1 veut', p, flags=re.IGNORECASE)
    p = re.sub(r'\b(ils|elles)\s+veut\b', r'\1 veulent', p, flags=re.IGNORECASE)
    p = re.sub(r'\b(il|elle|on)\s+font\b', r'\1 fait', p, flags=re.IGNORECASE)
    p = re.sub(r'\b(ils|elles)\s+fait\b', r'\1 font', p, flags=re.IGNORECASE)
    p = re.sub(r'\b(il|elle|on)\s+vont\b', r'\1 va', p, flags=re.IGNORECASE)
    p = re.sub(r'\b(ils|elles)\s+va\b', r'\1 vont', p, flags=re.IGNORECASE)
    
    p = re.sub(r'\bpour\s+corrige\b', "pour corriger", p, flags=re.IGNORECASE)
    p = re.sub(r'\bpour\s+comprend\b', "pour comprendre", p, flags=re.IGNORECASE)
    p = re.sub(r'\bpour\s+analyse\b', "pour analyser", p, flags=re.IGNORECASE)
    p = re.sub(r'\bdoit\s+analyse\b', "doit analyser", p, flags=re.IGNORECASE)
    p = re.sub(r'\bdoit\s+corrige\b', "doit corriger", p, flags=re.IGNORECASE)
    p = re.sub(r'\bdoit\s+comprend\b', "doit comprendre", p, flags=re.IGNORECASE)
    p = re.sub(r'\bdoit\s+aller\b', "doit aller", p, flags=re.IGNORECASE)
    p = re.sub(r'\bpeut\s+analyse\b', "peut analyser", p, flags=re.IGNORECASE)
    p = re.sub(r'\bpeut\s+corrige\b', "peut corriger", p, flags=re.IGNORECASE)
    
    p = re.sub(r'\b(la|une)\s+phrase\s+complet\b', r'\1 phrase complete', p, flags=re.IGNORECASE)
    p = re.sub(r'\b(la|une)\s+phrase\s+entierenre\b', r'\1 phrase entiere', p, flags=re.IGNORECASE)
    p = re.sub(r'\bune\s+nouvel\b', "une nouvelle", p, flags=re.IGNORECASE)
    p = re.sub(r'\bnouvel\s+boucle\b', "nouvelle boucle", p, flags=re.IGNORECASE)
    p = re.sub(r'\bdas\s+l\b', "dans le", p, flags=re.IGNORECASE)
    p = re.sub(r'\bfaired\s+e\b', "faire de", p, flags=re.IGNORECASE)
    p = re.sub(r'\bans\s+faired?\s+e?\b', "sans faire de", p, flags=re.IGNORECASE)
    p = re.sub(r'\bans\s+faire\b', "sans faire", p, flags=re.IGNORECASE)
    
    mots = p.split()
    mots_c = []
    for m in mots:
        clean = m.lower().strip(".,!?:;\"()-_/")
        if "'" in m or clean in PROTEGES or clean in spell or len(clean) <= 2:
            mots_c.append(m)
        else:
            cor = spell.correction(clean)
            if cor and len(clean) >= 3:
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
