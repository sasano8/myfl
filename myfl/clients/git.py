def get_workspace(path) -> "GitWorkspace":
    return GitWorkspace(path)


class GitWorkspace:
    def __init__(self, path):
        ...
