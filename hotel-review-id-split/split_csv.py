import pandas as pd
import os

# 入力ファイル名 / Input file name
source_file = "AnnotationTest_with_id.csv"

# 出力先ディレクトリ / Output directory
output_dir = "output_splits"

# 分割単位 / Rows per split file
chunk_size = 50

# 出力ファイル名のプレフィックス / Output file prefix
base_name = "AnnotationSplit_part"

# ディレクトリがなければ作成 / Create directory if not exists
os.makedirs(output_dir, exist_ok=True)

# ファイル読み込み / Load CSV
df = pd.read_csv(source_file, encoding="cp932")

# 列順を明示的に指定 / Reorder columns: ID and text first
priority_cols = ['review_id', 'review_text']
other_cols = [col for col in df.columns if col not in priority_cols]
df = df[priority_cols + other_cols]

# 分割して保存 / Split and save
for i in range(0, len(df), chunk_size):
    chunk = df.iloc[i:i + chunk_size]
    output_file = os.path.join(output_dir, f"{base_name}{i // chunk_size + 1}.csv")
    chunk.to_csv(output_file, index=False, encoding="cp932")
    print(f"{output_file} を保存しました。")
