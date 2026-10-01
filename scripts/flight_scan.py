#!/usr/bin/env python3
"""境内交通深链网格生成器 — trip-planner（境内版）的一部分。

本 skill 仅支持境内行程,且不再使用任何境外服务:国内没有免钥的机票票价 API
(携程/去哪儿不开放公开票价端点,抓取搜索页会被反爬),因此本脚本不做任何网络
请求,只把日期网格翻译成可直接点开的国内 OTA 深链,价格由用户点开链接核对 —
"—, 点链接核对"的诚实标注,绝不猜价(硬规则)。

Examples:
  # 往返,行程 10-15 晚,出发日 +/- 2 天:机票(携程/去哪儿/Trip.com) + 火车(携程火车票)
  python3 flight_scan.py --from PVG --to KMG --depart 2026-10-01 --nights 10-15 --flex 2
  # 单程(开放式行程分段各跑一次)
  python3 flight_scan.py --from KMG --to XIY --depart 2026-10-14 --oneway
  # 只要火车(高铁/动车)深链
  python3 flight_scan.py --from 北京南 --to 上海虹桥 --depart 2026-10-01 --oneway --rail
  # 2 人
  python3 flight_scan.py --from PEK --to CTU --depart 2026-10-01 --nights 7 --adults 2

说明:
  * --from/--to 接受机场三字码(如 PVG/KMG)或中文站名/城市名;OTA 搜索页两者
    都能解析,但**深链以打开后的页面为准**,写进计划 legs[] 前先点开核对。
  * 每个日期组合给 机票 3 条(携程 / Trip.com / 去哪儿)+ 火车 1 条(携程火车票,
    12306 需要站名电报码,常规入口走携程或官方 App/小程序;15 天预售、候补优先)。
  * 深链打开后核对:价格、时刻、直飞/中转、行李额度。≥2 源规则在境内改为
    "携程 + 去哪儿/航司官网/Trip.com 任一"。
"""
import argparse
import sys
from datetime import date, timedelta
from urllib.parse import quote


def parse_nights(s):
    if "-" in s:
        a, b = s.split("-", 1)
        return list(range(int(a), int(b) + 1))
    return [int(s)]


def flight_links(orig, dest, dep, ret, adults):
    """国内机票深链(携程/Trip.com/去哪儿)。无免钥票价 API,价格点开核对。"""
    o, d = orig.lower(), dest.lower()
    trip_type = "roundtrip" if ret else "oneway"
    ctrip = ("https://flights.ctrip.com/online/list/{}-{}-{}?depdate={}".format(
        trip_type, o, d, dep)
        + ("&retdate={}".format(ret) if ret else ""))
    tripcom = ("https://www.trip.com/flights/showfarefirst?dcity={}&acity={}"
               "&ddate={}&triptype={}&quantity={}").format(
        quote(orig), quote(dest), dep, "RT" if ret else "OW", adults) \
        + ("&rdate={}".format(ret) if ret else "")
    qunar = ("https://flight.qunar.com/site/inter/oneway_arrival.htm"
             "?searchType=OneWayFlight&from={}&to={}&departureDate={}"
             "&fromCode={}&toCode={}".format(
                 quote(orig), quote(dest), dep,
                 quote(orig), quote(dest)))
    return "  机票·携程  {}\n  机票·Trip.com  {}\n  机票·去哪儿  {}".format(
        ctrip, tripcom, qunar)


# 12306 车站电报码（官网查询深链需要）。城市名映射到其主要车站；未收录的
# 车站退回携程深链。电报码极少变动（铁路调图不改站码），维护成本低。
STATION_TELECODE = {
    # 直辖市
    "北京": "BJP", "北京南": "VNP", "北京西": "BXP", "北京北": "VAP", "北京丰台": "FTP",
    "上海": "SHH", "上海虹桥": "AOH", "上海南": "SNH", "上海西": "SXH",
    "天津": "TJP", "天津西": "TXP", "广州": "GZQ", "广州南": "IZQ", "深圳": "SZQ",
    "深圳北": "IOQ", "重庆": "CQW", "重庆北": "CUW", "重庆西": "CXW",
    # 华东
    "杭州": "HZH", "杭州东": "HGH", "南京": "NJH", "南京南": "NKH", "苏州": "SZH",
    "苏州北": "OHH", "无锡": "WXH", "常州": "CZH", "合肥": "HFH", "合肥南": "ENH",
    "宁波": "NGH", "温州南": "VRH", "福州": "FZS", "福州南": "FYS", "厦门": "XMS",
    "厦门北": "XKS", "南昌": "NCG", "南昌西": "NKG", "济南": "JNK", "济南西": "JGK",
    "青岛": "QDK", "青岛北": "QHK",
    # 华中/华南
    "武汉": "WHN", "汉口": "HKN", "长沙": "CSQ", "长沙南": "CWQ", "郑州": "ZZF",
    "郑州东": "ZEF", "南宁": "NNZ", "南宁东": "NDZ", "桂林": "GLZ", "桂林北": "GBZ",
    "海口": "VUQ", "三亚": "SEQ",
    # 西南/西北/华北
    "成都": "CDW", "成都东": "ICW", "成都南": "CNW", "昆明": "KMM", "昆明南": "KOM",
    "贵阳": "GIW", "贵阳北": "GHW", "西安": "XAY", "西安北": "EAY", "兰州": "LZJ",
    "兰州西": "LAJ", "西宁": "XNO", "乌鲁木齐": "WAR", "太原": "TYV", "太原南": "TNV",
    "石家庄": "SJP", "呼和浩特": "HHC", "银川": "YIJ", "拉萨": "LSO", "哈密": "HMR",
    # 东北
    "哈尔滨": "HBB", "哈尔滨西": "VAB", "长春": "CCT", "长春西": "CCT", "沈阳": "SHT",
    "沈阳北": "SBT", "大连": "DLT", "大连北": "DGT", "丹东": "DUT",
}


