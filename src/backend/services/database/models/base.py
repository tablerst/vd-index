import orjson


def orjson_dumps(v, *, default=None, sort_keys=False, indent_2=True):
    """
    自定义orjson序列化函数，确保中文字符不被转义为Unicode码
    """
    # 基础选项：不转义非ASCII字符（保持中文字符原样）
    option = 0

    # 添加排序选项
    if sort_keys:
        option |= orjson.OPT_SORT_KEYS

    # 添加缩进选项
    if indent_2:
        option |= orjson.OPT_INDENT_2

    # 关键修复：不转义非ASCII字符，保持中文字符原样显示
    # 注意：orjson默认会转义非ASCII字符，我们需要确保中文字符保持原样
    # 这里我们不使用任何会导致字符转义的选项

    if default is None:
        return orjson.dumps(v, option=option).decode()
    return orjson.dumps(v, default=default, option=option).decode()
