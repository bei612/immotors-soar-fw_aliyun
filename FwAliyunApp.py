from alibabacloud_cloudfw20171207.client import Client as Cloudfw20171207Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_cloudfw20171207 import models as cloudfw_20171207_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as UtilClient
from loguru import logger  # 导入日记库，没有请先安装 pip install loguru
import os
import ipaddress
import random
import string
import re

class FwAliyunApp:
    # 封禁、接封禁业务场景的常量配置
    BLACKLIST_IN_GROUP = "DEV-P-Deny-Secops-Blacklist-In" # 入向地址资源组和控制策略组
    BLACKLIST_OUT_GROUP = "DEV-P-Deny-Secops-Blacklist-Out" # 出向地址资源组和控制策略组
    MAX_ADDRESS_GROUP_SIZE = 2000  # 当前购买的阿里云的地址资源组最大数量是 2000
    ACL_ACTION_DROP = 'log'  # 控制策略动作  生产用drop，测试用log
    
    def __init__(self, ak, sk, endpoint, proxies):
        self.ak = ak
        self.sk = sk
        self.endpoint = endpoint
        self.proxies = self.process_proxy_config(proxies.strip() if proxies else "")
        pass
    
    def process_proxy_config(self, proxy_url):
        """
        处理代理配置，解析统一格式并转换为阿里云SDK支持的格式
        支持多种格式：
        - 无代理：None 或 空字符串
        - 无认证：http://proxy.example.com:8080
        - 有认证：http://user:pass@proxy.example.com:8080
        - SOCKS5：socks5://user:pass@proxy.example.com:1080
        
        Args:
            proxy_url (str): 代理URL，格式：协议://[用户名:密码@]地址:端口
            
        Returns:
            dict: 包含代理配置信息的字典，如果为空则返回None
                 格式: {'protocol': 'http|https|socks5', 'url': '完整URL'}
        """
        if not proxy_url:
            return None
            
        # 验证代理URL格式
        proxy_pattern = r'^(https?|socks5)://(?:([^:]+):([^@]+)@)?([^:]+):(\d+)$'
        match = re.match(proxy_pattern, proxy_url)
        if not match:
            logger.warning(f"代理URL格式不正确: {proxy_url}")
            return None
            
        protocol, username, password, host, port = match.groups()
        # 验证协议支持
        if protocol not in ['http', 'https', 'socks5']:
            logger.warning(f"不支持的代理协议: {protocol}")
            return None
        # 验证端口范围
        try:
            port_num = int(port)
            if not (1 <= port_num <= 65535):
                logger.warning(f"代理端口超出范围: {port}")
                return None
        except ValueError:
            logger.warning(f"代理端口格式错误: {port}")
            return None
        # 验证主机地址格式
        if not host or len(host.strip()) == 0:
            logger.warning(f"代理主机地址为空")
            return None
        
        logger.info(f"使用代理: {protocol}://{host}:{port}" + 
                   (f" (用户: {username})" if username else " (无认证)"))
        
        # 返回代理配置信息
        return {
            'protocol': protocol,
            'url': proxy_url
        }

    def create_runtime_options(self):
        """
        根据代理配置创建RuntimeOptions
        
        Returns:
            util_models.RuntimeOptions: 配置了代理的运行时选项
        """
        if not self.proxies:
            return util_models.RuntimeOptions()
        
        proxy_protocol = self.proxies['protocol']
        proxy_url = self.proxies['url']
        
        if proxy_protocol == 'socks5':
            # SOCKS5代理
            return util_models.RuntimeOptions(socks_5proxy=proxy_url)
        else:
            # HTTP/HTTPS代理
            return util_models.RuntimeOptions(https_proxy=proxy_url, http_proxy=proxy_url)

    def check_address_type(self, addresslist):
        try:
            ipaddress.IPv4Address(addresslist)
            return "ipv4"
        except ipaddress.AddressValueError:
            pass

        try:
            ipaddress.IPv6Address(addresslist)
            return "ipv6"
        except ipaddress.AddressValueError:
            pass
        try:
            ipaddress.IPv4Network(addresslist)
            return "network"
        except (ipaddress.AddressValueError, ipaddress.NetmaskValueError):
            pass
        return "domain"

    def check_os_type(self):
        sysname = os.uname().sysname
        logs_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__))) + "/logs"
        file_name = os.path.splitext(os.path.basename(__file__))[0].lower()
        logger.remove()
        if sysname == "Darwin":
            logger.add(f'{logs_path}/{file_name}_run.log', rotation='00:00', encoding='utf-8', enqueue=True,
                       retention="30 days")
        elif sysname == "Linux":
            logger.add(f'{os.path.dirname(__file__)}/run.log', rotation='500MB')

    def filter_check(self, addr, network):
        if ipaddress.ip_address(addr) in ipaddress.ip_network(network):
            return True
        else:
            return False

    def create_client(self) -> Cloudfw20171207Client:
        config = open_api_models.Config(
            access_key_id=self.ak,
            access_key_secret=self.sk
        )
        config.endpoint = self.endpoint
        return Cloudfw20171207Client(config)

    def add_address_book(self, groupname, grouptype, description, addresslist):
        client = self.create_client()
        random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
        
        add_address_book_request = cloudfw_20171207_models.AddAddressBookRequest(
            description=f"{description}-{random_string}",
            group_name=f"{groupname}-{random_string}",
            group_type=grouptype,
            address_list=addresslist
        )
        runtime = self.create_runtime_options()
        # 定义日志配置
        self.check_os_type()
        try:
            res = client.add_address_book_with_options(add_address_book_request, runtime).to_map()
            logger.info(f'{res}')
            if res['statusCode'] == 200:
                msg = {
                    "groupname": f"{groupname}-{random_string}",
                    "description": f"{description}-{random_string}",
                    "groupuuid": res['body']['GroupUuid'],
                    "grouptype": f"{grouptype}",
                    "desc": "创建成功"
                }
                return msg
            else:
                msg = {
                    "groupname": f"{groupname}-{random_string}",
                    "description": f"{description}-{random_string}",
                    "grouptype": f"{grouptype}",
                    "desc": "创建失败"
                }
                return msg
        except Exception as e:
            res = UtilClient.assert_as_string(e.message)
            logger.error(f'{e}')
            return res


    def delete_address_book(self, groupuuid):
        client = self.create_client()
        delete_address_book_request = cloudfw_20171207_models.DeleteAddressBookRequest(
            group_uuid=groupuuid
        )
        runtime = self.create_runtime_options()
        # 定义日志配置
        self.check_os_type()
        try:
            res = client.delete_address_book_with_options(delete_address_book_request, runtime).to_map()
            logger.info(f'{res}')
            return res
        except Exception as e:
            res = UtilClient.assert_as_string(e.message)
            logger.error(f'{e}')
            return res

    def describe_address_book(self, query, grouptype):
        client = self.create_client()
        describe_address_book_request = cloudfw_20171207_models.DescribeAddressBookRequest(
            query=query,
            current_page=1,
            page_size=500,
            group_type=grouptype
        )
        runtime = self.create_runtime_options()
        # 定义日志配置
        self.check_os_type()
        try:
            res = client.describe_address_book_with_options(describe_address_book_request, runtime).to_map()
            logger.info(f'{res}')
            return res
        except Exception as e:
            res = UtilClient.assert_as_string(e.message)
            logger.error(f'{e}')
            return res

    def modify_address_book(self, groupname, groupuuid, description, addresslist):
        client = self.create_client()
        modify_address_book_request = cloudfw_20171207_models.ModifyAddressBookRequest(
            description=description,
            group_name=groupname,
            group_uuid=groupuuid,
            address_list=addresslist
        )
        runtime = self.create_runtime_options()
        # 定义日志配置
        self.check_os_type()
        try:
            res = client.modify_address_book_with_options(modify_address_book_request, runtime).to_map()
            logger.info(f'{res}')
            return res
        except Exception as e:
            res = UtilClient.assert_as_string(e.message)
            logger.error(f'{e}')
            return res

    def describe_control_policy(self, direction):
        client = self.create_client()
        describe_control_policy_request = cloudfw_20171207_models.DescribeControlPolicyRequest(
            direction=direction,
            current_page=1,
            page_size=500
        )
        runtime = self.create_runtime_options()
        # 定义日志配置
        self.check_os_type()
        try:
            res = client.describe_control_policy_with_options(describe_control_policy_request, runtime).to_map()
            logger.info(f'{res}')
            return res
        except Exception as e:
            res = UtilClient.assert_as_string(e.message)
            logger.error(f'{e}')
            return res

    def add_control_policy(self, aclaction, description, destination, destinationtype, direction, proto, source,
                           sourcetype, neworder, applicationname=None, applicationnamelist=None):
        client = self.create_client()
        if applicationname:
            add_control_policy_request = cloudfw_20171207_models.AddControlPolicyRequest(
                acl_action=aclaction,
                description=description,
                destination=destination,
                destination_type=destinationtype,
                direction=direction,
                proto=proto,
                source=source,
                source_type=sourcetype,
                new_order=neworder,
                application_name=applicationname
            )
        elif applicationnamelist:
            if type(applicationnamelist) == str:
                applicationnamelist = ['HTTP','HTTPS','SSL','SMTP','SMTPS']
            add_control_policy_request = cloudfw_20171207_models.AddControlPolicyRequest(
                acl_action=aclaction,
                description=description,
                destination=destination,
                destination_type=destinationtype,
                direction=direction,
                proto=proto,
                source=source,
                source_type=sourcetype,
                new_order=neworder,
                application_name_list=applicationnamelist
            )
        runtime = self.create_runtime_options()
        # 定义日志配置
        self.check_os_type()
        try:
            res = client.add_control_policy_with_options(add_control_policy_request, runtime).to_map()
            logger.info(f"{res}")
            if res['statusCode'] == 200:
                msg = {
                    "policyname": f"{destination}",
                    "description": f"{description}",
                    "grouptype": f"{destinationtype}",
                    "desc": "创建成功"
                }
                return msg
            else:
                msg = {
                    "policyname": f"{destination}",
                    "description": f"{description}",
                    "grouptype": f"{destinationtype}",
                    "desc": "创建失败"
                }
                return msg
        except Exception as e:
            res = UtilClient.assert_as_string(e.message)
            logger.error(f'{e}')
            return res

    def delete_control_policy(self, acluuid, direction):
        client = self.create_client()
        delete_control_policy_request = cloudfw_20171207_models.DeleteControlPolicyRequest(
            acl_uuid=acluuid,
            direction=direction
        )
        runtime = self.create_runtime_options()
        # 定义日志配置
        self.check_os_type()
        try:
            res = client.delete_control_policy_with_options(delete_control_policy_request, runtime).to_map()
            logger.info(f'{res}')
            return res
        except Exception as e:
            res = UtilClient.assert_as_string(e.message)
            logger.error(f'{e}')
            return res

    def single_block_address(self, addr, direction=None):
        # 定义日志配置
        self.check_os_type()
        # 判断需要解封的地址资源属于ip类型或net类型或domain类型
        if self.check_address_type(addr) == "ipv4":
            addr_obj = f"{addr}/32"
            describe_address_book_grouptype = "ip"
        elif self.check_address_type(addr) == "network":
            addr_obj = f"{addr}"
            describe_address_book_grouptype = "ip"
        elif self.check_address_type(addr) == "domain":
            addr_obj = f"{addr}"
            describe_address_book_grouptype = "domain"
        elif self.check_address_type(addr) == "ipv6":
            msg = {
                "addr": f"{addr}",
                "desc": "无需封禁"
            }
            logger.info(f'{msg}')
            return msg
        # 验证direction参数并查询相应的地址资源组
        if direction == 'in':
            query_prefix = self.BLACKLIST_IN_GROUP
        elif direction == 'out':
            query_prefix = self.BLACKLIST_OUT_GROUP
        else:
            # direction参数无效时返回错误信息
            msg = {
                "addr": f"{addr}",
                "desc": "direction参数必须为'in'或'out'"
            }
            logger.error(f'{msg}')
            return msg
            
        res_describe_address_book = self.describe_address_book(
            query=query_prefix,
            grouptype=describe_address_book_grouptype
        )
        # 判断需要封禁的地址资源是否已存在于现有封禁策略中，如存在则found赋值为True，如不存在则found赋值为False
        found = False
        for list_res_describe_address_book in res_describe_address_book['body']['Acls']:
            # 需要检查组名，因为query可能是模糊搜索，返回的结果可能包含其他相关组
            if ((direction == 'in' and self.BLACKLIST_IN_GROUP in list_res_describe_address_book['GroupName']) or
                (direction == 'out' and self.BLACKLIST_OUT_GROUP in list_res_describe_address_book['GroupName'])):
                match_list = list_res_describe_address_book['AddressList']
                if addr_obj in match_list:
                    found = True
                    break
        # 判断需要封禁的地址资源是否执行封禁任务，如found值为True，返回msg无需封禁
        if found == True:
            msg = {
                "addr": f"{addr}",
                "desc": "无需封禁"
            }
            logger.info(f'{msg}')
            return msg
        # 判断需要封禁的地址资源是否执行封禁任务，如found值为False，执行封禁任务序列
        elif found == False:
            if direction == 'in':
                # 将包含入站黑名单的地址资源组汇总成addrgrps地址资源组列表
                addrgrps = [data_describe_address_book for data_describe_address_book in
                            res_describe_address_book['body']['Acls']
                            if self.BLACKLIST_IN_GROUP in data_describe_address_book['GroupName']]
                print(f'包含入站黑名单的地址资源组: {addrgrps}')
                for addrgrp in addrgrps:
                    len_addrgrp = len(addrgrp['AddressList'])
                    data_len_addrgrp = len_addrgrp + 1
                    # 判断需要封禁的地址资源组内的地址资源是否超过最大上限，如不超过限制，将需要封禁的地址资源更新至地址资源组
                    if len_addrgrp < self.MAX_ADDRESS_GROUP_SIZE:
                        addrgrp_groupname = addrgrp['GroupName']
                        addrgrp_groupuuid = addrgrp['GroupUuid']
                        addrgrp_description = addrgrp['Description']
                        list_addrgrp_addresslist = addrgrp['AddressList']
                        list_addrgrp_addresslist.append(addr_obj)
                        data_addrgrp_addresslist = ','.join(list_addrgrp_addresslist)
                        # 将需要封禁的地址资源更新至地址资源组
                        res_modify_address_book = self.modify_address_book(
                            groupname=addrgrp_groupname,
                            groupuuid=addrgrp_groupuuid,
                            description=addrgrp_description,
                            addresslist=data_addrgrp_addresslist
                        )
                        if res_modify_address_book['statusCode'] == 200:
                            msg = {
                                "addr": f"{addr}",
                                "groupname": f"{addrgrp_groupname}",
                                "groupuuid": f"{addrgrp_groupuuid}",
                                "description": f"{addrgrp_description}",
                                "grouplen": f"{data_len_addrgrp}",
                                "desc": "封禁成功"
                            }
                            logger.info(f'{msg}')
                            return msg
                        else:
                            msg = {
                                "addr": f"{addr}",
                                "groupname": f"{addrgrp_groupname}",
                                "groupuuid": f"{addrgrp_groupuuid}",
                                "description": f"{addrgrp_description}",
                                "grouplen": f"{data_len_addrgrp}",
                                "desc": "封禁失败"
                            }
                            logger.info(f'{msg}')
                            return msg
                    # 判断需要封禁的地址资源组内的地址资源是否超过最大上限，如超过限制，新建控制策略组，新建地址资源组，将需要封禁的地址资源更新至新建的地址资源组
                    else:
                        # 创建地址资源组，将需要封禁的地址资源更新至新至新建的地址资源组
                        res_add_address_book = self.add_address_book(
                            groupname=self.BLACKLIST_IN_GROUP,
                            grouptype=describe_address_book_grouptype,
                            description=self.BLACKLIST_IN_GROUP,
                            addresslist=addr_obj
                        )
                        res_add_address_book_groupname = res_add_address_book['groupname']
                        res_add_address_book_description = res_add_address_book['description']
                        res_add_address_book_groupuuid = res_add_address_book['groupuuid']
                        # 创建控制策略组，将需要封禁的地址资源组更新至新建的控制策略组
                        res_add_control_policy = self.add_control_policy(
                            aclaction=self.ACL_ACTION_DROP,
                            description=res_add_address_book_description,
                            destination='0.0.0.0/0',
                            destinationtype='net',
                            direction=direction,
                            proto='ANY',
                            source=res_add_address_book_groupname,
                            sourcetype='group',
                            neworder=2,
                            applicationname='ANY'
                        )
                        if res_add_address_book['desc'] == "创建成功" and res_add_control_policy['desc'] == "创建成功":
                            msg = {
                                "addr": f"{addr}",
                                "groupname": f"{res_add_address_book_groupname}",
                                "groupuuid": f"{res_add_address_book_groupuuid}",
                                "description": f"{res_add_address_book_description}",
                                "grouplen": 1,
                                "desc": "封禁成功"
                            }
                            logger.info(f'{msg}')
                            return msg
                        else:
                            msg = {
                                "addr": f"{addr}",
                                "groupname": f"{res_add_address_book_groupname}",
                                "groupuuid": f"{res_add_address_book_groupuuid}",
                                "description": f"{res_add_address_book_description}",
                                "grouplen": 1,
                                "desc": "封禁失败"
                            }
                            logger.info(f'{msg}')
                            return msg
                
                # 如果没有找到现有的入站黑名单地址组，创建第一个地址组和控制策略
                if not addrgrps:
                    # 创建地址资源组，将需要封禁的地址资源更新至新建的地址资源组
                    res_add_address_book = self.add_address_book(
                        groupname=self.BLACKLIST_IN_GROUP,
                        grouptype=describe_address_book_grouptype,
                        description=self.BLACKLIST_IN_GROUP,
                        addresslist=addr_obj
                    )
                    res_add_address_book_groupname = res_add_address_book['groupname']
                    res_add_address_book_description = res_add_address_book['description']
                    res_add_address_book_groupuuid = res_add_address_book['groupuuid']
                    # 创建控制策略组，将需要封禁的地址资源组更新至新建的控制策略组
                    res_add_control_policy = self.add_control_policy(
                        aclaction=self.ACL_ACTION_DROP,
                        description=res_add_address_book_description,
                        destination='0.0.0.0/0',
                        destinationtype='net',
                        direction=direction,
                        proto='ANY',
                        source=res_add_address_book_groupname,
                        sourcetype='group',
                        neworder=2,
                        applicationname='ANY'
                    )
                    if res_add_address_book['desc'] == "创建成功" and res_add_control_policy['desc'] == "创建成功":
                        msg = {
                            "addr": f"{addr}",
                            "groupname": f"{res_add_address_book_groupname}",
                            "groupuuid": f"{res_add_address_book_groupuuid}",
                            "description": f"{res_add_address_book_description}",
                            "grouplen": 1,
                            "desc": "封禁成功"
                        }
                        logger.info(f'{msg}')
                        return msg
                    else:
                        msg = {
                            "addr": f"{addr}",
                            "groupname": f"{res_add_address_book_groupname}",
                            "groupuuid": f"{res_add_address_book_groupuuid}",
                            "description": f"{res_add_address_book_description}",
                            "grouplen": 1,
                            "desc": "封禁失败"
                        }
                        logger.info(f'{msg}')
                        return msg
            elif direction == 'out':
                # 将包含出站黑名单的地址资源组汇总成addrgrps地址资源组列表
                addrgrps = [data_describe_address_book for data_describe_address_book in
                            res_describe_address_book['body']['Acls']
                            if self.BLACKLIST_OUT_GROUP in data_describe_address_book['GroupName']]
                for addrgrp in addrgrps:
                    len_addrgrp = len(addrgrp['AddressList'])
                    data_len_addrgrp = len_addrgrp + 1
                    # 判断需要封禁的地址资源组内的地址资源是否超过最大上限，如不超过限制，将需要封禁的地址资源更新至地址资源组
                    if len_addrgrp < self.MAX_ADDRESS_GROUP_SIZE:
                        addrgrp_groupname = addrgrp['GroupName']
                        addrgrp_groupuuid = addrgrp['GroupUuid']
                        addrgrp_description = addrgrp['Description']
                        list_addrgrp_addresslist = addrgrp['AddressList']
                        list_addrgrp_addresslist.append(addr_obj)
                        data_addrgrp_addresslist = ','.join(list_addrgrp_addresslist)
                        # 将需要封禁的地址资源更新至地址资源组
                        res_modify_address_book = self.modify_address_book(
                            groupname=addrgrp_groupname,
                            groupuuid=addrgrp_groupuuid,
                            description=addrgrp_description,
                            addresslist=data_addrgrp_addresslist
                        )
                        if res_modify_address_book['statusCode'] == 200:
                            msg = {
                                "addr": f"{addr}",
                                "groupname": f"{addrgrp_groupname}",
                                "groupuuid": f"{addrgrp_groupuuid}",
                                "description": f"{addrgrp_description}",
                                "grouplen": f"{data_len_addrgrp}",
                                "desc": "封禁成功"
                            }
                            logger.info(f'{msg}')
                            return msg
                        else:
                            msg = {
                                "addr": f"{addr}",
                                "groupname": f"{addrgrp_groupname}",
                                "groupuuid": f"{addrgrp_groupuuid}",
                                "description": f"{addrgrp_description}",
                                "grouplen": f"{data_len_addrgrp}",
                                "desc": "封禁失败"
                            }
                            logger.info(f'{msg}')
                            return msg
                    # 判断需要封禁的地址资源组内的地址资源是否超过最大上限，如超过限制，新建控制策略组，新建地址资源组，将需要封禁的地址资源更新至新建的地址资源组
                    else:
                        # 创建地址资源组，将需要封禁的地址资源更新至新至新建的地址资源组
                        res_add_address_book = self.add_address_book(
                            groupname=self.BLACKLIST_OUT_GROUP,
                            grouptype=describe_address_book_grouptype,
                            description=self.BLACKLIST_OUT_GROUP,
                            addresslist=addr_obj
                        )
                        res_add_address_book_groupname = res_add_address_book['groupname']
                        res_add_address_book_description = res_add_address_book['description']
                        res_add_address_book_groupuuid = res_add_address_book['groupuuid']
                        # 创建控制策略组，将需要封禁的地址资源组更新至新建的控制策略组
                        res_add_control_policy = self.add_control_policy(
                            aclaction=self.ACL_ACTION_DROP,
                            description=res_add_address_book_description,
                            destination=res_add_address_book_groupname,
                            destinationtype='group',
                            direction=direction,
                            proto='ANY',
                            source='0.0.0.0/0',
                            sourcetype='net',
                            neworder=2,
                            applicationname='ANY'
                        )
                        if res_add_address_book['desc'] == "创建成功" and res_add_control_policy['desc'] == "创建成功":
                            msg = {
                                "addr": f"{addr}",
                                "groupname": f"{res_add_address_book_groupname}",
                                "groupuuid": f"{res_add_address_book_groupuuid}",
                                "description": f"{res_add_address_book_description}",
                                "grouplen": 1,
                                "desc": "封禁成功"
                            }
                            logger.info(f'{msg}')
                            return msg
                        else:
                            msg = {
                                "addr": f"{addr}",
                                "groupname": f"{res_add_address_book_groupname}",
                                "groupuuid": f"{res_add_address_book_groupuuid}",
                                "description": f"{res_add_address_book_description}",
                                "grouplen": 1,
                                "desc": "封禁失败"
                            }
                            logger.info(f'{msg}')
                            return msg
                
                # 如果没有找到现有的出站黑名单地址组，创建第一个地址组和控制策略
                if not addrgrps:
                    # 创建地址资源组，将需要封禁的地址资源更新至新建的地址资源组
                    res_add_address_book = self.add_address_book(
                        groupname=self.BLACKLIST_OUT_GROUP,
                        grouptype=describe_address_book_grouptype,
                        description=self.BLACKLIST_OUT_GROUP,
                        addresslist=addr_obj
                    )
                    res_add_address_book_groupname = res_add_address_book['groupname']
                    res_add_address_book_description = res_add_address_book['description']
                    res_add_address_book_groupuuid = res_add_address_book['groupuuid']
                    # 创建控制策略组，将需要封禁的地址资源组更新至新建的控制策略组
                    res_add_control_policy = self.add_control_policy(
                        aclaction=self.ACL_ACTION_DROP,
                        description=res_add_address_book_description,
                        destination=res_add_address_book_groupname,
                        destinationtype='group',
                        direction=direction,
                        proto='ANY',
                        source='0.0.0.0/0',
                        sourcetype='net',
                        neworder=2,
                        applicationname='ANY'
                    )
                    if res_add_address_book['desc'] == "创建成功" and res_add_control_policy['desc'] == "创建成功":
                        msg = {
                            "addr": f"{addr}",
                            "groupname": f"{res_add_address_book_groupname}",
                            "groupuuid": f"{res_add_address_book_groupuuid}",
                            "description": f"{res_add_address_book_description}",
                            "grouplen": 1,
                            "desc": "封禁成功"
                        }
                        logger.info(f'{msg}')
                        return msg
                    else:
                        msg = {
                            "addr": f"{addr}",
                            "groupname": f"{res_add_address_book_groupname}",
                            "groupuuid": f"{res_add_address_book_groupuuid}",
                            "description": f"{res_add_address_book_description}",
                            "grouplen": 1,
                            "desc": "封禁失败"
                        }
                        logger.info(f'{msg}')
                        return msg

    def single_unblock_address(self, addr, direction=None):
        # 定义日志配置
        self.check_os_type()
        # 判断需要解封的地址资源属于ip类型或net类型或domain类型
        if self.check_address_type(addr) == "ipv4":
            addr_obj = f"{addr}/32"
            describe_address_book_grouptype = "ip"
        elif self.check_address_type(addr) == "network":
            addr_obj = f"{addr}"
            describe_address_book_grouptype = "ip"
        elif self.check_address_type(addr) == "domain":
            addr_obj = f"{addr}"
            describe_address_book_grouptype = "domain"
        elif self.check_address_type(addr) == "ipv6":
            msg = {
                "addr": f"{addr}",
                "desc": "无需解封"
            }
            logger.info(f'{msg}')
            return msg
        # 验证direction参数并查询相应的地址资源组
        if direction == 'in':
            query_prefix = self.BLACKLIST_IN_GROUP
        elif direction == 'out':
            query_prefix = self.BLACKLIST_OUT_GROUP
        else:
            # direction参数无效时返回错误信息
            msg = {
                "addr": f"{addr}",
                "desc": "direction参数必须为'in'或'out'"
            }
            logger.error(f'{msg}')
            return msg
            
        res_describe_address_book = self.describe_address_book(
            query=query_prefix,
            grouptype=describe_address_book_grouptype
        )
        # 判断需要解封的地址资源是否已存在于现有封禁策略中，如存在则found赋值为True，如不存在则found赋值为False
        found = False
        for list_res_describe_address_book in res_describe_address_book['body']['Acls']:
            # 需要检查组名，因为query可能是模糊搜索，返回的结果可能包含其他相关组
            if ((direction == 'in' and self.BLACKLIST_IN_GROUP in list_res_describe_address_book['GroupName']) or
                (direction == 'out' and self.BLACKLIST_OUT_GROUP in list_res_describe_address_book['GroupName'])):
                match_list = list_res_describe_address_book['AddressList']
                if addr_obj in match_list:
                    found = True
                    break
        # 判断需要解封的地址资源是否执行封禁任务，如found值为True，执行解封任务序列
        if found == True:
            if direction == "in":
                # 将包含入站黑名单的地址资源组汇总成addrgrps地址资源组列表
                addrgrps = [data_describe_address_book for data_describe_address_book in
                            res_describe_address_book['body']['Acls']
                            if self.BLACKLIST_IN_GROUP in data_describe_address_book['GroupName'] and addr_obj in
                            data_describe_address_book['AddressList']]
                # 构建解封return msg列表
                list_msg = []
                for addrgrp in addrgrps:
                    # 将汇总的addrgrps中的addrgrp内的AddressList从字符串转换成列表，并计算长度
                    len_addrgrp = len(addrgrp['AddressList'])
                    data_len_addrgrp = len_addrgrp - 1
                    # 判断需要解封的地址资源组内的地址资源是否少于1个最小下限，如解封前大于1个地址资源，将包含解封地址资源的资源地址组从封禁策略中去除，删除地址资源
                    if len_addrgrp > 1:
                    # if len_addrgrp < 1:
                        addrgrp_groupname = addrgrp['GroupName']
                        addrgrp_groupuuid = addrgrp['GroupUuid']
                        addrgrp_description = addrgrp['Description']
                        list_addrgrp_addresslist = addrgrp['AddressList']
                        list_addrgrp_addresslist.remove(addr_obj)
                        data_addrgrp_addresslist = ','.join(list_addrgrp_addresslist)
                        # 将需要封禁的地址资源更新至地址资源组
                        res_modify_address_book = self.modify_address_book(
                            groupname=addrgrp_groupname,
                            groupuuid=addrgrp_groupuuid,
                            description=addrgrp_description,
                            addresslist=data_addrgrp_addresslist
                        )
                        if res_modify_address_book['statusCode'] == 200:
                            msg = {
                                "addr": f"{addr}",
                                "groupname": f"{addrgrp_groupname}",
                                "groupuuid": f"{addrgrp_groupuuid}",
                                "description": f"{addrgrp_description}",
                                "grouplen": f"{data_len_addrgrp}",
                                "desc": "解封成功"
                            }
                            logger.info(f'{msg}')
                        else:
                            msg = {
                                "addr": f"{addr}",
                                "groupname": f"{addrgrp_groupname}",
                                "groupuuid": f"{addrgrp_groupuuid}",
                                "description": f"{addrgrp_description}",
                                "grouplen": f"{data_len_addrgrp}",
                                "desc": "解封失败"
                            }
                            logger.info(f'{msg}')
                        # 将需要解封的地址资源msg汇总至return msg列表
                        list_msg.append(msg)
                    # 判断需要解封的地址资源组内的地址资源是否少于1个最小下限，如解封前等于1个地址资源，将包含解封地址资源的控制策略组及资源地址组删除
                    else:
                        addrgrp_groupname = addrgrp['GroupName']
                        addrgrp_groupuuid = addrgrp['GroupUuid']
                        addrgrp_description = addrgrp['Description']
                        # 查询所有控制策略组
                        res_describe_control_policy = self.describe_control_policy(
                            direction=direction
                        )
                        # 将包含入站黑名单且包含需解封地址对象的策略控制组汇总成policygrp控制策略组列表，dict.values()为精确匹配
                        policygrps = [data_describe_control_policy for data_describe_control_policy in
                                      res_describe_control_policy['body']['Policys'] if
                                      addrgrp_groupname in data_describe_control_policy.values()]
                        # 遍历控制策略列表中的控制策略
                        for policygrp in policygrps:
                            policygrp_acluuid = policygrp['AclUuid']
                            # 删除包含需解封地址资源的策略控制组
                            res_delete_control_policy = self.delete_control_policy(
                                acluuid=policygrp_acluuid,
                                direction=direction
                            )
                            # 删除包含需解封地址资源的地址资源组
                            res_delete_address_book = self.delete_address_book(
                                groupuuid=addrgrp_groupuuid
                            )
                            if res_delete_control_policy['statusCode'] == 200 and res_delete_address_book[
                                'statusCode'] == 200:
                                msg = {
                                    "addr": f"{addr}",
                                    "groupname": f"{addrgrp_groupname}",
                                    "groupuuid": f"{addrgrp_groupuuid}",
                                    "description": f"{addrgrp_description}",
                                    "ruleid": f"{policygrp_acluuid}",
                                    "desc": "解封成功"
                                }
                                logger.info(f'{msg}')
                            else:
                                msg = {
                                    "addr": f"{addr}",
                                    "groupname": f"{addrgrp_groupname}",
                                    "groupuuid": f"{addrgrp_groupuuid}",
                                    "description": f"{addrgrp_description}",
                                    "ruleid": f"{policygrp_acluuid}",
                                    "desc": "解封失败"
                                }
                                logger.info(f'{msg}')
                            # return msg
                            # 将需要解封的地址资源msg汇总至return msg列表
                            list_msg.append(msg)
                logger.info(f'{list_msg}')
                return list_msg
            elif direction == "out":
                # 将包含出站黑名单的地址资源组汇总成addrgrps地址资源组列表
                addrgrps = [data_describe_address_book for data_describe_address_book in
                            res_describe_address_book['body']['Acls']
                            if self.BLACKLIST_OUT_GROUP in data_describe_address_book['GroupName'] and addr_obj in
                            data_describe_address_book['AddressList']]
                # 构建解封return msg列表
                list_msg = []
                for addrgrp in addrgrps:
                    # 将汇总的addrgrps中的addrgrp内的AddressList从字符串转换成列表，并计算长度
                    len_addrgrp = len(addrgrp['AddressList'])
                    data_len_addrgrp = len_addrgrp - 1
                    # 判断需要解封的地址资源组内的地址资源是否少于1个最小下限，如解封前大于1个地址资源，将包含解封地址资源的资源地址组从封禁策略中去除，删除地址资源
                    if len_addrgrp > 1:
                    # if len_addrgrp < 1:
                        addrgrp_groupname = addrgrp['GroupName']
                        addrgrp_groupuuid = addrgrp['GroupUuid']
                        addrgrp_description = addrgrp['Description']
                        list_addrgrp_addresslist = addrgrp['AddressList']
                        list_addrgrp_addresslist.remove(addr_obj)
                        data_addrgrp_addresslist = ','.join(list_addrgrp_addresslist)
                        # 将需要封禁的地址资源更新至地址资源组
                        res_modify_address_book = self.modify_address_book(
                            groupname=addrgrp_groupname,
                            groupuuid=addrgrp_groupuuid,
                            description=addrgrp_description,
                            addresslist=data_addrgrp_addresslist
                        )
                        if res_modify_address_book['statusCode'] == 200:
                            msg = {
                                "addr": f"{addr}",
                                "groupname": f"{addrgrp_groupname}",
                                "groupuuid": f"{addrgrp_groupuuid}",
                                "description": f"{addrgrp_description}",
                                "grouplen": f"{data_len_addrgrp}",
                                "desc": "解封成功"
                            }
                            logger.info(f'{msg}')
                        else:
                            msg = {
                                "addr": f"{addr}",
                                "groupname": f"{addrgrp_groupname}",
                                "groupuuid": f"{addrgrp_groupuuid}",
                                "description": f"{addrgrp_description}",
                                "grouplen": f"{data_len_addrgrp}",
                                "desc": "解封失败"
                            }
                            logger.info(f'{msg}')
                        # 将需要解封的地址资源msg汇总至return msg列表
                        list_msg.append(msg)
                    # 判断需要解封的地址资源组内的地址资源是否少于1个最小下限，如解封前等于1个地址资源，将包含解封地址资源的控制策略组及资源地址组删除
                    else:
                        addrgrp_groupname = addrgrp['GroupName']
                        addrgrp_groupuuid = addrgrp['GroupUuid']
                        addrgrp_description = addrgrp['Description']
                        # 查询所有控制策略组
                        res_describe_control_policy = self.describe_control_policy(
                            direction=direction
                        )
                        # 将包含出站黑名单且包含需解封地址对象的策略控制组汇总成policygrp控制策略组列表，dict.values()为精确匹配
                        policygrps = [data_describe_control_policy for data_describe_control_policy in
                                      res_describe_control_policy['body']['Policys'] if
                                      addrgrp_groupname in data_describe_control_policy.values()]
                        # 遍历控制策略列表中的控制策略
                        for policygrp in policygrps:
                            policygrp_acluuid = policygrp['AclUuid']
                            # 删除包含需解封地址资源的策略控制组
                            res_delete_control_policy = self.delete_control_policy(
                                acluuid=policygrp_acluuid,
                                direction=direction
                            )
                            # 删除包含需解封地址资源的地址资源组
                            res_delete_address_book = self.delete_address_book(
                                groupuuid=addrgrp_groupuuid
                            )
                            if res_delete_control_policy['statusCode'] == 200 and res_delete_address_book[
                                'statusCode'] == 200:
                                msg = {
                                    "addr": f"{addr}",
                                    "groupname": f"{addrgrp_groupname}",
                                    "groupuuid": f"{addrgrp_groupuuid}",
                                    "description": f"{addrgrp_description}",
                                    "ruleid": f"{policygrp_acluuid}",
                                    "desc": "解封成功"
                                }
                                logger.info(f'{msg}')
                            else:
                                msg = {
                                    "addr": f"{addr}",
                                    "groupname": f"{addrgrp_groupname}",
                                    "groupuuid": f"{addrgrp_groupuuid}",
                                    "description": f"{addrgrp_description}",
                                    "ruleid": f"{policygrp_acluuid}",
                                    "desc": "解封失败"
                                }
                                logger.info(f'{msg}')
                            # 将需要解封的地址资源msg汇总至return msg列表
                            list_msg.append(msg)
                logger.info(f'{list_msg}')
                return list_msg
        # 判断需要封禁的地址资源是否执行封禁任务，如found值为False，返回msg无需解封
        elif found == False:
            msg = {
                "addr": f"{addr}",
                "desc": "无需解封"
            }
            return msg

    def hw_block_address(self, direction):
        with open(f'{os.path.dirname(__file__)}/block.txt', 'r') as block, open(f'{os.path.dirname(__file__)}/white.txt', 'r') as white:
            block_ips = block.read().splitlines()
            white_ips = white.read().splitlines()
            filter_ips = []
            for addr in block_ips:
                if any(self.filter_check(addr, network) for network in white_ips):
                    logger.remove()
                    logger.add(f'{os.path.dirname(__file__)}/filter_ips.log', rotation='500MB')
                    logger.info(f"白名单地址，无需封禁：{addr}")
                else:
                    filter_ips.append(addr)
            with open(f'{os.path.dirname(__file__)}/block.txt', 'w') as block:
                block.write('\n'.join(filter_ips))
        with open(f'{os.path.dirname(__file__)}/block.txt', 'r') as block:
            block_ips = block.read().splitlines()
            for addr in block_ips:
                res = self.single_block_address(addr, direction=direction)
                if res['desc'] == "无需封禁":
                    logger.remove()
                    logger.add(f'{os.path.dirname(__file__)}/hw.log', rotation='500MB')
                    logger.info(f"无需封禁：{addr}")
                elif res['desc'] == "封禁成功":
                    with open(f'{os.path.dirname(__file__)}/bak.log', 'a') as bak:
                        bak_content = res['addr'].split('/')[0]
                        bak.write('\n' + bak_content)
                    logger.remove()
                    logger.add(f'{os.path.dirname(__file__)}/hw.log', rotation='500MB')
                    logger.info(f"封禁成功：{addr}")
                elif res['desc'] == "封禁失败":
                    logger.remove()
                    logger.add(f'{os.path.dirname(__file__)}/hw.log', rotation='500MB')
                    logger.info(f"封禁失败：{addr}")
            msg = {
                "desc": "护网封禁任务执行完毕"
            }
            return msg

    def hw_block_check(self, query, grouptype):
        res_describe_address_book = self.describe_address_book(query, grouptype)
        acls = res_describe_address_book['body']['Acls']
        list_describe_address_book_addresslist = [ip for acl in acls for ip in acl['AddressList']]
        with open(f'{os.path.dirname(__file__)}/check_ips.log', 'w') as check_ips:
            for ips in list_describe_address_book_addresslist:
                check_ips.write(ips + '\n')
        with open(f'{os.path.dirname(__file__)}/check_ips.log', 'r') as check_ips:
            check_ips = check_ips.readlines()
        with open(f'{os.path.dirname(__file__)}/check_ips_output.log', 'w') as check_ips_output:
            for ips in check_ips:
                ips = ips.replace('"', '').replace('/32', '').replace(' ', '').replace(',', '').replace('\n', '')
                check_ips_output.write(ips + '\n')
        with open(f'{os.path.dirname(__file__)}/check_ips_output.log', 'r') as check_ips_output, open(
                f'{os.path.dirname(__file__)}/bak.log', 'r') as bak:
            check_ips = set(ip.replace('"', '').replace('/32', '').replace(' ', '').replace(',', '').replace('\n', '') for ip in check_ips_output)
            bak_ips = set(ip.replace('"', '').replace('/32', '').replace(' ', '').replace(',', '').replace('\n', '') for ip in bak)
        new_ips = check_ips - bak_ips
        with open(f'{os.path.dirname(__file__)}/check_ips_output.log', 'w') as check_ips_output:
            for ips in new_ips:
                check_ips_output.write(ips + '\n')
        msg = {
            "desc": "护网封禁任务校验完毕"
        }
        return msg