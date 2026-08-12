---
name: reference_shared_drive_permission_floor
description: 共有ドライブ内はサブフォルダを作っても閲覧範囲を狭められない。機微の隔離は「別の共有ドライブへ出す」しか効かない
metadata: 
  node_type: memory
  type: reference
  originSessionId: 72d12c17-4bf6-4c52-9291-4421d31f8dab
  modified: 2026-08-02T23:49:11.703Z
---

**共有ドライブのメンバー権限は配下の全ファイル・全フォルダに継承され、個別アイテムで「継承された権限を外す」ことはできない。** 追加（メンバー外への共有）は可能だが、削除は不可。

つまり共有ドライブの中に `_機微` サブフォルダを作っても、**そのドライブのメンバー全員が中を見られる**。見た目だけの隔離になる。

[[feedback_confidential_two_layer_rule]] の `_機微` サブフォルダ方式は**マイドライブ（17分類の本棚）向けに設計したもの**で、共有ドライブには構造的に当てはまらない。共有ドライブ上の機微を隔離するには、

```plain text
案a  メンバーを絞った別の共有ドライブを新設して移す   ← 組織資産のまま残る。推奨
案b  個人のマイドライブの `_機微` へ移す              ← 所有が個人になり引き継ぎが効かない
```

判定の手がかり：Drive APIの permissions で `role: "organizer"` が返るアイテムは共有ドライブ配下。親を辿って `0A` で始まるIDに到達したら、それが共有ドライブのルート。

関連: [[feedback_confidential_two_layer_rule]] [[project_sales_pipeline_workbook]] [[project_downloads_archive_system]]
