#!/usr/bin/env python3
import sys
import re
import configparser
import yaml
from colorama import Fore, Style, init

# 初始化colorama
init(autoreset=True)

class StringMessager:
    def __init__(self, initial=''):
        self.string = initial
    
    def write(self, other):
        self.string += other + ' | '
    
    def read(self):
        return self.string
    
    def reset(self):
        self.string = ''


class ConfigAnalysis:
    def __init__(self, eds_file_path, bus_file_path):
        self.eds_param_data = self._parse_eds_param(eds_file_path)
        self.eds_datatype_data = self._parse_eds_datatype(eds_file_path)
        self.bus_yaml_data = self._parse_bus_yaml(bus_file_path)

    def _parse_eds_datatype(self, file_path):
        config = configparser.ConfigParser(strict=False, interpolation=None)
        with open(file_path, 'r') as file:
            context = file.read()
        config.read_string(context)
        eds_data = {section: config.get(section, 'DataType', fallback='') for section in config.sections()}
        return eds_data

    def _parse_eds_param(self, file_path):
        config = configparser.ConfigParser(strict=False, interpolation=None)
        with open(file_path, 'r') as file:
            context = file.read()
        config.read_string(context)
        eds_data = {section: config.get(section, 'ParameterName', fallback='') for section in config.sections()}
        return eds_data

    def _parse_bus_yaml(self, file_path):
        with open(file_path, 'r') as file:
            bus_config = yaml.safe_load(file)
        bus_yaml_dict = {}
        for pdo_type in ['tpdo', 'rpdo']:
            for n in range(1, 5):
                temp_pdo = bus_config['joint_1'][pdo_type]
                if n not in temp_pdo or 'mapping' not in temp_pdo[n] or \
                   ('enabled' in temp_pdo[n] and temp_pdo[n]['enabled'] == 'false'):
                    break
                pdo_key = f"{pdo_type.upper()}{n}"
                bus_yaml_dict[pdo_key] = temp_pdo[n]['mapping']
        for key in bus_yaml_dict:
            temp_index_list = []
            for node in bus_yaml_dict[key]:
                if node['sub_index'] != 0:
                    temp_index = f"{hex(node['index'])[2:].upper()}sub{node['sub_index']}"
                else:
                    temp_index = hex(node['index'])[2:].upper()
                temp_index_list.append(temp_index)
            bus_yaml_dict[key] = temp_index_list
        return bus_yaml_dict


help_message = StringMessager()
config_analysis = ConfigAnalysis(
    # '/home/say/code/ros/canopen/install/canopen_tests/share/canopen_tests/config/robot_control/cia402_slave.eds',
    # '/home/say/code/ros/canopen/install/canopen_tests/share/canopen_tests/config/robot_control/bus.yml'
    '/home/say/ros2_example/r/install/canopen_tests/share/canopen_tests/config/robot_control/cia402_slave.eds',
    '/home/say/ros2_example/r/install/canopen_tests/share/canopen_tests/config/robot_control/bus.yml'
)

object_datatype = {
    '0x0001': 1, '0x0002': 1, '0x0003': 2, '0x0004': 4,
    '0x0005': 1, '0x0006': 2, '0x0007': 4, '0x0008': 4,
}

nmt_control_dict = {
    '01': '切换到操作状态', '02': '切换到停止状态',
    '80': '切换到预操作状态', '81': '重置节点', '82': '重置通信'
}

function_dict = {
    0x080: 'EMCY', 0x180: 'TPDO1', 0x280: 'TPDO2', 0x380: 'TPDO3',
    0x480: 'TPDO4', 0x200: 'RPDO1', 0x300: 'RPDO2', 0x400: 'RPDO3',
    0x500: 'RPDO4', 0x580: 'RSDO', 0x600: 'TSDO'
}

