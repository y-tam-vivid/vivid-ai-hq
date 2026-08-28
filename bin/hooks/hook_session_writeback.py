#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Stop フック ── 書き戻さずにターンを終えようとしたら1回だけ差し戻す

なぜ要るか（2026-08-25 有璽氏）
  > 「これでオペレーション上は問題ないと思ってるけど、落ちへんの。
  >   ★途中で止まったりするんだよね、このオペレーションがね。確実に回るようにしてほしい」

  「離席宣言」「区切り」で書き戻す手順は **AIの規律に依存している**。
  規律に依存する対策は、規律が切れた回にだけ効かない（reference_hooks_enforce_what_discipline_cannot）。
  ★だから合図を増やすのではなく、**ターンが終わるたび**に機械で見る。

何を見るか（★誤爆しないための線引き）
  対象   memory/ ・ WORKING.md ・ .claude/ ・ bin/ の未コミット
  条件   ★最終更新から10分以上たっているものだけ
         ＝ いま書いている最中のもの・他セッションが書き込んだ直後のものでは鳴らない
  無限ループ対策  stop_hook_active が true（＝すでに1度差し戻した）なら黙って通す

★2つ目の検査 ── 探さずに人へ投げていないか（2026-08-29 有璽氏）
  > 「散々書きますとかなんとかしますって言っててもそれ見ないんやったら意味ないやん。
  >   根本的にどうやって解決すんのそういうの」

  実測した構造 ── **検問が1つも無い経路が1本だけ残っていた**。

    ファイルを触る       → PreToolUse が地雷を突きつける   効いている
    ターンを終える       → 上の書き戻し検査               効いている
    ★人へ作業を依頼する → 何も鳴らない
    ★「無い/分からない」→ 何も鳴らない

  2026-08-28、Drive に実物があるのに「kintone の CSV を書き出していただけますか」と
  有璽氏へ投げた。**その場所は自分で作った場所だった。** ファイルを触っていないので
  フックは鳴らず、memory は引きに行かないと来ないので来なかった。
  「あとから記憶に書いてありました」と言うのも同じ理由 ── **指摘されて初めて探すから**。

  だから：**人へ投げる／無いと言うターンでは、探した形跡があるかを機械で見る。**
  探していれば黙って通す。探していなければ1度だけ差し戻す。

出力の作法
  exit 2 ＋ stderr  → Claude に差し戻される（stderr の中身がそのまま指示になる）
  exit 0            → そのまま終了
  ★何があっても exit 1 で落とさない。フック自身の失敗でセッションを止めない
