from typing import Union
from pydantic import BaseModel


class TorchLoader(BaseModel):
    # dataset
    dataset_name: str
    save_path: str = ".fed/datasets"
    download: bool = True

    # loader
    batch_size: int = 64

    def list(self):
        from torchvision import datasets

        return datasets.__all__

    def get_save_path(self, default_root_path: str = None):
        return self.save_path

    def load(self):
        from torchvision import datasets
        from torchvision import transforms

        transform = transforms.Compose([transforms.ToTensor()])

        names = set(self.list())

        if self.dataset_name not in names:
            KeyError(f"{self.dataset_name}")

        save_path = self.get_save_path()

        dataset = getattr(datasets, self.dataset_name)
        return dataset(
            root=save_path, train=False, download=self.download, transform=transform
        )

    def train(self):
        from torch.utils.data import DataLoader

        trainloader = DataLoader(self.load(), batch_size=self.batch_size)
        testloader = DataLoader(self.load(), batch_size=self.batch_size)
