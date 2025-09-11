# -*- coding: utf-8 -*-
# @Autor : immotors

from cbt.base_app import BaseApp
from cbt.action_result import ActionResult
import cbt.status as cbt_status
from apps.fw_aliyun.FwAliyunApp import FwAliyunApp
from loguru import logger  # 导入日记库，没有请先安装 pip install loguru
import os
import ipaddress

class App(BaseApp):

    def initialize(self, asset_config):
        self.ak = asset_config.get('ak')
        self.sk = asset_config.get('sk')
        self.endpoint = asset_config.get('endpoint')
        self.proxies = asset_config.get("proxy_url", "")
        
        return cbt_status.APP_SUCCESS

    def unload(self):
        pass

    def handle_action(self, action_id, params, action_context):
        # action_id 动作ip，数据类型string
        # params 动作参数，数据类型dict
        # action_context 动作上下文
        result = ActionResult()
        # 脚本调用的接口
        if hasattr(App, action_id):
            func = getattr(App, action_id)
            # 连通性测试
            if func.__code__.co_name == "test_connectivity":
                if func(self):
                    result.status = cbt_status.ACTION_STATUS_SUCCESS
                    result.message = "连通性测试成功"
                else:
                    result.status = cbt_status.ACTION_STATUS_FAILURE
                    result.message = "连通性测试失败"
                return result
            else:
                data = func(self, params)
                result.data = data
        return result
        
    def test_connectivity(self):
        # 连通性测试
        # return: True or False
        # TODO 自己实现联通性测试的逻辑
        try:
            app = FwAliyunApp(ak=self.ak, sk=self.sk, endpoint=self.endpoint, proxies=self.proxies)
            # 简单测试：尝试查询地址簿来验证连通性
            app.describe_address_book("", "ip")
            return True
        except Exception as e:
            logger.error(f"连通性测试失败: {e}")
            return False

    def AddAddressBook(self, params):
        groupname = params.get("groupname")
        grouptype = params.get("grouptype")
        description = params.get("description")
        addresslist = params.get("addresslist")
        addaddressbookobj = FwAliyunApp(ak=self.ak, sk=self.sk, endpoint=self.endpoint, proxies=self.proxies)
        res = addaddressbookobj.add_address_book(groupname, grouptype, description, addresslist)
        return res

    def DeleteAddressBook(self, params):
        groupuuid =  params.get("groupuuid")
        deleteaddressbookobj = FwAliyunApp(ak=self.ak, sk=self.sk, endpoint=self.endpoint, proxies=self.proxies)
        res = deleteaddressbookobj.delete_address_book(groupuuid)
        return res

    def DescribeAddressBook(self, params):
        query = params.get("query")
        grouptype = params.get("grouptype")
        describeaddressbookobj = FwAliyunApp(ak=self.ak, sk=self.sk, endpoint=self.endpoint, proxies=self.proxies)
        res = describeaddressbookobj.describe_address_book(query, grouptype)
        return res

    def ModifyAddressBook(self, params):
        groupname = params.get("groupname")
        groupuuid = params.get("groupuuid")
        description = params.get("description")
        addresslist = params.get("addresslist")
        modifyaddressbookobj = FwAliyunApp(ak=self.ak, sk=self.sk, endpoint=self.endpoint, proxies=self.proxies)
        res = modifyaddressbookobj.modify_address_book(groupname, groupuuid, description, addresslist)
        return res

    def DescribeControlPolicy(self, params):
        direction = params.get("direction")
        describecontrolpolicyobj = FwAliyunApp(ak=self.ak, sk=self.sk, endpoint=self.endpoint, proxies=self.proxies)
        res = describecontrolpolicyobj.describe_control_policy(direction)
        return res

    def AddControlPolicy(self, params):
        aclaction = params.get("aclaction")
        description = params.get("description")
        destination = params.get("destination")
        destinationtype = params.get("destinationtype")
        direction = params.get("direction")
        proto = params.get("proto")
        source = params.get("source")
        sourcetype = params.get("sourcetype")
        neworder = params.get("neworder")
        applicationname = params.get("applicationname")
        applicationnamelist = params.get("applicationnamelist")
        addcontrolpolicyobj = FwAliyunApp(ak=self.ak, sk=self.sk, endpoint=self.endpoint, proxies=self.proxies)
        res = addcontrolpolicyobj.add_control_policy(aclaction, description, destination, destinationtype, direction, proto, source, sourcetype, neworder, applicationname, applicationnamelist)
        return res

    def DeleteControlPolicy(self, params):
        acluuid = params.get("acluuid")
        direction = params.get("direction")
        deletecontrolpolicyobj = FwAliyunApp(ak=self.ak, sk=self.sk, endpoint=self.endpoint, proxies=self.proxies)
        res = deletecontrolpolicyobj.delete_control_policy(acluuid, direction)
        return res

    def SingleBlockAddress(self, params):
        addr = params.get("addr")
        direction = params.get("direction")
        singleblockaddressobj = FwAliyunApp(ak=self.ak, sk=self.sk, endpoint=self.endpoint, proxies=self.proxies)
        res = singleblockaddressobj.single_block_address(addr, direction)
        return res

    def SingleUnblockAddress(self, params):
        addr = params.get("addr")
        direction = params.get("direction")
        singleunblockaddressobj = FwAliyunApp(ak=self.ak, sk=self.sk, endpoint=self.endpoint, proxies=self.proxies)
        res = singleunblockaddressobj.single_unblock_address(addr, direction)
        return res

    def HwBlockAddress(self, params):
        direction = params.get("direction")
        hwblockaddressobj = FwAliyunApp(ak=self.ak, sk=self.sk, endpoint=self.endpoint, proxies=self.proxies)
        res = hwblockaddressobj.hw_block_address(direction)
        return res

    def HwBlockCheck(self, params):
        query = params.get("query")
        grouptype = params.get("grouptype")
        hwblockcheckobj = FwAliyunApp(ak=self.ak, sk=self.sk, endpoint=self.endpoint, proxies=self.proxies)
        res = hwblockcheckobj.hw_block_check(query, grouptype)
        return res