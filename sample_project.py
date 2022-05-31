from pydantic import BaseModel


class ML:
    def trainer(self):
        class Trainer:
            def __call__(self, *args, **kwargs):
                ...

        return Trainer()


ml = ML()
trainer = ml.trainer()


@trainer
def train(model):
    ...


class TorchLoaderConfig(BaseModel):
    target: str = "CIFAR10"
    name: str = "CIFAR10"
    classes: tuple = (
        "plane",
        "car",
        "bird",
        "cat",
        "deer",
        "dog",
        "frog",
        "horse",
        "ship",
        "truck",
    )
    batch_size: int = 4
    num_workers: int = 2


class LoaderConfig(BaseModel):
    type: str = "torchvision"
    conf: TorchLoaderConfig


def sample():
    import torch
    import torchvision
    import torchvision.transforms as transforms
    import torch.nn as nn
    import torch.nn.functional as F
    import matplotlib.pyplot as plt
    import numpy as np

    # 画像の表示関数
    def imshow(img):
        img = img / 2 + 0.5  # 正規化を戻す
        npimg = img.numpy()
        plt.imshow(np.transpose(npimg, (1, 2, 0)))
        plt.show()

    def load_data(path="./.fed/datasets/CIFAR10", batch_size=4, num_workers=2):
        """
        CIFAR10の読み込みと正規化
        """

        transform = transforms.Compose(
            [
                transforms.ToTensor(),
                transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
            ]
        )

        trainset = torchvision.datasets.CIFAR10(
            root=path, train=True, download=True, transform=transform
        )
        trainloader = torch.utils.data.DataLoader(
            trainset, batch_size=batch_size, shuffle=True, num_workers=num_workers
        )

        testset = torchvision.datasets.CIFAR10(
            root=path, train=False, download=True, transform=transform
        )
        testloader = torch.utils.data.DataLoader(
            testset, batch_size=batch_size, shuffle=False, num_workers=num_workers
        )

        classes = (
            "plane",
            "car",
            "bird",
            "cat",
            "deer",
            "dog",
            "frog",
            "horse",
            "ship",
            "truck",
        )

        # 適当な訓練セットの画像を取得
        dataiter = iter(trainloader)
        images, labels = dataiter.next()

        # 画像の表示
        imshow(torchvision.utils.make_grid(images))
        # ラベルの表示
        print(" ".join("%5s" % classes[labels[j]] for j in range(4)))

        return trainset, trainloader, testset, testloader, classes

    def define_cnn():
        """
        CNN/Convolutional Neural Network（畳み込みニューラルネットワーク）を定義する
        3chのカラー画像を入力にとる
        """

        class Net(nn.Module):
            def __init__(self):
                super(Net, self).__init__()
                self.conv1 = nn.Conv2d(3, 6, 5)
                self.pool = nn.MaxPool2d(2, 2)
                self.conv2 = nn.Conv2d(6, 16, 5)
                self.fc1 = nn.Linear(16 * 5 * 5, 120)
                self.fc2 = nn.Linear(120, 84)
                self.fc3 = nn.Linear(84, 10)

            def forward(self, x):
                x = self.pool(F.relu(self.conv1(x)))
                x = self.pool(F.relu(self.conv2(x)))
                x = x.view(-1, 16 * 5 * 5)
                x = F.relu(self.fc1(x))
                x = F.relu(self.fc2(x))
                x = self.fc3(x)
                return x

        return Net()

    trainset, trainloader, testset, testloader, classes = load_data()
    model = define_cnn()

    # optimizer
    import torch.optim as optim

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(model.parameters(), lr=0.001, momentum=0.9)

    # train
    epoch = 2
    for i in range(epoch):  # エポック数分ループを回します

        running_loss = 0.0
        for i, data in enumerate(trainloader, 0):
            # データセットのデータを [inputs, labels]の形で取得
            inputs, labels = data

            # パラメータの勾配をリセット
            optimizer.zero_grad()

            # 順伝搬＋逆伝搬＋パラメータ更新
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            # 統計情報の表示
            running_loss += loss.item()
            if i % 2000 == 1999:  # 2,000ミニバッチにつき1度表示
                print("[%d, %5d] loss: %.3f" % (i + 1, i + 1, running_loss / 2000))
                running_loss = 0.0

    print("Finished Training")

    # 保存（パラメータのみ）
    PATH = "./.fed/models/cifar_net.pth"
    torch.save(model.state_dict(), PATH)

    # 保存（モデル全体pickle）
    # torch.save(model, PATH)
    # model = torch.load(PATH)
    # model.eval()

    # test
    dataiter = iter(testloader)
    images, labels = dataiter.next()

    # 画像と正解ラベルの表示
    imshow(torchvision.utils.make_grid(images))
    print("GroundTruth: ", " ".join("%5s" % classes[labels[j]] for j in range(4)))

    # モデルをロードする場合（モデル定義そのものが必要なのか？）
    model = define_cnn()
    model.load_state_dict(torch.load(PATH))

    # 確認
    outputs = model(images)

    # 最も確率が高いカテゴリを取得
    _, predicted = torch.max(outputs, 1)
    print("Predicted: ", " ".join("%5s" % classes[predicted[j]] for j in range(4)))

    # # GPUで学習する場合
    # device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    # model.to(device)

    # # ループ内では、以下のように、毎ステップ、入力データと正解ラベルもGPUに送る必要がある
    # inputs, labels = data[0].to(device), data[1].to(device)

    # # 日本語訳注：GPU版で訓練を実行した場合

    # # optimizerを再定義（netがGPU上に移動したので）
    # optimizer = optim.SGD(model.parameters(), lr=0.001, momentum=0.9)

    # for epoch in range(2):  # データセットを何巡繰り返すか

    #     running_loss = 0.0
    #     for i, data in enumerate(trainloader, 0):
    #         # 入力を取得します; 変数dataはリスト[inputs, labels]です
    #         # inputs, labels = data  # cpuの場合をコメントアウト
    #         inputs, labels = data[0].to(device), data[1].to(device)

    #         # 勾配を0に初期化
    #         optimizer.zero_grad()

    #         # 順伝搬、逆伝搬、パラメータ更新
    #         outputs = model(inputs)
    #         loss = criterion(outputs, labels)
    #         loss.backward()
    #         optimizer.step()

    #         # 統計情報を出力
    #         running_loss += loss.item()
    #         if i % 2000 == 1999:  # 2000ミニバッチごとに出力
    #             print("[%d, %5d] loss: %.3f" % (epoch + 1, i + 1, running_loss / 2000))
    #             running_loss = 0.0

    # print("Finished Training")


sample()


# https://federated-xgboost.readthedocs.io/en/latest/
# pip3 install xgboost

import xgboost as xgb

# read in data
dtrain = xgb.DMatrix("demo/data/agaricus.txt.train")
dtest = xgb.DMatrix("demo/data/agaricus.txt.test")
# specify parameters via map
param = {"max_depth": 2, "eta": 1, "silent": 1, "objective": "binary:logistic"}
num_round = 2
bst = xgb.train(param, dtrain, num_round)
# make prediction
preds = bst.predict(dtest)