def _station_code(name):
    """车站/城市名 -> (电报码, 官方名)。未收录返回 None。"""
    if name in STATION_TELECODE:
        return name, STATION_TELECODE[name]
    for stn, code in STATION_TELECODE.items():
        if name.endswith(stn) or stn in name:
            return stn, code
    return None


def rail_links(orig, dest, dep, ret, adults):
    """火车票深链：12306 官网直查(电报码，收录车站) + 携程火车票(任意车站兜底)。"""
    q = quote("{}-{}火车票".format(orig, dest))
    ctrip_train = ("https://trains.ctrip.com/trainbooking/search?from={}&to={}"
                   "&date={}&quantity={}").format(
        quote(orig), quote(dest), dep, adults)
    fo = _station_code(orig)
    fd = _station_code(dest)
    if fo and fd:
        rail_12306 = ("https://kyfw.12306.cn/otn/leftTicket/init?linktypeid=dc"
                      "&fs={},{}&ts={},{}&date={}&flag=N,N").format(
            quote(fo[0]), fo[1], quote(fd[0]), fd[1], dep)
        rail_line = "  火车·12306官网  {}  (15天预售,候补优先于捡漏)".format(rail_12306)
    else:
        rail_line = ("  火车·12306  「{}」未收录电报码,请在官方 App/小程序查询"
                     "(或向 scripts/flight_scan.py STATION_TELECODE 补录)").format(
                         orig if not fo else dest)
    return "{}\n  火车·携程  {}".format(rail_line, ctrip_train)


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--from", dest="orig", required=True,
                    help="出发机场三字码或车站/城市名, e.g. PVG / 北京南")
    ap.add_argument("--to", dest="dest", required=True)
    ap.add_argument("--depart", required=True, help="YYYY-MM-DD")
    ap.add_argument("--nights", default=None,
                    help='往返行程长度, e.g. "12" 或区间 "10-15"')
    ap.add_argument("--oneway", action="store_true")
    ap.add_argument("--flex", type=int, default=0,
                    help="同时扫描出发日 +/- N 天")
    ap.add_argument("--adults", type=int, default=1,
                    help="人数(写入深链的 quantity 参数)")
    ap.add_argument("--rail", action="store_true",
                    help="只输出火车深链(高铁/动车为主的城际段用这个)")
    ap.add_argument("--no-rail", action="store_true",
                    help="不输出火车深链(只看机票)")
    args = ap.parse_args()

    if not args.oneway and not args.nights:
        ap.error("--nights is required unless --oneway")
    if args.oneway and args.nights:
        ap.error("--oneway and --nights are mutually exclusive")

    base = date.fromisoformat(args.depart)
    print("境内交通深链网格 — 价格一律以打开链接后的页面为准(无免钥票价 API,"
          "计划中先写 '—, 点链接核对');{} 人;{}。"
          .format(args.adults,
                  "单程" if args.oneway else
                  "往返,行程 {}".format(args.nights)))
    deps = [base + timedelta(days=d) for d in range(-args.flex, args.flex + 1)]
    nights_list = [None] if args.oneway else parse_nights(args.nights)
    for d0 in deps:
        for n0 in nights_list:
            ret0 = (d0 + timedelta(days=n0)).isoformat() if n0 else None
            hdr = "{} -> {} {}{}".format(args.orig, args.dest, d0.isoformat(),
                                         " / 返程 " + ret0 if ret0 else "")
            print("\n== {} ==".format(hdr))
            if not args.rail:
                print(flight_links(args.orig, args.dest, d0.isoformat(),
                                   ret0, args.adults))
            if not args.no_rail:
                print(rail_links(args.orig, args.dest, d0.isoformat(),
                                  ret0, args.adults))
    print("\n提醒:写入 legs[] 前,每个组合点开核对价格/时刻/直飞/行李;"
          "≥2 源 = 携程 + 去哪儿或航司官网。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
