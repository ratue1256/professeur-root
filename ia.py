import re
from spellchecker import SpellChecker

# correcteur francais base sur pyspellchecker
spell = SpellChecker(language="fr")

# liste des mots a surtout pas toucher (jeux, jargon dev, pseudos hackathon)
CUSTOM_IGNORED = {
    "osu", "ezio", "roblox", "discord", "steam", "valorant", "minecraft",
    "git", "github", "commit", "push", "pull", "add", "fix", "wip", "merge",
    "aywen", "root", "professeur", "python", "dev", "bug", "bugs", "linux", "win"
}

def clean_token(w):
    return w.lower().strip(".,!?:;\"'()-_/[]{}~`")

def check_sentence_errors(raw):
    raw = raw.strip()
    if not raw or len(raw) < 3:
        return None

    words = raw.split()
    fixed_words = []
    has_typo = False

    for w in words:
        c = clean_token(w)
        
        # regles de bypass rapides : mot avec apostrophe, mot court, whitelist ou mot valide
        if "'" in w or len(c) <= 2 or c in CUSTOM_IGNORED or c in spell:
            fixed_words.append(w)
            continue
            
        # suggestion du dico
        cand = spell.correction(c)
        if cand and cand.lower() != c and len(c) >= 3:
            # garde la casse originale si majuscule au debut
            if w[0].isupper():
                cand = cand.capitalize()
            fixed_words.append(cand)
            has_typo = True
        else:
            fixed_words.append(w)

    reconstructed = " ".join(fixed_words)

    # on ne trigger Root que si le texte change vraiment
    if has_typo and reconstructed.lower() != raw.lower():
        return {
            "original_text": raw,
            "corrected_text": reconstructed
        }

    return None
