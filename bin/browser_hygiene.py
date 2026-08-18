#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ブラウザ衛生の週次チェック（読み取り専用）。

★このファイルがルールの正本。文章側に同じルールを書かないこと（二重管理になる）。

何を見るか ── 2026-08-17 に実測して決めた「軽い状態」を、毎週まだ保てているかだけ見る。

    ① 構造で持つ    全ページにコードを注入する拡張の数
                     （タブ数との掛け算になるので、ここが唯一の大物）
    ② 既定値で持つ  メモリセーバー / 常にアクティブなサイト / 起動時のタブ復元
    ③ 人が見る      重量級タブ・同名タブの重複（判定しない。並べるだけ）

信号の意味 ── **慢性的な黄色を出さない**のが設計の要。毎週同じ警告が出る仕組みは、
出し続けた時点で読まれなくなる（＝信号が死ぬ）。だから2本立てにする。

    🔴  閾値を超えた            例: 注入が7個以上 / 起動時にタブを全部復元する
    🟡  先週から変わった        例: 注入が2→4に増えた / メモリセーバーが切られた
    🟢  先週と同じで閾値内
    ⚪  報告のみ（判定しない）  例: MV2拡張の残数・常にアクティブなサイト・重いタブ

「常にアクティブにするサイト」を悪と決めつけない。業務上わざと入れることがある。
勝手に判定せず、**増減したときだけ**知らせる。

設計の約束:
  - **読むだけ。ブラウザの設定は絶対に書き換えない。** 直すのは人の手。
  - **起動していないブラウザを起動しない。** AppleScript は `tell application` した時点で
    アプリを起動してしまうので、必ず先に pgrep で生存を確かめてから呼ぶ。
  - 絶対値で判定できないもの（メモリセーバーの enum など）は、
    **既知の良い値からの変化**として見る。意味を推測で埋めない。
  - Chrome が自分で入れる部品拡張（ウェブストア決済など）は人が消せないので数えない。
  - 心拍は成功でも警告でも必ず打つ。沈黙＝レジスタ側で 🔴 になる。

使い方:
    python3 browser_hygiene.py            # 判定して心拍を打つ。前回状態を更新する
    python3 browser_hygiene.py --dry-run  # 画面に出すだけ。心拍も前回状態も触らない