sdo_cs_dict = {
    # 快速SDO命令符
    '2F': '写一个字节', '40': '读取', '2B': '写两个字节', '4F': '读响应一个字节',
    '27': '写三个字节', '4B': '读响应两个字节', '23': '写四个字节',
    '47': '读响应三个字节', '60': '写成功应答', '43': '读响应四个字节',
    '80': '异常响应',
    # 普通SDO下载命令符(前一分段帧CS为10h)
    '0F': '本段写一个字节(前CS=10h)', '0D': '本段写两个字节(前CS=10h)',
    '0B': '本段写三个字节(前CS=10h)', '09': '本段写四个字节(前CS=10h)',
    '07': '本段写五个字节(前CS=10h)', '05': '本段写六个字节(前CS=10h)',
    '03': '本段写七个字节(前CS=10h)',
    # 普通SDO下载命令符(前一分段帧CS为00h)
    '1F': '本段写一个字节(前CS=00h)', '1D': '本段写两个字节(前CS=00h)',
    '1B': '本段写三个字节(前CS=00h)', '19': '本段写四个字节(前CS=00h)',
    '17': '本段写五个字节(前CS=00h)', '15': '本段写六个字节(前CS=00h)',
    '13': '本段写七个字节(前CS=00h)',
    # 普通SDO上传命令符(前一分段帧CS为10h)
    '0F': '本段写一个字节(前CS=10h)', '0D': '本段写两个字节(前CS=10h)',
    '0B': '本段写三个字节(前CS=10h)', '09': '本段写四个字节(前CS=10h)',
    '07': '本段写五个字节(前CS=10h)', '05': '本段写六个字节(前CS=10h)',
    '03': '本段写七个字节(前CS=10h)',
    # 普通SDO上传命令符(前一分段帧CS为00h)
    '1F': '本段写一个字节(前CS=00h)', '1D': '本段写两个字节(前CS=00h)',
    '1B': '本段写三个字节(前CS=00h)', '19': '本段写四个字节(前CS=00h)',
    '17': '本段写五个字节(前CS=00h)', '15': '本段写六个字节(前CS=00h)',
    '13': '本段写七个字节(前CS=00h)',
    # 通用异常响应
    '80': '异常响应'
}

error_code_dict = {
    '2211': '软件过流', '2212': '硬件过流', '3130': '缺相',
    '3150': '电流检测回路错误', '3151': '电流检测回路错误',
    '3152': '模拟量输入回路错误', '3153': '缺相', '3154': '模拟量输入回路错误',
    '3160': '模拟量1输入过大', '3161': '模拟量2输入过大', '3162': '模拟量3输入过大',
    '3201': '直流母线基准电压错误', '3205': '控制电压过低', '3206': '控制电压过高',
    '3211': '直流母线电压过高', '3221': '直流母线电压过低', '3222': '主电源断线',
    '4201': '温度基准采样错误', '4210': '驱动器温度过高',
    '5201': '不支持操作模式下驱动器使能', '5202': '同步模式下不支持该操作模式启动',
    '5441': '10台停', '5510': 'RAW不足', '5511': 'RAW越界',
    '5530': '保存参数错误', '5531': 'EEPROM硬件错误', '5532': '保存历史报警错误',
    '5533': '保存厂商参数错误', '5534': '保存通讯参数错误', '5535': '保存402参数错误',
    '5536': '保存断电数据错误', '5550': 'ESC EEPROM无法访问', '5551': 'ESI文件保存错误',
    '5552': '链路建立失败', 'FF01': '单位时间ECAT帧丢失过多',
    '6201': '保存的ESI文件与驱动器组件不匹配', '6202': 'FOE升级固件失败',
    '6203': '固件无效/失效', '6321': '输入10参数重复', '6322': '输入10参数超过范围',
    '6323': '输出10参数超过范围', '6329': 'FPGA写参数错误', '7122': '电机型号错误',
    '7321': '编码器断线', '7322': '编码器通讯错误', '7323': '编码器初始化位置错误',
    '7324': '编码器数据错误', '7325': '编码器数据加载错误', '7326': '编码器数据加载错误',
    '7327': '编码器数据加载错误', '7328': '编码器数据加载错误',
    '7329': '限位报警,限位功能选择为报警时有效', '7701': '泄放过载', '7702': '泄放电阻故障',
    '8110': 'CAN超载报警', '8120': '被动错误', '8130': '心跳/节点保护超时',
    '8140': '掉线恢复', '8141': '掉线', '8150': 'ID冲突', '8201': '通讯未知错误',
    '8207': 'PDO映射的对象不存在', '8208': 'PDO映射的对象长度错误',
    '8210': '由于长度错误PDO未处理/处理超时', '8211': '由于长度错误TPDO未处理/处理超时',
    '8212': '由于长度错误RPDO未处理/处理超时', '8213': 'BOOT不支持',
    '8215': 'BOOT模式配置无效', '8216': 'Preop无效配置', '8217': '无效SM配置/',
    '821B': 'SM看门狗超时', '821C': '无效SM类型', '821D': '无效输出配置',
    '821E': '无效输入配置', '821F': '无效看门狗配置', '8220': 'PDO长度越界',
    '8224': 'TFF00映射无效', '8225': 'RFF00映射无效', '8226': '配置不一致',
    '8310': '过载', '8311': '过载', '8301': '电机堵转', '8305': '转矩越界',
    '8401': '振动过大报警', '8402': '超速', '8403': '速度失控',
    '8503': '电子齿轮比错误', '8611': '位置环超差', '8610': '位置跟踪错误',
    '8612': '位置增量过大', '871A': '同步丢失错误', '8727': '不支持自由运行模式',
    '8728': '不支持同步模式', '872C': '致命同步错误', '872D': '无同步错误',
    '872E': '同步周期过小', '8730': '无效的DC配置', '8732': 'DC PLL错误',
    '8733': 'DC同步10错误', '8734': 'DC同步超时', '8735': 'DC周期无效',
    '8736': 'sync0周期无效', '8737': 'sync1周期无效', '873A': 'SW2丢失过多',
    '873B': 'Sync0丢失过多', '873C': 'DC误差过大', '8313': 'STO故障', '8150': 'ID重复'
}


