from spellchecker import SpellChecker

# Instance spellchecker configuree sur le dictionnaire francais
fr_spell = SpellChecker(language="fr")

# Whitelist de pseudos, jeux et termes tech a preserver imperativement
# (pour eviter les faux positifs sur discord / gaming)
WHITELIST_TOKENS = {
    "osu", "ezio", "roblox", "discord", "steam", "valorant", "minecraft",
    "git", "github", "commit", "push", "pull", "add", "fix", "wip", "merge", "fetch",
    "python", "docker", "linux", "windows", "dev", "bug", "bugs", "root"
}

def check_sentence_errors(raw_input_text):
    text = raw_input_text.strip()
    if not text or len(text) < 3:
        return None

    words_list = text.split()
    corrected_tokens = []
    has_modifications = False

    for token in words_list:
        # Nettoyage de la ponctuation autour du mot pour l'analyse lexicale
        clean_word = token.lower().strip(".,!?:;\"'()-_/")
        
        # Conditions d'exclusion : mot avec apostrophe, mot whitelist, mot court ou deja correct
        if "'" in token or clean_word in WHITELIST_TOKENS or clean_word in fr_spell or len(clean_word) <= 2:
            corrected_tokens.append(token)
        else:
            suggested_fix = fr_spell.correction(clean_word)
            if suggested_fix and len(clean_word) >= 3 and suggested_fix.lower() != clean_word:
                corrected_tokens.append(suggested_fix)
                has_modifications = True
            else:
                corrected_tokens.append(token)

    final_sentence = " ".join(corrected_tokens)

    # Si une faute a ete corrigee, on renvoie les deux versions pour l'anim de Root
    if has_modifications and final_sentence.lower() != text.lower():
        return {
            "original_text": text,
            "corrected_text": final_sentence
        }

    return None
