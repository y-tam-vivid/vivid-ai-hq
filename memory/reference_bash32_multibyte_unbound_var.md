# bash 3.2(macOS標準)は `$変数` 直後の全角文字を変数名の一部と誤認する

**2026-08-20 実測（`bin/daily_jobs.sh` 作成時）。**

## 症状

```bash
#!/bin/bash
set -u
name="intake_register"
log "起動: $name（定刻 ...）"
```

これを `bash script.sh` で実行すると、
`script.sh: line N: name<不可視バイト>: unbound variable` で落ちる。
**`$name` の直後に全角括弧「（」を置いただけ**で再現する。

## 原因

Mac mini・MacBookとも `/bin/bash --version` は **3.2.57**（Appleが2007年のGPLv3回避以降
バージョンを凍結した標準bash。`brew install bash` の5系とは別物で、スクリプトに
`#!/bin/bash` と書いても呼び出し側が `/bin/bash` を使えばこの3.2が動く）。
この3.2が `set -u` 下で、非ブレース変数展開 `$name` の直後にある全角(マルチバイト)文字を
変数名の続きとして誤って取り込み、存在しない変数として unbound variable を出す。
`${name}` とブレースで区切れば発生しない。

## 対策

**全角文字（句読点・括弧・記号・日本語）が変数展開の直後に来る行は、必ず `${var}` で書く。**
`$var ` のように半角スペースやASCII記号が続く場合は問題ない（今回 `$hhmm $name` は無事だった。
壊れたのは `$name（` `$hhmm・` の2箇所だけ）。

```bash
# 危険（bash 3.2で unbound variable）
echo "起動: $name（定刻 $hhmm・実行時刻）"

# 安全
echo "起動: ${name}（定刻 ${hhmm}・実行時刻）"
```

## 見つけ方

```bash
grep -n '\$[A-Za-z_][A-Za-z_0-9]*[^ -~]' script.sh
```
（`$変数名` の直後にASCII範囲外のバイトが続く行を機械的に洗い出す）

## 影響範囲

`~/vivid-ai-hq/bin/*.sh` を grep した限り、この地雷を踏んでいたのは新規作成した
`daily_jobs.sh` の1箇所のみ（`vivid-sync.sh` / `cron_apply.sh` / `setup_hooks.sh` は無事）。
**ただし今後 mini/MacBook 向けに書く全シェルスクリプトで同じ検査が要る。**
`set -u` を使わなければ症状は出ない（未定義変数扱いにならず空文字として素通りする）だけで、
根本原因（誤ったバイト範囲の識別子解釈）は残るため、`set -u` を外すのは対策にならない。

## 実害

`bin/daily_jobs.sh` の初回実装がこれで即クラッシュしたが、クラッシュ位置がログ出力
（`bash -c "$cmd"` で実ジョブを起動する**前**）だったため、実データへの書き込みは
発生していない。本番の `~/.vivid-relay/daily_jobs_state/` と `intake_register.log` を
突合し実行痕跡ゼロを確認済み。
