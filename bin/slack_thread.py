#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Slack で始めた件を Claude Code から読む・続ける（どの機からでも。本体は mini の ~/.vivid-relay/slack_thread.py）

なぜ要るか（2026-10-17 有璽氏「Slack で依頼したものを、Slack 以外でも続けられる形に」）
  窓口ビビの受付の返事に受付番号（#s＋6桁）が出る。有璽氏が Claude Code で「#s028c4b の続き」と言ったら：
    1  python3 bin/slack_thread.py show '#s028c4b'      流れを読む（Slack のリンクや ts でもよい）
    2  続きの作業をする
    3  python3 bin/slack_thread.py reply '#s028c4b' "結果"   ★同じスレッドへ書き戻す（Slack 側でも経緯が切れない）
  一覧：python3 bin/slack_thread.py list [日数]
"""
import os, sys, shlex, subprocess

HERE_MINI = '/Users/yuji_macmini/.vivid-relay'
args = sys.argv[1:]
if not args:
    print(__doc__); sys.exit(1)
cmd = 'cd ~/.vivid-relay && python3 slack_thread.py ' + ' '.join(shlex.quote(a) for a in args)
if os.path.isdir(HERE_MINI):
    sys.exit(subprocess.call(['bash', '-lc', cmd]))
sys.exit(subprocess.call(['ssh', '-o', 'ConnectTimeout=5', 'mini', cmd]))
