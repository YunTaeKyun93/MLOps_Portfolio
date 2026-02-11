import os
import pandas as pd 
BASE_DIR = os.path.dirname(__file__)
file_path = os.path.join(BASE_DIR, 'titanic', 'train.csv')


df = pd.read_csv(file_path)

print(df.shape)
print('\n 컬럼정보')
print(df.info())
print('\n 데이터미리보기')
print(df.head())


print('\n 통계정보')
print(df.describe())

print('\n 결측치 확인')
print(df.isnull().sum())

