from spellchecker import SpellChecker

# spellchecker francais officiel
spell = SpellChecker(language="fr")

# liste des mots gaming / dev a ne jamais corriger
IGNORED_WORDS = {
    "osu", "ezio", "roblox", "discord", "steam", "valorant", "minecraft",
    "git", "github", "commit", "push", "pull", "add", "fix", "wip", "merge",
    "aywen", "root", "professeur", "python", "dev", "bug", "bugs", "fps", "tk"
}

def clean_word(w):
    # vire la ponctuation autour du mot
    return w.lower().strip(".,!?:;\"'()-_/[]{}~`")

def check_sentence_errors(raw_sentence):
    text = raw_sentence.strip()
    if not text or len(text) < 3:
        return None

    words = text.split()
    corrected_list = []
    has_changes = False

    for w in words:
        clean = clean_word(w)
        
        # exclusions : mot avec apostrophe, mot dans la whitelist, mot court ou mot valide dans le dico
        if "'" in w or len(clean) <= 2 or clean in IGNORED_WORDS or clean in spell:
            corrected_list.append(w)
            continue
            
        # tentative de correction
        fix = spell.correction(clean)
        if fix and fix.lower() != clean and len(clean) >= 3:
            # conserve la majuscule si le mot d'origine en avait une
            if w[0].isupper():
                fix = fix.capitalize()
            corrected_list.append(fix)
            has_changes = True
        else:
            corrected_list.append(w)

    rebuilt = " ".join(corrected_list)

    # retourne le diff seulement si le texte a change
    if has_changes and rebuilt.lower() != text.lower():
        return {
            "original_text": text,
            "corrected_text": rebuilt
        }

    return None
