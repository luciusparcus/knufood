# -*- coding: utf-8 -*-

from datetime import date, datetime, timedelta
import dateutil.parser
import json
import os
import pandas as pd
import bs4
import requests
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

def is_dormitory(name):
    return name in ("문화관", "첨성관", "누리관", "상주생활관")


def get_day(weekday, strftime=True):
    now = datetime.now()
    current = now.weekday()

    if weekday == current:
        return now.strftime('%m월 %d일') if strftime else now
    elif weekday < current:
        date = now - timedelta(days=(current - weekday))
        return date.strftime('%m월 %d일') if strftime else date
    elif weekday > current:
        date = now + timedelta(days=(weekday - current))
        return date.strftime('%m월 %d일') if strftime else date


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
            self.data = []

            if is_dormitory(name):
                if name == "상주생활관":
                    url = "https://dorm.knu.ac.kr/scdorm/_new_ver/newlife/05.php"
                else:
                    url = "https://dorm.knu.ac.kr/_new_ver/newlife/05.php?get_mode=" + str(self.id[name])

                page = requests.get(url).content
                soup = bs4.BeautifulSoup(page, 'lxml')

                data_date = []
                data_all = []

                # Retrieve all menus
                for i in soup.find_all("div", {"id": "menu_boxa"}):
                    menus = []
                    ignore = []
                    day = []

                    for menu in i.get_text().split('\n'):
                        if menu not in ('', '\r', '\t', "아침메뉴", "점심메뉴", "저녁메뉴", "CLOSE "):
                            menus.append(menu.lstrip(' ').rstrip('\r').rstrip('\t'))

                    for j in range(len(menus)):
                        # If j is date
                        if "식단표" in str(menus[j]):
                            data_date.append(datetime.strptime(menus[j], "%Y년 %m월 %d일 식단표"))
                        elif j not in ignore:
                            # If the menu starts with A, merge it with the following components
                            if menus[j][:1] == 'A':
                                cnt = j + 1
                                items = menus[j] + " / " + menus[j + 1]
                                items_to_ignore = [j + 1]

                                # Removes '※ A 혹은 B 중 선택1가지만...'
                                if '※' in menus[j + 2]:
                                    items_to_ignore.append(j + 2)
                                # Removes '품절될 수 있습니다'
                                if "있습니다" in menus[j + 3]:
                                    items_to_ignore.append(j + 3)

                                day.append(items)
                                ignore.extend(items_to_ignore)
                            else:
                                day.append(menus[j])

                            if len(day) >= 3:
                                data_all.append(day)
                                day = []

                # Parse the current week
                monday = get_day(0, strftime=False)

                for day in data_date:
                    if day.year == monday.year and day.month == monday.month and day.day == monday.day:
                        idx_monday = data_date.index(day)
                        for idx in range(idx_monday, idx_monday + 7):
                            try:
                                self.data.append(data_all[idx])
                            except:
                                self.data.append(("없음", "없음", "없음"))
            else:
                url = "https://coop.knu.ac.kr/sub03/sub01_01.html?shop_sqno=" + str(self.id[name])

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
            if is_dormitory(self.name):
                menu = (self.data[weekday][0], self.data[weekday][1], self.data[weekday][2])
            else:
                menu = (self.data[0][weekday], self.data[1][weekday], self.data[2][weekday])
        except:
            menu = ("없음", "없음", "없음")

        return """{}
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