"""
import json, os, re, subprocess, sys, time

REPO = os.path.expanduser('~/vivid-ai-hq')
WATCH = ('memory/', 'WORKING.md', '.claude/', 'bin/')
STALE_MIN = 10
LOG = os.path.expanduser('~/.vivid-relay/hook_writeback.log')


def log(verdict, detail=''):
    """★毎回1行残す。「鳴っていない」と「動いていない」を区別するため（2026-08-28 有璽氏）

    このフックは exit 2 の中身が Claude にしか返らず、有璽氏の画面には出ない。
    ログが無いと「消えてる気がする」を実測で否定できない。★何があっても例外を外に出さない。
    """
    try:
        os.makedirs(os.path.dirname(LOG), exist_ok=True)
        with open(LOG, 'a') as f:
            f.write('%s\t%s\t%s\n' % (time.strftime('%Y-%m-%dT%H:%M:%S'), verdict, detail))
    except Exception:
        pass


# ─────────────────────────────────────────────────────────────
# 検査2 ── 探さずに人へ投げていないか
# ─────────────────────────────────────────────────────────────

# ★狭く取る。誤爆すると「またフックがうるさい」で読まれなくなり、無いのと同じになる
#   （reference_delivered_but_unread の型）。だから「人に手を動かさせる依頼」と
#   「無いと断定した」だけに絞る。「〜しますか」「承認してください」では鳴らせない。
ASK_HUMAN = re.compile(
    r'(いただけますか|いただけません|していただ|もらえますか|もらえません'
    r'|送ってください|共有してください|共有してほしい'
    r'|出力してください|貼ってください'
    # ★2026-08-29 ステラ指摘 ── 「書き出して」「エクスポートして」「アップロードして」を
    #   裸で入れていたため、**完了報告**「CSVを書き出しておきました」が差し戻されていた。
    #   要求形の接尾辞を必須にする（誤爆が常態化するとフックは読まれなくなる）
    r'|書き出して(ください|もらえ|いただ)|エクスポートして(ください|もらえ|いただ)'
    r'|アップロードして(ください|もらえ|いただ))')
CLAIM_ABSENT = re.compile(
    r'(見つかりませんでした|見つかりません|見当たりません|存在しません'
    r'|どこにあるか(は)?(分|わ)かりません|所在が(分|わ)かりません'
    r'|こちらには(ありません|無い|持っていません)|手元にありません)')

# ★「探す」ツールだけを証拠に数える。Edit / Write は数えない（ステラ指摘）
SEARCH_TOOLS = {'Read', 'Grep', 'Glob', 'WebFetch', 'WebSearch', 'Bash', 'Agent', 'Task'}

# 探した形跡（★実際に叩いたツールの入力から見る。言葉でなく行為で判定する）
#
# ★2026-08-29 つる2周目の指摘（実測）── つる自身が daily_jobs.conf を find で
#   探して0件→別の場所で発見、という**最も基本的な探索行為**が「探していない」と
#   判定される構造だった（語彙が memory/ Drive/ Notion 系の固有名詞にしか当たらず、
#   find/ls/grep/cat のような汎用コマンド名が抜けていたため）。
#
# ★設計判断（トレードオフ・ビビの依頼どおり報告する）
#   採った案：コマンド名（単語境界）だけを見る。対象パスが「探すべき場所」
#     （memory/Drive/Notion等）に関係しているかまでは見ない。
#   理由：①話題関連性の判定は自由記述の依頼文から対象を推定する必要があり、
#     実装が複雑になるうえ誤判定（見逃し・過検知の両方）が増える。
#     ②既存設計（SEARCH_TOOLS によるツール種別の絞り込み）自体が既に
#       「厳密な対象特定」までは行っていない粒度なので、一貫性がある。
#     ③「うるさくして読まれなくなる」よりは、狭く始めて様子を見る方が安全
#       （reference_delivered_but_unread の教訓）。
#   捨てたリスク：無関係な `ls ~/Downloads` 等でも「探した」と判定され通ってしまう
#     ＝ 見逃し方向のリスク（誤爆で止められすぎるより安全側と判断した）。
#     精度を上げるなら、コマンドの引数に WORKING.md/memory/Drive/Notion 等の
#     語が含まれるかを追加条件にできる（未実装。次に踏んだら検討）。
SEARCHED = re.compile(
    r'(vivid-ai-hq/memory|memory/|INDEX_|MEMORY\.md'          # 記憶を引いた
    r'|drive\.files|files\(\)\.list|search_files|Google_Drive'  # Drive を探した
    r'|notion-search|notion-fetch'                              # Notion を探した
    r'|\bfind\b|\bls\b|\bgrep\b|\bcat\b|\brg\b)')                # ★基本的な探索コマンド（単語境界）


def _turn_messages(path):
    """直近の人の発言以降の、こちらの発話とツール入力を取り出す"""
    said, tooled = [], []
    try:
        lines = open(path, encoding='utf-8').read().splitlines()
    except Exception:
        return said, tooled
    start = 0
    for i, ln in enumerate(lines):
        try:
            o = json.loads(ln)
        except Exception:
            continue
        if o.get('type') != 'user' or o.get('isMeta'):
            continue
        c = (o.get('message') or {}).get('content')
        # ツール結果だけの user 行は「人の発言」ではない
        if isinstance(c, list) and all(
                isinstance(b, dict) and b.get('type') == 'tool_result' for b in c):
            continue
        txt = c if isinstance(c, str) else ' '.join(
            b.get('text', '') for b in c or [] if isinstance(b, dict))
        if '<system-reminder>' in txt and len(txt) > 4000:
            continue
        start = i
    for ln in lines[start + 1:]:
        try:
            o = json.loads(ln)
        except Exception:
            continue
        if o.get('type') != 'assistant':
            continue
        for b in (o.get('message') or {}).get('content') or []:
            if not isinstance(b, dict):
                continue
            if b.get('type') == 'text':
                said.append(b.get('text', ''))
            elif b.get('type') == 'tool_use':
                # ★2026-08-29 ステラ指摘（実測で再現）── 以前は全ツールの入力を
                #   「探した証拠」に数えていた。すると **この検問のコード自身が
                #   memory/ や Notion の語を含むため、それを Edit するだけで検問が無効化**
                #   された。＝ 検問を直す作業がいちばん素通りする、という自己言及的な穴。
                #   → 探す行為のツールだけを証拠に数える。書く行為は数えない。
                nm = b.get('name', '')
                if nm in SEARCH_TOOLS or nm.startswith('mcp__'):
                    tooled.append(json.dumps(b.get('input', {}), ensure_ascii=False))
    return said, tooled


def check_asked_without_looking(payload):
    """人へ投げた／無いと言った、のに探していないなら差し戻し文を返す"""
    tp = payload.get('transcript_path')
    if not tp or not os.path.isfile(tp):
        return None
    said, tooled = _turn_messages(tp)
    if not said:
        return None
    body = '\n'.join(said)
    ask = ASK_HUMAN.search(body)
    absent = CLAIM_ABSENT.search(body)
    if not ask and not absent:
        return None
    if any(SEARCHED.search(t) for t in tooled):
        return None                       # 探したうえで言っている。通す
    what = []
    if ask:
        what.append('有璽氏に手を動かしてもらう依頼（「%s」）' % ask.group(1))
    if absent:
        what.append('「%s」という断定' % absent.group(1))
    return [
        '★探さずに人へ投げようとしています。',
        '',
        'このターンで ' + ' と '.join(what) + ' を書いていますが、',
        'このターンでは memory も Drive も Notion も1度も検索していません。',
        '',
        '2026-08-28、Drive に実物があるのに「kintone の CSV を書き出していただけますか」と',
        '有璽氏へ投げました。★その場所は自分で作った場所でした。',
        '',
        '終える前に、次を実際に叩いてください（言うだけでなく実行する）：',
        '  1  grep -ril "<いま探している語>" ~/vivid-ai-hq/memory/',
        '  2  Drive を検索する（drive.files().list / search_files）',
        '  3  それでも無ければ「◯◯と△△を探したが無い」と探した先を明記して渡す',
        '',
        '★探したうえで人に依頼するのは正しい行為です。探さずに渡すのだけが問題です。',
        '（意図して省いている場合は、その旨を1行述べればそのまま終えられます）',
    ]


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        payload = {}

    # すでに1度差し戻している。2度目は通す（無限ループにしない）
    if payload.get('stop_hook_active'):
        log('通した', '2度目（stop_hook_active）')
        return 0

    # ★検査2を先に見る。書き戻しより前に「そもそも探したか」を問う
    try:
        lines = check_asked_without_looking(payload)
    except Exception as e:
        lines = None
        log('検査2で例外', str(e))
    if lines:
        sys.stderr.write('\n'.join(lines) + '\n')
        log('★差し戻した(検査2)', '探さずに人へ投げた')
        return 2

    if not os.path.isdir(os.path.join(REPO, '.git')):
        log('通した', 'リポジトリが無い')
        return 0

    r = subprocess.run(['git', '-C', REPO, 'status', '--porcelain', '-z'],
                       capture_output=True, text=True)
    if r.returncode != 0 or not r.stdout:
        log('通した', '未コミット0件')
        return 0

    entries = [e for e in r.stdout.split('\0') if e]
    targets = []
    i = 0
    while i < len(entries):
        e = entries[i]
        code, path = e[:2], e[3:]
        i += 1
        if code[0] in ('R', 'C'):
            i += 1
        if not path.startswith(WATCH):
            continue
        full = os.path.join(REPO, path)
        if 'D' in code:
            targets.append((path, '削除'))
            continue
        if not os.path.isfile(full):
            continue
        if (time.time() - os.path.getmtime(full)) / 60.0 < STALE_MIN:
            continue          # いま書いている最中。触らない
        targets.append((path, '変更' if code.strip() != '??' else '新規'))

    if not targets:
        log('通した', '%d分超の対象なし（未コミット%d件）' % (STALE_MIN, len(entries)))
        return 0

    lines = [
        '★書き戻しが終わっていません。ターンを終える前に片づけてください。',
        '',
        f'{STALE_MIN}分以上さわっていない未コミットが {len(targets)} 件あります：',
    ]
    for p, kind in targets[:15]:
        lines.append(f'  [{kind}] {p}')
    if len(targets) > 15:
        lines.append(f'  …ほか {len(targets)-15} 件')
    lines += [
        '',
        '順番も固定です（memory/feedback_write_back_before_you_go.md）：',
        '  1  この会話で分かった事実を memory/ の該当ファイルへ書く（無ければ作る）',
        '  2  索引（MEMORY.md か INDEX_*.md）の現在地を1行だけ差し替える',
        '  3  WORKING.md の自分のブロックを実態に合わせる（終わったものは消す）',
        '  4  ./check.sh を通す',
        '  5  ★触ったファイルを明示して commit（git add -A は使わない）',
        '',
        '他セッションの書きかけで自分は触っていない、あるいは意図して置いている場合は、',
        'その旨を1行述べてそのまま終えて構いません（2度目はこのフックは鳴りません）。',
    ]
    sys.stderr.write('\n'.join(lines) + '\n')
    log('★差し戻した', '%d件: %s' % (len(targets), ' '.join(p for p, _ in targets[:5])))
    return 2


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as e:               # フック自身の失敗でセッションを止めない
        sys.stderr.write(f'(hook_session_writeback: {e})\n')
        sys.exit(0)
