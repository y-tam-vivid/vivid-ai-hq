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

# ★2026-08-29 ステラ検査指摘（軽微・条件2）対応：以前は check_single_route_claim() が
#   呼ばれるたびに sys.path.insert() していた（Stopフック発火のたびにsys.pathへ同じ
#   パスが重複追加される冗長性）。モジュールロード時に1回だけ追加する形に直した。
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

REPO = os.path.expanduser('~/vivid-ai-hq')
WATCH = ('memory/', 'WORKING.md', '.claude/', 'bin/')
STALE_MIN = 10
LOG = os.path.expanduser('~/.vivid-relay/hook_writeback.log')

# ★検査3（1経路断定）を実際にブロックするか。2026-08-29 導入時点では False（観測のみ）。
#
# ★2026-08-29 実測（このプロジェクトの実transcript全236ファイルで計測・一時検証スクリプトは
#   scratchpad側。このリポジトリには含めていない）：
#     総ターン数 953 ／ 断定語を含むターン 667（70%）
#     うち1経路以下（検査3が検出＝差し戻し候補）  188（断定ターンの28%）
#     うち2経路以上（通過）                        479
#   hook_output_guard の「88本で誤検知0件」とは桁違いに高い比率。
#   ★2026-08-29 ステラ検査で訂正（自分の当初の原因説明は不正確だった）：
#   188件から10件サンプリングして実物を読んだところ、主因は「有璽氏の短い『はい』への
#   定型的な返信」ではなく、**ターン跨ぎの検証**だった（前のターンで既に2経路以上で
#   確認済みのものを、このターンでは結論だけ短く述べているケース）。この場合、
#   check_single_route_claim() は「このターン」の tool_calls しか見ないため、
#   実際には複数方式で確認済みでも「1経路」に誤判定される。
#   これは自分がdocstring内「ステラが明記した漏れる箇所2」に既に書いていた限界
#   （ターン跨ぎの検証は誤検知しうる）が主因だった、という意味で、指摘の方が正確。
#   結論（ENABLE_CHECK3=False）自体は変わらない。
#   ★結論：現状のまま有効化すると「うるさくて読まれなくなる」
#   （reference_delivered_but_unread）を確実に踏む。ENABLE_CHECK3 は False のまま維持する。
#   次に着手する人は、CLAIM_WORDSを「探索の結果としての断定」に絞る条件
#   （例：直前に検索系ツール呼び出しが1つ以上あることを前提条件にする等）を
#   検討してから再計測すること。
ENABLE_CHECK3 = False


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
    """直近の人の発言以降の、こちらの発話とツール入力を取り出す

    戻り値: (said, tooled, tool_calls)
      tooled       検査2用（従来どおり・文字列化したinput）
      tool_calls   検査3用（★2026-08-29追加）。[(tool_name, input_dict), ...]
                   ツール名と生の input を両方保持する（method_signature() が使う）
    """
    said, tooled, tool_calls = [], [], []
    try:
        lines = open(path, encoding='utf-8').read().splitlines()
    except Exception:
        return said, tooled, tool_calls
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
                inp = b.get('input', {}) or {}
                if nm in SEARCH_TOOLS or nm.startswith('mcp__'):
                    tooled.append(json.dumps(inp, ensure_ascii=False))
                    tool_calls.append((nm, inp))
    return said, tooled, tool_calls


def check_asked_without_looking(payload):
    """人へ投げた／無いと言った、のに探していないなら差し戻し文を返す"""
    tp = payload.get('transcript_path')
    if not tp or not os.path.isfile(tp):
        return None
    said, tooled, _tool_calls = _turn_messages(tp)
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


