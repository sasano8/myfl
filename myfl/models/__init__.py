"""
# https://analysis-navi.com/?p=2007


# 回帰木

温度と湿度がどのようなときにどれくらいの水を飲むのか？を表現したツリー

# 分類木

温度と湿度がどのようなときに暑いと感じるのか？を表現したツリー

# 決定木

分類木と回帰木のことを合わせて決定木

# 関連するフレームワーク

LightGBM


- 連合学習サーバ（aggregator）を起動
- cordinator
    - p2pで通信経路を調整するために使用する
    - cordinatorに自信のエンドポイントURLを伝える


# 相関ルール抽出フレームワーク

mlxtend
"""

[
    ("suport", "itemsets"),
    (0.222, ("whole milk",)),
    (0.222, ("rolls/buns",)),
]


{
    "antecedents": "前提条件（事象A）",
    "consequents": "結果（事象B）",
    "antecedent_support": "全体の中で、事象Aが占める割合（=事象Aの期待信頼度）",
    "consequent_support": "全体の中で、事象Bが占める割合（=事象Bの期待信頼度）",
    "support": "	全体の中で、事象Aと事象Bの組み合わせが占める割合",
    "confidence": "事象Aを含むデータの中で、事象Bが占める確率",
    "lift": "lift = confidence/consequent support",
    "leverage": "事象Aと事象Bの観測頻度と、事象Aと事象Bが独立している場合に予想される頻度の差 leverage=0は完全な独立性を示す",
    "conviction": "convictionが高い場合、事象Bが事象Aとの相互性が高いことを指す",
}


from sklearn.datasets import load_iris

iris_dataset = load_iris()  # csvとかマトリクスデータっぽい
iris_dataset["DESCR"]  # helpを表示

from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    iris_dataset["data"], iris_dataset["target"], test_size=0.25, random_state=0
)
