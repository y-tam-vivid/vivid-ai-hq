#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskUserQuestion を機械で受け止める ── PreToolUse フック

なぜ要るか（部品の言葉を使わずに）
  「mini で走っている担当が、誰も押せない問いを出して止まる、ということが起こらない」
  ようにするための機械の検問。`claude -p`（非対話）で起動されたセッションが
  AskUserQuestion を呼ぶと、答える人がいないため無言で止まり続ける。これを止める。

  ★2026-09-05 追加事実（ビビ経由・有璽氏の3回目の指摘）：対話セッション（端末のTUI）
  であっても、この2機（MacBook / Mac mini）は `~/.claude/settings.json` の
  `permissions.defaultMode = 'dontAsk'` になっており、AskUserQuestion は端末の
  ダイアログとして出ても押せず拒否される可能性が高い。有璽氏自身の言葉：
    ✕ ターミナルに選択肢の表を書く（端末の前に居る必要がある）
    ✕ AskUserQuestion（端末のダイアログ。don't ask mode で拒否される・端末依存も同じ）
    ◎ ask_hub.ask()（プッシュで届く・押せる・その他は記述で返せる）
  ＝「対話なら正しい道具」という当初の前提はこの2機では成り立たない。
  そのため**対話セッションでも止めはしないが警告は出す**（2段構え）。

判定方法（★ピタゴラス実測済み。数値・observedの部分は推測で変えない）
  CLAUDE_CODE_ENTRYPOINT == 'cli'       → 対話（端末のTUI）        ★通す・ただし警告は出す
  CLAUDE_CODE_ENTRYPOINT が 'sdk-' 始まり → 非対話（claude -p 等）  ★止める（exit 2）
  CLAUDE_CODE_ENTRYPOINT が無い/その他   → 判定不能                ★通す・無言（fail-open）

  実測の根拠：
  経路1: claude 実体(199MB)の該当関数 ── `ENTRYPOINT = 非対話 ? "sdk-cli" : "cli"`。
    呼び出し元は `O = interactivity.kind === "non-interactive" || wir(argv)` で、
    Claude Code 自身の「非対話か」の判定そのものが入っている。
  経路2: 実機A/B。`claude -p` のフックが見た値 = 'sdk-cli'／
    pty上で起こした対話TUIのフックが見た値 = 'cli'。フックの子プロセスへ
    環境変数は継承されることも同時に確認。
  経路3: mini の transcript 25,261 assistant行の `entrypoint` 欄は
    `cli` 18,538 ／ `sdk-cli` 6,723 の2値のみ。欠測・第3の値は0件。

  ★実装時の訂正（依頼文との矛盾を実装側で解消した点を正直に記す）：
    最初の依頼文の「判定方法」本文は `entrypoint == 'sdk-cli'` の完全一致のみを
    非対話とする仕様だったが、依頼側の回帰テスト仕様（T4）は `sdk-ts` / `sdk-py`
    （TypeScript/Python 版 Claude Agent SDK 経由の非対話呼び出しを想定した値と
    思われる）も exit 2 でブロックすることを要求しており、両者は矛盾していた。
    実測（経路3）で観測された非対話値は `sdk-cli` の1種類のみで `sdk-ts`/`sdk-py`
    は実データに登場しないため、「sdk-cli専用」と書くか「sdk-*全般」と書くかは
    実測だけでは決め切れない。テスト仕様を優先し、**`sdk-` で始まる値はすべて
    非対話とみなす**プレフィックス判定へ実装した。
    ★この拡張（sdk-ts/sdk-py を非対話とみなす部分）は実機で確認していない・推測に
    基づく。fail-open の安全側原則は変えていない（cli以外・sdk-以外の未知の値は
    引き続き通す＝無言）。

  ★`agent_id` は使えない（実測済み）。非対話メインセッションの PreToolUse payload に
  `agent_id` は含まれない（実測キー = cwd, effort, hook_event_name, permission_mode,
  prompt_id, session_id, tool_input, tool_name, tool_use_id, transcript_path）。
  `agent_id` はメイン/サブの区別には使えるが、対話/非対話の区別はできない。
  なお環境変数方式はサブエージェントにも自動で効く（環境変数を継承するため）
  ＝この点で agent_id 方式より広く効く。

  ★fail-open にする理由：判定不能な値まで止めると、未知の呼び出し方（将来のSDKや
  この2機以外の環境）を誤ってブロックする恐れがある。取りこぼしは層1
  （`stall_watch.py`・別セッションが新設中）が検知側として拾う＝多層で受ける設計。

