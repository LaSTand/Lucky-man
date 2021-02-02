import csv
import re
import requests
from bs4 import BeautifulSoup

header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36"}
filename1 = "./files/draw_result.csv"
filename2 = "./files/number_stats.csv"
filename3 = "./files/color_stats.csv"


def write_to_csv(filename, data):
    """ csv 파일에 작성하기
    1. filename ; 파일명[string]
    2. data ; csv에 입력할 데이터[list]
    """
    with open(filename, "a", encoding="utf8", newline="") as fp:
        writer = csv.writer(fp)
        writer.writerow(data)


def get_last_draw_no():
    """ 최근 추첨 회차 가져오기
    :return: 최신 회차[int]
    """
    url = "https://dhlottery.co.kr/gameResult.do?method=byWin"
    res = requests.get(url, headers=header)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "lxml")

    last_draw_no = soup.find("div", {"class": "win_result"}).strong.get_text()

    return int(last_draw_no[0:-1])


def get_draw_result():
    """ 추첨 결과 갱신(733회 ~)
    기존의 파일의 마지막 회차 이후부터 최신 추첨 결과까지 .csv 파일 갱신
    """
    print("=" * 10, "최신 당첨 결과 반영 중", "=" * 10)

    end_drw_no = get_last_draw_no()

    # 파일에 저장된 마지막 회차 값 구하기
    with open(filename1, "r", newline="") as fp:
        lines = fp.readlines()
        start_drw_no = int(lines[-1].split(',')[0])

    # 파일 마지막 ~ 최근 추첨 회차까지 스크래핑
    for draw_number in range(start_drw_no + 1, end_drw_no + 1):
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

        write_to_csv(filename1, result)
        print(draw_number, "회 완료")


def get_number_stats():
    """ dhlottery 통계 중, '번호별 통계' 가져오기 (733회 ~)
    프로그램 실행 시, 매번 갱신
    """
    # csv 파일 헤드라인 입력
    with open(filename2, "w", encoding="utf-8-sig", newline="") as fp:
        writer = csv.writer(fp)
        title = ["number", "percentage", "win_count"]
        writer.writerow(title)
    
    # csv 파일 데이터 가져오기
    last_drw_no = get_last_draw_no()

    url = "https://dhlottery.co.kr/gameResult.do?method=statByNumber&sortOrder=DESC&srchType=list&sltBonus=1&sttDrwNo=733&edDrwNo={}".format(last_drw_no)
    res = requests.get(url, headers=header)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "lxml")

    data_rows = soup.find("table", attrs={"class": "tbl_data tbl_data_col"}).find("tbody").find_all("tr")

    for row in data_rows:
        columns = row.find_all("td")
        data = [column.get_text().strip() for column in columns]
        write_to_csv(filename2, data)


def get_color_stats():
    """ 색상 통계 구하기
    기존에 구한 추첨 결과 정보 csv 파일을 토대로 색상 통계값 산출
    """
    with open(filename1, "r", newline="") as fp:
        src_lines = fp.readlines()  # 추첨 결과 데이터

        # color_stats.csv 파일에 몇회차까지 저장되어있는지 확인
        with open(filename3, "r", newline="") as fp1:
            dst_lines = fp1.readlines()     
            start_drw_no = int(dst_lines[-1].split(',')[0])

        # 추첨 결과 데이터로부터 통계 산출
        with open(filename3, "a", encoding="utf8", newline="") as fp2:
            for src_line in src_lines:
                draw_no = int(src_line.split(',')[0])
                if draw_no <= start_drw_no:
                    continue
                else:
                    stat = [draw_no, 0, 0, 0, 0, 0]  # yellow, blue, red, grey, green
                    for win_numbers in src_line.split(','):
                        number = int(win_numbers)
                        if 0 < number <= 10:
                            stat[1] += 1
                        elif 10 < number <= 20:
                            stat[2] += 1
                        elif 20 < number <= 30:
                            stat[3] += 1
                        elif 30 < number <= 40:
                            stat[4] += 1
                        elif 40 < number <= 45:
                            stat[5] += 1
                writer = csv.writer(fp2)
                writer.writerow(stat)


if __name__ == '__main__':
    # get_draw_result()
    # get_number_stats()
    # get_color_stats()