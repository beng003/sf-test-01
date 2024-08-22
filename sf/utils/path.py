import os
from pathlib import Path


# DATA_PATH = Path(os.path.realpath(__file__)).parent.parent.parent/'data'
# CONFIG_PATH = DATA_PATH / "configuration"
# ALICE_PATH = DATA_PATH / "alice"
# BOB_PATH = DATA_PATH / "bob"
# CAROL_PATH = DATA_PATH / "carol"


class PathManager:
    def __init__(self):
        # 初始化基本路径
        self.base_path = Path(os.path.realpath(__file__)).parent.parent.parent
        # 定义各个路径
        self.data_path = self.base_path / "data"
        self.config_path = self.data_path / "configuration"
        self.alice_path = self.data_path / "alice"
        self.bob_path = self.data_path / "bob"
        self.carol_path = self.data_path / "carol"

    def get_data_path(self):
        return self.data_path

    def get_config_path(self):
        return self.config_path

    def get_alice_path(self):
        return self.alice_path

    def get_bob_path(self):
        return self.bob_path

    def get_carol_path(self):
        return self.carol_path

    def __str__(self):
        return (
            f"Base Path: {self.base_path}\n"
            f"Data Path: {self.data_path}\n"
            f"Config Path: {self.config_path}\n"
            f"Alice Path: {self.alice_path}\n"
            f"Bob Path: {self.bob_path}\n"
            f"Carol Path: {self.carol_path}"
        )


# 使用 PathManager 类
if __name__ == "__main__":
    path_manager = PathManager()
    print(path_manager)
