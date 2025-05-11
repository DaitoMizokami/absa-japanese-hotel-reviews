#!/usr/bin/env python3
# =============================================================
#  add_ids.py
#
#  Append a 22‑character URL‑safe unique ID to each row of a CSV.
#  衝突確率は 2^-128 と極めて低いため、研究用データセット間でも
#  実質的に重複しません。ファイル内で既に ID があれば空セルのみ補完します。
#
#  使い方:
#      python add_ids.py input.csv
#      python add_ids.py input.csv -o output.csv --id-col uid --encoding cp932
# =============================================================

import argparse
import os
import secrets
import sys
import pandas as pd

# --- デフォルト設定 -------------------------------------------------------
DEFAULT_ENCODING = "cp932"
DEFAULT_ID_COL   = "review_id"     # 追加・補完する列名
# -------------------------------------------------------------------------

def generate_id(existing: set[str]) -> str:
    """Generate a 22‑char ID not in *existing*."""
    while True:
        uid = secrets.token_urlsafe(16)     # 16 bytes → 22 chars
        if uid not in existing:
            return uid

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Add unique IDs to a CSV (日本語コメント参照)")
    parser.add_argument("input", help="入力 CSV ファイル")
    parser.add_argument("-o", "--output",
                        help="出力 CSV (省略時 input_with_id.csv)")
    parser.add_argument("--id-col", default=DEFAULT_ID_COL,
                        help=f"ID 列名 (既定: {DEFAULT_ID_COL})")
    parser.add_argument("--encoding", default=DEFAULT_ENCODING,
                        help=f"文字コード (既定: {DEFAULT_ENCODING})")
    args = parser.parse_args()

    infile  = args.input
    outfile = args.output or os.path.splitext(infile)[0] + "_with_id.csv"
    id_col  = args.id_col
    enc     = args.encoding

    # --- CSV 読み込み ------------------------------------------------------
    try:
        df = pd.read_csv(infile, encoding=enc)
    except FileNotFoundError:
        sys.exit(f"[ERROR] ファイルが見つかりません: {infile}")
    except UnicodeDecodeError as e:
        sys.exit(f"[ERROR] 文字コードエラー: {e}")

    # --- 既存 ID の取得 ----------------------------------------------------
    if id_col in df.columns:
        used = set(df[id_col].dropna().astype(str))
    else:
        used = set()
        df[id_col] = ""                      # 新規列を追加

    # --- ID 付与 -----------------------------------------------------------
    for idx, val in df[id_col].items():
        if pd.isna(val) or val == "":
            uid = generate_id(used)
            df.at[idx, id_col] = uid
            used.add(uid)

    # 二重チェック（理論上発生しないが念のため）
    if df[id_col].duplicated().any():
        sys.exit("[ERROR] 生成後に重複 ID が検出されました。")

    # --- 保存 --------------------------------------------------------------
    df.to_csv(outfile, index=False, encoding=enc)
    print(f"[OK] {len(df)} 件を書き込み: {outfile}")

if __name__ == "__main__":
    main()
