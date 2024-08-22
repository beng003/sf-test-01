import os
from pathlib import Path

__all__ = ["PathManager"]

# 数据文件存储路径
DATA_PATH = Path(os.path.realpath(__file__)).parent.parent / "data"
# 配置文件存储路径
CONFIG_PATH = DATA_PATH / "configuration"
ALICE_PATH = DATA_PATH / "alice"
BOB_PATH = DATA_PATH / "bob"
CAROL_PATH = DATA_PATH / "carol"

# sf集群配置文件路径
CLUSTER_CONFIG_PATH = CONFIG_PATH / "cluster_config.yaml"
# SPU初始化配置文件路径
CLUSTER_DEF_PATH = CONFIG_PATH / "cluster_def.yaml"
LINK_DESC_PATH = CONFIG_PATH / "link_desc.yaml"
# 证书路径
TLS_PATH = CONFIG_PATH / "tls_config.yaml"

class PathManager:
    def __init__(self):
        """初始化路径管理器，使用一个字典将变量名和路径绑定。"""
        self.paths = {}
        # 添加默认路径
        self.add_path("DATA_PATH", DATA_PATH, False)
        self.add_path("CONFIG_PATH", CONFIG_PATH, False)
        self.add_path("ALICE_PATH", ALICE_PATH, False)
        self.add_path("BOB_PATH", BOB_PATH, False)
        self.add_path("CAROL_PATH", CAROL_PATH, False)

        self.add_path("CLUSTER_CONFIG_PATH", CLUSTER_CONFIG_PATH, False)
        self.add_path("CLUSTER_DEF_PATH", CLUSTER_DEF_PATH, False)
        self.add_path("LINK_DESC_PATH", LINK_DESC_PATH, False)
        self.add_path("TLS_PATH", TLS_PATH, False)

    def add_path(self, var_name, new_path, print_tf = True):
        """添加路径并与变量名绑定，路径将被标准化为Path对象。"""
        path = Path(new_path).resolve()  # 使用 Path 并转换为绝对路径
        if var_name not in self.paths:
            self.paths[var_name] = path
            if print_tf:
                print(f"添加路径：{var_name} -> {path}")
        else:
            print(f"变量名 '{var_name}' 已存在，绑定的路径为：{self.paths[var_name]}")

    def update_path(self, var_name, new_path):
        """修改指定变量名绑定的路径。"""
        if var_name in self.paths:
            path = Path(new_path).resolve()  # 使用 Path 并转换为绝对路径
            self.paths[var_name] = path
            print(f"更新路径：{var_name} -> {path}")
        else:
            self.add_path(self, var_name, new_path)
            print(f"变量名 '{var_name}' 不存在，添加路径：{var_name} -> {new_path}")

    def remove_path(self, var_name):
        """移除指定变量名绑定的路径。"""
        if var_name in self.paths:
            del self.paths[var_name]
            print(f"移除了路径变量：{var_name}")
        else:
            print(f"变量名 '{var_name}' 不存在。")

    def get_path(self, var_name):
        """根据变量名获取路径，如果不存在则提示。"""
        if var_name in self.paths:
            return self.paths[var_name]
        else:
            print(f"变量名 '{var_name}' 不存在。")
            return None

    def get_all_paths(self):
        """返回所有变量名和路径的映射。"""
        return self.paths

    def path_exists(self, var_name):
        """检查路径是否存在于系统中。"""
        path = self.get_path(var_name)
        if path and path.exists():
            return True
        else:
            return False

    def to_absolute_path(self, var_name):
        """将变量名对应的路径转换为绝对路径（已默认转为绝对路径）。"""
        path = self.get_path(var_name)
        if path:
            return path.resolve()
        else:
            return None

    def clear_paths(self):
        """清除所有路径绑定。"""
        self.paths.clear()
        print("已清空所有路径。")


# 示例用法
if __name__ == "__main__":
    path_manager = PathManager()

    # 添加路径并绑定变量
    path_manager.add_path("docs", "./my_project/docs")
    path_manager.add_path("config", "/etc/config")

    # 获取特定路径
    print("docs路径：", path_manager.get_path("docs"))

    # 检查路径是否存在
    print("docs路径是否存在：", path_manager.path_exists("docs"))

    # 转换为绝对路径
    print("config的绝对路径：", path_manager.to_absolute_path("config"))

    # 移除路径
    path_manager.remove_path("docs")
    print("移除后的所有路径：", path_manager.get_all_paths())

    # 清空所有路径
    path_manager.clear_paths()
    print("清空后的所有路径：", path_manager.get_all_paths())
