import re


def filter(output_str: str, status_codes: list = None, size_filter: tuple = None, path_regex: str = None):
    if status_codes is None:
        status_codes = []

    if not isinstance(output_str, str):
        raise ValueError("output_str must be a string.")
    if not isinstance(status_codes, list) or not all(isinstance(code, str) for code in status_codes):
        raise ValueError("status_codes must be a list of strings.")
    if size_filter is not None and (not isinstance(size_filter, tuple) or len(size_filter) != 3):
        raise ValueError("size_filter must be a tuple of (min, max, unit) or None.")

    # 默认值
    min_bytes, max_bytes = 0, float('inf')
    unit_multiplier = {'B': 1, 'KB': 1024, 'MB': 1024**2, 'GB': 1024**3}

    if size_filter:
        min_size, max_size, unit = size_filter

        if min_size is None:
            min_size = 0
        if max_size is None:
            max_size = float('inf')

        if not isinstance(min_size, (int, float)) or not isinstance(max_size, (int, float)):
            raise ValueError("min and max size must be numbers.")
        if min_size < 0 or (max_size < 0 if max_size != float('inf') else False) or min_size > max_size:
            raise ValueError("min_size must be >= 0 and min_size must be <= max_size.")
        if unit and unit not in unit_multiplier:
            raise ValueError("unit must be one of: 'B', 'KB', 'MB', 'GB'.")
        min_bytes = min_size * unit_multiplier.get(unit, 1)
        max_bytes = max_size * unit_multiplier.get(unit, float('inf'))
    patterns = [
        r'\[(\d{2}:\d{2}:\d{2})\]\s*(\d{3})\s*-\s*(\d+)\s*(B|KB|MB|GB)\s*-\s*(.+?\s*-?>?\s*.+)?',
        r'(\d{3})\s+(\d+)\s*(B|KB|MB|GB)\s+(http[^\s]+)\s*(->\s*REDIRECTS TO:\s*(.+))?'
    ]

    filtered = []
    for pattern in patterns:
        matches = re.findall(pattern, output_str)
        for match in matches:
            if len(match) == 5:  # 第一个模式
                time, status, size, size_unit, path = match
                if '->' in path:
                    path = path.split('->')[0].strip()
                    redirect_path = ''.join(path.split('->')[::])
                else:
                    redirect_path = ''
            elif len(match) == 6:  # 第二个模式
                time = ''
                status, size, size_unit, path = match[:4]
                redirect_path = match[5] if match[5] else ''
            else:
                print("长度不一致")
                print(len(match), match)

            # 确保 size 是数字
            try:
                size_bytes = int(size) * unit_multiplier[size_unit]
            except (ValueError, KeyError):
                continue  # 跳过该匹配

            # 路径正则匹配
            if path_regex and not re.search(path_regex, path, re.IGNORECASE):
                continue

            if (not status_codes or status in status_codes) and (size_filter is None or min_bytes <= size_bytes <= max_bytes):
                filtered.append((time, status, size, size_unit, path.strip(), redirect_path.strip()))

    return filtered


if __name__ == '__main__':
    output_str = r""" 
Target: http://127.0.0.1/

[09:45:35] Starting:
[09:45:39] 301 -    0B  - /\..\..\..\..\..\..\..\..\..\etc\passwd  ->  /%5C..%5C..%5C..%5C..%5C..%5C..%5C..%5C..%5C..%5Cetc%5Cpasswd/
[09:45:40] 301 -    0B  - /a%5c.aspx  ->  /a%5C.aspx/
[09:45:52] 200 -    1KB - /Desktop.ini
[09:45:52] 200 -    20KB - /Desktop.ini
[09:45:52] 200 -    1KB - /Desktop.ini
[09:45:52] 200 -    500KB - /Desktop.ini
[09:45:52] 200 -    12MB - /Desktop.ini
[09:46:09] 301 -    0B  - /reports  ->  /reports/

Task Completed

# Dirsearch started Tue Oct  1 09:46:09 2024 as: F:\web_tools\/dirsearch-目录扫描/dirsearch.py -u http://127.0.0.1:80

301     0B   http://127.0.0.1/\..\..\..\..\..\..\..\..\..\etc\passwd    -> REDIRECTS TO: /%5C..%5C..%5C..%5C..%5C..%5C..%5C..%5C..%5C..%5Cetc%5Cpasswd/
301     0B   http://127.0.0.1/a%5c.aspx    -> REDIRECTS TO: /a%5C.aspx/
200     1KB  http://127.0.0.1/Desktop.ini
301     0B   http://127.0.0.1/reports    -> REDIRECTS TO: /reports/
    """

    status_codes = None
    size_filter = (2, None, 'B')  # 示例: (None, 1, None) 表示大小在 0 到 1 KB 之间
    path_regex = ''  # 例子：匹配路径中包含 "desktop.ini" 的情况
    filtered_results = filter(output_str, status_codes, size_filter, path_regex)

    for result in filtered_results:
        time, status, size, size_unit, path, redirect_output = result
        print(f"[{time}] {status} - {size}{size_unit} - {path}{' -> ' + redirect_output if redirect_output else ''}")
