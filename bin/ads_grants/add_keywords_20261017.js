/**
 * こどもステーション Ad Grants ─ 2026-10-17 キーワードの追加（一回きり）
 * 理由   10/7〜10/17 表示0。既存32語の大半が「無効：検索ボリュームが少ない」（地名＋3語のフレーズ一致）。
 *        2語の広めの言葉を足し、地域はキャンペーンの地域設定で絞る。既存語は消さない。
 * 実行   「AdGrants 書き出し」の中身を一時的にこれへ替えて実行 → 直後に export_script.js へ戻す
 * DRY    true のあいだは書かない（地域設定と、足す予定の語を Logger に出すだけ）
 */
var DRY = true;
var PLAN = {
  'みんなの食堂（こども食堂）': {
    '広告グループ 1 個': ['子ども食堂 近く', 'こども食堂 近く', '子ども食堂 大阪', 'こども食堂 大阪', '子ども食堂 無料'],
    'ボランティア': ['子ども食堂 ボランティア', 'こども食堂 ボランティア', 'ボランティア 子ども', 'ボランティア募集 子ども']
  },
  'こども向けのくらぶ・教室': {
    '科学・図工・英語': ['科学教室 子ども', '実験教室 小学生', '図工教室 子ども', '子ども 英語教室', '習い事 小学生'],
    '習字': ['習字教室 子ども', '書道教室 子ども', '習字 小学生', '書道 小学生'],
    '学びの居場所': ['子ども 居場所', '放課後 居場所', '学習支援 中学生', '無料 学習支援']
  },
  '冬のイベント（もちつき・人形劇）': {
    'もちつき大会': ['もちつき大会 子ども', '餅つき大会 大阪', 'もちつき イベント', '餅つき イベント'],
    '人形劇': ['人形劇 子ども', '人形劇 公演', '親子 観劇', '人形劇 大阪']
  }
};

function main() {
  var added = 0, skipped = 0;
  for (var cname in PLAN) {
    var cit = AdsApp.campaigns().withCondition("campaign.name = '" + cname + "'").get();
    if (!cit.hasNext()) { Logger.log('★キャンペーンが無い: ' + cname); continue; }
    var camp = cit.next();
    var locs = [];
    var lit = camp.targeting().targetedLocations().get();
    while (lit.hasNext()) { var l = lit.next(); locs.push(l.getName() + '(' + l.getTargetType() + ')'); }
    var pit = camp.targeting().targetedProximities().get();
    while (pit.hasNext()) { var p = pit.next(); locs.push('半径' + p.getRadius() + p.getRadiusUnits()); }
    Logger.log('■ ' + cname + ' 地域: ' + (locs.length ? locs.join('、') : '★指定なし（全域）'));
    for (var gname in PLAN[cname]) {
      var git = camp.adGroups().withCondition("ad_group.name = '" + gname + "'").get();
      if (!git.hasNext()) { Logger.log('  ★広告グループが無い: ' + gname); continue; }
      var g = git.next();
      var have = {};
      var kit = g.keywords().get();
      while (kit.hasNext()) have[kit.next().getText()] = 1;
      PLAN[cname][gname].forEach(function (t) {
        var kw = '"' + t + '"';
        if (have[kw]) { skipped++; Logger.log('  済 ' + gname + ' ' + kw); return; }
        Logger.log('  ' + (DRY ? '予定 ' : '追加 ') + gname + ' ' + kw);
        if (!DRY) {
          var op = g.newKeywordBuilder().withText(kw).build();
          if (!op.isSuccessful()) Logger.log('  ★失敗 ' + kw + ' ' + op.getErrors().join(' / '));
          else added++;
        }
      });
    }
  }
  Logger.log('完了 追加' + added + ' 既存' + skipped + (DRY ? '（DRY）' : ''));
}
