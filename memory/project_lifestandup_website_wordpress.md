---
name: project_lifestandup_website_wordpress
description: LIFE STAND UP のウェブサイトはSTUDIOでなくWordPressで作る。デザインは完成済みでHTMLをアップロードする方針。実物はDriveのClaudeProject配下
metadata:
  type: project
---

# LIFE STAND UP ウェブサイト構築（WordPress方針）

**2026-09-03 有璽氏の指示。** 検証を開始した段階で、方式はまだ確定していない。

## 有璽氏が示した前提（この日に足された事実）

```
方式        ★STUDIO ではなく WordPress に実装する
デザイン     ★すでにある程度完成している。作り直す対象ではない
渡し方      ★デザインを HTML 形式にしてアップロードさせる形
過去の型     STUDIO のときは Figma 経由で STUDIO に落としていた
            ＝今回は「Figma を経由しない」ことが方針として含まれる
```

**★「デザインは完成している」を軽く扱わない。** 依頼は実装方式の検証であって、
デザインの作り直し・作り足しではない → [[feedback_dont_remake_what_was_approved]]

## 実物の置き場（2026-09-03 実測。パスの実在を確認済み）

有璽氏が渡した Drive リンク `1YJWq21N4ZgC3gAvpwuPb4o4sP040REle` は
**Drive for Desktop のエイリアス**（mimeType `application/drive-fs.osx.alias`）で、
指している実体はフォルダ「Claude ILIFE WEBサイトリニューアル」
（Drive上の実フォルダID `1GVKzwE2DNRKx4M9YALTFBW1knhp4DMs5`）。

```
~/Library/CloudStorage/GoogleDrive-y_tam@vivid-global.com/マイドライブ/
  Downloads書類アーカイブ/01_AI・開発/ClaudeProject LIFE STAND UP/
    Claude ILIFE WEBサイトリニューアル/
      ├ ClaudeDesign v1.0 / v2.0 / v2.1     設計書(md)。v2.1が最新・handover 23本
      ├ ILIFE WEBサイトリニューアル v1.0 / v2.0 / v2.1   成果物HTML
      └ top_page_wireframe.html ほか
```

**v2.1 に18ページ分のHTMLが実在**（top-page / stand-up-top / stand-up-programs /
stand-up-daily-schedule / guide-top / guide-flow / guide-pricing / guide-area / guide-faq /
testimonials / about-ilife / about-staff / about-company / contact / news / privacy-policy /
recruit-top / recruit-interview / recruit-apply / recruit-values）。30KB〜140KB。

## ★最初に確かめる点 ── 既知の地雷

Claudeデザインの書き出しHTMLは **bundler形式**（`<script type="__bundler/manifest">` に
フォントbase64が十数MB、`__bundler/template` に JSONエスケープされた実HTML文字列）で、
**JSで展開するため生ファイルは静的HTMLとして機能しない** ── これは既に実測済みの事実
→ [[project_html_to_figma_pipeline]]

**この形式のままなら「HTMLをアップロードする」は成立しない。** デコードして実HTML/CSSを
取り出す工程が必ず要る。**ここの判定が方式選択の分岐点。**

## ★未確定 ── 有璽氏に確認が要る

- **対象はどこまでか。** 有璽氏は「LIFE STAND UP のサイト」と言ったが、実物のフォルダは
  「ILIFE WEBサイトリニューアル」で、**ILIFE法人サイトと STAND UP（放課後等デイ）の
  両方のページが混在している**。どちらが今回の対象かで工数もドメインも変わる。
- 既存の ILIFE 本体サイト `https://i-life-fukushi.com` は**既にWordPress**
  → [[reference_group_blogs_and_cms]]。新サイトをそこへ載せるのか、別インスタンスか。

## 状態

```
2026-09-03  ビビが実物を特定・リリス(web-developer)へ検証7項目を依頼（走行中）
            台帳・Notion・kintone・サーバへは1文字も書いていない
```

関連 → [[project_orangeworks_portfolio_site]]（こちらはSTUDIO。混同しない）
