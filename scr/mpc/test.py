from scr.utils import *
import spu

# import sys
# from pathlib import Path

# # 将项目根目录添加到 sys.path
# sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

# from sf.utils import *


path_manager = PathManager()
LINK_DESC_PATH = path_manager.get_path("LINK_DESC_PATH")
print(LINK_DESC_PATH)

link_desc = {
    "recv_timeout_ms": 6000,
}

write_yaml(LINK_DESC_PATH, link_desc)
print(read_yaml(LINK_DESC_PATH))
