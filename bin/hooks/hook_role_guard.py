#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
役割違反を機械で止める ── PreToolUse フック

なぜ要るか（2026-08-29 有璽氏・memory/feedback_use_the_team_not_alone.md 2度目）
  > 「そもそもビビ自身が実装するってのがおかしな話だよな。あんたの役割はそうじゃないって
  >  何回も言っとるし。一人でやんなっつってんのもそういうことやな。」
  > 「なんで俺が言われてからしかこの動きをせんねん」
  > 「直後だけなんだよいつもよ。積極的に働きかけるのは。ですぐ忘れる。すぐ忘れていく。」

  同じ日の朝に「担当を並列で走らせる」を守った。その数十分後、検査役が出した指摘を
  ビビが自分の手で直していた。担当へ渡していない。守れたのは指摘された直後だけだった。
  ＝ **規範は毎ターン届いているのに守られなかった。届く ≠ 守る。**
  → [[reference_no_gate_on_asking_the_human]] と同じ形。「探さずに人へ投げる」経路に
    検問が無かったのと同じで、**「ビビが実装コードを書く」経路にも検問が無かった。**

線引き（memory/feedback_use_the_team_not_alone.md より）
  ビビがやってよい      memory ／ WORKING.md ／ 索引 ／ 議題を投げる ／ 束ねる ／ 報告
  ビビがやってはいけない 実装コードの編集・新規作成（.py .js .gs .sh .ts 等）
                        → ピタゴラス（システム）／ステラ配下へ投げる

判定方法（★2026-08-29 実測。公式ドキュメント hooks-guide には agent_id/agent_type の
  記載が無いが、実際の PreToolUse payload には確実に含まれることを実測で確認した）
  agent_id が存在する（truthy）  → Task/Agent 経由で起動されたサブエージェント（担当）＝許可
  agent_id が存在しない          → メインセッション（ビビ）とみなす
  ★メインセッション側で agent_id が本当に欠落するかは、この検問を書いた
    ピタゴラス自身では実測できていない（自分がメインセッションとして動けないため）。
    設計としては「見逃しても実害は誤検知（機能しない）に留まり、逆に誤爆はしない」
    フェイルセーフ側に倒してある。★通し検証はビビか有璽氏が1回行うこと。

対象と止め方
  Write / Edit  file_path の拡張子が実装コード系なら **止める**（exit 2）。
                可逆な操作（保存前で止めるだけ）なので、警告ではなくブロックにした。
                過去に「警告だけ」では規範が繰り返し破られた実績があるため
                （このファイルの動機そのものがその実例）。
  Bash          ヒューリスティックでリダイレクト/teeによる書き込みを検出したら
                **警告に留める**（exit 0 + additionalContext）。シェルコマンドの完全な
                パースはできないため、誤検知（読み取り専用コマンドを誤爆）のリスクが高い。
                ブロックすると「うるさくて読まれなくなる」（reference_delivered_but_unread）
                の型を踏む。

  ★2026-08-29 一度8パターン化してexit2ブロックまで実装・実測したが、撤回した経緯を残す
  （一度踏んだ地雷は個別に直さず記録に落とす、の実例として）。
    試みた内容：redirect/tee 以外に sed/perl -i・dd of=・curl/wget・cp/mv/rsync/install・
    Python open()/pathlib・Node fs.write系の計8パターンを正規表現で検出しexit 2でブロック。
    実測は良好だった（書込16/16検出・読取30/30誤検知ゼロ）が、ビビ経由でクローバー博士の
    調査が入り、**この設計自体が誤りだと判明**：
      ① Claude Code には公式のOSレベル・サンドボックス機能がある
        （settings.json の sandbox.filesystem.denyWrite。macOS=Seatbelt/Linux=seccomp。
        https://code.claude.com/docs/en/sandboxing）。カーネルレベルで拒否するため、
        どんな経路（正規表現で拾えない書き方）で来ても効く。正規表現検出は原理的に
        後追い・不完全にしかなり得ない。
      ② Saltzer & Schroeder (1975) の「ブラックリスト方式（検出型）は原理的に不完全」
        という古典的知見に、今回の実装がそのまま当てはまっていた。
    → **正規表現によるBash検出の強化はやめ、sandbox.filesystem.denyWrite の導入検討へ
      切り替えた**（別スクリプト・別検討。このファイルでは扱わない）。
    → hook_role_guard.py 自体は残す。**役割を分ける**：
      サンドボックス＝OSレベルで書けなくする（防御）
      このフック＝「担当へ渡すべき仕事を自分でやろうとした」という役割判定を伝える（教育）
      Bash側は元の「リダイレクト/tee のみ検出・警告のみ」へ差し戻した。

ログ
  ~/.vivid-relay/role_guard.log に全判定を1行残す（self_audit.py の②観点に使う）。
