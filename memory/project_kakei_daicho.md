---
name: project_kakei_daicho
description: 家計台帳（FP向け・Next.js＋Supabase）の実装。M2まで有璽氏の確認済み・M4まで確認済み・M5着手。マイルストーンごとにcommit
metadata:
  type: project
---

家計台帳（株式会社ビビッド・FPが担当世帯の家計を入力し、顧客は閲覧のみ）を Next.js で実装している。
置き場は `~/Downloads/kakei-daicho`（**独立した git リポジトリ・リモート無し**。vivid-ai-hq とは別）。作業指示の正本は同フォルダの `CLAUDE.md`。

**現在地（2026-09-30）**
- M1（基盤・ログイン・二段階認証・役割振り分け）… 有璽氏が管理者で確認済み
- M2（世帯一覧・世帯詳細5タブ・予定・閲覧記録）… 有璽氏が実データ【テスト】3世帯で確認「問題ない」
- M3（ヒアリング編集）… 有璽氏が管理者で実データ確認済み（確定・一覧/推移への反映・破棄）。commit 済み
- M4（顧客画面と招待）… 有璽氏が実メールで確認済み（招待→パスワード設定→閲覧のみ）。commit 済み
- M5（管理者機能と仕上げ）… **着手（2026-09-30 有璽氏の指示）**。始める前に型を再生成
- **顧客名の編集の方針（2026-09-30 有璽氏決定）**
  - 招待時：『お名前』欄 → `inviteUserByEmail` の `options.data = { display_name }`。DBのアカウント作成の仕組みが profiles.display_name へ入れる＝**アプリから profiles を更新しない**
  - 招待後の修正：RPC `set_client_display_name(p_user_id, p_display_name)`。管理者と、その顧客が閲覧する世帯の担当FP（主・副）だけ。対象は顧客のみ・前後空白を除き1〜50文字。権限なし 42501／入力不正 22023。世帯詳細『顧客の閲覧』の各行に『名前を編集』
  - 管理者画面：FP・管理者を含む全利用者の表示名は profiles の直接更新（管理者はRLSで許可済み）招待を受けた人のパスワード設定画面（/auth/accept）も作る。★Resend（招待メール送信）は未設定＝メール到達の確認は後回し（それまで Supabase 組織のメンバー宛てにしか届かない）。★「〇〇さんが編集中です」は他アカウントの下書きが無く未確認

**有璽氏の決まり（2026-09-30）**
- **マイルストーンごとにコミットする。** 最初のコミット `8beae5e` = M2完了時点／M3完了も commit 済み
- **`.env.local` は必ず除外**（`.gitignore` の `.env*`。コミット前に秘密鍵の値が入っていないか `git grep --cached` で確かめる）

**踏んだこと・決めたこと**
- 招待の戻り先 `/auth/accept` は Redirect URLs に登録済み（2026-09-30 有璽氏）
- **Resend の SMTP と日本語の招待テンプレートは設定済み**（2026-09-30 有璽氏）。リンクは `{{ .SiteURL }}/auth/accept?token_hash={{ .TokenHash }}&type=invite`＝アプリの redirectTo ではなく **Site URL** が行き先を決める（ローカル確認時は Site URL が localhost か要注意）
- **accepted_at はDBのトリガーが本人確認の時点で自動記録する。アプリから更新しない**（顧客に書き込み手段を持たせない原則とも一致）
- 招待リンクの形は3通り受ける（#access_token／?token_hash&type／?code）。ブラウザ出力に `inviteUserByEmail` の文字が1件あるのは supabase-js 本体のコード（秘密鍵なしでは使えない）で、自前の招待処理はサーバー側だけ
- **Node 22 に固定**（`.nvmrc`・engines）。最新の supabase-js は Node 22 以上が必要で、Node 20 ではサーバー用クライアントを作る時点で落ちる（WebSocket が無い）。Mac の既定 Node は 20 のまま＝作業前に `nvm use`
- **ESLint は 9 系**。eslint-plugin-react / import / jsx-a11y が 10 未対応
- 雛形コマンド（create-next-app）と Supabase の型生成は、AI 側からは権限で止まる。型は有璽氏が `npx supabase login` → `npm run gen:types` で生成した
- Next.js 16 では middleware が `proxy.ts` に改名されている
- AI は二段階認証を通れないので実データの画面は確認できない。代わりに試作品 `docs/prototype-v0.2.html` の世帯データを部品へ流して描画し、試作品自身の計算と突き合わせた（計算13項目・期日8件一致）

**Why:** マイルストーンごとの停止は CLAUDE.md の明文の決まり。Node の版は次のセッションが再び踏む。
**How to apply:** 再開時は `CLAUDE.md` を読み、`nvm use` してから。M3 は有璽氏の指示を受けてから着手する。
