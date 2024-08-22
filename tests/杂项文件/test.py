def get_variable_name(var):
    # 遍历全局变量字典
    for name, value in globals().items():
        if value is var:
            return name
    return None


# 示例用法
my_var = 42
print(get_variable_name(my_var))  # 输出: my_var
