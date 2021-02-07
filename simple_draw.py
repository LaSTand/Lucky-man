import pandas as pd
from random import *

data = pd.read_csv('./files/draw_result.csv', index_col=0)
columns_cnt = data.shape[1]
rows_cnt = data.shape[0]
total_item = columns_cnt * rows_cnt

''' 번호 등장 확률 DataFrame 
인덱스가 번호(1 ~ 45)
1 열 : 등장 횟수
2 열 : 확률
3 열 : 누적 확률
'''
prob_df = pd.DataFrame(columns=['count', 'prob', 'cum_prob'])

# 확률 정보 DataFrame 초기화(1 ~ 45)
for i in range(0, 46):
    prob_df.loc[i] = [0, 0, 0]

# 등장 횟수(1열) 계산
for j in range(0, rows_cnt):
    for k in range(0, columns_cnt):
        prob_df.iloc[data.iloc[j, k], 0] += 1

# 확률 및 누적확률(2, 3열) 계산
cum_prob = 0
for i in range(0, 46):
    cum_prob += prob_df.iloc[i, 0] / total_item * 100
    prob_df.iloc[i, 1] = prob_df.iloc[i, 0] / total_item * 100
    prob_df.iloc[i, 2] = cum_prob

last_game = data.iloc[rows_cnt - 1].tolist()
# 누적 확률에 따른 랜덤 값 추출(이전 회차 제외)
for i in range(0, 5):
    num_set = []
    idx = random() * 100
    selected_num = prob_df[(prob_df['cum_prob'] < idx)].last_valid_index() + 1
    for j in range(0, 6):
        while selected_num in last_game + num_set:
            idx = random() * 100
            selected_num = prob_df[(prob_df['cum_prob'] < idx)].last_valid_index() + 1
        num_set.append(selected_num)
        # print("idx : ", idx, "selected num : ", selected_num)
    print("Set ", i+1, " :", num_set)

print("** Last Game Set is : ", last_game)