def parse_nmt_state(nmt_message):
    temp_help_message = 'nmt 广播 ' if nmt_message[1] == '00' else f'nmt node{nmt_message[1]} '
    temp_help_message += nmt_control_dict.get(nmt_message[0], '未知命令')
    help_message.write(temp_help_message)
    return True


def parse_sync_message():
    help_message.write('sync')
    return True


def parse_node_id_message(message_id):
    cob_id = int(message_id, 16)
    function_id = cob_id & 0x780
    node_id = cob_id & 0x7F
    if function_id not in function_dict:
        return False
    temp_help_message = f'node{node_id} {function_dict[function_id]}'
    help_message.write(temp_help_message)
    return function_id


def parse_function_emcy(message_data):
    pass


def parse_function_pdo(function_name, message_data):
    if function_name not in config_analysis.bus_yaml_data:
        help_message.write('bus.yml not define mapping')
        return
    
    object_index = config_analysis.bus_yaml_data[function_name]
    index = 0
    temp_help_message = ''
    
    for node in object_index:
        param_name = config_analysis.eds_param_data.get(node, 'Unknown')
        temp_help_message += f"{node}({param_name})("
        
        temp_data = object_datatype.get(config_analysis.eds_datatype_data.get(node, '0x0001'), 1)
        data_values = []
        
        while temp_data > 0 and index < len(message_data):
            data_values.append(message_data[index])
            index += 1
            temp_data -= 1
            
        temp_help_message += ' '.join(data_values) + ') '
    
    help_message.write(temp_help_message)


def parse_function_sdo(message_data):
    pass


def parse_function_id(function_id, message_data):
    if function_dict[function_id] == 'EMCY':
        parse_function_emcy(message_data)
    elif 'TPDO' in function_dict[function_id] or 'RPDO' in function_dict[function_id]:
        parse_function_pdo(function_dict[function_id], message_data)
    elif 'SDO' in function_dict[function_id]:
        parse_function_sdo(message_data)


def parse_can_id(message):
    can_id = message['can_id']
    if can_id == '000':
        parse_nmt_state(message['message_data'].split())
    elif can_id == '080':
        parse_sync_message()
    else:
        function_id = parse_node_id_message(can_id)
        if function_id:
            parse_function_id(function_id, message['message_data'].split())


def parse_candump_line(line):
    pattern = r'(\S+)\s+(\S+)\s+\[(\d+)\]\s*(.*)'
    match = re.match(pattern, line)
    if not match:
        return False
    return {
        "interface": match.group(1),
        "can_id": match.group(2),
        "message_len": match.group(3),
        "message_data": match.group(4)
    }


def format_output(original_line, interpretation):
    """格式化输出，使其更加美观"""
    # 获取终端宽度 (默认为80)
    term_width = 80
    
    # 分割线
    separator = "─" * term_width
    
    # 原始数据部分
    raw_data = f"{Fore.CYAN}原始数据:{Style.RESET_ALL} {original_line}"
    
    # 解析部分
    interpretation_text = f"{Fore.GREEN}解析内容:{Style.RESET_ALL} {interpretation}"
    
    # 按字段拆分原始行格式化输出
    parts = original_line.split()
    if len(parts) >= 4:
        interface = parts[0]
        can_id = parts[1]
        length = parts[2]
        data = ' '.join(parts[3:])
        
        formatted_raw = (
            f"{Fore.CYAN}接口:{Style.RESET_ALL} {interface.ljust(10)} "
            f"{Fore.CYAN}ID:{Style.RESET_ALL} {can_id.ljust(6)} "
            f"{Fore.CYAN}长度:{Style.RESET_ALL} {length.ljust(4)} "
            f"{Fore.CYAN}数据:{Style.RESET_ALL} {data}"
        )
    else:
        formatted_raw = raw_data
    
    return f"{separator}\n{formatted_raw}\n{interpretation_text}"


def main():
    print(f"{Fore.YELLOW}CAN 数据解析工具 - 开始监听标准输入{Style.RESET_ALL}")
    print("按 Ctrl+C 终止")
    print("-" * 80)
    
    try:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
                
            help_message.reset()
            parsed_data = parse_candump_line(line)
            
            if parsed_data:
                parse_can_id(parsed_data)
                formatted_output = format_output(line, help_message.read().strip())
                print(formatted_output)
            else:
                print(f"{Fore.RED}无法解析行:{Style.RESET_ALL} {line}")
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}程序已终止{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