# ─────────────────────────────────────────────────────────────
# 検査3 ── 1つの方法でしか探していないのに断定していないか（2026-08-29 ステラ設計）
# ─────────────────────────────────────────────────────────────
#
# 検査2との違い
#   検査2   探した形跡が「ある/ない」だけを見る（0か1か）
#   検査3   探した形跡が「複数の独立した方式か」を見る（1種類か2種類以上か）
#           ＝ 検査2を通っても、1つの方法だけで断定していれば検査3で差し戻す
#
# ★語彙は原理的に閉じない（設計中にステラ自身が実証した事実）
#   プロトタイプ1回目：既存の判定語をそのまま流用 → テスト8ケース中 6/8 しか捕まらなかった。
#   漏れた2件は、まさに2026-08-29 の実際の失敗②③だった。
#   原因：活用ゆれ（「入っていない」の正規表現はあったが「入っていません」の形が無かった）。
#   2回目：語彙を活用ゆれ込みで拡張し 8/8 で検出。
#   → **対策を作った本人が、1つの書き方しか想定しなかったために漏らした。**
#     Anthropic 自身が認める偽陰性率17%と同じ性質の限界が、この設計にも即座に出た。
#     ＝ このCLAIM_WORDSも将来また同じ形で漏れうる。閉じたと思わないこと。
#
# ★ステラが明記した「漏れる箇所」（隠さず記録する）
#   1  語彙は原理的に閉じない（上記で実証済み）
#   2  ターン跨ぎの検証は誤検知しうる。前ターンで既に2経路で検証済みで、今ターンでは
#      結論だけを述べている場合、このターンの tool_calls だけを見ると「1経路」に見える。
#      ★1経路断定はコード編集より発生頻度が高いと見込まれる。検査2以上に
#      「うるさくて読まれない」リスクがある → 実装後1週間は差し戻し比率を計測し、
#      多すぎれば緩める（このdocstringへ追記すること）。
#   3  Write/Edit でファイルに直接断定を書いた場合は対象外（この Stop hook は
#      アシスタントの発話（text block）しか見ておらず、ファイルの中身は見ていない）。
#   4  「方式が2つ違う」は独立性の代理指標にすぎない。同じ壊れた前提を2つの方式
#      （例：grep と find）で読んでも、前提が壊れていれば2経路とも同じ誤りに一致しうる。
#      ＝ 方式の数は「独立に確認した証拠」であって「正しさの証明」ではない。
#   5  サブエージェント経由の発話でこの Stop hook がどう発火するか（そもそも
#      サブエージェントの Stop で発火するか）は、この実装では未実測。
#
# 判定
#   断定語（CLAIM_WORDS）が発話に出たとき、このターンで使った探索ツールの
#   method_signature() の distinct 数が1以下（0または1種類）なら差し戻す。
#   ★合格ライン：実データ（実際のtranscript）で誤検知率を計測してから有効化する。
#     hook_output_guard の「88本で誤検知0件」と同水準を求める（docstring内に実測記録）。

# ★ステラ指定の5語彙のみ（0件／すべて／入っていない／存在しません／更新されている）＋活用ゆれ。
#   検査2の CLAIM_ABSENT とは独立した語彙（検査3は「断定全般」を対象にする）。
#   ★誤検知回避のため、指定外の語（「完了」「終わった」等）は含めない
#   （実測で「実装が完了しました」等の正当な完了報告に誤爆しないことを確認済み）。
CLAIM_WORDS = re.compile(
    r'(0件'
    r'|すべて|全部|全て'
    r'|入って(?:い)?(?:ない|ません|ませんでした)'
    r'|存在し(?:ない|ません)'
    r'|更新され(?:ている|ていません|ました|ていない))')


def method_signature(tool_name, tool_input):
    """検証手段の「方式」を1つの文字列（シグネチャ）として返す。

    ★Bash はコマンド文字列の内容から grep/find/cat/stat/hash/other に細分化する
    （ステラ指定）。それ以外のツール（Read/Grep/Glob/WebFetch/WebSearch/Agent/Task/mcp__*）は
    ツール名そのものを signature とする（＝ Bash の grep と Grep ツールは別方式として扱う。
    どちらも「検索」だが実行系路が異なるため独立性の代理指標として意味がある）。

    ★できないこと：Bash の command 文字列を正確に構文解析していない（正規表現のみ）。
    パイプで複数コマンドを繋いだ場合、最初にマッチしたキーワードで分類される
    （例: `find . | grep foo` は 'bash:find' と 'bash:grep' の両方にマッチしうるが、
    この実装では if-elif 順に最初の一致だけを返す。優先順位は grep→find→cat→stat→hash→other）。
    """
    if tool_name == 'Bash':
        cmd = str((tool_input or {}).get('command', ''))
        if re.search(r'\bgrep\b|\brg\b', cmd):
            return 'bash:grep'
        if re.search(r'\bfind\b', cmd):
            return 'bash:find'
        if re.search(r'\bcat\b|\bhead\b|\btail\b', cmd):
            return 'bash:cat'
        if re.search(r'\bstat\b|\bls\b|\bwc\b', cmd):
            return 'bash:stat'
        if re.search(r'\bmd5\b|\bmd5sum\b|\bsha256sum\b|\bshasum\b', cmd):
            return 'bash:hash'
        return 'bash:other'
    return tool_name


