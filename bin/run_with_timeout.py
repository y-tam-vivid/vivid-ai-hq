#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""任意のコマンドをタイムアウト付きで実行する（汎用ヘルパー）

なぜ要るか（2026-09-07 有璽氏の指摘・kadoban_deploy.sh の詰まり対策）
  macOS 標準の bash/zsh には `timeout` コマンドが無い（実測・gtimeout/timeout とも not found）。
  `cmd & pid=$!; sleep N; kill $pid` だけだと、`vercel deploy` のような
  「シェル→npx→node」の多段プロセスで、殺せるのは先頭のシェルだけ。
  子・孫プロセスは生き残りうる（多段プロセスに対する素朴な kill が子を取り逃がすのは
  一般的な既知の弱点。今回は実測ではなく設計判断として、より確実な方式を採る）。

やり方
  os.setsid() で新しいプロセスグループを作って起動し、
  タイムアウト時は os.killpg() でグループごと殺す。子・孫プロセスも道連れにできる。

使い方
  python3 bin/run_with_timeout.py <timeout_sec> -- <command...>
  終了コード: 通常はコマンドのrc。タイムアウトした場合は 124（timeoutコマンドの慣習に合わせた）
  標準出力・標準エラーはそのまま流す（呼び出し元のログに乗る）
"""
import os
import signal
import subprocess
import sys


def main():
    argv = sys.argv[1:]
    if len(argv) < 2 or argv[1] != '--':
        sys.stderr.write('使い方: run_with_timeout.py <timeout_sec> -- <command...>\n')
        return 2
    try:
        timeout = float(argv[0])
    except ValueError:
        sys.stderr.write('timeout_sec が数値でない: %r\n' % argv[0])
        return 2
    cmd = argv[2:]
    if not cmd:
        sys.stderr.write('コマンドが空\n')
        return 2

    proc = subprocess.Popen(
        cmd,
        stdout=sys.stdout,
        stderr=sys.stderr,
        preexec_fn=os.setsid,  # ★新しいプロセスグループ。これが無いと孫プロセスを殺せない
    )
    try:
        rc = proc.wait(timeout=timeout)
        return rc
    except subprocess.TimeoutExpired:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except ProcessLookupError:
            pass
        try:
            proc.wait(timeout=5)
        except Exception:
            pass
        sys.stderr.write('★TIMEOUT（%s秒）。プロセスグループごと終了させた\n' % timeout)
        return 124


if __name__ == '__main__':
    sys.exit(main())
