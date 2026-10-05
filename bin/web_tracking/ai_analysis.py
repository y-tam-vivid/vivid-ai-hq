#!/usr/bin/env python3
"""SEO週次・月次レポート用の AI 分析（Mac mini の claude -p を呼ぶ）。

  from ai_analysis import analyze
  result = analyze(data, mode='weekly')   # or 'monthly'

data は「数字だけ」を渡す（Search Console・Clarity・改善ログの状態）。AI には★渡した数字以外を書かせない。
戻り値 {"sites":[{"site","what","why","next"}], "actions":[{"site","area","title","why","how","who","effort"}], "summary": str}
失敗したら {"error": "..."}（レポート本体は止めない）
"""
import json
import os
import subprocess

CLAUDE = os.path.expanduser('~/.npm-global/bin/claude')
MODEL = 'claude-sonnet-5-5'

RULES = """あなたは ふくち。グループ（大阪・南河内の福祉事業者グループ）の Web 担当アナリストです。
対象は自社の福祉施設・法人サイトで、目的は「見学・問い合わせ・採用につながる訪問を増やすこと」。
★守ること
- 渡したデータにある数字だけを使う。無い数字を推測で作らない。足りない時は「データ不足」と書く
- 数字は出典が分かる形で書く（例：「クリック 351→87（Search Console・月）」）
- 訪問数が少ない（目安：Clarity 訪問20未満）指標は「参考値」と断る
- 専門用語を使わない。経営者が読んで分かる日本語で、1文を短く
- 打ち手は具体的に（どのページの・何を・どう変える）。AIが自分でできる作業（説明文・タイトル・robots.txt・サイトマップ・構造化データ等のサイト編集）は who="AI"、人の判断や素材・現場の協力が要るものは who="人"
- 事業と無関係な検索語（例：「ベビーカステラ 英語」）は伸びしろではなくノイズとして扱う
出力は次の JSON だけ（前後に文章を書かない）:
{"summary": "全体の要点（%s）",
 "sites": [{"site": "サイト名", "what": "何が起きたか", "why": "考えられる理由（根拠の数字つき）", "next": "次に見る・やること"}],
 "actions": [{"site": "サイト名", "area": "SEO|MEO|AIEO|使いやすさ（Clarity）|計測", "title": "打ち手（1行）",
              "why": "なぜ（根拠の数字）", "how": "具体的なやり方", "who": "AI|人", "effort": "小|中|大"}]}
"""

MODES = {
    'weekly': ('3行以内', '打ち手は効果が大きく手間の小さいものから最大3件。データの少ないサイトは what に「データ蓄積中」と書き、無理に打ち手を作らない'),
    'monthly': ('5〜8行。先月との比較・効果が出た打ち手・次の1か月の重点', '各サイトについて月の実測を踏まえて深く分析する。打ち手は優先度順に最大8件。改善ログで実施済みの打ち手は、数字が動いたかを why で評価する'),
}


def analyze(data, mode='weekly', timeout=600):
    summary_len, extra = MODES[mode]
    prompt = (RULES % summary_len) + '\n★今回の範囲：' + extra + '\n\n# データ（JSON）\n' + \
        json.dumps(data, ensure_ascii=False, default=str)
    env = dict(os.environ)
    try:
        for line in open(os.path.expanduser('~/.vivid-relay/config.env')):
            if line.startswith('CLAUDE_CODE_OAUTH_TOKEN='):
                env['CLAUDE_CODE_OAUTH_TOKEN'] = line.split('=', 1)[1].strip().strip('"\'')
    except OSError:
        pass
    try:
        p = subprocess.run([CLAUDE, '-p', '--model', MODEL], input=prompt, capture_output=True,
                           text=True, timeout=timeout, cwd='/tmp', env=env)
    except Exception as ex:
        return {'error': 'claude 起動失敗：%s' % ex}
    out = p.stdout.strip()
    i, j = out.find('{'), out.rfind('}')
    if i < 0 or j < 0:
        return {'error': 'AIの出力にJSONが無い：%s' % out[:200]}
    try:
        return json.loads(out[i:j + 1])
    except json.JSONDecodeError as ex:
        return {'error': 'AIの出力を読めない：%s' % ex}
