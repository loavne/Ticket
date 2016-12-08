"""Train tickets query via command-line.

Usage:
    tickets [-gdtkz] <from> <to> <date>

Options:
    -h,--help   显示帮助菜单
    -g          高铁
    -d          动车
    -t          特快
    -k          快速
    -z          直达

Example:
    tickets beijing shanghai 2016-08-25
"""
from docopt import docopt
from stations import stations
import requests
from prettytable import PrettyTable
from colorama import init, Fore

init()


class TrainsCollection:
    header = "车次 车站 时间 历时 一等 二等 软卧 硬卧 硬座 无座".split()

    def __init__(self, trains, options):
        """查询到的火车班次集合
        :param trains:一个列表[]
        :param options:查询的选项，如高铁，动车。。。
        """
        self.trains = trains
        self.options = options

    def get_duration(self, row_train):
        duration = Fore.BLUE + row_train.get("lishi").replace(":", "小时") + "分" + Fore.RESET
        if duration.startswith("00"):
            return duration[4]
        if duration.startswith("0"):
            return duration[1:]
        return duration

    @property
    def all_train(self):
        for row_train in self.trains:
            if not self.options or row_train["station_train_code"][0].lower() in self.options:
                train = [  # 一趟车次是一个列表
                    row_train["station_train_code"],  # 车次
                    "\n".join([row_train["from_station_name"], row_train["to_station_name"]]),  # 起点站、终点站
                    "\n".join([Fore.GREEN + row_train["start_time"] + Fore.RESET,
                               Fore.RED + row_train["arrive_time"] + Fore.RESET]),  # 出发/到达时间
                    self.get_duration(row_train),  # 历时
                    row_train["zy_num"],  # 一等座
                    row_train["ze_num"],  # 二等座
                    row_train["rw_num"],  # 软卧
                    row_train["yw_num"],  # 硬卧
                    row_train["yz_num"],  # 硬座
                    row_train["wz_num"]  # 无座
                ]
                yield train

    def pretty_print(self):
        """格式化显示数据"""
        pt = PrettyTable()
        pt._set_field_names(self.header)  # 设置每一列的标题名字
        for train in self.all_train:
            pt.add_row(train)
        print(pt)


def cli():
    """命令行接口"""
    arguments = docopt(__doc__)
    print(arguments)
    from_station = stations.get(arguments["<from>"])  # 起始站
    to_station = stations.get(arguments["<to>"])  # 终点站
    date = arguments["<date>"]  # 日期

    # 构建URL
    url = 'https://kyfw.12306.cn/otn/lcxxcx/query?purpose_codes=ADULT&queryDate={}&from_station={}&to_station={}'.format(
        date, from_station, to_station)

    # 添加verify=False参数不验证证书
    response = requests.get(url, verify=False)
    rows = response.json()["data"]["datas"]

    # 获取命令行参数（输入的参数）
    options = "".join([key for key, value in arguments.items() if value is True])

    TrainsCollection(rows, options).pretty_print()


if __name__ == "__main__":
    cli()
