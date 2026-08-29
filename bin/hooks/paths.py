#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""vivid-ai-hq リポジトリの主要パスを1箇所に定義する（2026-08-29 ビビ依頼①）

なぜ要るか（穴Aと同じ型の再発防止）
  self_audit.py の穴A（bin/hooks/role_guard.log という誤ったパスを独自定義し、
  実物のログ ~/.vivid-relay/role_guard.log と食い違って「まだ稼働していない」と
  言い続けた事故）と同じ型が、check.sh 項目8（bin/check_path_duplication.py）で
  さらに2件見つかった：WORKING.md・memory を3〜4ファイルがそれぞれ別の書き方
  （os.path.expanduser(...) と os.path.join(REPO/ROOT, '...')）で独立に定義していた。
  ★片方だけ変えた瞬間に同じ事故が起きる。1箇所に集約し、他は import する。

使い方
  bin/hooks/ 配下のファイルから：
    from paths import REPO, WORKING_MD, MEMORY_DIR
  bin/ 直下（bin/hooks/ の外）のファイルから：
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hooks'))
    from paths import REPO, WORKING_MD, MEMORY_DIR

★このファイル自体は check_path_duplication.py の対象外にしない（正本を明示するため、
  ここにこそ os.path.expanduser(...) の代入文を書く。他のファイルはここから import
  するだけにし、独自の代入文を持たない）。
"""
import os

REPO = os.path.expanduser('~/vivid-ai-hq')
WORKING_MD = os.path.join(REPO, 'WORKING.md')
MEMORY_DIR = os.path.join(REPO, 'memory')
