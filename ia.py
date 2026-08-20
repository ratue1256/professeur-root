import os
import threading
import unicodedata
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

ia_prete = False
tokenizer = None
model = None
device = "cuda" if torch.cuda.is_available() else "cpu"

def sans_accents(t):
    return "".join(c for c in unicodedata.normalize('NFD', t) if unicodedata.category(c) != 'Mn')

def charger_ia():
    global ia_prete, tokenizer, model
    try:
        model_id = "Qwen/Qwen2.5-0.5B-Instruct"
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            dtype=torch.float16 if device == "cuda" else torch.float32
        ).to(device)
        ia_prete = True
    except Exception:
        pass

thread = threading.Thread(target=charger_ia, daemon=True)
thread.start()

def analyser_texte(texte):
    texte = texte.strip()
    if not texte or len(texte) < 3 or not ia_prete:
        return None

    try:
        prompt = (
            "<|im_start|>system\n"
            "Tu es un correcteur orthographique francais. Tu corriges uniquement les vraies fautes de frappe et de grammaire. "
            "Si la phrase est deja correcte, recopie la a l'identique sans rien changer. "
            "Ne change jamais les pseudos, l'ordre des mots, ni les jeux (osu, ezio, roblox). "
            "Renvoie STRICTEMENT la phrase corrigee sur une ligne.<|im_end|>\n"
            "<|im_start|>user\nbonjout je suis sur mon oridnateur<|im_end|>\n"
            "<|im_start|>assistant\nbonjour je suis sur mon ordinateur<|im_end|>\n"
            "<|im_start|>user\nil doivent analyse la phrase complet<|im_end|>\n"
            "<|im_start|>assistant\nil doit analyser la phrase complete<|im_end|>\n"
            "<|im_start|>user\nje joue a osu avec ezio<|im_end|>\n"
            "<|im_start|>assistant\nje joue a osu avec ezio<|im_end|>\n"
            f"<|im_start|>user\n{texte}<|im_end|>\n"
            "<|im_start|>assistant\n"
        )
        
        inputs = tokenizer(prompt, return_tensors="pt").to(device)
        with torch.no_grad():
            outputs = model.generate(**inputs, max_new_tokens=45, do_sample=False, pad_token_id=tokenizer.eos_token_id)
            
        rep = tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True).strip()
        texte_corrige = rep.split("\n")[0].strip('\"\'')
        
        if texte_corrige.startswith("Voici") or texte_corrige.startswith("Correction"):
            texte_corrige = texte_corrige.split(":")[-1].strip()
            
        if texte_corrige and sans_accents(texte_corrige.lower()) != sans_accents(texte.lower()):
            return {
                "texte_original": texte,
                "texte_corrige": texte_corrige
            }
    except Exception:
        pass
        
    return None
