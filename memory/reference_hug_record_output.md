---
name: reference_hug_record_output
description: HUG（STAND UPの療育システム）から「利用者の様子」を期間×利用者で出す入口と、出力がPDFでなくHTML＋印刷ダイアログである事実
metadata:
  type: reference
---

2026-10-20 MacBook の Claude in Chrome で実測（Slack `#sf7f2a3`・有璽氏ログイン済み・読むだけ）。

- **★「利用者の様子」は実績記録票には無い。** `service_record.php?mode=select`（サービス提供実績記録票一括印刷）は日付・時間・加算・保護者確認欄の国保連用の帳票。
- **★様子の入口は「本日の様子一括印刷」** `https://www.hug-ilife.link/hug/wm/contact_book.php?mode=selectComment`
  （サービス提供記録・ケア記録・生活記録の一覧 `contact_book.php` の上のボタン）。
  - 絞り込み：日付の範囲・施設・利用サービス・下書き含む/含まない・保護者コメント表示 → 児童を選んで「印刷」
  - 出る欄：日付／施設／本日の様子／記録者名。期間の絞り込みは効く（9月で出したら9月の行だけ）
  - 2026年9月・STAND UP で 38人
- 「ケア記録・生活記録一括印刷」（`?mode=select`）は別物。1年半の範囲でも6人しか出ない＝STAND UP ではほぼ使っていない。
- **★出力はPDFではない。** 「印刷」は POST で HTML を返し、読み込むと `window.print()` でブラウザの印刷ダイアログが開く。
  ★Chrome 拡張は印刷ダイアログで止まる＝★画面で「印刷」を押さない。同じ POST を `fetch` で送れば HTML を受け取れる（同じログインのまま）。
- PDF にするには、受け取った HTML を手元のヘッドレス Chrome（`--print-to-pdf`）で変換する案。★ダウンロードは有璽氏の許可が要る・置き場は機微。

関連：[[project_gov_filings_drive_structure]]（10/16 に HUG のメニュー名を読んだ記録）

- **★2026-10-20 自動保存は止められた。** HUG の HTML を `fetch` で受けて Blob でダウンロードさせる JS を、Claude Code の自動許可の判定が「個人情報の扱い」で拒否した。
  ★回り道はしない。有璽氏の手で HUG の「印刷」→「PDFに保存」が正規の経路。自動化するなら有璽氏が許可の設定を判断してから。
  ★JS でチェックを入れても「出力人数」は0人のままで「印刷」が押せない＝★チェックは画面上のクリックで入れる。
