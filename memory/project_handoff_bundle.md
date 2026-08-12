---
name: project-handoff-bundle
description: "This working directory is a Claude Design (Claudesign) handoff bundle for the ふくち。group umbrella site (vivid-global rebrand). Static HTML + shared.css, no build step."
metadata: 
  node_type: memory
  type: project
  originSessionId: 592209ce-4f2a-490a-940d-506c96fe4a57
---

`/Users/yujimac/Downloads/サイト改修2026/ビビッドグループポータルサイトv2.0 (Remix)/` は Claude Design からのハンドオフ・バンドル。「ふくち。」（旧ビビッドグループ）のアンブレラサイト v2.0 リミックス版。

**Why:** 大阪府を本拠とする福祉事業グループ（株式会社ビビッド／ILIFE／SWELLSOCIETY）を「ふくち。」アンブレラブランドへ統合するリブランド・サイト改修プロジェクト。toB経営者層を主軸、福祉×お金リテラシーがコアコンセプト。元サイトは vivid-global.com。投入用プロンプトは uploads/ふくち。グループ_Claudesign投入用プロンプト_v1.0.md 参照。

**How to apply:**
- 静的HTML群（日本語ファイル名）＋ `shared.css` の素朴な構成。ビルドステップなし
- 一部ファイル名に全角スラッシュ ／ (U+FF0F) を含む（例: `for You／当事者向け.html`）— 通常のスラッシュではないので注意
- ローカル確認は `python3 -m http.server 8000 --bind 127.0.0.1` をディレクトリ直下で実行、`index.html`（ローカル確認用に追加）から各ページに遷移
- 2026-05-21時点でリンク切れだった for You 配下3ページ（当事者向け／ご家族向け／福祉従事者向け）は暫定スタブで埋めた。本実装で差し替え予定
- トップページは `トップページ.html`（旧）と `トップページ v2.html`（新／latest）が併存
- トップ2種ともグローバルナビは内部アンカー（#about など）のみで他ページへのリンク未配線