# ファイルパス／固有名詞らしき文字列（対象の代理）
_CLAIM_TARGET_RE = re.compile(r'[\w./_-]+\.(?:py|md|json|js|ts|tsx|jsx|sh|yml|yaml|txt|csv|gs|rb)\b')


def _claim_key_hint(text, claim_word):
    """断定文からfindings_trackerのキーに使う『対象』のヒントを抽出する。

    ★2026-08-29 ステラ指摘対応：_normalize()（findings_tracker.py側）は数字を#に
    伏せるだけで、自然文の断定同士は表記が少しでも違うと別々のキーになり慢性化を
    追えない。findings_tracker.py 本体は変更せず（既存の呼び出し元3本への影響を
    避けるため）、ここで「対象ファイル／対象命題」を軸にした短い文字列を組み立ててから
    track() へ渡すことで、実質的にキーの軸を変える。
    優先度：①拡張子つきのファイルパスらしき文字列 ②断定語の前後の短い文脈。
    ★これも語彙と同じく閉じない設計であることを明記する（ファイルパス以外の対象
    ── Notionページ・DBの行・人名等 ── は②のフォールバックにしか乗らない）。
    """
    m = _CLAIM_TARGET_RE.search(text)
    if m:
        return '%s:%s' % (m.group(0), claim_word)
    idx = text.find(claim_word)
    if idx >= 0:
        start = max(0, idx - 20)
        return text[start:idx + len(claim_word)]
    return claim_word


def check_single_route_claim(payload):
    """断定語が出たとき、そのターンの検証手段が実質1種類以下なら差し戻す（検査3）"""
    tp = payload.get('transcript_path')
    if not tp or not os.path.isfile(tp):
        return None
    said, _tooled, tool_calls = _turn_messages(tp)
    if not said:
        return None
    body = '\n'.join(said)
    m = CLAIM_WORDS.search(body)
    if not m:
        return None
    sigs = sorted(set(method_signature(nm, inp) for nm, inp in tool_calls))
    if len(sigs) >= 2:
        return None                       # 2方式以上で確認済み。通す

    # ★2026-08-29 findings_trackerへの配線。ENABLE_CHECK3がFalse（観測モード）でも、
    #   検出したこと自体は記録する（将来の有効化判断の材料にするため）。
    #   track()自体は findings_tracker.py 側で例外を握りつぶさないので、ここで守る。
    #   ★sys.pathへの追加はモジュールロード時に1回だけ（ファイル冒頭の_HERE参照）。
    try:
        from findings_tracker import track
        key_hint = _claim_key_hint(body, m.group(1))
        track('single_route_claim', [key_hint])
    except Exception as e:
        log('検査3のtrack失敗', str(e))
    return [
        '★1つの方法でしか確認していないのに断定しています（検査3）。',
        '',
        '「%s」という断定を書いていますが、このターンで使った検証手段は %s 種類だけです（%s）。'
        % (m.group(1), len(sigs), '、'.join(sigs) or 'なし'),
        '',
        '2026-08-29、この検問を設計する過程でステラ自身が実例を出しました：',
        '判定語彙のプロトタイプが8ケース中6/8しか捕まえられず、漏れた2件はその日の',
        '実際の失敗そのものでした（活用ゆれの語彙漏れが原因）。',
        '**1つの方法・1つの視点だけで確認したことは、間違っている可能性を消しません。**',
        '',
        '終える前に、別方式で確認してください（例）：',
        '  grep で確認したなら → find や wc、あるいは実際に該当ファイルを開いて確かめる',
        '  1回のBashコマンドだけで判断したなら → 別の角度（別のツール）でもう一度見る',
        '',
        '★同じ壊れた前提を2つの方式で読んでも同じ誤りに一致することがあります。',
        '方式を増やすことは「正しさの証明」ではなく「独立に確認した」という代理指標です。',
        '（意図して1方式で十分と判断した場合は、その理由を1行述べればそのまま終えられます）',
    ]



