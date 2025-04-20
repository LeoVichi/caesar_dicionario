# 📚 Caesar Dicionário do De Bello Gallico – Frequência com Definições Latinas


Este script realiza a análise de frequência de lemas do *De Bello Gallico*, utilizando NLP para Latim com [Stanza](https://stanfordnlp.github.io/stanza) e adiciona definições a partir do dicionário **Lewis & Short**. Ele fornece o token, o lema, frequência, categoria gramatical,  para substantivos e adjetivos fornece a declinação, e a definição extraída do dicionário de **Lewis & Short**.

---

> [!Warning]
> Este código ainda está em desenvolvimento e os resultados podem não ser ideais. Limitações na Base do Dicionário de Latim Lewis & Short geram saídas truncadas para algumas definições.

---

## 📄 Arquivo

- `dicionario.py`: Script principal com análise de lemas, POS tagging e busca de definições.

---

### 1. Clone o repositório:
```bash
git clone https://github.com/LeoVichi/caesar_dicionario
cd caesar_dicionario
```

### 2. Crie e ative um ambiente virtual Python:
```bash
python -m venv .venv
source .venv/bin/activate

---

## 🛠️ Requisitos

Instale as dependências com:

```bash
pip install -r requirements.txt
```

---

## 📁 Pré-requisitos

Clone o repositório com os arquivos JSON do dicionário Lewis & Short:

```bash
mkdir repositoria
cd repositoria
git clone https://github.com/IohannesArnold/lewis-short-json
```
Obs.: Se der erro ou não aparecerem as definições, mova a pasta 'repositoria' para o diretório anterior ao 'caesar_dicionario'.

---

## 🧪 Uso

```bash
python dicionario.py [--no-stopwords] [--minfreq 5]
```

### Argumentos opcionais:

- `--no-stopwords`: Remove stopwords latinas.
- `--minfreq`: Frequência mínima de ocorrência (padrão: 5).

---

## 📦 Saídas

- `lemas_pos_defs.csv`: Lemas anotados com POS, declinação/conjugação e definição.
- `lemas_sem_defs.csv`: Lista dos lemas que não tiveram definição localizada (fallback incluído).

---

## 🔎 Exemplo

```bash
python dicionario.py --no-stopwords --minfreq 10
```

---

## 🧑‍💻 Autor

**Leonardo Vichi**  
Desenvolvido por [Leonardo Vichi](https://github.com/LeoVichi) para atividade de Estágio Pós-Doutoral junto ao Programa de Pós-Graduação em Letras Clássicas da Universidade Federal do Rio de Janeiro - PPGLC/UFRJ.

---

## ⚖️ Licença

Distribuído sob a licença [MIT](https://opensource.org/licenses/MIT).
