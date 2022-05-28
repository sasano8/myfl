import torch
from pydantic import BaseModel
from pathlib import Path
from typing import Optional, Callable


class DataSet(BaseModel):
    save_as: str = "FashionMNIST"
    dataset: str = "FashionMNIST"
    download: bool = False
    transform: str = "ToTensor"
    target_transform: Optional[Callable] = None

    def __call__(self, dataset_path: Path):
        import torchvision

        dataset = getattr(torchvision.datasets, self.dataset)
        # dataset = torchvision.datasets.FashionMNIST
        transform = self.get_transform()
        transform = {"transform": transform} if transform else {}
        train_dataloader = dataset(
            dataset_path, download=self.download, **transform, train=True
        )
        test_dataloader = dataset(
            dataset_path, download=self.download, **transform, train=False
        )
        return train_dataloader, test_dataloader

    def get_transform(self):
        import torchvision.transforms as transforms

        if self.transform == "ToTensor":
            return transforms.ToTensor()
        else:
            raise ValueError(self.transform)


class LoadData(BaseModel):
    batch_size: int = 1024
    shuffle: bool = False
    num_workers: int = 1

    def __call__(self, train_dataloader, test_dataloader):
        train_data = torch.utils.data.DataLoader(train_dataloader, **self.dict())
        test_data = torch.utils.data.DataLoader(test_dataloader, **self.dict())
        return train_data, test_data


class Train(BaseModel):
    epoch: int = 1
    model: str = "models.Net"
    optim: str = "SGD"
    lr: float = 0.001
    momentum: float = 0.9

    def __call__(self, train_data, test_data, **kwargs):
        import torch.optim as optim
        import torch.nn as nn

        criterion = nn.CrossEntropyLoss()
        optimizer = optim.SGD(model.parameters(), lr=self.lr, momentum=self.momentum)

        # train
        epoch = 2
        for i in range(epoch):  # エポック数分ループを回します

            running_loss = 0.0
            for i, data in enumerate(train_data, 0):
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