対象と止め方（2段構え・2026-09-05 改訂）
  対象ツールは AskUserQuestion のみ（GUARDED_TOOLS）。★ExitPlanMode 等は未実測なので
  対象に含めない（未検証）。

  非対話（sdk-*）  → ★ブロック（exit 2 + stderr）。
    hook_role_guard.py / hook_session_writeback.py と同じ実績パターン。
    ★JSON の permissionDecision はこのコードベースで未検証のため使わない。
  対話（cli）      → ★警告のみ（exit 0 + additionalContext。ブロックしない）。
    形は hook_role_guard.py の Bash 側と同じ
    （{"hookSpecificOutput":{"hookEventName":"PreToolUse","additionalContext":...},
      "suppressOutput":true}）。
  判定不能         → ★通す・無言（exit 0、追加情報なし）。

  なぜ非対話はブロックで、対話は警告止まりか：
    非対話セッションには定義上そこに人が居ない。警告を出してもツールはそのまま実行され、
    やはり答える人がいないので無言で止まる＝警告では直らない。だから止めるしかない。
    対話セッションは、端末のダイアログが出ること自体は起こる（拒否されるにせよ）ため、
    「実行してみたら分かる」ではなく「実行前に道具の選び方を教える」警告が有効。
    加えて実測で、mini の非対話 6,723 assistant行のうち AskUserQuestion は0件＝
    ブロックにしても実運用でほぼ発火しない（うるささのコストが極めて低い）。

止めるなら逃げ道を必ず添える（memory/reference_silent_failure_kills_adoption.md）
  非対話ブロック時の stderr メッセージには必ず ①なぜ止めたか ②聞こうとした中身そのまま
  ③逃げ道3つ（①既定を選んで進む ②ask_hub.ask()を自分で呼ぶ ③保留して残りをやり切る）
  ④記録した場所、を入れる。
  対話警告時は短く：①この機は dontAsk のため拒否される可能性が高いこと
  ②判断は ask_hub.ask() で出すこと（選択式の要件＝①プッシュで届く②押せる③それ以外は
  書いて返せる、の3つがそろって初めて満たされる。①が抜けたものは選択肢があっても不可）。

ループ対策（非対話ブロックのみ）
  同一 session_id で3回目以降ブロックしたときは、メッセージの冒頭を強い文言に変える。
  回数は log（interactive_guard.log）を読んで数える。新しい状態ファイルは作らない。

堅牢性
  何があっても例外を外へ出さない（fail-open）。stdin が空・壊れたJSONでも落ちない。
  ★notify も ask_hub も import しない。ネットワークに一切触らない
  （＝Slackへ実投稿しない、を構造で保証する）。

ログ
  ~/.vivid-relay/interactive_guard.log へ全判定を1行。
  形式: time.strftime('%Y-%m-%dT%H:%M:%S %Z') + TAB + 判定 + TAB + 詳細
  判定は「★ブロック」「★警告」「通した」「例外」の4種。
