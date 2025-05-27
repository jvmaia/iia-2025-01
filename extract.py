'''
arquivo responsavel por extrair as tabelas do pdf e salvar em um csv
'''

import tabula
import pandas as pd

tables = tabula.read_pdf(
    "relatorio3.pdf",
    pages="1-3",
    multiple_tables=True,
    lattice=True,
    stream=True,
)

major_crops_data = []
current_header = None

for table in tables:
    df = table.copy()
    major_crops_data.append(df)

final_df = pd.concat(major_crops_data, ignore_index=True)

final_df = final_df.dropna(how='all')
final_df = final_df.reset_index(drop=True)

final_df.to_csv("Frutiferas.csv", index=False, encoding='utf-8-sig')
print("Extraction complete. Saved to 'major_crops.csv'.")