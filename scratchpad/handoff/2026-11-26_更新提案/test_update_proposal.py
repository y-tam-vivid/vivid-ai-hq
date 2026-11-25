"""python3 -m unittest test_update_proposal  （このフォルダで実行）"""
import datetime as dt
import unittest

import update_proposal as up

NOW = dt.datetime(2026, 11, 26, 9, 0)
CTX = up.Context(source="議事録の仕分け", source_url="https://docs.google.com/document/d/X",
                 customer_id="B-0408", person="大畑海太", company="人生の代理店(個人事業主)")
ROW_B0408 = {"社内顧客ID": "B-0408", "会社名": "人生の代理店(個人事業主)", "URL": "", "事業ライン": "",
             "備考": "", "都道府県": "", "電話番号": "0120-000-000"}


def col(r, name):
    return r[up.COL[name]]


class Classify(unittest.TestCase):
    def test_fill_empty_even_if_guess(self):
        rows = up.build_rows(CTX, ROW_B0408, [up.Fact("URL", "https://hp.life-agencypro.com/", "議事録AI要約")], NOW)
        self.assertEqual(col(rows[0], "種別"), up.TYPE_FILL)
        self.assertEqual(col(rows[0], "提案する値"), "https://hp.life-agencypro.com/")
        self.assertEqual(col(rows[0], "反映"), "未")

    def test_rewrite_guess_becomes_confirm_only_without_value(self):
        rows = up.build_rows(CTX, ROW_B0408, [up.Fact("電話番号", "06-1111-2222", "本人談")], NOW)
        self.assertEqual(col(rows[0], "種別"), up.TYPE_CONFIRM)
        self.assertEqual(col(rows[0], "提案する値"), "")
        self.assertIn("06-1111-2222", col(rows[0], "根拠"))

    def test_rewrite_sure(self):
        rows = up.build_rows(CTX, ROW_B0408, [up.Fact("電話番号", "06-1111-2222", "名刺", up.SURE)], NOW)
        self.assertEqual(col(rows[0], "種別"), up.TYPE_REWRITE)

    def test_same_value_after_normalize_is_skipped(self):
        rows = up.build_rows(CTX, ROW_B0408, [up.Fact("電話番号", "０１２０－０００－０００", "名刺", up.SURE)], NOW)
        self.assertEqual(rows, [])

    def test_never_and_out_of_scope_columns(self):
        facts = [up.Fact("担当", "田村", "x"), up.Fact("最新ステータス", "商談化", "x"), up.Fact("会社名", "別名", "x")]
        self.assertEqual(up.build_rows(CTX, ROW_B0408, facts, NOW), [])

    def test_relation_is_confirm_only(self):
        rows = up.build_rows(CTX, ROW_B0408, [up.Fact("関係区分_パートナー", "TRUE", "紹介し合う関係")], NOW)
        self.assertEqual(col(rows[0], "種別"), up.TYPE_CONFIRM)
        self.assertEqual(col(rows[0], "提案する値"), "")

    def test_sensitive_minutes_produce_nothing(self):
        ctx = up.Context(**{**CTX.__dict__, "sensitive_flag": "法的紛争"})
        self.assertEqual(up.build_rows(ctx, ROW_B0408, [up.Fact("URL", "https://a", "x")], NOW), [])

    def test_sensitive_words_in_value(self):
        rows = up.build_rows(CTX, ROW_B0408, [up.Fact("備考", "代表は通院中", "x")], NOW)
        self.assertEqual(rows, [])


class Merge(unittest.TestCase):
    def test_pending_same_item_annotates_instead_of_new_row(self):
        first = up.build_rows(CTX, ROW_B0408, [up.Fact("URL", "https://a.example/", "1回目")], NOW)
        second = up.build_rows(CTX, ROW_B0408, [up.Fact("URL", "https://a.example/", "2回目")], NOW)
        append, annotate = up.merge_pending(first, second)
        self.assertEqual(append, [])
        self.assertEqual(annotate[0][0], 2)
        self.assertIn("2回目", annotate[0][1])

    def test_rejected_row_does_not_block_new_proposal(self):
        first = up.build_rows(CTX, ROW_B0408, [up.Fact("URL", "https://a.example/", "1回目")], NOW)
        first[0][up.COL["確認"]] = up.NG_MARK
        second = up.build_rows(CTX, ROW_B0408, [up.Fact("URL", "https://a.example/", "2回目")], NOW)
        append, annotate = up.merge_pending(first, second)
        self.assertEqual(len(append), 1)
        self.assertEqual(annotate, [])


class Bulk(unittest.TestCase):
    def test_bulk_only_fill(self):
        rows = up.build_rows(CTX, ROW_B0408, [
            up.Fact("URL", "https://a.example/", "x"),
            up.Fact("電話番号", "06-1111-2222", "名刺", up.SURE),
            up.Fact("電話番号", "06-3333-4444", "本人"),
        ], NOW)
        numbered = list(enumerate(rows, start=2))
        self.assertEqual(up.bulk_ok_targets(numbered), [2])


class Apply(unittest.TestCase):
    def _rows(self):
        rows = up.build_rows(CTX, ROW_B0408, [
            up.Fact("URL", "https://a.example/", "x"),
            up.Fact("電話番号", "06-1111-2222", "名刺", up.SURE),
            up.Fact("関係区分_パートナー", "TRUE", "x"),
        ], NOW)
        for r in rows:
            r[up.COL["確認"]] = up.OK_MARK
        return rows

    def test_plan(self):
        plans = up.plan_apply(self._rows(), {"B-0408": ROW_B0408})
        self.assertEqual([p[1] for p in plans], ["write", "write", "done_no_write"])

    def test_ledger_changed_after_proposal_fails(self):
        changed = {**ROW_B0408, "URL": "https://other.example/"}
        plans = up.plan_apply(self._rows(), {"B-0408": changed})
        self.assertEqual(plans[0][1], "fail")

    def test_unapproved_and_done_rows_are_ignored(self):
        rows = self._rows()
        rows[0][up.COL["確認"]] = up.HOLD_MARK
        rows[1][up.COL["反映"]] = "済"
        plans = up.plan_apply(rows, {"B-0408": ROW_B0408})
        self.assertEqual(len(plans), 1)

    def test_missing_customer_fails(self):
        plans = up.plan_apply(self._rows(), {})
        self.assertTrue(all(p[1] in ("fail", "done_no_write") for p in plans))

    def test_hand_typed_rewrite_guess_is_refused(self):
        rows = self._rows()
        rows[1][up.COL["確度"]] = up.GUESS
        plans = up.plan_apply(rows, {"B-0408": ROW_B0408})
        self.assertEqual(plans[1][1], "fail")


if __name__ == "__main__":
    unittest.main()
