#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
~/.claude/settings.json を固める ── 有璽氏が1回叩くための1手スクリプト

なぜ要るか（2026-08-29 ビビの依頼③・センゴク「穴E」指摘）
  承認6種のうち「規範の変更」「お金」の2つが settings.json の ask に無く無防備だった。
  AIからは settings.json を書き換えられない（Edit/Bash 両方で権限拒否を実測済み）。
  ＝ 人が1回叩けば済む形にしてある。

やること（--run を付けたときだけ実行。既定はドライラン）
  ① 現在の settings.json をバックアップ（同ディレクトリへタイムスタンプ付き）
  ② permissions.ask へ、以下のパターンを「無ければ」追加する
       Edit(.claude/skills/**)     ── 規範・Skillの編集をask化（fukuchi-core含む・穴E対応）
       Write(.claude/skills/**)    ── 同上・新規作成側
  ③ 「お金」に該当する既存ツールは実測で0件だった（下記docstring参照）。
     追加しない。無理に埋めない。
  ④ 変更前後で allow/deny の件数・中身が完全一致することを検証してから書き込む
     （想定外の変化があれば中止し、バックアップを消さずに終了する）
  ⑤ 追加後の ask 配列を表示する

「お金」の実測（2026-08-29 ピタゴラス）
  ~/.claude/settings.json の permissions.allow 59件を全数走査し、
  課金・契約・発注に類するキーワード（pay/charge/stripe/invoice/購入/課金/契約/発注/billing）
  を含むツールが無いか調べた。★該当0件。
  現状のツール一覧（Notion/Slack/Gmail/Drive/Calendar/Figma/Canva/Gamma/Bash 等）には
  課金・契約・発注を直接実行するものが無い。Bash経由でAPI課金操作をする余地は理論上あるが、
  Bash は汎用コマンドで個別パターン化できない（ask に置くと通常のBash作業まで巻き込む）。
  → 「お金」の ask 追加は見送る。将来、課金APIを叩くツール/MCPを新規に足す際は、
    その時点でこのスクリプトへ1行足すこと。

★sandbox.filesystem.denyWrite について（実測済み・未実装のまま報告）
  クローバー博士の調査を受け、~/.vivid-relay/scratchpad 配下で実測した。
    sandbox.enabled=true + filesystem.denyWrite=[絶対パス] を設定した一時 settings.json で
    新規 claude プロセスを起動し、対象パスへの Bash 書き込み（echo > file）が
    「operation not permitted」でOSレベル（macOS Seatbelt）に拒否されることを確認した。
  ★このスクリプトでは sandbox.enabled は変更しない。理由：
    sandbox.enabled=true は Bash 全体をサンドボックス化し、ネットワーク許可リスト
    （network.allowedDomains）等、影響範囲が広い。bin/への書き込み・git操作・
    ~/.vivid-relay/ への配布など既存の運用フローへの影響を、このセッションでは
    十分に検証しきれなかった（子プロセスでの検証中、意図しない副作用が実際に発生した
    ＝ 新規claudeプロセスがcwdを無視して本物の vivid-ai-hq/memory へ書き込んだ）。
    sandbox.enabled=true 化は次回、影響範囲を洗い出したうえで別途提案する。

使い方
  python3 bin/settings_harden_norms.py            ドライラン（何も書かない。差分だけ表示）
  python3 bin/settings_harden_norms.py --run       実際に書き込む
"""
import json
import os
import shutil
import sys
import time

SETTINGS = os.path.expanduser('~/.claude/settings.json')

# ★2026-08-29 実測できていない点：Edit(...)/Write(...) の ** グロブが実際に
#   Claude Code のマッチャーで機能するかは未検証（公式ドキュメントの例は
#   "Edit(.claude)"「ディレクトリ名のみ」と "Edit(//etc/*)"「絶対パス+単一*」の2例のみで、
#   相対パス+** の例が無い）。構文が効かない場合に備え、具体的ファイルパスも併記して
#   リスクを分散する（依頼元の③要件＝fukuchi-core/SKILL.md個別と、穴E＝skills/全体の両方）。
#   ★書き込み後、有璽氏かビビが /hooks か実際の編集操作で「本当にaskが出るか」を
#   1回確認すること。効かないパターンが判明したら、このリストから削って正しい構文へ直す。
NEW_ASK_ITEMS = [
    'Edit(.claude/skills/**)',
    'Write(.claude/skills/**)',
    'Edit(.claude/skills/fukuchi-core/SKILL.md)',
    'Write(.claude/skills/fukuchi-core/SKILL.md)',
]


def main():
    run = '--run' in sys.argv

    if not os.path.exists(SETTINGS):
        print('★中止：settings.json が見当たりません: %s' % SETTINGS)
        sys.exit(1)

    try:
        raw = open(SETTINGS, encoding='utf-8').read()
        before = json.loads(raw)
    except Exception as e:
        print('★中止：settings.json の読み込み・パースに失敗しました: %s' % e)
        sys.exit(1)

    # ★想定外の形式なら中止する
    perms = before.get('permissions')
    if not isinstance(perms, dict):
        print('★中止：permissions がオブジェクトではありません（想定外の形式）。')
        sys.exit(1)
    allow_before = perms.get('allow', [])
    deny_before = perms.get('deny', [])
    ask_before = perms.get('ask', [])
    if not isinstance(allow_before, list) or not isinstance(deny_before, list) \
            or not isinstance(ask_before, list):
        print('★中止：allow/deny/ask が配列ではありません（想定外の形式）。')
        sys.exit(1)

    to_add = [item for item in NEW_ASK_ITEMS if item not in ask_before]

    print('現在の ask 件数: %d' % len(ask_before))
    print('追加候補: %s' % (to_add or '（すでに全て入っている・追加なし）'))
    print('「お金」の追加: 見送り（実測0件。docstring参照）')

    if not to_add:
        print('やることがありません。終了します。')
        return

    if not run:
        print('\n（ドライラン。実際に書き込むには --run を付けてください）')
        return

    # ① バックアップ
    ts = time.strftime('%Y%m%d-%H%M%S')
    backup_path = SETTINGS + '.backup_%s' % ts
    shutil.copy2(SETTINGS, backup_path)
    print('バックアップ: %s' % backup_path)

    # ② 追加
    after = json.loads(raw)  # 生のJSONを再パースし、他キーを一切触らない
    after['permissions']['ask'] = ask_before + to_add

    # ④ allow/deny が変わっていないことを検証
    allow_after = after['permissions'].get('allow', [])
    deny_after = after['permissions'].get('deny', [])
    if allow_after != allow_before or deny_after != deny_before:
        print('★中止：allow/deny が変化しています（想定外）。書き込みません。')
        print('バックアップは %s に残っています。' % backup_path)
        sys.exit(1)

    # 他のトップレベルキー（hooks等）も一切変えていないことを検証
    for key in before:
        if key == 'permissions':
            continue
        if before.get(key) != after.get(key):
            print('★中止：permissions 以外のキー "%s" が変化しています（想定外）。' % key)
            print('バックアップは %s に残っています。' % backup_path)
            sys.exit(1)

    with open(SETTINGS, 'w', encoding='utf-8') as f:
        json.dump(after, f, ensure_ascii=False, indent=2)
        f.write('\n')

    print('★書き込み完了。')
    print('追加後の ask (%d件):' % len(after['permissions']['ask']))
    for item in after['permissions']['ask']:
        print('  - %s' % item)


if __name__ == '__main__':
    main()
