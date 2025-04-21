import openai
import os
import json
import time

# Caminho do cache em disco
CACHE_FILE = "trad_cache.json"
cache = {}

# Carrega cache do disco (se existir)
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        try:
            cache = json.load(f)
        except json.JSONDecodeError:
            cache = {}

# Configura chave da API
openai.api_key = os.getenv("OPENAI_API_KEY")

def traduzir_definicao(definicao_ingles):
    """Traduz uma definição do inglês para o português usando a API da OpenAI, com cache."""
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
        print(f"[⚠
