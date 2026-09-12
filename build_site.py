#!/usr/bin/env python3
"""
外匯網站建置腳本
- 為 forex_reports/*.html 加上導覽列（最新報表 / 歷史報表）
- 產生 index.html（= 最新一期報表的完整拷貝）
- 產生 history.html（掃描 forex_reports/ 目錄，由新到舊列出所有日期）
"""
import re
import glob
import os

SITE_DIR = os.path.dirname(os.path.abspath(__file__))
# 1. 資料夾路徑修改為 forex_reports
REPORTS_DIR = os.path.join(SITE_DIR, "forex_reports")

NAV_CSS = """
  .site-nav { max-width: 1100px; margin: 0 auto 18px; display: flex; gap: 16px; font-size: 13px; }
  .site-nav a { color: #1976d2; text-decoration: none; font-weight: 700; padding: 6px 14px; background: #ffffff; border: 1px solid #bbdefb; border-radius: 4px; }
  .site-nav a:hover { background: #1976d2; color: #fff; }
  .site-nav a.active { background: #1976d2; color: #fff; }
"""

def date_from_filename(path):
    # 2. 支援「每日外匯市場報表_YYYY-MM-DD.html」格式抓取日期
    m = re.search(r"(\d{4}-\d{2}-\d{2})\.html$", path)
    return m.group(1) if m else None

def inject_nav(html, latest_href, history_href, active):
    if "</style>" in html:
        html = html.replace("</style>", NAV_CSS + "</style>", 1)
    nav_html = (
        '\n<nav class="site-nav">'
        f'<a href="{latest_href}"{" class=\"active\"" if active=="latest" else ""}>最新報表</a>'
        f'<a href="{history_href}"{" class=\"active\"" if active=="history" else ""}>歷史報表</a>'
        '</nav>\n'
    )
    if '<div class="wrap">' in html:
        html = html.replace('<div class="wrap">', '<div class="wrap">' + nav_html, 1)
    else:
        html = html.replace("<body>", "<body>" + nav_html, 1)
    return html

def main():
    report_files = sorted(glob.glob(os.path.join(REPORTS_DIR, "*.html")))
    dated_files = []
    for f in report_files:
        d = date_from_filename(f)
        if d:
            dated_files.append((d, f))
    dated_files.sort(key=lambda x: x[0])

    if not dated_files:
        print("forex_reports/ 內沒有找到符合格式的檔案，中止。")
        return

    # 1) 幫每個報表加上導覽列
    for d, f in dated_files:
        with open(f, "r", encoding="utf-8") as fh:
            html = fh.read()
        if 'class="site-nav"' not in html:
            html = inject_nav(html, latest_href="../index.html", history_href="../history.html", active=None)
            with open(f, "w", encoding="utf-8") as fh:
                fh.write(html)
            print(f"已加上導覽列: forex_reports/{os.path.basename(f)}")
        else:
            print(f"已存在導覽列，略過: forex_reports/{os.path.basename(f)}")

    # 2) 產生 index.html
    latest_date, latest_file = dated_files[-1]
    with open(latest_file, "r", encoding="utf-8") as fh:
        latest_html = fh.read()
    index_html = latest_html.replace('href="../index.html"', 'href="index.html"') \
                            .replace('href="../history.html"', 'href="history.html"')
    index_html = index_html.replace('<a href="index.html">最新報表</a>',
                                    '<a href="index.html" class="active">最新報表</a>')
    index_path = os.path.join(SITE_DIR, "index.html")
    with open(index_path, "w", encoding="utf-8") as fh:
        fh.write(index_html)
    print(f"已產生 index.html（內容 = {latest_date} 外匯報表）")

    # 3) 產生 history.html
    dated_files_desc = list(reversed(dated_files))
    list_items = "\n".join(
        f'        <li><a href="forex_reports/{os.path.basename(f)}">{d.replace("-", "/")} 外匯市場報表</a></li>'
        for d, f in dated_files_desc
    )
    history_html = f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<title>每日外匯市場報表歷史紀錄</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: #f0f4f8; color: #333333; font-family: "Noto Sans TC", "PingFang TC", "Microsoft JhengHei", sans-serif; padding: 32px 24px; }
  .wrap { max-width: 700px; margin: 0 auto; }
  header { display: flex; justify-content: space-between; align-items: baseline; border-bottom: 2px solid #1976d2; padding-bottom: 14px; margin-bottom: 22px; }
  header h1 { font-size: 20px; letter-spacing: 1px; color: #1976d2; }
  .site-nav { display: flex; gap: 16px; font-size: 13px; margin-bottom: 22px; }
  .site-nav a { color: #1976d2; text-decoration: none; font-weight: 700; padding: 6px 14px; background: #ffffff; border: 1px solid #bbdefb; border-radius: 4px; }
  .site-nav a:hover { background: #1976d2; color: #fff; }
  .site-nav a.active { background: #1976d2; color: #fff; }
  ul { list-style: none; background: #ffffff; border: 1px solid #bbdefb; border-radius: 6px; overflow: hidden; }
  li { border-bottom: 1px solid #bbdefb; }
  li:last-child { border-bottom: none; }
  li a { display: block; padding: 14px 20px; color: #1565c0; text-decoration: none; font-family: "JetBrains Mono", monospace; font-size: 15px; font-weight: 600; transition: background 0.2s; }
  li a:hover { background: #e3f2fd; color: #0d47a1; }
  footer { text-align: center; font-size: 11px; color: #78909c; margin-top: 20px; padding-top: 12px; border-top: 1px solid #bbdefb; }
</style>
</head>
<body>
<div class="wrap">
  <header>
    <h1>每日外匯市場報表歷史紀錄</h1>
  </header>
  <nav class="site-nav">
    <a href="index.html">最新報表</a>
    <a href="history.html" class="active">歷史報表</a>
  </nav>
  <ul>
{list_items}
  </ul>
  <footer>共 {len(dated_files_desc)} 期報表</footer>
</div>
</body>
</html>
"""
    history_path = os.path.join(SITE_DIR, "history.html")
    with open(history_path, "w", encoding="utf-8") as fh:
        fh.write(history_html)
    print(f"已產生 history.html（共 {len(dated_files_desc)} 期）")

if __name__ == "__main__":
    main()
