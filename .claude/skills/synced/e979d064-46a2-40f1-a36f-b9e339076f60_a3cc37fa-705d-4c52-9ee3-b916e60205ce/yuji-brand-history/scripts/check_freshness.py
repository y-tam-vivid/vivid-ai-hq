#!/usr/bin/env python3
"""
ブランドヒストリーSkillの鮮度チェック。
SKILL.md冒頭の「最終更新日」から現在までの経過月数を計算し、
推奨更新サイクル（6か月）を超えていれば警告を出す。
"""
import datetime
import os
import re
import sys

RECOMMENDED_CYCLE_MONTHS = 6

def find_skill_md():
    # スクリプトの一つ上の階層にSKILL.mdがある想定
    here = os.path.dirname(os.path.abspath(__file__))
    candidate = os.path.join(here, "..", "SKILL.md")
    candidate = os.path.normpath(candidate)
    if os.path.exists(candidate):
        return candidate
    # フォールバック: カレントディレクトリ
    if os.path.exists("SKILL.md"):
        return "SKILL.md"
    return None

def get_last_updated(skill_md_path):
    with open(skill_md_path, encoding="utf-8") as f:
        text = f.read()
    m = re.search(r"最終更新日[:：]\s*(\d{4})-(\d{2})-(\d{2})", text)
    if not m:
        return None
    y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
    return datetime.date(y, mo, d)

def months_between(start, end):
    return (end.year - start.year) * 12 + (end.month - start.month) - (1 if end.day < start.day else 0)

def main():
    skill_md = find_skill_md()
    if not skill_md:
        print("[鮮度チェック] SKILL.mdが見つかりませんでした。手動で最終更新日を確認してください。")
        return
    last = get_last_updated(skill_md)
    if not last:
        print("[鮮度チェック] 最終更新日を読み取れませんでした。手動で確認してください。")
        return
    today = datetime.date.today()
    elapsed = months_between(last, today)
    print(f"[鮮度チェック] 最終更新日: {last.isoformat()} / 本日: {today.isoformat()} / 経過: 約{elapsed}か月")
    if elapsed >= RECOMMENDED_CYCLE_MONTHS:
        print("=" * 60)
        print(f"⚠️  警告: 前回更新から約{elapsed}か月が経過しています（推奨サイクル: {RECOMMENDED_CYCLE_MONTHS}か月）。")
        print("    以下の項目に変更がないか、田村氏に確認を促してください:")
        print("    ・肩書き／役職")
        print("    ・グループ内の法人数と設立状況（特に非営利法人）")
        print("    ・運営施設数")
        print("    ・共同研究／倫理審査の進捗")
        print("    ・対外公開可となった情報の範囲")
        print("    確認の上、SKILL.md冒頭の『最終更新日』と各referencesファイルを更新してください。")
        print("=" * 60)
    else:
        remaining = RECOMMENDED_CYCLE_MONTHS - elapsed
        print(f"[鮮度チェック] 情報は新しい状態です（次回更新目安まで約{remaining}か月）。")

if __name__ == "__main__":
    main()