"""
import json
import os
import sys
import time

LOG = os.path.expanduser('~/.vivid-relay/interactive_guard.log')

# ★対象は AskUserQuestion のみ。ExitPlanMode 等は未実測のため含めない。
GUARDED_TOOLS = {'AskUserQuestion'}

INTERACTIVE_VALUE = 'cli'
NON_INTERACTIVE_PREFIX = 'sdk-'

# 何回目からループ対策の強い文言に切り替えるか
LOOP_THRESHOLD = 3


def log(verdict, detail=''):
    """★何があっても例外を外に出さない。hook_role_guard.py と同じ作法で
    %Z を必ず出す（タイムゾーン混在によるログ突合の事故を避けるため）。"""
    try:
        os.makedirs(os.path.dirname(LOG), exist_ok=True)
        with open(LOG, 'a') as f:
            f.write('%s\t%s\t%s\n' % (time.strftime('%Y-%m-%dT%H:%M:%S %Z'), verdict, detail))
    except Exception:
        pass


def _count_recent_blocks(session_id):
    """このセッションが直近すでに何回★ブロックされたかをログから数える。

    ★新しい状態ファイルは作らない（ログが正）。ログが読めない/存在しない場合は
    0を返す（fail-safe。ループ対策が働かないだけで、誤爆方向には振れない）。
    """
    if not session_id:
        return 0
    try:
        if not os.path.isfile(LOG):
            return 0
        n = 0
        needle = 'session=%s' % session_id
        with open(LOG, encoding='utf-8', errors='replace') as f:
            for line in f:
                if '★ブロック' in line and needle in line:
                    n += 1
        return n
    except Exception:
        return 0


def _format_questions(tool_input):
    """聞こうとした中身をそのまま返す。★ここを落とすと考えた内容が消える。"""
    try:
        questions = tool_input.get('questions') or []
        lines = []
        for q in questions:
            header = q.get('header', '')
            question = q.get('question', '')
            lines.append('  【%s】%s' % (header, question) if header else '  %s' % question)
            for opt in (q.get('options') or []):
                label = opt.get('label', '') if isinstance(opt, dict) else str(opt)
                lines.append('    - %s' % label)
        return '\n'.join(lines) if lines else '（questions の中身を取得できませんでした）'
    except Exception:
        return '（questions の整形に失敗しました）'


def _ask_hub_snippet(tool_input):
    """ask_hub.ask() の呼び出し例を、実際の questions/options から組み立てて貼れる形で出す。"""
    try:
        questions = tool_input.get('questions') or []
        q0 = questions[0] if questions else {}
        subject = q0.get('header', '判断') or '判断'
        question = q0.get('question', '') or ''
        opts = []
        for opt in (q0.get('options') or [])[:4]:
            label = opt.get('label', '') if isinstance(opt, dict) else str(opt)
            if label:
                opts.append(label)
        if not opts:
            opts = ['進める', '保留']
        opts_repr = ', '.join('(%r, None)' % o for o in opts)
        return (
            "    from ask_hub import ask\n"
            "    ask(\n"
            "        subject=%r,\n"
            "        question=%r,\n"
            "        options=[%s],\n"
            "        kind='開発',  # 開発／営業／福祉／広報／財務／法務／個人／その他 の8つだけ\n"
            "        asked_by='AI',\n"
            "    )"
        ) % (subject, question, opts_repr)
    except Exception:
        return (
            "    from ask_hub import ask\n"
            "    ask(subject='判断', question='(内容を書く)', options=[('進める', None), ('保留', None)],\n"
            "        kind='開発', asked_by='AI')"
        )


def build_block_message(tool_input, session_id, block_count):
    """非対話セッション向け。止めた理由・聞こうとした中身・逃げ道3つ・記録場所。"""
    questions_text = _format_questions(tool_input)
    snippet = _ask_hub_snippet(tool_input)

    header = (
        '★これ以上 AskUserQuestion を呼ばないでください。①か③で必ず先へ進んでください。\n\n'
        if block_count >= LOOP_THRESHOLD else ''
    )

    lines = [
        header +
        '★非対話セッション（claude -p 等）です。ここには答える人がいないため、'
        'このまま呼んでも誰にも届かず無言で止まり続けます。',
        '',
        '聞こうとした内容：',
        questions_text,
        '',
        '次の3つのうち、いずれかで進めてください。',
        '',
        '①【まず試すべき】既定を選んで進む',
        '  いちばん安全な選択肢を自分で選び、選んだ理由を成果物へ1行書いてください。',
        '',
        '②本当に人の判断が要るなら ask_hub.ask() を自分で呼ぶ（ボタン付きでSlackへ出ます）',
        snippet,
        '  ★注意：発行は Mac mini からのみ（判断台帳が mini にしかありません）。',
        '  ★kind は 開発／営業／福祉／広報／財務／法務／個人／その他 の8つだけです。',
        '  ★選択肢は4個までです。',
        '  ★投げっぱなしです。後で ask_hub.answer_of(受付番号) を自分で見に行ってください。',
        '',
        '③保留して残りを全部やり切る',
        '  判断が要る点を成果物に「人の判断が要る点」として書き残し、それ以外の作業を進めてください。',
        '',
        '記録した場所：%s' % LOG,
    ]
    return '\n'.join(lines)


def build_warn_message():
    """対話セッション向け。短く要点だけ（ブロックしない）。"""
    return (
        '★注意：この環境は permissions.defaultMode = dontAsk のため、'
        'AskUserQuestion（端末のダイアログ）は拒否される可能性が高いです。\n'
        '判断は ask_hub.ask() で出してください。「選択式」の要件は3つそろって初めて'
        '満たされます：①プッシュで届く ②押せる（打たせない） ③それ以外は書いて返せる。\n'
        '★①が抜けているものは、選択肢が並んでいても不可です。'
    )


def main():
    try:
        raw = sys.stdin.read()
        d = json.loads(raw) if raw.strip() else {}
    except Exception:
        log('例外', 'stdin のJSON解析に失敗')
        print(json.dumps({}))
        return

    tool = str(d.get('tool_name', ''))
    if tool not in GUARDED_TOOLS:
        # ★対象外ツールはログにも残さない（role_guard/output_guard と異なり、
        #   このフックは対象を1種類に絞っているため通過ログの量が支配的になるのを避ける）
        print(json.dumps({}))
        return

    session_id = d.get('session_id', '')
    tool_input = d.get('tool_input', {}) or {}
    entrypoint = os.environ.get('CLAUDE_CODE_ENTRYPOINT', '')

    if entrypoint == INTERACTIVE_VALUE:
        # ★2026-09-05 変更：対話でも止めない。ただし dontAsk の実害があるため警告は出す。
        msg = build_warn_message()
        log('★警告', 'entrypoint=%s（対話） session=%s' % (entrypoint, session_id))
        print(json.dumps({
            'hookSpecificOutput': {
                'hookEventName': 'PreToolUse',
                'additionalContext': msg,
            },
            'suppressOutput': True,
        }, ensure_ascii=False))
        return

    if not entrypoint.startswith(NON_INTERACTIVE_PREFIX):
        # ★判定不能。fail-open・無言。
        log('通した', 'entrypoint=%r（判定不能・fail-open） session=%s' % (entrypoint, session_id))
        print(json.dumps({}))
        return

    # ここに来たら非対話（sdk- で始まる）。ブロックする。
    block_count = _count_recent_blocks(session_id) + 1  # 今回の分を含める
    msg = build_block_message(tool_input, session_id, block_count)
    log('★ブロック', 'entrypoint=%s tool=%s 回数=%d session=%s' % (
        entrypoint, tool, block_count, session_id))
    sys.stderr.write(msg + '\n')
    sys.exit(2)


if __name__ == '__main__':
    try:
        main()
    except SystemExit:
        raise
    except Exception as e:
        # ★フック自身の失敗でセッションを止めない（fail-open）
        try:
            log('例外', str(e))
        except Exception:
            pass
        print(json.dumps({}))
    sys.exit(0)
