
``` mermaid
sequenceDiagram
    participant Server
    participant Client

    Server->>Client: MyMessage.MSG_TYPE_S2C_INIT_CONFIG
    Client->>Server: MyMessage.MSG_TYPE_S2C_SYNC_MODEL_TO_CLIENT
    Server->>Client: MyMessage.MSG_TYPE_S2C_SYNC_MODEL_TO_CLIENT
    Client->>Server: MyMessage.MSG_TYPE_C2S_SEND_MODEL_TO_SERVER
```

GRPCのポートは、ServerManagerによってrank（プロセス番号）+ 50000となっている。
単一ジョブでポートが重複しないが、複数のジョブを実行すると衝突してしまうと思われる。
また、クライアントもClientManagerによってGRPCサーバを起動する（GRPCCommManagerはServer/Client共通）。

これはクロスサイロ構成（組織等ドメイン間でデータ非共有・モデル共有）に向いている。


```
PORT = 50000 + rank
```


```
standalone/fedavg/main_fedavg.py

- wandb.init
    - どう作動するか分からん
    - 何をウォッチする？
- torchを準備する
    - gpu か cpuか
    - 色々初期化
- load_data(args, args.dataset)
    - centralized = True if args.client_num_in_total == 1 else False
    - full_batch = args.batch_size <= 0  args.batch_size = 128
    - class_num = load_partition_data_federated_shakespeare(args.dataset, args.data_dir)
        - DEFAULT_TRAIN_CLIENTS_NUM = 715 の数だけデータセットを分割する？
            - get_dataloader(dataset, data_dir, train_bs, test_bs, client_idx=None) -> クライアント分のデータローダを作成する
                - train用データセットとtest用データセットを読み込む
                - utils.preprocess: よく分からないが前処理をしているようだ
                - utils.split: datasetをx, yにsplitする
                - テンソルデータセット（pytorchで提供する型）
                - data.DataLoader(dataset=train_ds, batch_size=train_bs,shuffle=True,drop_last=False) クラスを初期化し、train用data_loaderとtest用data_loaderを初期化する
        - クライアント分のデータローダを１つにし、train用とtest用loaderを作成する（なんか意味ないようにみえる）
        - 統計情報やtrain用・test用データローダ色々返す
    - args.client_num_in_total = client_num  # standaloneだからクライアント数は無視される？
    - centralizedならなんかする
    - full_batchならなんかする
    - 色々一つに含めてそれを返す
- create_model(dataset, model_name, output_dim): モデルを作成する。これは一般的な機械学習と同じ
    - modelのインターフェースは何か？
- custom_model_trainer
- FedAvgAPI(dataset, device, args, model_trainer).train() -> トレーナーを実行する
    - comm_roundの数繰り返す
        - clientの数？繰り返す
            - trainする
    - aggregate（グローバルパラメータを更新）する
    - トレーナーのパラメータをグローバルパラメータでアップデートする
    - テストする

```

```
# distributed/fedavg/main_fedavg.py

- device = mapping_processes_to_gpu_device_from_yaml_file(...)
- dataset = load_data(args, args.dataset)
- model = create_model(args, model_name=args.model, output_dim=dataset[7])
- FedML_FedAvg_distributed(
        process_id,
        worker_number,
        device,
        comm,
        model,
        train_data_num,
        train_data_global,
        test_data_global,
        train_data_local_num_dict,
        train_data_local_dict,
        test_data_local_dict,
        args,
    )
    - if process_id == 0:
        - init_server
            - トレーナを初期化
            - アグリゲータを初期化 aggregator = FedAVGAggregator
            - サーバマネージャを初期化 server_manager = FedAVGServerManager(args, aggregator, comm, rank, size, backend)
            - 初期化メッセージを送信: server_manager.send_init_msg()
                - self.aggregator.get_global_model_params(): トレーナのモデルからグローバルパラメータを取得
                - グローバルパラメータと共に、MyMessage.MSG_TYPE_S2C_INIT_CONFIGを送信（FedAVGClientManager.handle_message_initが受け取る）
            - 実行＆待機: server_manager.run()
                - messageを監視する
    - else:
        - init_client
            - トレーナを初期化
            - FedAVGTrainerを初期化
            - FedAVGClientManagerを初期化
            - FedAVGClientManagerを実行
```

```
# https://github.com/FedML-AI/FedML-IoT/blob/master/raspberry_pi/fedavg/fedavg_rpi_client.py

## server
- サーバを起動しておく


## client

- client_ID, args = register(server_ip, uuid, args): サーバに任意のclient_uuidを登録
    - result = requests.post(url=URL, params={"device_id": uuid})
    - client_id = result["client_id"]
    - training_task_args = result['training_task_args']
    - return training_task_args
    - シードを初期化
    - init_training_device(client_ID - 1, args.client_num_per_round - 1, 4)  # 4 - gpu_num_per_machine
        - torch.deviceを返す
    - load_data
    - create_model
    - trainerを初期化（他のトレーナと変わりなし）&& model_trainer.set_id(client_index)
    - FedAVGTrainerを初期化
    - FedAVGClientManager(args, trainer, rank=client_ID, size=size, backend="MQTT")
    - client_manager.run()
    - client_manager.start_training()
    - time.sleep(100000): !???

```





fedml_apiは汎用的に使えるAPIだと思ったが、かなり具体的なようだ

```
fedml_api/data_preprocessing/fed_shakespeare

def load_partition_data_distributed_federated_shakespeare(...
def load_partition_data_federated_shakespeare(...
```

