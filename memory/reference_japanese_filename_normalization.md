---
name: reference_japanese_filename_normalization
description: macOSの日本語ファイル名はNFD（濁点分解）。NFCの文字列で grep / in 判定すると必ず0件になる
metadata:
  type: reference
---

# 日本語ファイル名は正規化しないと必ず0件になる（2026-08-29 実地）

`/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc` は**両機に実在する**。
それを次の2つの方法で探し、**どちらも0件**になった。

```
❌ ls /System/Library/Fonts/ | grep -i 'ヒラギノ角ゴ'        → 0件
❌ python3 … if 'ヒラギノ' in os.path.basename(f)            → 0件
✅ unicodedata.normalize('NFC', name) を通してから比較        → 10本ヒット
```

**原因** ── macOS のファイル名は **NFD**（`ギ` = `キ` + 濁点の2文字）で保存される。
コード中の文字列リテラルは通常 **NFC**（`ギ` の1文字）。**見た目は同一、バイト列は別物。**
だから「無い」と出る。**エラーは出ない。静かに0件になる。**

## ★これで危うく誤った差し戻しをするところだった

ピタゴラス（system-developer）が「ヒラギノ角ゴシック W0〜W9 を採用。両機に実在」と報告。
ビビが検算したら0件で、**「両機とも存在しない。申告は誤り」と断定しかけた。**
実際は**担当の申告が正しく、検算した側の条件が壊れていた。**

- **★「0件でした」は、条件が壊れている可能性を先に疑う。**（既出の規範 → [[reference_log_needs_an_exit]]）
  **1回疑ったのに、2回目も同じ壊れた条件で数えたのが今回の失敗。**
  疑ったら**別の方法**で数え直す。同じ関数をもう一度呼んでも同じ0が返るだけ。
- **★検算が担当の申告と食い違ったら、まず検算side を疑う。** 担当は実物を見て書いている。
  食い違いは「相手が間違えた」より「こちらの測り方が違う」ほうが多い。
- **★日付・IDと同じで、ファイル名も正規化してから数える。**
  → [[feedback_never_write_an_unmeasured_number]]（norm_date を通した値だけを使う）と同じ型。

## 正しい数え方（両機で実測済み）

```python
import unicodedata, glob, os
def name_has(path, kw):
    b = unicodedata.normalize('NFC', os.path.basename(path))
    return unicodedata.normalize('NFC', kw) in b
```

シェルで探すなら、日本語を条件にせず**拡張子や場所で絞って全件を Python へ渡す**。

## ついでに確定した事実（両機共通・2026-08-29 実測）

フォントは MacBook 368本／mini 371本、**共通364本**。うち日本語グリフを持つのは **23本**。
主なもの ── `ヒラギノ角ゴシック W0〜W9.ttc`（ウェイト別に独立ファイル・**両機に在る**）／
`ヒラギノ明朝 ProN.ttc`／`ヒラギノ丸ゴ ProN W4.ttc`／`Arial Unicode.ttf`／`Hiragino Sans GB.ttc`。
**Noto Sans CJK は両機に無い。** macOS は MacBook 14.6.1 ／ mini 26.5.2 で**版が違う**。

関連 → [[project_event_skills_suite]]（snspipe.py の FONT_DIR が Linux 決め打ちだった件）