"""
import json
import os
import re
import sys
import time

LOG = os.path.expanduser('~/.vivid-relay/role_guard.log')

# ★依頼にある「.py .js .gs .sh .ts など」を軸に、実務で使う拡張子を広めに取る。
#   誤爆を避けるため .md .json .yaml .yml .txt .csv .html 等の
#   データ・ドキュメント・設定系は含めない（ビビが memory や設定値を書くのは正当な業務）
CODE_EXTS = {'.py', '.js', '.ts', '.tsx', '.jsx', '.gs', '.sh', '.rb'}

# Bash 経由でコード拡張子ファイルへ書き込む簡易ヒューリスティック
#   例: `cat > foo.py <<EOF` / `echo x >> bar.sh` / `... | tee baz.ts`
#   ★完全なシェルパースはしない。誤検知が出ても警告止まりにして実害を出さない
#   ★2026-08-29 一度8パターン・exit2化を試みたが撤回した（docstring参照）。
#   Bash側の完全な防御は sandbox.filesystem.denyWrite（OSレベル）へ委ねる方針。
BASH_WRITE_PATTERN = re.compile(
    r'(?:>>?|\btee\b)\s+[\'"]?([^\s\'"|;&<>]+\.(?:py|js|ts|tsx|jsx|gs|sh|rb))\b')


def log(verdict, detail=''):
    """★何があっても例外を外に出さない（reference_hooks_enforce_what_discipline_cannot と同じ作法）

    ★2026-08-29 改修（ビビ指摘）：フックの実行と別に手動テストでログへ追記した際、
      date -u を使って前日UTC時刻が混入し、ステラ・ビビ・ピタゴラスの3者が
      「5件」「6行」「5行」と3様に数えて誰の申告とも一致しない事故が起きた
      （実物は7行）。%Z でタイムゾーン名を必ず出すことで、手動追記が別基準の
      時刻を使っても一目で分かるようにする（★根絶ではなく検知しやすくする対策）。"""
    try:
        os.makedirs(os.path.dirname(LOG), exist_ok=True)
        with open(LOG, 'a') as f:
            f.write('%s\t%s\t%s\n' % (time.strftime('%Y-%m-%dT%H:%M:%S %Z'), verdict, detail))
    except Exception:
        pass


def block_message(file_path, tool):
    return (
        '★役割違反：メインセッション（ビビ）は実装コードを直接書けません。\n\n'
        'このターンで %s しようとしたファイル：%s\n\n'
        '規範（memory/feedback_use_the_team_not_alone.md 2026-08-29 2度目）：\n'
        '  ビビがやってよい：memory／WORKING.md／索引／議題を投げる／束ねる／報告\n'
        '  ビビがやってはいけない：実装コードの編集・新規作成（.py .js .gs .sh .ts）\n'
        '  → ピタゴラス（system-developer）／ステラ（dev-producer）配下へ投げる\n\n'
        'このファイルの中身はこのツール呼び出しの引数に既にあります。\n'
        'Agent tool で system-developer（ピタゴラス）か dev-producer（ステラ）へ\n'
        'そのまま渡してください。自分で保存しないでください。\n\n'
        '（有璽氏の明示の指示で、この検査自体を通す必要がある特殊な事情がある場合は、\n'
        '　その理由を1行述べたうえで、ピタゴラス／ステラ経由に切り替えてください。\n'
        '　この検問はバイパス手段を用意していません）'
    ) % (tool, file_path)


def warn_message(file_path):
    return (
        '★注意：Bash 経由で実装コードらしきファイルへ書き込もうとしています（%s）。\n'
        'メインセッション（ビビ）は実装コードを直接書けません '
        '（memory/feedback_use_the_team_not_alone.md）。\n'
        '意図した書き込みなら、Write/Edit ではなく Agent tool で担当へ渡してください。\n'
        '（★このパターン検出は限定的です。完全な防御は sandbox.filesystem.denyWrite '
        '（OSレベル）の導入で検討中。docstring参照）'
    ) % file_path


def main():
    try:
        raw = sys.stdin.read()
        d = json.loads(raw) if raw.strip() else {}
    except Exception:
        print(json.dumps({}))
        return

    agent_id = d.get('agent_id')
    session_id = d.get('session_id', '')
    tool = str(d.get('tool_name', ''))
    inp = d.get('tool_input', {}) or {}

    # ★2026-08-29 改修（ビビ指摘）：ログを見ても「誰の実行か」が分からず
    #   物証として弱いと3者（ステラ・ビビ・ピタゴラス）から指摘された。
    #   agent_id が無い呼び出し（メインセッション判定）でも session_id を残し、
    #   手動テストと本物のイベントを区別できるようにする。
    actor = ('agent_id=%s agent_type=%s' % (agent_id, d.get('agent_type', ''))
             if agent_id else 'メインセッション(agent_idなし) session=%s' % session_id)

    if agent_id:
        # サブエージェント（担当）─ 実装は担当の仕事。何もしない
        log('通した', '%s tool=%s' % (actor, tool))
        print(json.dumps({}))
        return

    if tool in ('Write', 'Edit'):
        file_path = str(inp.get('file_path', ''))
        ext = os.path.splitext(file_path)[1].lower()
        if ext in CODE_EXTS:
            msg = block_message(file_path, tool)
            log('★ブロック', '%s %s %s' % (tool, file_path, actor))
            # ★既存の hook_session_writeback.py と同じ実績パターン（exit 2 + stderr）に
            #   合わせる。JSON の hookSpecificOutput.permissionDecision は
            #   この実装では未検証のため使わない（実測できたものだけを信用する）
            sys.stderr.write(msg + '\n')
            sys.exit(2)
        log('通した', '%s %s（対象拡張子でない） %s' % (tool, file_path, actor))
        print(json.dumps({}))
        return

    if tool == 'Bash':
        command = str(inp.get('command', ''))
        m = BASH_WRITE_PATTERN.search(command)
        if m:
            msg = warn_message(m.group(1))
            log('★警告', 'Bash書込み疑い %s %s' % (m.group(1), actor))
            print(json.dumps({
                'hookSpecificOutput': {
                    'hookEventName': 'PreToolUse',
                    'additionalContext': msg,
                },
                'suppressOutput': True,
            }, ensure_ascii=False))
            return
        print(json.dumps({}))
        return

    print(json.dumps({}))


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        # ★フック自身の失敗でセッションを止めない
        try:
            log('例外', str(e))
        except Exception:
            pass
        print(json.dumps({}))
    sys.exit(0)
