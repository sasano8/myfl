def create_cli(app: "App"):

    from myfl.core.workspace import WorkSpace as Config, LocalRepository
    from myfl.server_factories import build_server
    from .utils import echo
    from .. import functions

    common_opt = {"no_args_is_help": True}

    app = typer.Typer(**common_opt)
    config = typer.Typer(**common_opt)
    server = typer.Typer(**common_opt)
    domain = typer.Typer(**common_opt)
    dataset = typer.Typer(**common_opt)
    model = typer.Typer(**common_opt)
    loader = typer.Typer(**common_opt)
    train = typer.Typer(**common_opt)
    federate = typer.Typer(**common_opt)

    @app.command()
    def init(use_remote: bool = True):
        import os
        from myfl import server_config

        host = os.environ.get(server_config.ENV_DEFAULT_HOST, None)
        if use_remote and host:
            raise NotImplementedError()

        Config.from_cwd().init()

    @app.command()
    def login(token: str = None):
        ...

    @app.command()
    def logout():
        ...

    @app.command()
    def purge():
        ...

    @config.command()
    def list(config_name: str = None):
        ...

    @config.command()
    def validate(config_name: str = None):
        conf = Config.from_cwd().get(config_name)

    @config.command()
    def show(config_name: str = None):
        conf = Config.from_cwd().get(config_name)
        echo(json.dumps(conf, indent=2, ensure_ascii=False))

    @config.command()
    def pull(config_name: str = None):
        conf = Config.from_cwd().get(config_name)

    @config.command()
    def set(config_name: str = None):
        conf = Config.from_cwd().get(config_name)

    @loader.command()
    def list(config_name: str = None):
        conf = Config.from_cwd().get(config_name)

    @loader.command()
    def run(config_name: str = None):
        conf = Config.from_cwd().get(config_name)

    @loader.command()
    def dry_run(config_name: str = None):
        conf = Config.from_cwd().get(config_name)

    @loader.command()
    def show(config_name: str = None, n: int = None):
        conf = Config.from_cwd().get(config_name)

    @train.command()
    def list(config_name: str = None):
        conf = Config.from_cwd().get(config_name)

    @train.command()
    def run(config_name: str = None, standalone: bool = False):
        conf = Config.from_cwd().get(config_name)
        functions.train(conf)

    @train.command()
    def dry_run(config_name: str = None, standalone: bool = False):
        conf = Config.from_cwd().get(config_name)
        logs = [
            "[client]request hello",
            "[server]response hello",
            "[client]request pull_config",
            "[server]response pull_config",
            "[client]start train",
            "[client]request pull_model",
            "[server]response pull_model",
            "[client]request pull_data",
            "[server]response pull_data",
            "[client]request push_model",
            "[server]response push_model",
            "[client]request pull_model",
            "[server]response pull_model",
            "[client]request commit",
            "[server]request push_model",
            "[upstream]response push_model",
            "[server]response commit",
            "[client]finish train",
            "[client]request bye",
            "[server]response bye",
        ]

        echo(logs)

    @federate.command()
    def list(config_name: str = None):
        conf = Config.from_cwd().get(config_name)

    @federate.command()
    def join(config_name: str = None):
        conf = Config.from_cwd().get(config_name)

    @federate.command()
    def run(config_name: str = None):
        conf = Config.from_cwd().get(config_name)

    @federate.command()
    def dry_run(config_name: str = None):
        conf = Config.from_cwd().get(config_name)

    @dataset.command("list")
    def dataset_list(config_name: str = None):
        result = LocalRepository.from_cwd(config_name).get_datasets()
        echo(result)

    @dataset.command("show")
    def dataset_show(name: str, *, config_name: str = None):
        result = LocalRepository.from_cwd(config_name).get_dataset(name)
        echo(result)

    @dataset.command("pull")
    def dataset_pull(config_name: str = None):
        conf = Config.from_cwd().get(config_name)

    @dataset.command("push")
    def dataset_push(config_name: str = None):
        conf = Config.from_cwd().get(config_name)

    @model.command()
    def list(config_name: str = None):
        conf = Config.from_cwd().get(config_name)

    @model.command()
    def pull(config_name: str = None):
        conf = Config.from_cwd().get(config_name)

    @model.command()
    def push(config_name: str = None):
        conf = Config.from_cwd().get(config_name)

    @server.command()
    def hosts(config_name: str = None):
        conf = Config.from_cwd().get(config_name)

    @server.command()
    def devices(config_name: str = None):
        conf = Config.from_cwd().get(config_name)

    @server.command()
    def users(config_name: str = None):
        conf = Config.from_cwd().get(config_name)

    @server.command()
    def run(
        config_name: str = None,
        port: int = 5000,
        log_level: str = "info",
    ):
        import uvicorn
        from myfl import server_config

        conf = Config.from_cwd().get(config_name)
        config_store = {}
        data_store = {}
        model_store = {}

        server = build_server(
            root_prefix=server_config.ROOT_PREFIX,
            router_prefix=server_config.ROUTER_PREFIX,
            path=server_config.PATH,
            config_store=config_store,
            data_store=data_store,
            model_store=model_store,
        )

        uvicorn.run(server, port=port, log_level=log_level)

    @domain.command()
    def hosts(config_name: str = None):
        conf = Config.from_cwd().get(config_name)

    @domain.command()
    def devices(config_name: str = None):
        conf = Config.from_cwd().get(config_name)

    @domain.command()
    def users(config_name: str = None):
        conf = Config.from_cwd().get(config_name)

    @domain.command()
    def start(config_name: str = None):
        conf = Config.from_cwd().get(config_name)

    @domain.command()
    def stop(config_name: str = None):
        conf = Config.from_cwd().get(config_name)

    app.add_typer(config, name="config")
    app.add_typer(server, name="server")
    app.add_typer(domain, name="domain")
    app.add_typer(dataset, name="dataset")
    app.add_typer(model, name="model")
    app.add_typer(loader, name="loader")
    app.add_typer(train, name="train")
    app.add_typer(federate, name="federate")
