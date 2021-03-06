# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import dateutil.parser
import json
import os
import pandas as pd
# import shutil


# Create menu directory
def makedir():
    try:
        os.mkdir("menu")
    except:
        print("The menu directory already exists.")

# # Create menu directory
# makedir()


def parse(target):
    return list(target[0].to_dict().values())


def get_day(weekday):
    now = datetime.now()
    current = now.weekday()

    if weekday == current:
        return now.strftime('%m월 %d일')
    elif weekday < current:
        date = now - timedelta(days=(current - weekday))
        return date.strftime('%m월 %d일')
    elif weekday > current:
        date = now + timedelta(days=(weekday - current))
        return date.strftime('%m월 %d일')


def get_weekday(day):
    week = ['월', '화', '수', '목', '금', '토', '일']
    return week[day]


def get_available_menus(reload=False):
    # if reload:
    #     shutil.rmtree("menu")
    return {
        "누리관": Menu("누리관"),
        "감꽃푸드코트": Menu("감꽃푸드코트"),
        "공학관교직원식당": Menu("공학관교직원식당"),
        "공학관학생식당": Menu("공학관학생식당"),
        "복지관": Menu("복지관"),
        "복현카페테리아": Menu("복현카페테리아"),
        "정보센터식당": Menu("정보센터식당"),
        "카페테리아첨성": Menu("카페테리아첨성")
    }


class Menu:
    id = {
        "문화관": 2,
        "첨성관": 3,
        "누리관": 4,
        "상주생활관": None,
        "정보센터식당": 35,
        "복지관": 36,
        "카페테리아첨성": 37,
        "감꽃푸드코트": 46,
        "복현카페테리아": 79,
        "공학관교직원식당": 85,
        "공학관학생식당": 86
    }

    def __init__(self, name, date=datetime.now(), force_retrieve=True, force_dump=False):
        print("Creating the Menu object for {}...".format(name))

        self.name = name
        if type(name) != str:
            raise ValueError

        self.json_path = "menu/" + name + ".json"

        # Try to restore the stored menu
        if not force_retrieve and os.path.isfile(self.json_path):
            self.date, self.weekday_number, self.data = self.load()
        else:
            self.date = date
            self.weekday_number = self.date.weekday()

            if name == "상주생활관":
                url = "https://dorm.knu.ac.kr/scdorm/_new_ver/newlife/05.php" + str(self.id[name])
                self.data = list(parse(pd.read_html(url, match=name + " 오늘의 식단"))[1].values())
            elif name in ("문화관", "첨성관", "누리관"):
                url = "https://dorm.knu.ac.kr/_new_ver/newlife/05.php?get_mode=" + str(self.id[name])
                self.data = list(parse(pd.read_html(url, match=name + " 오늘의 식단"))[1].values())
            else:
                url = "https://coop.knu.ac.kr/sub03/sub01_01.html?shop_sqno=" + str(self.id[name])
                self.data = []

                for i in ("조식", "중식", "석식"):
                    data_day = []
                    try:
                        self.data_week = parse(pd.read_html(url, match=i))
                        for data_raw in self.data_week:
                            try:
                                for j in data_raw:
                                    text = data_raw[j]

                                    # Remove titles
                                    while text[:2] in ("정식", "특식"):
                                        text = text[2:]

                                    # Remove nan
                                    if type(text) != str:
                                        raise ValueError
                                    # Remove blank strings
                                    if text.strip():
                                        data_day.append(text)
                            except:
                                data_day.append("없음")
                        # Add sunday
                        data_day.append("없음")
                    except:
                        # Make the entire week NaN
                        for i in range(7):
                            data_day.append("없음")

                    # Add the menu of the day to the menus of the week
                    self.data.append(data_day)

            # Save data
            if force_dump:
                self.dump()

    def show(self, weekday):
        try:
            menu = (self.data[0][weekday], self.data[1][weekday], self.data[2][weekday])
        except:
            menu = ("없음", "없음", "없음")

        return """!!요일 선택 기능 개발 중!!
일부 응답이 불안정하거나 요청이 거부될 수 있습니다. 불편을 드려 죄송합니다.
(1시간 정도 소요됨)

{}
{} {}요일

아침: {}

점심: {}

저녁: {}""".format(self.name, get_day(weekday), get_weekday(weekday), menu[0], menu[1], menu[2])

    def is_expired(self):
        return self.date.date() < datetime.now().date()

    def load(self):
        with open(self.json_path) as f:
            data = json.load(f)
            return dateutil.parser.parse(data["date"]), data["weekday_number"], data["data"]

    def dumps(self):
        return {
            "name": self.name,
            "date": self.date.isoformat(),
            "weekday_number": self.weekday_number,
            "data": self.data
        }

    def dump(self):
        with open(self.json_path, 'w') as f:
            json.dump(self.dumps(), f)
