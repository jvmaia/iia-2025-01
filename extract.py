import tabula
import pandas as pd

# Step 1: Extract tables from PDF
# Note: Adjust 'pages' and 'area' based on your PDF layout
tables = tabula.read_pdf(
    "relatorio3.pdf",
    pages="1-3",  # Pages containing the Major Crops table
    multiple_tables=True,
    lattice=True,  # Use lattice mode for grid-like tables
    stream=True,   # Use stream mode for non-grid tables
)

# Step 2: Clean and merge extracted tables
# (Tabula may split tables across pages; this combines them)
major_crops_data = []
current_header = None

for table in tables:
    df = table.copy()

    # Detect header rows (adjust based on your PDF's structure)
    # if df.iloc[0, 0] == "Localidade / Cultura":
    #     current_header = df.iloc[0].tolist()
    #     df = df[1:]  # Remove header row

    # if current_header is not None:
    #     df.columns = current_header  # Apply consistent headers
    major_crops_data.append(df)

# Combine all fragments into one DataFrame
final_df = pd.concat(major_crops_data, ignore_index=True)

# Step 3: Clean the data
final_df = final_df.dropna(how='all')  # Remove empty rows
final_df = final_df.reset_index(drop=True)

# Step 4: Save to CSV
final_df.to_csv("Frutiferas.csv", index=False, encoding='utf-8-sig')
print("Extraction complete. Saved to 'major_crops.csv'.")