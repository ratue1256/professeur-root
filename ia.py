from spellchecker import SpellChecker

# dico fr pour chopper les fautes
spell = SpellChecker(language="fr")

def clean_word(w):
    # vire la ponctuation qui traine autour
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
        
        # si y a une apostrophe, mot trop court ou si le mot existe dans le dico on touche pas
        if "'" in w or len(clean) <= 2 or clean in spell:
            corrected_list.append(w)
            continue
            
        # check avec le dico
        fix = spell.correction(clean)
        if fix and fix.lower() != clean and len(clean) >= 3:
            # remet la majuscule si y en avait une
            if w[0].isupper():
                fix = fix.capitalize()
            corrected_list.append(fix)
            has_changes = True
        else:
            corrected_list.append(w)

    rebuilt = " ".join(corrected_list)

    # renvoie la faute seulement si y a eu un vrai changement
    if has_changes and rebuilt.lower() != text.lower():
        return {
            "original_text": text,
            "corrected_text": rebuilt
        }

    return None