Python 3.9 互換（Mac mini が 3.9.6）。
"""

import json
import os
import subprocess
import sys
from collections import Counter

BEAT_NAME = "ブラウザ衛生の週次チェック"   # ⚙️自動処理レジスタの「処理名」と完全一致させる
RELAY = os.path.expanduser("~/.vivid-relay")
STATE = os.path.join(RELAY, "browser_hygiene_state.json")   # 前回の状態（機械が書く）

# ── ルールの正本（閾値） ───────────────────────────────────────────
MAX_INJECTORS = 3           # 全ページ注入する拡張の上限。4〜6で🟡、7以上で🔴
WANT_MEMORY_SAVER = (2, 2)  # (state, aggressiveness) = オン・最大。2026-08-17実測の良い値
BROAD = {"<all_urls>", "*://*/*", "http://*/*", "https://*/*"}
COMPONENT_LOCATION = 5      # Chrome内部の部品拡張。人が消せないので数えない

# 見つかったものだけ検査する（将来 Arc や Dia が入っても行を足すだけ）
CHROMIUM = [
    ("Google Chrome", "Google/Chrome"),
    ("Microsoft Edge", "Microsoft Edge"),
    ("Brave", "BraveSoftware/Brave-Browser"),
    ("Vivaldi", "Vivaldi"),
    ("Arc", "Arc/User Data"),
]

RED, YEL, GRN, GRY = "🔴", "🟡", "🟢", "⚪"
findings = []   # (信号, 見出し, 詳細)
now = {}        # 今回の状態。前回と突き合わせて「変化」を出す


def note(sig, head, detail=""):
    findings.append((sig, head, detail))
    print("  %s %-22s %s" % (sig, head, detail))


def load(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def is_running(proc):
    try:
        return subprocess.call(["pgrep", "-x", proc],
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL) == 0
    except Exception:
        return False


def changed(key, value, head, fmt=str):
    """前回と違えば🟡。同じなら黙る。初回は基準を置くだけで鳴らさない。"""
    now[key] = value
    if PREV is None or key not in PREV:
        return False
    if PREV[key] != value:
        note(YEL, head, "先週 %s → 今週 %s" % (fmt(PREV[key]), fmt(value)))
        return True
    return False


def ext_name(eid, base, prof, manifest):
    """拡張の表示名。__MSG_ は _locales から引く（引けなければIDの頭）。"""
    n = (manifest or {}).get("name", "")
    if n and not n.startswith("__MSG_"):
        return n
    d = os.path.join(base, prof, "Extensions", eid)
    try:
        vers = sorted(os.listdir(d))
    except Exception:
        return eid[:12]
    if not vers:
        return eid[:12]
    key = n[6:].rstrip("_") if n.startswith("__MSG_") else None
    if key:
        for loc in ("ja", "en", "en_US"):
            msgs = load(os.path.join(d, vers[-1], "_locales", loc, "messages.json"))
            if msgs:
                for k in msgs:
                    if k.lower() == key.lower():
                        return msgs[k].get("message", n)
    return eid[:12]


# ── ① 構造: 全ページに注入する拡張 ─────────────────────────────────
def check_injectors(base, prof, prof_name):
    sec = load(os.path.join(base, prof, "Secure Preferences"))
    if sec is None:
        return
    setts = sec.get("extensions", {}).get("settings", {})
    inject, mv2, total = [], [], 0
    for eid, v in setts.items():
        if not os.path.isdir(os.path.join(base, prof, "Extensions", eid)):
            continue
        if v.get("was_installed_by_default") or v.get("location") == COMPONENT_LOCATION:
            continue                      # Chromeの部品。人が消せないので数えない
        total += 1
        mani = v.get("manifest", {}) or {}
        name = ext_name(eid, base, prof, mani)
        if mani.get("manifest_version") == 2:
            mv2.append(name)
        wants = set()
        for cs in (mani.get("content_scripts") or []):
            wants |= set(cs.get("matches") or [])
        wants |= set(mani.get("host_permissions") or [])
        if not (wants & BROAD):
            continue
        act = v.get("active_permissions", {}) or {}
        have = set(act.get("scriptable_host") or []) | set(act.get("explicit_host") or [])
        if v.get("withholding_permissions") is True or not (have & BROAD):
            continue                      # クリック時のみ / 特定サイトのみ＝注入されない
        inject.append(name)

    if total == 0:
        return                            # 拡張を持たないプロファイルは黙る

    n = len(inject)
    key = "inject:" + prof_name
    if n > 6:
        note(RED, "全ページ注入の拡張",
             "%s: %d個（上限%d）%s" % (prof_name, n, MAX_INJECTORS, " / ".join(sorted(inject))))
        now[key] = sorted(inject)
    elif not changed(key, sorted(inject), "全ページ注入の拡張",
                     lambda v: "%d個" % len(v)):
        sig = GRN if n <= MAX_INJECTORS else YEL
        note(sig, "全ページ注入の拡張",
             "%s: %d個（上限%d）%s" % (prof_name, n, MAX_INJECTORS, " / ".join(sorted(inject))))
    if mv2:
        note(GRY, "MV2拡張の残存",
             "%s: %d個。いずれChromeが動かさなくなる: %s"
             % (prof_name, len(mv2), " / ".join(sorted(mv2))))


# ── ② 既定値: メモリセーバー / 例外サイト / 起動時復元 ──────────────
def check_defaults(label, base):
    ls = load(os.path.join(base, "Local State"))
    if ls is None:
        note(GRY, "メモリセーバー", "%s: Local State を読めない" % label)
        return {}
    pt = (ls.get("performance_tuning") or {}).get("high_efficiency_mode") or {}
    got = [pt.get("state"), pt.get("aggressiveness")]
    key = "saver:" + label
    if not changed(key, got, "メモリセーバー",
                   lambda v: "state/aggr=%s/%s" % tuple(v)):
        if tuple(got) == WANT_MEMORY_SAVER:
            note(GRN, "メモリセーバー", "%s: オン・最大" % label)
        else:
            note(YEL, "メモリセーバー",
                 "%s: %s（期待 %s）chrome://settings/performance を確認"
                 % (label, got, list(WANT_MEMORY_SAVER)))
    return ls.get("profile", {}).get("info_cache", {}) or {}


def check_profile_prefs(base, prof, prof_name):
    pr = load(os.path.join(base, prof, "Preferences"))
    if pr is None:
        return
    exc = ((pr.get("performance_tuning") or {}).get("tab_discarding") or {}).get("exceptions") or []
    exc = sorted(map(str, exc))
    if not changed("exempt:" + prof_name, exc, "常にアクティブなサイト",
                   lambda v: "%d件%s" % (len(v), ("(" + ", ".join(v) + ")") if v else "")):
        if exc:
            note(GRY, "常にアクティブなサイト",
                 "%s: %d件。このサイトはメモリが解放されない: %s"
                 % (prof_name, len(exc), ", ".join(exc)[:200]))
    if (pr.get("session") or {}).get("restore_on_startup") == 1:
        note(RED, "起動時のタブ復元", "%s: 前回のタブを全部開き直す設定" % prof_name)


# ── ③ 人が見る: 重複タブ・重量級タブ ────────────────────────────────
def check_tabs():
    if not is_running("Google Chrome"):
        note(GRY, "タブの点検", "Chromeが起動していないので省略（起動はさせない）")
        return
    script = ('tell application "Google Chrome"\n'
              '  set o to ""\n'
              '  repeat with w in windows\n'
              '    repeat with t in tabs of w\n'
              '      set o to o & (title of t) & linefeed\n'
              '    end repeat\n'
              '  end repeat\n'
              '  return o\n'
              'end tell')
    try:
        out = subprocess.check_output(["osascript", "-e", script],
                                      stderr=subprocess.DEVNULL, timeout=30)
        titles = [t.strip() for t in out.decode("utf-8", "replace").splitlines() if t.strip()]
    except Exception as e:
        note(GRY, "タブの点検", "タイトルを取得できず: %r" % e)
        return

    dup = [(t, c) for t, c in Counter(titles).items() if c > 1]
    if dup:
        note(YEL, "同じタブの重複",
             "%d組: %s" % (len(dup),
                          " / ".join("%s ×%d" % (t[:36], c)
                                     for t, c in sorted(dup, key=lambda x: -x[1]))))
    else:
        note(GRN, "同じタブの重複", "なし（タブ %d枚）" % len(titles))

    try:
        ps = subprocess.check_output(
            "ps axo rss,args | grep '[G]oogle Chrome Helper (Renderer)' | sort -rn | head -5",
            shell=True, timeout=30).decode("utf-8", "replace")
        tops = [int(l.split()[0]) / 1024 for l in ps.splitlines() if l.split()]
        if tops:
            note(GRY, "重いタブ 上位5枚",
                 " / ".join("%.0fMB" % m for m in tops)
                 + "  ← どのタブかは タスクマネージャ（メニュー→その他のツール）で")
    except Exception:
        pass


PREV = None


def main():
    global PREV
    dry = "--dry-run" in sys.argv
    PREV = load(STATE)

    print("=== ブラウザ衛生の週次チェック ===")
    if PREV is None:
        print("（前回の記録が無いので、今回は基準を置くだけ。変化の検出は次回から）")
    seen = 0
    for label, rel in CHROMIUM:
        base = os.path.expanduser("~/Library/Application Support/" + rel)
        if not os.path.exists(os.path.join(base, "Local State")):
            continue
        seen += 1
        print("\n[%s]" % label)
        info = check_defaults(label, base)
        for prof in sorted(info.keys()):
            if not os.path.isdir(os.path.join(base, prof)):
                continue
            pname = info[prof].get("name", prof)
            check_injectors(base, prof, pname)
            check_profile_prefs(base, prof, pname)
    if seen == 0:
        note(GRY, "対象ブラウザ", "Chromium系が1つも見つからない")

    print("\n[タブ（実行時点のスナップショット）]")
    check_tabs()

    reds = sum(1 for s, _, _ in findings if s == RED)
    yels = sum(1 for s, _, _ in findings if s == YEL)
    heads = [h for s, h, _ in findings if s in (RED, YEL)]
    summary = "%s%d %s%d" % (RED, reds, YEL, yels)
    if heads:
        summary += " / " + " ・ ".join(sorted(set(heads)))
    else:
        summary += " / 先週から変化なし"
    print("\n=== まとめ: %s ===" % summary)

    if dry:
        print("(--dry-run のため心拍も前回状態も更新しません)")
        return 0

    try:
        with open(STATE, "w", encoding="utf-8") as f:
            json.dump(now, f, ensure_ascii=False, indent=1, sort_keys=True)
    except Exception as e:
        print("[state] 保存できず: %r" % e, file=sys.stderr)

    sys.path.insert(0, RELAY)
    try:
        from heartbeat import beat
        beat(BEAT_NAME, "警告" if (reds or yels) else "成功", summary)
    except Exception as e:      # 心拍で本体を落とさない
        print("[heartbeat] 送信できず: %r" % e, file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
