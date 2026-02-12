import pandas as pd
import matplotlib.pyplot as plt
import os


BASE_DIR = os.path.dirname(__file__)
file_path = os.path.join(BASE_DIR, '..', 'titanic', 'train.csv')
save_path = os.path.join(BASE_DIR, '..', 'class_distribution.png')


df = pd.read_csv(file_path)


print("🎯 타겟(Survived) 분포:")
print(df['Survived'].value_counts())
print("\n비율:")
print(df['Survived'].value_counts(normalize=True))

# 정해진 비율이 있는건 아니지만
# 비율	상태
# 50:50	균형
# 60:40	경미
# 80:20	중간
# 95:5	심각
#라고 생각하면 되려나 

plt.figure(figsize=(8,6))  
#그래프 크기 
df["Survived"].value_counts().plot(kind="bar")
# "Survived컬럼의 갯수로 bar chart 생성
plt.title("Class Distribution (Survived)")
plt.xlabel("Survived")
plt.ylabel("Count")
plt.xticks([0, 1], ['Not Survived (0)', 'Survived (1)'], rotation=0)
# x축 라벨 명확하게 지정
plt.tight_layout()
# 각 그래프 간격 조절
plt.savefig(save_path)
print("\n📊 그래프 저장: class_distribution.png")


class_counts = df['Survived'].value_counts()
print("class_counts",class_counts)
imbalance_ratio = class_counts.max() / class_counts.min()

print(f"\n⚖️ Imbalance Ratio: {imbalance_ratio:.2f}")
if imbalance_ratio > 3:
    print("⚠️ Class Imbalance 심각! 처리 필요")
else:
    print("✅ Class Imbalance 양호")