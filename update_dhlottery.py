import csv
import requests
from bs4 import BeautifulSoup

header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36"}


# csv 파일에 작성하기
def write_to_csv(data):
    filename = "./files/lottery.csv"
    with open(filename, "a", encoding="utf8", newline="") as f2:
        writer = csv.writer(f2)
        writer.writerow(data)


# 마지막 회차 번호 가져오기
def get_last_draw_no():
    url = "https://dhlottery.co.kr/gameResult.do?method=byWin"
    res = requests.get(url, headers=header)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "lxml")

    last_draw_no = soup.find("div", {"class": "win_result"}).strong.get_text()

    return int(last_draw_no[0:-1])


# 각 회차별 당첨번호 가져와서 쓰기(보너스 번호 포함)
def get_draw_result(start_drw_no, end_drw_number):
    print("=" * 10, "최신 당첨 결과 반영 중", "=" * 10)

    for draw_number in range(start_drw_no+1, end_drw_number+1):
        url = "https://dhlottery.co.kr/gameResult.do?method=byWin&drwNo={}".format(draw_number)
        res = requests.get(url, headers=header)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "lxml")

        result = [draw_number, ]  # 최종 회차 정보 리스트
        win_numbers = soup.find("div", {"class": "num win"}).p.find_all("span")
        bonus_number = soup.find("div", {"class": "num bonus"}).p.find("span").get_text()

        for win_number in win_numbers:
            result.append(int(win_number.get_text()))

        result.append(int(bonus_number))

        write_to_csv(result)
        print(draw_number, "회 완료")


if __name__ == '__main__':
    with open("./files/lottery.csv", "r", newline="") as f1:
        lines = f1.readlines()
        last_draw_in_file = int(lines[-1].split(',')[0])

    get_draw_result(last_draw_in_file, get_last_draw_no())
