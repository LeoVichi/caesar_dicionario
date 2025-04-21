import openai
import os
import json
import time

CACHE_FILE = "trad_cache.json"
cache = {}

if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        try:
            cache = json.load(f)
        except json.JSONDecodeError:
            cache = {}

openai.api_key = os.getenv("OPENAI_API_KEY")

def traduzir_definicao(definicao_ingles):
    if definicao_ingles in cache:
        return cache[definicao_ingles]

    prompt = (
        "Traduza para o português o texto abaixo, mantendo termos técnicos em latim, "
        "como ablativo, acusativo, genitivo etc., e sem alterar o conteúdo semântico. "
        "Se a definição parecer truncada, corrija o sentido:\n\n"
        f"{definicao_ingles}"
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=500,
        )
        traducao = response.choices[0].message['content'].strip()
    except Exception as e:
        print(f"[⚠️ ERRO GPT]: {e}")
        traducao = definicao_ingles + " [ERRO AO TRADUZIR]"

    cache[definicao_ingles] = traducao
    salvar_cache()
    time.sleep(1.5)

    return traducao

def salvar_cache():
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[⚠️ ERRO AO SALVAR CACHE]: {e}")
