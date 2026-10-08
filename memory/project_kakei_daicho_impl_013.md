---
name: project_kakei_daicho_impl_013
description: 家計台帳の実装担当側から見た 013〜015（受け取った人・世帯作成）の現在地。統合側セッションの記録（project_kakei_daicho）とは別ファイルにしている
metadata:
  type: project
---

★統合側セッションが [[project_kakei_daicho]] を「触らないで」に入れているため、実装担当側の現在地はこちらに書く。

- ★リポジトリが★移った：`~/Downloads/家計台帳/kakei-daicho`（旧 `~/Downloads/kakei-daicho` は無い）。HEAD＝839974f（M10）
- 10/8 12時台に実測（開発用DB・読むだけ）：
  - 013〜015は★適用済み。表＝persons／household_persons、households に kind 列
  - 関数＝create_customer_household(p_name, p_person_ids, p_primary_person_id, p_primary_fp_id)／assign_person_fp(p_person_id, p_fp_id)／upsert_person_from_crm、ビュー crm_results
  - ★persons も household_persons も0件。38件は削除済みで、架空の2件も削除済み
- 型は開発用から作り直した（36,759→40,951B）。tsc は通り、テストは92件すべて合格
- 🔴★設計担当の実装指示文（013〜015）が★実装側に届いていない。統合側のセッションには届いていて、要点だけが [[project_kakei_daicho]] §「2026-10-08 家計台帳側の実装指示」にある。★画面は全文を受け取ってから作る
- 統合側から、テスト用の架空10件（C-0903〜C-0912・担当は田村3／松本3／空4）を送る提案が来ている。道具は mini の `~/.vivid-relay/_testpersons.py`。★開発用に松本秋紀のFPアカウントは無い＝松本の3件も assigned=false になる
