"""python3 -m unittest test_intake_bc_rule  （このフォルダで実行）"""
import unittest

from intake_bc_rule import decide_by_company

# 受付タブで止まっていた10行（2026-11-26 実測）＋保留の4行
STUCK = [
    (34, "UPSTAJapan合同会社", "紙野一輝　執行役員", "まだ分からない", "B"),
    (38, "株式会社たすける", "代表取締役 リディティヨ様", "", "B"),
    (39, "株式会社Canvi ", "代表取締役社長 岡林優治", "まだ分からない", "B"),
    (40, "株式会社AMONA", "代表取締役　大和田優樹", "まだ分からない", "B"),
    (46, "株式会社YOMO", "中井", "まだ分からない", "B"),
    (59, "スマートコンテンツ", "辻", "", None),
    (60, "株式会社アトラス", "", "", "B"),
    (61, "株式会社八福神", "渡邊", "", "B"),
    (62, "特定非営利活動法人長居公園元気ネット", "チョウ", "", "B"),
    (63, "行政書士・社労士事務所", "", "", None),
    (64, "未登録", "", "", None),
    (65, "有璽(ビビッド田村)", "", "", None),
]


class Stuck10(unittest.TestCase):
    def test_each_row(self):
        for row, company, person, shohin, want in STUCK:
            got, reason = decide_by_company(company, person, shohin)
            self.assertEqual(got, want, f"{row}行目 {company}: {reason}")
            self.assertTrue(reason, f"{row}行目は理由が空")

    def test_count(self):
        ten = [r for r in STUCK if r[0] <= 63]
        self.assertEqual(sum(1 for r in ten if decide_by_company(*r[1:4])[0] == "B"), 8)

    def test_shohin_decides_is_left_to_existing_logic(self):
        self.assertEqual(decide_by_company("株式会社X", "", "福祉施設（toB）"), (None, ""))
        self.assertEqual(decide_by_company("", "山田", "保険・資産形成（toC）"), (None, ""))

    def test_marked_undecided_is_still_undecided(self):
        self.assertEqual(decide_by_company("株式会社Bring Flower", "", "まだ分からない（toB）")[0], "B")

    def test_fullwidth_and_abbr(self):
        self.assertEqual(decide_by_company("ＡＢＣ（株）", "", "")[0], "B")
        self.assertEqual(decide_by_company("Foo Inc.", "", "")[0], "B")

    def test_no_legal_form_stops_with_reason(self):
        got, reason = decide_by_company("ALLE", "中村", "まだ分からない")
        self.assertIsNone(got)
        self.assertIn("法人格が無い", reason)


if __name__ == "__main__":
    unittest.main()
