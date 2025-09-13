# -*- coding: utf-8 -*-
from alibabacloud_cloudfw20171207.client import Client as Cloudfw20171207Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_cloudfw20171207 import models as cloudfw_20171207_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as UtilClient
from loguru import logger
from apps.fw_aliyun import utils
import ipaddress
import random
import string

class FwAliyunApp:
    def __init__(self, ak, sk, endpoint, proxies=None):
        self.ak = ak
        self.sk = sk
        self.endpoint = endpoint
        self.proxies = proxies

    def create_client(self) -> Cloudfw20171207Client:
        config = open_api_models.Config(
            access_key_id=self.ak,
            access_key_secret=self.sk
        )
        config.endpoint = self.endpoint
        return Cloudfw20171207Client(config)

    # 阿里云云防火墙原子方法

    def add_address_book(self, groupname, grouptype, description, addresslist):
        client = self.create_client()
        add_address_book_request = cloudfw_20171207_models.AddAddressBookRequest(
            group_name=groupname,
            group_type=grouptype,
            description=description,
            address_list=addresslist
        )
        runtime = util_models.RuntimeOptions(https_proxy=self.proxies, http_proxy=self.proxies)
        utils.check_os_type()
        try:
            res = client.add_address_book_with_options(add_address_book_request, runtime).to_map()
            logger.info(f'{res}')
            if res['statusCode'] == 200:
                msg = {
                    "desc": "创建成功",
                    "groupname": groupname,
                    "groupuuid": res['body']['GroupUuid'],
                    "description": description
                }
                return msg
            else:
                msg = {
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
        runtime = util_models.RuntimeOptions(https_proxy=self.proxies, http_proxy=self.proxies)
        utils.check_os_type()
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
            group_type=grouptype,
            page_size=utils.get_config('describe_address_book.page_size')
        )
        runtime = util_models.RuntimeOptions(https_proxy=self.proxies, http_proxy=self.proxies)
        utils.check_os_type()
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
            group_name=groupname,
            group_uuid=groupuuid,
            description=description,
            address_list=addresslist
        )
        runtime = util_models.RuntimeOptions(https_proxy=self.proxies, http_proxy=self.proxies)
        utils.check_os_type()
        try:
            res = client.modify_address_book_with_options(modify_address_book_request, runtime).to_map()
            logger.info(f'{res}')
            return res
        except Exception as e:
            res = UtilClient.assert_as_string(e.message)
            logger.error(f'{e}')
            return res

    def describe_control_policy(self, direction, description=None):
        client = self.create_client()
        describe_control_policy_request = cloudfw_20171207_models.DescribeControlPolicyRequest(
            direction=direction,
            description=description,
            current_page=utils.get_config('describe_control_policy.current_page'),
            page_size=utils.get_config('describe_control_policy.page_size')
        )
        runtime = util_models.RuntimeOptions(https_proxy=self.proxies, http_proxy=self.proxies)
        utils.check_os_type()
        try:
            res = client.describe_control_policy_with_options(describe_control_policy_request, runtime).to_map()
            logger.info(f'{res}')
            return res
        except Exception as e:
            res = UtilClient.assert_as_string(e.message)
            logger.error(f'{e}')
            return res

    def add_control_policy(self, aclaction, description, destination, destinationtype, direction, proto, source,
                          sourcetype, neworder, applicationname=None, applicationnamelist=None, domainresolvetype=None):
        client = self.create_client()
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
                application_name=applicationname,
                application_name_list=applicationnamelist,
                domain_resolve_type=domainresolvetype
            )
        runtime = util_models.RuntimeOptions(https_proxy=self.proxies, http_proxy=self.proxies)
        utils.check_os_type()
        try:
            res = client.add_control_policy_with_options(add_control_policy_request, runtime).to_map()
            logger.info(f"{res}")
            if res['statusCode'] == 200:
                msg = {
                    "desc": "创建成功",
                    "acluuid": res['body']['AclUuid']
                }
                return msg
            else:
                msg = {
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
        runtime = util_models.RuntimeOptions(https_proxy=self.proxies, http_proxy=self.proxies)
        utils.check_os_type()
        try:
            res = client.delete_control_policy_with_options(delete_control_policy_request, runtime).to_map()
            logger.info(f'{res}')
            return res
        except Exception as e:
            res = UtilClient.assert_as_string(e.message)
            logger.error(f'{e}')
            return res

    def auto_block_task(self, addr, direction=None):
        # 加载日志配置
        utils.check_os_type()    
        
        # 验证SOAR入参IP or 手动入参IPS
        addrs = utils.parse_ip_list(addr)
        if not addrs:
            msg = {
                "addr": f"{addrs}",
                "desc": "无需封禁"
            }
            logger.info(f'{msg}')
            return msg
        
        # 初始化处理状态变量
        list_success_addrs = []
        list_failed_addrs = []
        list_existed_addrs = []
        list_remain_addrs = list(addrs)
        consecutive_failures = 0
        # 设置查询前缀和配置
        query_prefix = f"{utils.get_config('add_address_book.group_name_prefix', '')}-{direction.title()}"
        max_addresses_per_group = utils.get_config('modify_address_book.max_addresses_per_group')
        
        # 主处理循环
        while list_remain_addrs:
            len_list_remain_addrs = len(list_remain_addrs)
            msg = {
                "addr": f"{list_remain_addrs}",
                "desc": f"len({list_remain_addrs})"
            }
            logger.info(f'{msg}')
            
            # 按地址类型分组处理
            addrs_groups = {
                "ip" : [],
                "domain": []
            }
            for remain_addr in list_remain_addrs[:]:
                try:
                    ipaddress.IPv4Address(remain_addr.split('/')[0])
                    describe_address_book_grouptype = "ip"
                except ipaddress.AddressValueError:
                    try:
                        ipaddress.IPv6Address(remain_addr.split('/')[0])
                        # IPV6 无需封禁
                        list_existed_addrs.append({
                            "addr": f"{remain_addr}",
                            "desc": "无需封禁"
                        })
                        if remain_addr in list_remain_addrs:
                            list_remain_addrs.remove(remain_addr)
                        continue
                    except ipaddress.AddressValueError:
                        describe_address_book_grouptype = "domain"
                addrs_groups[describe_address_book_grouptype].append(remain_addr)
            
            # 处理每种地址类型
            for describe_address_book_grouptype, list_addrs_groups in addrs_groups.items():
                if not list_addrs_groups:
                    continue
                # 获取该类型的现有地址组
                res_describe_address_book = self.describe_address_book(
                    query=query_prefix,
                    grouptype=describe_address_book_grouptype
                )
                # 检查已存在的IP
                for addr in list_addrs_groups[:]:
                    found = False
                    for list_res_describe_address_book in res_describe_address_book['body']['Acls']:
                        if query_prefix in list_res_describe_address_book['GroupName']:
                            if addr in list_res_describe_address_book['AddressList']:
                                found = True
                                msg = list_existed_addrs.append({
                                    "addr": f"{addr}",
                                    "groupname": list_res_describe_address_book['GroupName'],
                                    "desc": "无需封禁"
                                })
                                logger.info(f'{msg}')
                                break
                    if found == True:
                        if addr in list_addrs_groups:
                            list_addrs_groups.remove(addr)
                        if addr in list_remain_addrs:
                            list_remain_addrs.remove(addr)
                
                # 将IP添加到现有组或创建新组
                addrgrps = [data_describe_address_book for data_describe_address_book in
                            res_describe_address_book['body']['Acls']
                            if query_prefix in data_describe_address_book['GroupName']]
                for addrgrp in addrgrps:
                    if not list_addrs_groups:
                        break
                    addrgrp_groupname = addrgrp['GroupName']
                    addrgrp_groupuuid = addrgrp['GroupUuid']
                    addrgrp_description = addrgrp['Description']
                    len_addrgrp = len(addrgrp['AddressList'])
                    if len_addrgrp < max_addresses_per_group:
                        res_describe_control_policy = self.describe_control_policy(
                            direction=direction,
                            description=addrgrp_groupname
                        )
                        if res_describe_control_policy['body']['TotalCount'] == 0:
                            continue
                        if len(list_addrs_groups[:]) > max_addresses_per_group - len_addrgrp:
                            list_addrgrp_addresslist = list_addrs_groups[:max_addresses_per_group - len_addrgrp]
                            data_addrgrp_addresslist = ','.join(addrgrp['AddressList'] + list_addrs_groups[:max_addresses_per_group - len_addrgrp])
                        else:
                            list_addrgrp_addresslist = list_addrs_groups[:]
                            data_addrgrp_addresslist = ','.join(addrgrp['AddressList'] + list_addrs_groups[:])
                        res_modify_address_book = self.modify_address_book(
                            groupname=addrgrp['GroupName'],
                            groupuuid=addrgrp['GroupUuid'],
                            description=addrgrp['Description'],
                            addresslist=data_addrgrp_addresslist
                        )
                        if res_modify_address_book['statusCode'] == 200:
                            msg = {
                                "addr": f"{data_addrgrp_addresslist}",
                                "groupname": f"{addrgrp_groupname}",
                                "groupuuid": f"{addrgrp_groupuuid}",
                                "description": f"{addrgrp_description}",
                                "desc": "封禁成功"
                            }
                            logger.info(f'{msg}')
                            list_success_addrs.append(msg)
                        else:
                            msg = {
                                "addr": f"{data_addrgrp_addresslist}",
                                "groupname": f"{addrgrp_groupname}",
                                "groupuuid": f"{addrgrp_groupuuid}",
                                "description": f"{addrgrp_description}",
                                "desc": "封禁失败"
                            }
                            logger.info(f'{msg}')
                            list_failed_addrs.append(msg)
                        list_addrs_groups = [x for x in list_addrs_groups if x not in list_addrgrp_addresslist]
                        list_remain_addrs = [x for x in list_remain_addrs if x not in list_addrgrp_addresslist]
                if list_remain_addrs:
                    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
                    res_add_address_book = self.add_address_book(
                        groupname=f"{query_prefix}-{random_string}",
                        grouptype=describe_address_book_grouptype,
                        description=f"{query_prefix}-{random_string}",
                        addresslist=utils.get_config('add_address_book.addresslist')
                    )
                    if res_add_address_book['desc'] == "创建成功":
                        if direction == 'in':
                            res_add_control_policy = self.add_control_policy(
                                aclaction=utils.get_config('add_control_policy.acl_action'),
                                description=res_add_address_book['description'],
                                destination=utils.get_config('add_control_policy.destination'),
                                destinationtype='net',
                                direction=direction,
                                proto=utils.get_config('add_control_policy.ip.proto'),
                                source=res_add_address_book['groupname'],
                                sourcetype='group',
                                neworder=utils.get_config('add_control_policy.new_order'),
                                applicationnamelist=utils.get_config('add_control_policy.ip.application_name_list')
                            )
                        elif direction == 'out':
                            if describe_address_book_grouptype == 'ip':
                                res_add_control_policy = self.add_control_policy(
                                    aclaction=utils.get_config('add_control_policy.acl_action'),
                                    description=res_add_address_book['description'],
                                    destination=res_add_address_book['groupname'],
                                    destinationtype='group',
                                    direction=direction,
                                    proto=utils.get_config('add_control_policy.ip.proto'),
                                    source=utils.get_config('add_control_policy.source'),
                                    sourcetype='net',
                                    neworder=utils.get_config('add_control_policy.new_order'),
                                    applicationnamelist=utils.get_config('add_control_policy.ip.application_name_list')    
                                )
                            elif describe_address_book_grouptype == 'domain':
                                res_add_control_policy = self.add_control_policy(
                                    aclaction=utils.get_config('add_control_policy.acl_action'),
                                    description=res_add_address_book['description'],
                                    destination=res_add_address_book['groupname'],
                                    destinationtype='group',
                                    direction=direction,
                                    proto=utils.get_config('add_control_policy.domain.proto'),
                                    source=utils.get_config('add_control_policy.source'),
                                    sourcetype='net',
                                    neworder=utils.get_config('add_control_policy.new_order'),
                                    applicationname=utils.get_config('add_control_policy.domain.application_name_list'),
                                    domainresolvetype=utils.get_config('add_control_policy.domain.domain_resolve_type')
                                )
                                if res_add_control_policy['desc'] == "创建成功":
                                    msg = {
                                        "groupname": res_add_address_book['groupname'],
                                        "groupuuid": res_add_address_book['groupuuid'],
                                        "description": res_add_address_book['description'],
                                        "acluuid": res_add_control_policy['AclUuid'],
                                        "desc": "创建成功"
                                    }
                                    logger.info(f'{msg}')
                                else:
                                    self.delete_address_book(
                                        groupuuid=res_add_address_book['groupuuid']
                                    )
                                    msg = {
                                        "groupname": res_add_address_book['groupname'],
                                        "groupuuid": res_add_address_book['groupuuid'],
                                        "description": res_add_address_book['description'],
                                        "acluuid": res_add_control_policy['AclUuid'],
                                        "desc": "创建失败"
                                    }
                                    logger.info(f'{msg}')
            # while主循环保护机制
            if len(list_remain_addrs) == len_list_remain_addrs:
                consecutive_failures += 1
                if consecutive_failures >= 2:
                    msg = {
                        "addr": f"{list_remain_addrs}",
                        "desc": "封禁失败"
                    }
                    logger.info(f"{msg}")
                    list_failed_addrs.append(msg)
                    break
            else:
                consecutive_failures = 0
        msg = list_success_addrs + list_failed_addrs + list_existed_addrs
        logger.info(f"{msg}")
        return msg     

    def auto_unblock_task(self, addr, direction=None):
        """批量解封IP地址"""
        try:
            utils.check_os_type()
            
            # 验证direction参数
            if direction not in ['in', 'out']:
                return {
                    "statusCode": 400,
                    "error": "direction参数必须为'in'或'out'",
                    "body": {}
                }
            
            # 解析和验证IP地址列表
            ips = utils.parse_ip_list(addr)
            if not ips:
                return {
                    "statusCode": 400,
                    "error": "没有有效的IP地址",
                    "body": {}
                }
            
            logger.info(f"开始批量解封 {len(ips)} 个地址，方向: {direction}")
            
            # 初始化处理状态变量
            success_ips = []
            failed_ips = []
            
            # 设置查询前缀
            group_name_prefix = utils.get_config('add_address_book.group_name_prefix', 'DEV-P-Deny-Secops-Blacklist')
            query_prefix = f"{group_name_prefix}-{direction.title()}"
            
            # 按地址类型分组处理
            for ip in ips:
                try:
                    ipaddress.IPv4Address(ip.split('/')[0])
                    addr_type = "ipv4" if '/' not in ip else "network"
                    grouptype = "ip"
                except ipaddress.AddressValueError:
                    try:
                        ipaddress.IPv6Address(ip.split('/')[0])
                        # IPv6直接跳过
                        continue
                    except ipaddress.AddressValueError:
                        addr_type = "domain"
                        grouptype = "domain"
                
                # 获取该类型的现有地址组
                res_describe_address_book = self.describe_address_book(
                    query=query_prefix,
                    grouptype=grouptype
                )
                
                if isinstance(res_describe_address_book, str) or res_describe_address_book.get('statusCode') != 200:
                    logger.error(f"查询地址组失败: {res_describe_address_book}")
                    failed_ips.append({
                        "addr": ip,
                        "desc": "查询地址组失败"
                    })
                    continue
                
                existing_groups = res_describe_address_book['body']['Acls']
                addr_obj = f"{ip}/32" if addr_type == "ipv4" and '/' not in ip else ip
                found_and_removed = False
                
                # 在所有相关组中查找并移除IP
                for group in existing_groups:
                    if query_prefix in group['GroupName'] and addr_obj in group['AddressList']:
                        # 从地址列表中移除该IP
                        new_address_list = [addr for addr in group['AddressList'] if not utils.ip_matches(addr, addr_obj)]
                        
                        if len(new_address_list) == 0:
                            # 删除空组和相关策略
                            # 先查找相关的控制策略
                            res_describe_control_policy = self.describe_control_policy(direction)
                            if not isinstance(res_describe_control_policy, str) and res_describe_control_policy.get('statusCode') == 200:
                                policies = res_describe_control_policy['body']['Policys']
                                for policy in policies:
                                    if ((direction == 'in' and policy.get('Source') == group['GroupName']) or
                                        (direction == 'out' and policy.get('Destination') == group['GroupName'])):
                                        policy_uuid = policy.get('AclUuid')
                                        if policy_uuid:
                                            res_delete_policy = self.delete_control_policy(policy_uuid, direction)
                                            if not isinstance(res_delete_policy, str) and res_delete_policy.get('statusCode') == 200:
                                                logger.info(f"成功删除控制策略: {policy_uuid}")
                                        else:
                                            logger.error(f"删除控制策略失败: {policy_uuid}")
                            
                            # 删除地址组
                            res_delete_group = self.delete_address_book(group['GroupUuid'])
                            if not isinstance(res_delete_group, str) and res_delete_group.get('statusCode') == 200:
                                # 原子操作：确保状态一致性
                                try:
                                    success_ips.append({
                                        "addr": ip,
                                        "groupname": group['GroupName'],
                                        "groupuuid": group['GroupUuid'],
                                        "desc": "解封成功（删除组）"
                                    })
                                    found_and_removed = True
                                except Exception as update_error:
                                    logger.error(f"更新删除组成功状态时发生异常: {update_error}")
                                    failed_ips.append({
                                        "addr": ip,
                                        "desc": "状态更新失败"
                                    })
                            else:
                                # 原子操作：确保状态一致性
                                try:
                                    logger.error(f"删除地址组失败: {group['GroupName']}")
                                    failed_ips.append({
                                        "addr": ip,
                                        "desc": "删除地址组失败"
                                    })
                                except Exception as update_error:
                                    logger.error(f"更新删除组失败状态时发生异常: {update_error}")
                        else:
                            # 更新组
                            new_address_str = ','.join(new_address_list)
                            res_modify = self.modify_address_book(
                                groupname=group['GroupName'],
                                groupuuid=group['GroupUuid'],
                                description=group['Description'],
                                addresslist=new_address_str
                            )
                            
                            if not isinstance(res_modify, str) and res_modify.get('statusCode') == 200:
                                # 原子操作：确保状态一致性
                                try:
                                    success_ips.append({
                                        "addr": ip,
                                        "groupname": group['GroupName'],
                                        "groupuuid": group['GroupUuid'],
                                        "grouplen": len(new_address_list),
                                        "desc": "解封成功"
                                    })
                                    found_and_removed = True
                                except Exception as update_error:
                                    logger.error(f"更新解封成功状态时发生异常: {update_error}")
                                    failed_ips.append({
                                        "addr": ip,
                                        "desc": "状态更新失败"
                                    })
                            else:
                                # 原子操作：确保状态一致性
                                try:
                                    logger.error(f"更新组失败: {group['GroupName']}")
                                    failed_ips.append({
                                        "addr": ip,
                                        "desc": "更新地址组失败"
                                    })
                                except Exception as update_error:
                                    logger.error(f"更新解封失败状态时发生异常: {update_error}")
                        break
                
                if not found_and_removed:
                    # 原子操作：确保状态一致性
                    try:
                        failed_ips.append({
                            "addr": ip,
                            "desc": "未找到该IP或移除失败"
                        })
                    except Exception as update_error:
                        logger.error(f"更新未找到IP状态时发生异常: {update_error}")
            
            # 生成处理结果
            result = {
                "statusCode": 200,
                "body": {
                    "success_ips": success_ips,
                    "failed_ips": failed_ips,
                    "summary": {
                        "total_ips": len(ips),
                        "success_count": len(success_ips),
                        "failed_count": len(failed_ips)
                    }
                }
            }
            
            logger.info(f"批量解封完成 - 总数:{len(ips)}, 成功:{len(success_ips)}, 失败:{len(failed_ips)}")
            return result
            
        except Exception as e:
            logger.error(f"批量解封异常: {str(e)}")
            return {
                "statusCode": 500,
                "error": f"批量解封异常: {str(e)}",
                "body": {}
            }