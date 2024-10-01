import re
import chardet


def process_fscan_data(fscan_data):
    results = {
        'OpenPort': [['IP', 'Port']],
        'OsList': [['IP', 'OS']],
        'Bug_ExpList': [['IP', 'Bug Exp']],
        'Bug_PocList': [['URL', 'Bug Poc']],
        'Title': [['URL', 'Code', 'Length', 'Title']],
        'WeakPasswd': [['IP', 'Server', 'Password']],
        'Finger': [['URL', 'Finger']],
        'NetInfo': [['IP', 'Netinfo']],
        'NetBios': [['IP', 'NetBios']]
    }
    datalist = [_.strip() for _ in fscan_data.split('\n')]

    def NetInfos():
        info_n = re.findall(r'(.*NetInfo.*\n.*(\n.*\[->].*)+)', fscan_data)
        for i in info_n:
            ip = re.findall(r'\[\*](\d+\.\d+\.\d+\.\d+)', i[0])
            netinfo_get = re.findall(r'((\n?.*\[->].*)+)', i[0])
            netinfo = netinfo_get[0][0]
            results['NetInfo'].append([ip[0], netinfo])

    NetInfos()

    for line in datalist:
        # 处理 OpenPort
        p = re.findall(r'^\d[^\s]+', line)
        if p:
            ip = re.findall(r"\d+\.\d+\.\d+\.\d+", p[0])
            port = re.findall("(?<=:)\d+", p[0])
            if ip and port:
                results['OpenPort'].append([ip[0], port[0]])

        # 处理 OsList
        p = re.findall(r"\[\*]\s\d+\.\d+\.\d+\.\d+.*", line)
        if p:
            ip = re.findall(r"\d+\.\d+\.\d+\.\d+", p[0])
            os_info = p[0].split(ip[0])[1].strip()
            if ip:
                results['OsList'].append([ip[0], os_info])

        # 处理 Bug_ExpList
        p = re.findall(r"\[\+]\s\d+\.\d+\.\d+\.\d+.*", line)
        if p:
            ip = re.findall(r"\d+\.\d+\.\d+\.\d+", p[0])
            bug = p[0].split(ip[0])[1].strip()
            if ip:
                results['Bug_ExpList'].append([ip[0], bug])

        # 处理 Bug_PocList
        p = re.findall(r"\[\+].*poc-yaml[^\s].*", line)
        if p:
            for u in p:
                url = re.findall(r"(?P<url>https?://\S+)", u)
                bug = re.findall(r"poc-yaml.*", u)

                if url and bug:
                    results['Bug_PocList'].append([url[0], bug[0]])

        # 处理 Title
        p = re.findall(r'\[\*]\sWebTitle.*', line)
        if p:
            url = re.findall(r"http[^\s]+", p[0])
            code = re.findall(r'(?<=code:)[^\s]+', p[0])
            length = re.findall(r'(?<=len:)[^\s]+', p[0])
            title = re.findall(r'(?<=title:).*', p[0])
            if url and code and length and title:
                results['Title'].append([url[0], code[0], length[0], title[0]])

        # 处理 WeakPasswd
        p = re.findall(r'((ftp|mysql|mssql|SMB|RDP|Postgres|SSH|oracle|SMB2-shares)(:|\s).*)', line, re.I)
        if p:
            ip = re.findall(r"\d+\.\d+\.\d+\.\d+", line)
            if ip:
                details = p[0][0].split(":")
                server = details[0]
                port = details[2] if len(details) > 2 else ''
                passwd = details[3] if len(details) > 3 else ''
                results['WeakPasswd'].append([ip[0], server, passwd])

        # 处理 Finger
        p = re.findall(r'.*InfoScan.*', line)
        if p:
            url = re.findall(r'http[^\s]+', p[0])
            if url:
                finger = p[0].split(url[0])[-1].strip()
                results['Finger'].append([url[0], finger])

        # 处理 NetBios
        if "NetBios" in line:
            ip = re.findall(r'\d+\.\d+\.\d+\.\d+', line)
            netbios_info = line.split("NetBios")[-1].strip()
            if ip:
                results['NetBios'].append([ip[0], netbios_info])

    return results


def get_encoding(file):
    # 二进制方式读取，获取字节数据，检测类型
    with open(file, 'rb') as f:
        data = f.read()
        return chardet.detect(data)['encoding']


def get_encode_info(file):
    with open(file, 'rb') as f:
        data = f.read()
        result = chardet.detect(data)
        return result['encoding']


def read_file(file):
    with open(file, 'rb') as f:
        return f.read()


def write_file(content, file):
    with open(file, 'wb') as f:
        f.write(content)


def convert_encode2utf8(file, original_encode, des_encode):
    file_content = read_file(file)
    file_decode = file_content.decode(original_encode, 'ignore')
    file_encode = file_decode.encode(des_encode)
    write_file(file_encode, file)


def OpenFile(file_name):
    datalist = []
    datastr = ''

    encode_info = get_encode_info(file_name)

    if encode_info == 'utf-8':

        with open(file_name, encoding='utf-8') as f:
            for i in f.readlines():
                datalist.append(i.strip())
        with open(file_name, encoding='utf-8') as f:
            datastr = f.read()

    elif encode_info != 'utf-8':

        convert_encode2utf8(file_name, encode_info, 'utf-8')

        with open(file_name, encoding='utf-8') as f:
            for i in f.readlines():
                datalist.append(i.strip())
        with open(file_name, encoding='utf-8') as f:
            datastr = f.read()

    return datalist, datastr


# 示例使用
if __name__ == "__main__":
    fscan_list, fscan_str = OpenFile('fscan_data.txt')
    print(process_fscan_data(fscan_str))