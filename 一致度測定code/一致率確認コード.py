# analyze_agreement_v3.py

import json
from collections import Counter

def load_json_file(filepath):
    """JSONファイルを安全に読み込む関数"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"エラー: ファイルが見つかりません: {filepath}")
        return None
    except json.JSONDecodeError:
        print(f"エラー: {filepath} は正しいJSON形式ではありません。")
        return None

def analyze_and_combine_data(data_a, data_b):
    """二人のアノテーションデータを分析し、統合データを作成する関数"""
    
    data_a_dict = {item['ID']: item for item in data_a if 'ID' in item}
    data_b_dict = {item['ID']: item for item in data_b if 'ID' in item}

    # 一致率分析用のカウンター
    annotator_a_counters = { "triplets": Counter(), "aspects": Counter(), "categories": Counter(), "opinions": Counter() }
    annotator_b_counters = { "triplets": Counter(), "aspects": Counter(), "categories": Counter(), "opinions": Counter() }
    
    # 統合データ保存用の辞書
    combined_data_for_saving = {}

    common_ids = data_a_dict.keys() & data_b_dict.keys()
    for id_ in common_ids:
        record_a = data_a_dict[id_]
        record_b = data_b_dict[id_]

        if record_a.get("Sentence") != record_b.get("Sentence"):
            continue
            
        # 統合データの作成
        combined_data_for_saving[id_] = {
            "sentence": record_a.get("Sentence"),
            "annotator_a": record_a,
            "annotator_b": record_b
        }

        # アノテーション要素数の整合性チェック
        is_record_a_valid = len(record_a.get("Aspect", [])) == len(record_a.get("Category", [])) == len(record_a.get("Opinion", []))
        is_record_b_valid = len(record_b.get("Aspect", [])) == len(record_b.get("Category", [])) == len(record_b.get("Opinion", []))

        if not is_record_a_valid:
            print(f"警告 (アノテーターA, ID: {id_}): 要素数が不整合のため、このIDの分析をスキップします。")
            continue
        if not is_record_b_valid:
            print(f"警告 (アノテーターB, ID: {id_}): 要素数が不整合のため、このIDの分析をスキップします。")
            continue

        # Triplet（タプル）の作成
        triplets_a = [(a, c, o) for a, c, o in zip(record_a["Aspect"], record_a["Category"], record_a["Opinion"])]
        triplets_b = [(a, c, o) for a, c, o in zip(record_b["Aspect"], record_b["Category"], record_b["Opinion"])]

        # カウンターの更新
        annotator_a_counters["triplets"].update(triplets_a)
        annotator_a_counters["aspects"].update(record_a["Aspect"])
        annotator_a_counters["categories"].update(record_a["Category"])
        annotator_a_counters["opinions"].update(record_a["Opinion"])

        annotator_b_counters["triplets"].update(triplets_b)
        annotator_b_counters["aspects"].update(record_b["Aspect"])
        annotator_b_counters["categories"].update(record_b["Category"])
        annotator_b_counters["opinions"].update(record_b["Opinion"])

    return annotator_a_counters, annotator_b_counters, combined_data_for_saving


def print_agreement_results(counters_a, counters_b):
    """一致率の計算と結果表示を行う関数"""
    
    def calculate_metrics(counter_a, counter_b):
        total_a = sum(counter_a.values())
        total_b = sum(counter_b.values())
        intersection = counter_a & counter_b
        matches = sum(intersection.values())
        
        dice_rate = (2 * matches) / (total_a + total_b) if (total_a + total_b) > 0 else 0.0
        
        larger_denominator = max(total_a, total_b)
        recall_based_rate = matches / larger_denominator if larger_denominator > 0 else 0.0
        
        return {
            "matches": matches,
            "total_a": total_a,
            "total_b": total_b,
            "dice": dice_rate,
            "recall_based": recall_based_rate
        }

    print("\nアノテーション一致率の計算結果")
    print("="*60)
    
    categories_to_check = {
        "完全一致（Triplet）": "triplets",
        "Aspect": "aspects",
        "Category": "categories",
        "Opinion": "opinions"
    }

    for display_name, key in categories_to_check.items():
        metrics = calculate_metrics(counters_a[key], counters_b[key])
        print(f"■ {display_name}")
        print(f"  - 一致数（実際に含まれていた数）   : {metrics['matches']}")
        print(f"  - アノテーターAの総数（母数）      : {metrics['total_a']}")
        print(f"  - アノテーターBの総数（母数）      : {metrics['total_b']}")
        print(f"  --------------------------------------------------------")
        print(f"  - 方法1: Dice係数（F1スコア）      : {metrics['dice']:.2%}")
        print(f"  - 方法2: 多い方の母数を基準 (再現率): {metrics['recall_based']:.2%}")

        if display_name != "Opinion":
            print("-" * 25)
    print("="*60)


def main():
    """メイン処理"""
    # ユーザーに入力を促す
    file_a_path = input("アノテーターAのファイル名を入力してください: ")
    file_b_path = input("アノテーターBのファイル名を入力してください: ")
    output_path = input("統合データを保存するファイル名を入力してください（例: combined.json）: ")

    # JSONファイルを読み込む
    data_a = load_json_file(file_a_path)
    data_b = load_json_file(file_b_path)

    if data_a is None or data_b is None:
        print("ファイルが読み込めなかったため、処理を中断します。")
        return

    # データの分析と統合
    counters_a, counters_b, combined_data = analyze_and_combine_data(data_a, data_b)
    
    # 統合したデータを新しいJSONファイルとして保存
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(combined_data, f, ensure_ascii=False, indent=4)
        print(f"\n統合データを '{output_path}' に保存しました。")
    except Exception as e:
        print(f"エラー: 統合データのファイル保存に失敗しました。 {e}")

    # 一致率の分析結果を表示
    print_agreement_results(counters_a, counters_b)


if __name__ == '__main__':
    main()