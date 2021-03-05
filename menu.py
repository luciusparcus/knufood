# -*- coding: utf-8 -*-

from datetime import datetime
from pytz import timezone
import pandas as pd


def parse(target):
    return list(target[0].to_dict().values())


def get_weekday(day):
    week = ['월', '화', '수', '목', '금', '토', '일']
    return week[day]


class Menu:
    id = {
        u"정보센터식당": 35,
        u"복지관": 36,
        u"카페테리아첨성": 37,
        u"감꽃푸드코트": 46,
        u"복현카페테리아": 79,
        u"공학관교직원식당": 85,
        u"공학관학생식당": 86
    }

    date = datetime.now(timezone('Asia/Seoul'))
    weekday_number = date.weekday()

    def __init__(self, name):
        self.name = name
        if type(name) != str:
            raise ValueError

        url = "https://coop.knu.ac.kr/sub03/sub01_01.html?shop_sqno=" + str(self.id[name])
        self.title = list(pd.read_html(url, match="주간메뉴")[0].columns.values)

        try:
            self.breakfast = self.__mkstr(parse(pd.read_html(url, match="조식")))[self.weekday_number]
        except:
            self.breakfast = "없음"
        try:
            self.lunch = self.__mkstr(parse(pd.read_html(url, match="중식")))[self.weekday_number]
        except:
            self.lunch = "없음"
        try:
            self.dinner = self.__mkstr(parse(pd.read_html(url, match="석식")))[self.weekday_number]
        except:
            self.dinner = "없음"

        print(self.breakfast, self.lunch, self.dinner)

    def show(self):
        return self.lunch
#         return """{} {} {}요일 식단
# 아침: {}
#
# 점심: {}
#
# 저녁: {}""".format(self.name, self.date.strftime('%m월 %d일'), get_weekday(self.weekday_number), self.breakfast,
#                  self.lunch, self.dinner)

    def __mkstr(self, target):
        ret = []
        if self.title[0] == "분류":
            self.title.remove("분류")

        for i in range(len(self.title)):
            text = str(list(target[i].values())[0])

            while text[:2] == "정식":
                text = text[2:]

            if text == "nan":
                text = ""

            ret.append(text)

        return ret


class DormMenu:
    id = {
        "문화관": 2,
        "첨성관": 3,
        "누리관": 4
    }

    date = datetime.now(timezone('Asia/Seoul'))
    weekday_number = date.weekday()

    def __init__(self, name):
        self.name = name

        if type(name) != str:
            raise ValueError

        if name == "상주생활관":
            url = "https://dorm.knu.ac.kr/scdorm/_new_ver/newlife/05.php"
        else:
            url = "https://dorm.knu.ac.kr/_new_ver/newlife/05.php?get_mode=" + str(self.id[name])

        self.data = parse(pd.read_html(url, match=name + " 오늘의 식단"))[1]

    def show(self):
        return """{} {} {}요일 식단
아침: {}

점심: {}

저녁: {}""".format(self.name, self.date.strftime('%m월 %d일'), get_weekday(self.weekday_number), self.data[0], self.data[1], self.data[2])