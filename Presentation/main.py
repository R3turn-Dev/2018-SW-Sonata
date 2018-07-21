from tkinter import Tk, ttk, Canvas, Scrollbar

import requests
from bs4 import BeautifulSoup


class KBOBaseball:
    def __init__(self):
        self.uris = {
            "list": "https://sports.news.naver.com/kbaseball/schedule/index.nhn?month={month}&year=2018",
            "json": "https://sportsdata.pstatic.net/ndata//kbo/{year}/0{month}/{gid}.json"
        }

    def get_games(self, month="", parse=True):  # 전체 경기데이터 크롤링
        _selector = ".td_btn > a"
        _response = requests.get(self.uris['list'].format(month=month))

        if not _response.status_code == 200:
            return None

        _html = _response.text
        _games = BeautifulSoup(_html, 'html.parser').select(_selector)

        if not _games:
            return list()

        _game_id = [{"year": 0, "month": 0, "day": 0, "team": (), "gid": v.get("href")[-17:]} for v in _games]

        if parse:
            for i in range(len(_game_id)):
                _temp = _game_id[i]['gid']

                _game_id[i]["year"] = int(_temp[:4])
                _game_id[i]["month"] = int(_temp[4:6])
                _game_id[i]["day"] = int(_temp[6:8])
                _game_id[i]["team"] = (_temp[8:10], _temp[10:12])

        return _game_id

    def get_game_data(self, gid: str):
        game = {
            "year": int(gid[:4]),
            "month": int(gid[4:6]),
            "day": int(gid[6:8]),
            "team": (gid[8:10], gid[10:12]),
            "gid": gid
        }

        _response = requests.get(self.uris['json'].format(**game))

        if not _response.status_code == 200:
            return None

        return _response.json()

    def check(self, word):
        return word in self.filters

    def parse_data(self, game, target: list):
        self.filters = target

        comp = game['relayTexts']
        ret = "\t\t" + game['gameInfo']['aFullName'] + " " + str(comp['final'][-1]['awayScore']) + " : " + \
              str(comp['final'][-1]['homeScore']) + " " + game['gameInfo']['hFullName'] + "\n\n"
        ret += " ==== 요약 ====\n"
        for events in comp['final']:
            ret += events['liveText'] + "\n"

        ret += " =============\n\n"
        for i in range(1, len(comp) - 4):
            ret += f" ===== {i}회 =====\n"
            round = comp[str(i)][::-1]  # 역순배열

            for j in range(len(round)):
                words = round[j]['liveText'].split(" ")
                filtered = [v for v in filter(self.check, words)]
                if filtered:
                    ret += round[j]['liveText'] + "\n"
            ret += "\n\n"

        return ret


class MainWindow:
    def __init__(self, api):
        self.root = Tk()
        self.api = api

        self.months = []
        self.games = []
        for i in range(3, 10):
            bt = ttk.Button(self.root, text=f"{i}월", command=lambda m=i: self.show_games(m))
            bt.grid(row=1, column=i - 3)
            self.months.append(bt)

    def show_games(self, month):
        games = self.api.get_games(month=str(month))

        gids = [*{*[v['gid'] for v in games]}]
        gids.sort()

        for buttons in self.games:
            buttons.destroy()

        for i in range(len(gids)):
            gid = gids[i]
            bt = ttk.Button(self.root, text=gid, command=lambda gid=gid: self.show_parsed(gid))
            bt.grid(row=3 + i // 4, column=i % 4)
            self.games.append(bt)

    # 2주차 교육자료 참고
    def show_parsed(self, gid: str):
        new = Tk()
        canvas = Canvas(new, relief="sunken")

        vbar = Scrollbar(new, orient="vertical")
        vbar.config(command=canvas.yview)
        vbar.pack(side="right", fill="y")

        # 여기서 이상하게 스크롤 안됌
        # hbar = Scrollbar(new, orient="horizontal")
        # hbar.config(command=canvas.xview)
        # hbar.pack(side="bottom", fill="x")

        canvas.config(width=600, height=800)
        canvas.config(highlightthickness=0)
        # canvas.config(yscrollcommand=vbar.set)
        # canvas.config(xscrollcommand=hbar.set)

        canvas.config(scrollregion=(0, 0, 0, 1e1))
        canvas.pack(side="top", expand=True)

        try:
            _temp = self.api.get_game_data(gid)
            data = self.api.parse_data(_temp, ["홈런", '홈인', '공격'])

            canvas.config(scrollregion=(0, 0, 0, 15 * len(data.split("\n"))))  # 결과 길이에 따른 높이설정
            canvas.create_text(0, 0, text=data, anchor="nw")
        except Exception as ex:
            print(repr(ex))
            canvas.create_text(0, 0, text="경기 정보가 없습니다", anchor="nw")

        new.mainloop()

    def run(self):
        self.root.mainloop()


baseball = KBOBaseball()

mw = MainWindow(baseball)
mw.run()
