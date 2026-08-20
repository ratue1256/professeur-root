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

    mots = texte.split()
    mots_c = []
    
    for m in mots:
        clean = m.lower().strip(".,!?:;\"'()-_/")
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
