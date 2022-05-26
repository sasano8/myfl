class TrainerBase:
    LOADER_SELECTOR = None
    MODEL_SELECTOR = None

    def __init__(self, model, args=None):
        self.model = model
        self.id = 0
        self.args = args

    @classmethod
    def _select_loader(cls, key):
        return cls.LOADER_SELECTOR[key]

    @classmethod
    def _select_model(cls, key):
        return cls.MODEL_SELECTOR[key]

    def set_id(self, trainer_id):
        self.id = trainer_id

    def get_model_params(self):
        raise NotImplementedError()

    def set_model_params(self, model_parameters):
        raise NotImplementedError()

    def train(self, train_data, device, args=None):
        raise NotImplementedError()

    def test(self, test_data, device, args=None):
        raise NotImplementedError()

    def test_on_the_server(
        self, train_data_local_dict, test_data_local_dict, device, args=None
    ) -> bool:
        raise NotImplementedError()


class LocalTrainer(TrainerBase):
    def set_model_params(self, model_parameters):
        if "pytorch":
            self.model.load_state_dict(model_parameters)

    def save(self):
        torch.save(model.state_dict(), model_path)


class DummyTrainer:
    def __init__(self, comm):
        self.comm = comm

    async def train(self, comm):
        ...

    async def serve(self, comm):
        ...
