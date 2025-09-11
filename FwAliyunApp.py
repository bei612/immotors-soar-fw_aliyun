# -*- coding: utf-8 -*-
from alibabacloud_cloudfw20171207.client import Client as Cloudfw20171207Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_cloudfw20171207 import models as cloudfw_20171207_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as UtilClient
from loguru import logger
try:
    from apps.fw_aliyun import utils
except ImportError:
    import utils
import os
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
            page_size=utils.get_config('describe_address_book.page_size', 100)
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

    def describe_control_policy(self, direction):
        client = self.create_client()
        describe_control_policy_request = cloudfw_20171207_models.DescribeControlPolicyRequest(
            direction=direction,
            page_size=utils.get_config('describe_control_policy.page_size', 100)
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
                          sourcetype, neworder, applicationname, applicationnamelist=None):
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
                application_name_list=applicationnamelist
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
        """批量封禁IP地址"""
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
            
            logger.info(f"开始批量封禁 {len(ips)} 个地址，方向: {direction}")
            
            # 初始化处理状态变量
            success_ips = []
            failed_ips = []
            skipped_ips = []
            remaining_ips = list(ips)
            consecutive_failures = 0
            
            # 设置查询前缀和配置
            group_name_prefix = utils.get_config('add_address_book.group_name_prefix', 'DEV-P-Deny-Secops-Blacklist')
            query_prefix = f"{group_name_prefix}-{direction.title()}"
            max_addresses_per_group = utils.get_config('modify_address_book.max_addresses_per_group', 2000)
            
            # 主处理循环
            while remaining_ips:
                initial_count = len(remaining_ips)
                logger.info(f"剩余待处理IP数量: {len(remaining_ips)}")
                logger.debug(f"当前remaining_ips: {remaining_ips}")
                
                # 按地址类型分组处理
                ip_groups = {"ipv4": [], "network": [], "domain": []}
                for ip in remaining_ips[:]:
                    try:
                        ipaddress.IPv4Address(ip.split('/')[0])
                        addr_type = "ipv4" if '/' not in ip else "network"
                    except ipaddress.AddressValueError:
                        try:
                            ipaddress.IPv6Address(ip.split('/')[0])
                            # IPv6直接跳过
                            skipped_ips.append({
                                "addr": ip,
                                "desc": "无需封禁（IPv6）"
                            })
                            if ip in remaining_ips:
                                remaining_ips.remove(ip)
                            continue
                        except ipaddress.AddressValueError:
                            addr_type = "domain"
                    
                    ip_groups[addr_type].append(ip)
                
                # 处理每种地址类型
                for addr_type, type_ips in ip_groups.items():
                    if not type_ips:
                        continue
                        
                    # 获取该类型的现有地址组
                    grouptype = "ip" if addr_type in ["ipv4", "network"] else "domain"
                    res_describe_address_book = self.describe_address_book(
                        query=query_prefix,
                        grouptype=grouptype
                    )
                    
                    if res_describe_address_book.get('statusCode') != 200:
                        logger.error(f"查询地址组失败: {res_describe_address_book}")
                        consecutive_failures += 1
                        if consecutive_failures >= 3:
                            break
                        continue
                    
                    existing_groups = res_describe_address_book['body']['Acls']
                    
                    # 检查已存在的IP
                    for ip in type_ips[:]:
                        addr_obj = f"{ip}/32" if addr_type == "ipv4" and '/' not in ip else ip
                        found = False
                        
                        for group in existing_groups:
                            if query_prefix in group['GroupName']:
                                if addr_obj in group['AddressList']:
                                    found = True
                                    skipped_ips.append({
                                        "addr": ip,
                                        "groupname": group['GroupName'],
                                        "desc": "无需封禁（已存在）"
                                    })
                                    break
                        
                        if found:
                            if ip in type_ips:
                                type_ips.remove(ip)
                            if ip in remaining_ips:
                                remaining_ips.remove(ip)
                    
                    # 将IP添加到现有组或创建新组
                    for ip in type_ips[:]:
                        addr_obj = f"{ip}/32" if addr_type == "ipv4" and '/' not in ip else ip
                        processed = False
                        
                        # 添加到现有组
                        for group in existing_groups:
                            if query_prefix in group['GroupName']:
                                current_size = len(group['AddressList'])
                                if current_size < max_addresses_per_group:
                                    # 修改地址组
                                    new_address_list = group['AddressList'] + [addr_obj]
                                    new_address_str = ','.join(new_address_list)
                                    
                                    res_modify = self.modify_address_book(
                                        groupname=group['GroupName'],
                                        groupuuid=group['GroupUuid'],
                                        description=group['Description'],
                                        addresslist=new_address_str
                                    )
                                    
                                    if not isinstance(res_modify, str) and res_modify.get('statusCode') == 200:
                                        # 原子操作：先标记为已处理，再执行状态更新
                                        processed = True  # 先标记为已处理，防止重复处理
                                        try:
                                            # 更新组信息
                                            group['AddressList'] = new_address_list
                                            
                                            # 从处理列表中移除
                                            if ip in type_ips:
                                                type_ips.remove(ip)
                                            if ip in remaining_ips:
                                                remaining_ips.remove(ip)
                                            
                                            # 添加到成功列表
                                            success_ips.append({
                                                "addr": ip,
                                                "groupname": group['GroupName'],
                                                "groupuuid": group['GroupUuid'],
                                                "grouplen": len(new_address_list),
                                                "desc": "封禁成功"
                                            })
                                            
                                            logger.debug(f"IP {ip} 成功添加到现有组，已从remaining_ips移除")
                                            break  # 跳出 for group 循环
                                        except Exception as cleanup_error:
                                            logger.error(f"清理IP状态时发生异常: {cleanup_error}")
                                            # 即使清理失败，也不要重复处理，直接添加到失败列表
                                            failed_ips.append({
                                                "addr": ip,
                                                "desc": "状态清理失败"
                                            })
                                            break
                                    else:
                                        logger.error(f"修改地址组失败: {res_modify}")
                        
                        # 创建新组
                        logger.debug(f"IP {ip} processed标志: {processed}")
                        if not processed:
                            # 生成随机后缀
                            random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
                            new_group_name = f"{query_prefix}-{random_suffix}"
                            
                            res_add_address_book = self.add_address_book(
                                groupname=new_group_name,
                                grouptype=grouptype,
                                description=utils.get_config('add_address_book.description', '自动创建的安全封禁地址组'),
                                addresslist=addr_obj
                            )
                            
                            if res_add_address_book.get('desc') == "创建成功":
                                # 创建控制策略
                                acl_action = utils.get_config('add_control_policy.acl_action', 'log')
                                proto = utils.get_config('add_control_policy.proto', 'ANY')
                                application_name = utils.get_config('add_control_policy.application_name', 'ANY')
                                new_order = utils.get_config('add_control_policy.new_order', 2)
                                destination_any = utils.get_config('add_control_policy.destination_any', '0.0.0.0/0')
                                source_any = utils.get_config('add_control_policy.source_any', '0.0.0.0/0')
                                
                                if direction == 'in':
                                    res_add_control_policy = self.add_control_policy(
                                        aclaction=acl_action,
                                        description=res_add_address_book['description'],
                                        destination=destination_any,
                                        destinationtype='net',
                                        direction=direction,
                                        proto=proto,
                                        source=res_add_address_book['groupname'],
                                        sourcetype='group',
                                        neworder=new_order,
                                        applicationname=application_name
                                    )
                                else:  # direction == 'out'
                                    res_add_control_policy = self.add_control_policy(
                                        aclaction=acl_action,
                                        description=res_add_address_book['description'],
                                        destination=res_add_address_book['groupname'],
                                        destinationtype='group',
                                        direction=direction,
                                        proto=proto,
                                        source=source_any,
                                        sourcetype='net',
                                        neworder=new_order,
                                        applicationname=application_name
                                    )
                                
                                if res_add_control_policy.get('desc') == "创建成功":
                                    # 原子操作：先更新所有状态，再添加到结果列表
                                    try:
                                        # 添加到现有组列表以供后续使用
                                        new_group = {
                                            'GroupName': res_add_address_book['groupname'],
                                            'GroupUuid': res_add_address_book['groupuuid'],
                                            'Description': res_add_address_book['description'],
                                            'AddressList': [addr_obj]
                                        }
                                        existing_groups.append(new_group)
                                        
                                        # 从处理列表中移除
                                        if ip in type_ips:
                                            type_ips.remove(ip)
                                        if ip in remaining_ips:
                                            remaining_ips.remove(ip)
                                        
                                        # 只有在所有操作成功后才添加到成功列表
                                        success_ips.append({
                                            "addr": ip,
                                            "groupname": res_add_address_book['groupname'],
                                            "groupuuid": res_add_address_book['groupuuid'],
                                            "policyuuid": res_add_control_policy['acluuid'],
                                            "grouplen": 1,
                                            "desc": "封禁成功"
                                        })
                                    except Exception as cleanup_error:
                                        logger.error(f"创建新组后清理IP状态时发生异常: {cleanup_error}")
                                        # 如果清理失败，将IP添加到失败列表
                                        failed_ips.append({
                                            "addr": ip,
                                            "desc": "状态清理失败"
                                        })
                                else:
                                    # 原子操作：先清理状态，再添加到失败列表
                                    try:
                                        if ip in type_ips:
                                            type_ips.remove(ip)
                                        if ip in remaining_ips:
                                            remaining_ips.remove(ip)
                                        
                                        failed_ips.append({
                                            "addr": ip,
                                            "desc": "创建控制策略失败"
                                        })
                                    except Exception as cleanup_error:
                                        logger.error(f"处理失败IP时清理状态发生异常: {cleanup_error}")
                        else:
                            # 原子操作：先清理状态，再添加到失败列表
                            try:
                                if ip in type_ips:
                                    type_ips.remove(ip)
                                if ip in remaining_ips:
                                    remaining_ips.remove(ip)
                                
                                failed_ips.append({
                                    "addr": ip,
                                    "desc": "创建地址组失败"
                                })
                            except Exception as cleanup_error:
                                logger.error(f"处理创建地址组失败时清理状态发生异常: {cleanup_error}")
                
                # 检查处理进展
                if len(remaining_ips) == initial_count:
                    consecutive_failures += 1
                    logger.warning(f"本轮未处理任何IP，连续失败次数: {consecutive_failures}")
                    
                    if consecutive_failures >= 3:
                        logger.error("连续3轮未能处理任何IP，停止处理")
                        for ip in remaining_ips:
                            failed_ips.append({
                                "addr": ip,
                                "desc": "处理失败（达到最大重试次数）"
                            })
                        break
                else:
                    consecutive_failures = 0
            
            # 生成处理结果
            result = {
                "statusCode": 200,
                "body": {
                    "success_ips": success_ips,
                    "failed_ips": failed_ips,
                    "skipped_ips": skipped_ips,
                    "summary": {
                        "total_ips": len(ips),
                        "success_count": len(success_ips),
                        "failed_count": len(failed_ips),
                        "skipped_count": len(skipped_ips)
                    }
                }
            }
            
            logger.info(f"批量封禁完成 - 总数:{len(ips)}, 成功:{len(success_ips)}, 失败:{len(failed_ips)}, 跳过:{len(skipped_ips)}")
            return result
            
        except Exception as e:
            logger.error(f"批量封禁异常: {str(e)}")
            return {
                "statusCode": 500,
                "error": f"批量封禁异常: {str(e)}",
                "body": {}
            }

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