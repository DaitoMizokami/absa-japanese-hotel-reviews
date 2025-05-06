import pandas as pd

SRC = "japan_2024_reviews.csv"        # 元ファイル
CHUNK = 1100                          # 行数
OUT_DIR = "."                         # 出力先フォルダ（.＝同じ場所）

df = pd.read_csv(SRC)
for i in range(0, len(df), CHUNK):
    chunk = df.iloc[i:i + CHUNK]
    out_name = f"{OUT_DIR}/Dataset{i // CHUNK + 1}_{len(chunk)}Sentences.csv"
    chunk.to_csv(out_name, index=False, encoding="utf-8-sig")
    print(f"✔ saved {out_name}")
print("Done!")
