import calendar
import zipfile
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any


def find_values(
    obj: Any,
    key: str,
    is_predict_one: bool = False,
    key_white_list: list[str] = None,
    key_black_list: list[str] = None,
) -> Any | list[Any]:
    if not key_white_list:
        key_white_list = []
    if not key_black_list:
        key_black_list = []

    def _inner_helper(inner_obj: Any, inner_key: str, inner_result: list) -> list:
        if isinstance(inner_obj, dict) and (inner_dict := inner_obj):
            for k, v in inner_dict.items():
                if k == inner_key:
                    inner_result.append(v)
                if key_white_list and (k not in key_white_list):
                    continue
                if k in key_black_list:
                    continue
                inner_result.extend(_inner_helper(v, inner_key, []))
        if isinstance(inner_obj, list) and (inner_list := inner_obj):
            for element in inner_list:
                inner_result.extend(_inner_helper(element, inner_key, []))
        return inner_result

    result = _inner_helper(obj, key, [])
    if not is_predict_one:
        return result

    if len(result) == 0:
        raise ValueError(f"Value of key='{key}' is not found.")
    if len(result) > 1:
        raise ValueError(f"Values of key='{key}' are multiple found.")
    return result[0]


def to_jst(utc: datetime) -> datetime:
    if not isinstance(utc, datetime):
        raise ValueError("utc must be datetime.")
    jst = utc + timedelta(hours=9)
    return jst


def normalize_date_at(date_at_str: str) -> str:
    """日時文字列を日本時間に変換する

    Args:
        date_at_str (str): ISOフォーマットの日時文字列(UTC)

    Returns:
        str: ISOフォーマットの日時文字列(JST)
    """
    result = to_jst(datetime.fromisoformat(date_at_str)).isoformat()
    if result.endswith("+00:00"):
        result = result[:-6]
    return result


def tags_join(tags: list[str]) -> str:
    """タグ配列を文字列に整形する

    Args:
        tags (list[str]): webページから取得したタグ配列

    Note:
        整形について：
        タグの中の"author_tag_" は削除する
        "approved" を含むタグは出力に含めない
        タグはすべてアルファベット小文字に変換する
        区切り文字は '|' とする

    Returns:
        str: 整形後の文字列
    """
    if not isinstance(tags, list):
        return ""
    if not all([isinstance(tag, str) for tag in tags]):
        return ""

    sanitized_tags: list[str] = []
    for tag in tags:
        t = tag
        if t.startswith("author_tag_"):
            t = t.replace("author_tag_", "")
        if "approved" in tag:
            continue
        sanitized_tags.append(t.lower())
    return "|".join(sanitized_tags)


def tags_split(tags_string: str) -> list[str]:
    """文字列をタグ配列として解釈する

    Args:
        tags_string: 整形済の文字列

    Returns:
        list[str]: タグ配列
    """
    if not isinstance(tags_string, str):
        return []
    return tags_string.split("|")


def manage_cache_file(base_path: Path) -> None:
    """base_path 内のファイルを以下のように仕分けしてアーカイブする

    (1)更新日時基準で、同じ日付に更新されたファイルはyyyymmdd形式の名前で一つのzipファイルにして元ファイルは削除する
    (2)一月分たまったらyyyymmddのzipをyyyymmのzipに再度まとめる
    (3)1年以上前のyyyymmのzipファイルはyyyyのzipファイルにまとめる

    Args:
        base_path (Path): 対象ディレクトリパス（キャッシュファイルパスを想定）
    """
    # 入力チェック
    base_path = Path(base_path)
    if not base_path.is_dir():
        return

    # ---------------------------
    # 日単位でzip化（yyyymmdd.zip）
    # ---------------------------
    files_by_day: defaultdict[str, list[Path]] = defaultdict(list)
    now_date = datetime.now()
    now_date_str = now_date.strftime("%Y%m%d")

    # ディレクトリ内を走査
    for p in base_path.rglob("*"):
        # ファイルかつzipでないものを収集
        if p.is_file() and not p.suffix == ".zip":
            # 更新日時基準で日付単位でパスを記録する
            mtime = datetime.fromtimestamp(p.stat().st_mtime)
            key = mtime.strftime("%Y%m%d")
            if key == now_date_str:
                # 本日分のログは何もせずスルー
                continue
            files_by_day[key].append(p)

    # 記録した日付単位ごとに各ファイルをアーカイブする
    for day, files in files_by_day.items():
        zip_path = base_path / f"{day}.zip"
        with zipfile.ZipFile(zip_path, "a", compression=zipfile.ZIP_DEFLATED) as zf:
            for f in files:
                zf.write(f, arcname=f.name)
                f.unlink()  # 元ファイル削除

    # ---------------------------
    # 月単位でzip化（yyyymm.zip）
    # ---------------------------
    target_ym = []
    daily_zips: defaultdict[str, list[Path]] = defaultdict(list)

    # 日付のzipの数で判定すると不具合等で日付が疎になったときにうまく判定できないため
    # 月の最終日を格納したzipが存在するか確認して
    # その年月を対象月とする
    for p in base_path.glob("*.zip"):
        if len(p.stem) == 8:  # yyyymmdd
            year = p.stem[:4]
            month = p.stem[4:6]
            day = p.stem[6:]
            days_of_month = calendar.monthrange(int(year), int(month))[1]  # 28~31
            if int(day) == int(days_of_month):
                target_ym.append(f"{year}{month}")

    # 対象月を名前に含むzipファイルのパスを格納する
    if target_ym:
        for p in base_path.glob("*.zip"):
            if len(p.stem) == 8:  # yyyymmdd
                ym = p.stem[:6]
                if ym in target_ym:
                    daily_zips[ym].append(p)

    # 記録した対象月ごとに各ファイルをアーカイブする
    for ym, zips in daily_zips.items():
        month_zip = base_path / f"{ym}.zip"
        with zipfile.ZipFile(month_zip, "a", compression=zipfile.ZIP_DEFLATED) as zf:
            for z in zips:
                zf.write(z, arcname=z.name)
                z.unlink()

    # ---------------------------
    # 年単位でzip化（yyyy.zip）
    # ---------------------------
    THRESHOLD_DAYS = 365
    monthly_zips: defaultdict[str, list[Path]] = defaultdict(list)

    # 年月で格納されているファイルを対象に
    # THRESHOLD_DAYS 以前のものならば対象年とする
    for p in base_path.glob("*.zip"):
        if len(p.stem) == 6:  # yyyymm
            year = p.stem[:4]
            zip_date = datetime.strptime(p.stem, "%Y%m")
            if now_date - zip_date > timedelta(days=THRESHOLD_DAYS):
                monthly_zips[year].append(p)

    # 記録した対象年ごとに各ファイルをアーカイブする
    for year, zips in monthly_zips.items():
        year_zip = base_path / f"{year}.zip"
        with zipfile.ZipFile(year_zip, "a", compression=zipfile.ZIP_DEFLATED) as zf:
            for z in zips:
                zf.write(z, arcname=z.name)
                z.unlink()

    return
