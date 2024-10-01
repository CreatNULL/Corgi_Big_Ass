import re


def filter_response_data(output_str, methods: list = None, line_count: tuple = None, word_count: tuple = None, byte_count: tuple = None, path_regex: str = None, status_codes: list = None):
    filtered_results = []

    # 更新正则表达式以支持提取跳转路径
    pattern = re.compile(r'(\d{3})\s+(\w+)\s+(\d+)l\s+(\d+)w\s+(\d+)c\s+(http[^\s]+)(?:\s*=>\s*(http[^\s]+))?')

    for line in output_str.splitlines():
        match = pattern.match(line.strip())
        if not match:
            continue

        status_code = match.group(1)
        method = match.group(2)
        l_count = int(match.group(3))
        w_count = int(match.group(4))
        b_count = int(match.group(5))
        url = match.group(6)
        redirect_url = match.group(7) if match.group(7) else None

        # 过滤请求方法
        if methods and method not in methods:
            continue

        # 过滤状态码
        if status_codes and status_code not in status_codes:
            continue

        # 处理行数、字数、字节数范围
        if (line_count and
            (line_count[0] is not None and l_count < line_count[0] or
             line_count[1] is not None and l_count > line_count[1])) or \
                (word_count and
                 (word_count[0] is not None and w_count < word_count[0] or
                  word_count[1] is not None and w_count > word_count[1])) or \
                (byte_count and
                 (byte_count[0] is not None and b_count < byte_count[0] or
                  byte_count[1] is not None and b_count > byte_count[1])):
            continue

        # 过滤路径，忽略大小写
        if path_regex and not re.search(path_regex, url, re.IGNORECASE):
            continue

        filtered_results.append({
            'status_code': status_code,
            'method': method,
            'lines': l_count,
            'words': w_count,
            'bytes': b_count,
            'url': url,
            'redirect_url': redirect_url
        })

    return filtered_results

if __name__ == '__main__':
    # 使用示例
    output_data = """
200      GET        5l       31w      408c http://127.0.0.1/
301      GET        0l        0w        0c http://127.0.0.1/reports => http://127.0.0.1/reports/
301      GET        0l        0w        0c http://127.0.0.1/reports/http_127.0.0.1_80 => http://127.0.0.1/reports/http_127.0.0.1_80/
200      GET        0l        0w        0c http://127.0.0.1/con
301      GET        1l        0w        0c http://127.0.0.1/REPORTS => http://127.0.0.1/REPORTS/
301      POST        1l        0w        1c http://127.0.0.1/REPORTS => http://127.0.0.1/REPORTS/
    """

    # 设置范围过滤和路径正则
    result = filter_response_data(
        output_data,
        methods=["GET", "POST"],
        word_count=(None, None),
        byte_count=(None, None),
        path_regex='con',
        status_codes=["200",]
    )

    for entry in result:
        print(entry)
