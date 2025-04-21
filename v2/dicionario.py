#!/usr/bin/env python3
import argparse
import os
import json
import re
import unicodedata
from collections import Counter, defaultdict
import pandas as pd
import stanza
from tradutor import traduzir_definicao

# ----------------------------------------------------------------------------
# Frequência de lemas do De Bello Gallico com definições e
# lookup no Lewis & Short e classificação de declinação/conjugação
# ----------------------------------------------------------------------------

def main():
    # CLI: Argumentos
    parser = argparse.ArgumentParser(
        description="Frequência de lemas do De Bello Gallico com definições e classificação"
    )
    parser.add_argument(
        "--no-stopwords", action="store_true",
        help="Remove stopwords latinas do resultado"
    )
    parser.add_argument(
        "--minfreq", type=int, default=5,
        help="Frequência mínima para inclusão"
    )
    args = parser.parse_args()

    # Carrega e limpa texto
    with open("de_bello_gallico.txt", "r", encoding="utf-8") as f:
        texto = f.read()
    def pre_process(text):
        text = re.sub(r"\b[ADFIKLMNOPRUVX]+\.", "", text)
        text = re.sub(r"[^\w\sāēīōūæœ]", " ", text)
        text = re.sub(r"\d+", "", text)
        return re.sub(r"\s{2,}", " ", text).strip()
    texto = pre_process(texto)

    # NLP Stanza
    try:
        stanza.download('la')
    except:
        pass
    nlp = stanza.Pipeline(lang='la', processors='tokenize,mwt,pos,lemma', use_gpu=False)

    print("⏳ Analisando texto...")
    doc = nlp(texto)
    print("✔️ Análise concluída.")

    # Stopwords latinas
    stopwords = {"et","in","de","cum","ad","per","a","ab","ex","sub","sed","ut",
                 "non","autem","nam","ne","nec","vel","enim","atque","quoque",
                 "quod","quia","si","quoniam","dum","postquam","antequam","ubi",
                 "ita","tamen","ergo","inter","contra","propter","super",
                 "is","hic","ille","qui","quae","quis","ut","an","aut",
                 "etiam","igitur","sum","esse","fui","possum","idem",
                 "ipse","quidem","meus","tuus","suus","noster","vester",
                 "se","sui","ego","nos","tu","vos"}

    # Extrai tokens válidos (token, lema, upos)
    raw = []
    for sent in doc.sentences:
        for w in sent.words:
            token = w.text.lower().strip()
            lemma = w.lemma.lower().strip()
            upos = w.upos
            if not lemma or upos in {"PUNCT","SYM","NUM","X"}:
                continue
            if not re.match(r"^[a-zA-Zāēīōūæœ]+$", lemma):
                continue
            if args.no_stopwords and lemma in stopwords:
                continue
            raw.append((token, lemma, upos))

    # Conta frequência por (lemma,upos) e coleta contagem de tokens
    freq = Counter((lemma,upos) for token,lemma,upos in raw)
    token_counts = defaultdict(Counter)
    for token, lemma, upos in raw:
        if freq[(lemma,upos)] >= args.minfreq:
            token_counts[(lemma,upos)][token] += 1

    items = [((lemma,upos), count)
             for (lemma,upos), count in freq.items() if count >= args.minfreq]

    # Diretório do dicionário Lewis & Short
    base = os.path.dirname(os.path.abspath(__file__))
    dic_dir = os.path.join(os.path.dirname(base),
                           "repositoria/latin-dictionary/lewis-short-json-master")

    # Utilitários: normalizar e limpar definições
    def normalize(text):
        return unicodedata.normalize("NFKD", text).encode("ASCII","ignore").decode().lower()
    def clean_def(s):
        return re.sub(r"\b\d{1,4}\b","", s).strip()

    # Lookup no Lewis & Short
    def lookup_ls(lemma):
        norm = normalize(lemma)
        letter = norm[0].upper()
        path = os.path.join(dic_dir, f"ls_{letter}.json")
        if not os.path.exists(path):
            return None, None
        data = json.load(open(path, encoding='utf-8'))
        for ent in data:
            key = ent.get("key","",).lower()
            if norm == key or key.rstrip('0123456789') == norm:
                senses = ent.get("senses", [])
                for s in senses:
                    if isinstance(s, str) and 5 < len(s) < 300:
                        return clean_def(s), ent.get("declension")
                    if isinstance(s, list):
                        for sub in s:
                            if isinstance(sub, str) and 5 < len(sub) < 300:
                                return clean_def(sub), ent.get("declension")
                notes = ent.get("main_notes") or ""
                if notes:
                    return clean_def(notes), ent.get("declension")
        return None, None

    # Sufixos para fallback (NOUN/ADJ apenas)
    SUFFIXES = ["ae","am","as","is","os","orum","um","a"]

    # Monta resultados
    full, missing = [], []
    for (lemma,upos), count in items:
        # escolhe token mais comum
        token = token_counts[(lemma,upos)].most_common(1)[0][0]
        # busca definição e declinação
        definition, decl = lookup_ls(lemma)
        # fallback para substantivos/adjetivos
        if upos in {"NOUN","ADJ"} and not definition:
            for suf in SUFFIXES:
                if lemma.endswith(suf) and len(lemma) > len(suf)+2:
                    cand = lemma[:-len(suf)]
                    def2, decl2 = lookup_ls(cand)
                    if def2:
                        definition, decl = def2, decl2
                        break
        # registra misses
        if not definition:
            missing.append((token, lemma, upos, count))
            definition = "Def. não encontrada"
        full.append((token, lemma, upos, count, decl or "-", definition))

    # Exporta CSV completo
    df_full = pd.DataFrame(full,
        columns=["Token","Lema","POS","Freq","Declinação","Definição"]
    ).sort_values(by="Freq", ascending=False)
    df_full.to_csv(f"lemas_pos_defs{'_sem' if args.no_stopwords else ''}.csv", index=False)

    # Exporta CSV de termos sem definição
    if missing:
        df_miss = pd.DataFrame(missing,
            columns=["Token","Lema","POS","Freq"]
        ).sort_values(by="Freq", ascending=False)
        df_miss.to_csv(f"lemas_sem_defs{'_sem' if args.no_stopwords else ''}.csv", index=False)
        print(f"🔍 {len(missing)}/{len(full)} sem definição após fallback")

    print("✅ Processamento concluído.")

if __name__ == '__main__':
    main()