# ─────────────────────────────────────────────────────────────
# 検査4 ── 窓口が一人で実装して終わっていないか（2026-08-31）
# ─────────────────────────────────────────────────────────────
# なぜ要るか
#   2026-08-20 有璽氏「有機的に全然動かせてねえじゃん。役割分担してやれっつってんねん」
#   2026-08-31 有璽氏「全然エージェント同士がやり取りするみたいな状態になってなくない？
#                      俺がめっちゃ入らなあかんやんけ」
#   同じ指摘が3回。原因は bin/team_run.py（編成→並列→検査→統合を回す道具）が
#   2026-08-20 の作成から 8/31 まで一度も呼ばれていなかったこと（被参照0件を実測）。
#   ★規範に書くだけでは同じことが起きる。実際、この検査を書いた回でさえ、
#     書いた本人（ビビ）が team_run を通さず一人で実装していた。だから機械で止める。
#
# 判定材料（★曖昧なものを入れない。検査3が誤爆28%で観測モードのまま止まった反省）
#   条件A  このセッションで bin/ か .claude/ 配下の実装ファイルを Write/Edit した
#   条件B  かつ team_run.py を一度も呼んでいない
#   → A かつ B のときだけ差し戻す。どちらも tool_calls から機械的に判定でき、解釈が要らない。
#
# 誤爆させない除外
#   ・サブエージェント（agent_id あり）は対象外。担当として呼ばれた側が書くのは正しい姿
#   ・記録だけの編集（memory/ ・WORKING.md ・*.json のデータ更新）は対象外
GUARDED_DIRS = ('bin/', '.claude/')
IMPL_EXT = ('.py', '.sh', '.js', '.ts', '.tsx', '.jsx', '.gs', '.rb', '.json')

# team_run.py を「実行した」形だけを数える。grep/echo など言及だけでは通さない。
TEAM_RUN_EXEC = re.compile(r'(?:python[23]?|/\S*python\S*)\s+[^|;&]*team_run\.py')

# Bash 経由の書き込み先を拾う。★ここで捕まえられない書き方が残ることは
#   bin/hooks/adversarial_cases.md に列挙してある（完全ではない）。
BASH_WRITE_PATH = re.compile(
    r'(?:'
    r'>>?\s*(?P<path>[^\s;&|<>]+)'                        # > path  /  >> path
    r'|sed\s+-i[^\s]*\s+(?:-e\s+\S+\s+)?[^\s]*\s+(?P<path2>[^\s;&|]+)'   # sed -i ... path
    r"|tee\s+(?:-a\s+)?(?P<path3>[^\s;&|]+)"             # tee path
    r"|open\(\s*['\"](?P<path4>[^'\"]+)['\"]\s*,\s*['\"][wa]"  # open(path,'w')
    r'|(?:cp|mv)\s+\S+\s+(?P<path5>[^\s;&|]+)'           # cp src dst / mv src dst
    r')')


def _iter_write_paths(cmd):
    for m in BASH_WRITE_PATH.finditer(cmd):
        for g in ('path', 'path2', 'path3', 'path4', 'path5'):
            v = m.groupdict().get(g)
            if v:
                yield v


def _all_tool_calls(path):
    """セッション全体の (ツール名, input) を返す。
    ★_turn_messages() は使えない。あれは SEARCH_TOOLS と mcp__ しか拾わない設計で、
      Write/Edit が入らないうえ戻り値はタプル。辞書として扱うと例外になり、
      log('検査4で例外') で握りつぶされて「静かに無効化された検査」になる
      （2026-08-31、実際にその形で書いてしまい、逆検算の前に気づいた）。
    ★直近の人の発言以降ではなくセッション全体を見る。team_run を前のターンで
      呼んでいたら、それは通してよいため。"""
    out = []
    try:
        lines = open(path, encoding='utf-8').read().splitlines()
    except Exception:
        return out
    for ln in lines:
        try:
            o = json.loads(ln)
        except Exception:
            continue
        if o.get('type') != 'assistant':
            continue
        for b in (o.get('message') or {}).get('content') or []:
            if isinstance(b, dict) and b.get('type') == 'tool_use':
                out.append((b.get('name', ''), b.get('input') or {}))
    return out


