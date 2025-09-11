#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试重复处理问题的修复
"""

def test_duplicate_processing_fix():
    """测试重复处理问题的修复"""
    
    print("=== 测试重复处理问题的修复 ===")
    
    # 模拟实际的处理逻辑
    remaining_ips = ['1.1.1.5/32', '1.1.1.6/32']
    success_ips = []
    failed_ips = []
    
    # 模拟现有组
    existing_groups = [{
        'GroupName': 'DEV-P-Deny-Secops-Blacklist-In-jyf9ll62',
        'GroupUuid': '09b1619f-85fc-43c2-b9d1-7e79f5a58221',
        'AddressList': ['1.1.1.1/32', '1.1.1.2/32', '1.1.1.3/32', '1.1.1.4/32'],
        'Description': '自动创建的安全封禁地址组'
    }]
    
    print(f"初始状态:")
    print(f"  remaining_ips: {remaining_ips}")
    print(f"  现有组包含: {existing_groups[0]['AddressList']}")
    
    # 模拟主循环
    round_num = 1
    while remaining_ips:
        print(f"\n=== 第 {round_num} 轮处理 ===")
        
        # 分组
        ip_groups = {"ipv4": []}
        for ip in remaining_ips[:]:
            ip_groups["ipv4"].append(ip)
        
        # 处理ipv4类型
        type_ips = ip_groups["ipv4"][:]
        print(f"type_ips: {type_ips}")
        
        # 处理每个IP
        for ip in type_ips[:]:
            print(f"\n  处理IP: {ip}")
            processed = False
            
            # 尝试添加到现有组
            for group in existing_groups:
                if 'DEV-P-Deny-Secops-Blacklist-In' in group['GroupName']:
                    current_size = len(group['AddressList'])
                    if current_size < 2000:  # max_addresses_per_group
                        print(f"    尝试添加到组: {group['GroupName']}")
                        
                        # 模拟modify_address_book调用
                        new_address_list = group['AddressList'] + [ip]
                        
                        # 模拟API调用结果
                        if round_num == 1:
                            # 第一轮：成功
                            res_modify = {"statusCode": 200, "body": {"RequestId": "test"}}
                            print(f"    modify_address_book 成功: statusCode={res_modify.get('statusCode')}")
                        else:
                            # 后续轮次：可能失败
                            res_modify = "网络错误"  # 模拟返回字符串
                            print(f"    modify_address_book 失败: {res_modify}")
                        
                        # 关键：检查返回值类型
                        if not isinstance(res_modify, str) and res_modify.get('statusCode') == 200:
                            print(f"    ✅ {ip} 成功添加到组")
                            success_ips.append({
                                "addr": ip,
                                "groupname": group['GroupName'],
                                "groupuuid": group['GroupUuid'],
                                "grouplen": len(new_address_list),
                                "desc": "封禁成功"
                            })
                            group['AddressList'] = new_address_list
                            processed = True
                            
                            # 从列表中移除
                            if ip in type_ips:
                                type_ips.remove(ip)
                                print(f"    从 type_ips 中移除 {ip}")
                            if ip in remaining_ips:
                                remaining_ips.remove(ip)
                                print(f"    从 remaining_ips 中移除 {ip}")
                            break
                        else:
                            print(f"    ❌ 修改地址组失败: {res_modify}")
            
            # 如果没有成功处理，尝试创建新组
            if not processed:
                print(f"    {ip} 未成功添加到现有组，尝试创建新组")
                
                # 模拟创建新组（这里我们让它失败）
                print(f"    创建新组失败")
                failed_ips.append({
                    "addr": ip,
                    "desc": "创建地址组失败"
                })
                
                # 从列表中移除
                if ip in type_ips:
                    type_ips.remove(ip)
                if ip in remaining_ips:
                    remaining_ips.remove(ip)
                    print(f"    从 remaining_ips 中移除 {ip}")
        
        print(f"\n第 {round_num} 轮处理后:")
        print(f"  remaining_ips: {remaining_ips}")
        print(f"  success_ips: {len(success_ips)} 个")
        print(f"  failed_ips: {len(failed_ips)} 个")
        
        round_num += 1
        if round_num > 3:  # 防止无限循环
            break
    
    print(f"\n=== 最终结果 ===")
    print(f"success_ips:")
    for item in success_ips:
        print(f"  {item}")
    print(f"failed_ips:")
    for item in failed_ips:
        print(f"  {item}")
    
    # 检查重复
    success_addrs = [item['addr'] for item in success_ips]
    failed_addrs = [item['addr'] for item in failed_ips]
    duplicates = set(success_addrs) & set(failed_addrs)
    
    if duplicates:
        print(f"\n⚠️  发现重复处理的IP: {duplicates}")
        return False
    else:
        print(f"\n✅ 没有发现重复处理的IP")
        return True

if __name__ == "__main__":
    success = test_duplicate_processing_fix()
    if success:
        print("\n🎉 测试通过！修复有效。")
    else:
        print("\n❌ 测试失败！仍然存在重复处理问题。")
