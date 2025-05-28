"""
extract.py

Este script extrai tabelas de um PDF, unifica fragmentos de tabelas distribuídas em várias páginas,
realiza limpeza básica e salva o resultado em CSV.
"""
import tabula
import pandas as pd

# Configurações de entrada
PDF_PATH = "relatorio3.pdf"          # Caminho para o PDF de entrada
OUTPUT_CSV = "Frutiferas.csv"       # Nome do arquivo CSV de saída
PAGES = "1-3"                       # Intervalo de páginas a serem processadas
TABLE_READ_OPTIONS = {
    'multiple_tables': True,        # Extrai todas as tabelas das páginas
    'lattice': True,                # Usa modo lattice para tabelas com grade
    'stream': True,                 # Usa modo stream para tabelas sem linhas definidas
}

# === Extração das tabelas ===
# Ajuste 'pages' e TABLE_READ_OPTIONS conforme o layout do seu PDF
raw_tables = tabula.read_pdf(PDF_PATH, pages=PAGES, **TABLE_READ_OPTIONS)

# === Combinação de fragmentos de tabela ===
# Tabula pode dividir uma tabela única em várias partes. Aqui unimos todas em um DataFrame.
fragments = []
for fragment in raw_tables:
    # Mantém apenas dados não nulos e copia o fragmento
    df_fragment = fragment.dropna(how='all').copy()
    fragments.append(df_fragment)

# Concatena todos os fragmentos em um único DataFrame
combined_df = pd.concat(fragments, ignore_index=True)

# === Limpeza adicional ===
# Remove linhas totalmente vazias e redefine índices
clean_df = combined_df.dropna(how='all').reset_index(drop=True)

# === Exportação ===
clean_df.to_csv(OUTPUT_CSV, index=False, encoding='utf-8-sig')
print(f"Extração concluída. Dados salvos em '{OUTPUT_CSV}'.")