def check_solo_implementation(payload):
    """窓口が担当を1体も通さずに実装まで完結していたら差し戻す（検査4）"""
    if payload.get('agent_id') or payload.get('agent_type'):
        return None                      # サブエージェント＝担当として呼ばれた側。正常

    edited, called_team_run = [], False
    for name, inp in _all_tool_calls(payload.get('transcript_path') or ''):
        if name == 'Bash':
            cmd = str(inp.get('command', ''))
            # ★実行を伴う呼び出しだけを数える（2026-08-31 チーム検査の指摘①）。
            #   'team_run' in cmd だと `grep team_run` や `echo team_run` で素通りできた。
            if TEAM_RUN_EXEC.search(cmd):
                called_team_run = True
            # ★Bash経由の書き込みも数える。Write/Edit だけを見ていた版は
            #   heredoc・sed -i・tee・python -c open().write() を一切検知できなかった。
            #   これは bin/hooks/adversarial_cases.md のケース1・3そのもの。
            for wp in _iter_write_paths(cmd):
                rel = wp.split('vivid-ai-hq/')[-1].lstrip('./')
                if rel.startswith(GUARDED_DIRS) and rel.endswith(IMPL_EXT):
                    edited.append(rel)
        elif name in ('Write', 'Edit', 'MultiEdit', 'NotebookEdit'):
            fp = str(inp.get('file_path') or '')
            rel = fp.split('vivid-ai-hq/')[-1]
            if rel.startswith(GUARDED_DIRS) and rel.endswith(IMPL_EXT):
                edited.append(rel)
    if called_team_run or not edited:
        return None
    uniq = list(dict.fromkeys(edited))
    return [
        '★担当を1体も通さずに実装まで終えています（検査4）。',
        '',
        '  このセッションで書き換えた実装ファイル ： %s%s' % (
            '、'.join(uniq[:4]), '（ほか%d件）' % (len(uniq) - 4) if len(uniq) > 4 else ''),
        '  team_run.py の呼び出し ： 0回',
        '',
        '  窓口は投げて束ねる役です。作る役と検査役は別の主体でなければなりません。',
        '  次のどちらかをしてから終えてください。',
        '',
        '    python3 %s/bin/team_run.py "いま行った変更を検査してください"' % REPO,
        '    （編成だけ見るなら --dry を付ける）',
        '',
        '  正本 ： bin/coordination/roster.json ／ 規範 ： fukuchi-core「窓口と担当」',
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

    # ★検査3 ── 1つの方法でしか探していないのに断定していないか（2026-08-29 ステラ設計）
    #   ★観測モード：ENABLE_CHECK3=False の間はログに記録するだけで exit 2 にしない。
    #   ステラの指示「合格ライン：実データで誤検知率を計測してから有効化する」に従い、
    #   実運用のtranscriptで誤検知率が hook_output_guard 相当（0件近辺）になるまでは
    #   ブロックしない。有効化するときはこの定数を True にする（このファイルの1箇所のみ）。
    try:
        lines3 = check_single_route_claim(payload)
    except Exception as e:
        lines3 = None
        log('検査3で例外', str(e))
    if lines3:
        if ENABLE_CHECK3:
            sys.stderr.write('\n'.join(lines3) + '\n')
            log('★差し戻した(検査3)', '1経路断定')
            return 2
        else:
            log('検査3(観測のみ・未有効化)', '1経路断定を検出したがブロックしていない')

    # ★検査4 ── 窓口が一人で実装して終わっていないか（2026-08-31）
    try:
        lines4 = check_solo_implementation(payload)
    except Exception as e:
        lines4 = None
        log('検査4で例外', str(e))
    if lines4:
        sys.stderr.write('\n'.join(lines4) + '\n')
        log('★差し戻した(検査4)', '担当を通さず一人で実装した')
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
