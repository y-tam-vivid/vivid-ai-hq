#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""dashboard.html を Artifact に載る形へ変換する（デザインは1バイトも変えない）

なぜ要るか
  Artifact は公開時に <!doctype html><head>…</head><body> の骨組みで包む。
  dashboard_build.py が出すのは完全なHTMLなので、そのまま渡すと入れ子になる。
  ★ここでやるのは「包みを外す」だけ。★見た目・配色・スクリプトには手を入れない
  （既にあるデザインを尊重する。作り直さない）。

使い方
  python3 bin/dashboard_to_artifact.py <入力.html> <出力.html>

やること（3つだけ）
  1  <!DOCTYPE> / <html> / <head> / <body> の開閉タグを外す（title と style は残す）
  2  <meta http-equiv="refresh"> を外す（骨組みの外なので効かない。静的公開に不要）
  3  body の data-generated を .wrap へ移し、JSの参照先を差し替える
     （<body> タグが消えるので document.body.dataset.generated が読めなくなるため）
"""
import re, sys


def convert(html):
    m = re.search(r'<title>(.*?)</title>', html, re.S)
    title = m.group(1).strip() if m else 'ふくち。稼働盤'

    m = re.search(r'<style>(.*?)</style>', html, re.S)
    style = m.group(1) if m else ''

    m = re.search(r'<body([^>]*)>(.*)</body>', html, re.S)
    if not m:
        raise SystemExit('★<body> が見つからない。dashboard_build.py の出力形式が変わった可能性')
    body_attrs, body = m.group(1), m.group(2)

    gen = ''
    g = re.search(r'data-generated="([^"]+)"', body_attrs)
    if g:
        gen = g.group(1)
        # 生成時刻を .wrap へ載せ替える
        body = body.replace('<div class="wrap">',
                            '<div class="wrap" data-generated="%s">' % gen, 1)
    body = body.replace('document.body.dataset.generated',
                        "document.querySelector('.wrap').dataset.generated")

    return '<title>%s</title>\n<style>%s</style>\n%s\n' % (title, style, body)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise SystemExit('使い方: dashboard_to_artifact.py <入力.html> <出力.html>')
    out = convert(open(sys.argv[1], encoding='utf-8').read())
    open(sys.argv[2], 'w', encoding='utf-8').write(out)
    print('書き出し: %s (%d バイト)' % (sys.argv[2], len(out.encode('utf-8'))))
