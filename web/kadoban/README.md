# 稼働盤の公開用（Vercel）

**中身の HTML はここに置かない。**`dashboard_build.py` が生成したものを
`bin/kadoban_deploy.sh` が組み立てて deploy する。ここにあるのは設定だけ。

- `vercel.json` … 検索避け（noindex）とキャッシュ無効。**★中身は社内の運用実態なので検索に載せない**
- 組み立て先 … `~/.vivid-relay/kadoban_site/`（git外・毎回作り直す）
- 経緯 … `memory/project_ops_dashboard_artifact.md`
