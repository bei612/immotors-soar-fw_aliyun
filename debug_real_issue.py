#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试实际问题的脚本
"""

def simulate_real_issue():
    """模拟实际的重复处理问题"""
    
    print("=== 模拟实际问题场景 ===")
    
    # 从日志中我们知道：
    # 1. 有两次成功的 modify_address_book 调用
    # 2. 最终结果显示同样的IP既成功又失败
    
    # 模拟场景：6个IP，其中4个已存在，2个新IP
    remaining_ips = ['1.1.1.1/32', '1.1.1.2/32', '1.1.1.3/32', '1.1.1.4/32', '1.1.1.5/32', '1.1.1.6/32']
    existing_ips_in_group = ['1.1.1.1/32', '1.1.1.2/32', '1.1.1.3/32', '1.1.1.4/32']
    
    success_ips = []
    failed_ips = []
    skipped_ips = []
    
    print(f"初始 remaining_ips: {remaining_ips}")
    print(f"已存在的IP: {existing_ips_in_group}")
    
    # 模拟主循环
    round_num = 1
    while remaining_ips:
        print(f"\n=== 第 {round_num} 轮处理 ===")
        initial_count = len(remaining_ips)
        print(f"remaining_ips: {remaining_ips}")
        
        # 分组处理
        ip_groups = {"ipv4": []}
        for ip in remaining_ips[:]:
            ip_groups["ipv4"].append(ip)
        
        # 处理ipv4类型
        type_ips = ip_groups["ipv4"][:]
        print(f"type_ips: {type_ips}")
        
        # 检查已存在的IP
        for ip in type_ips[:]:
            if ip in existing_ips_in_group:
                print(f"  {ip} 已存在，跳过")
                skipped_ips.append({
                    "addr": ip,
                    "desc": "无需封禁（已存在）"
                })
                # 从列表中移除
                if ip in type_ips:
                    type_ips.remove(ip)
                if ip in remaining_ips:
                    remaining_ips.remove(ip)
        
        print(f"跳过已存在IP后，type_ips: {type_ips}")
        
        # 处理剩余的新IP
        for ip in type_ips[:]:
            print(f"  处理新IP: {ip}")
            processed = False
            
            # 模拟尝试添加到现有组
            print(f"    尝试添加 {ip} 到现有组")
            
            # 模拟modify_address_book调用
            # 根据日志，这两次调用都成功了
            if ip in ['1.1.1.5/32', '1.1.1.6/32']:
                modify_result = {"statusCode": 200, "body": {"RequestId": "test"}}
                print(f"    modify_address_book 成功: {modify_result}")
                
                # 添加到成功列表
                success_ips.append({
                    "addr": ip,
                    "groupname": "DEV-P-Deny-Secops-Blacklist-In-jyf9ll62",
                    "groupuuid": "09b1619f-85fc-43c2-b9d1-7e79f5a58221",
                    "grouplen": 5 if ip == '1.1.1.5/32' else 6,
                    "desc": "封禁成功"
                })
                processed = True
                
                # 从列表中移除
                if ip in type_ips:
                    type_ips.remove(ip)
                    print(f"    从 type_ips 中移除 {ip}")
                if ip in remaining_ips:
                    remaining_ips.remove(ip)
                    print(f"    从 remaining_ips 中移除 {ip}")
                
                # 这里是关键：如果由于某种原因，IP没有被正确移除，
                # 或者在后续的逻辑中又被重新添加到某个列表中，
                # 就会导致重复处理
                
                # 模拟一个bug：假设由于某种原因，IP又被添加回了某个列表
                # 这可能是由于：
                # 1. 并发问题
                # 2. 异常处理不当
                # 3. 列表操作的bug
                
                # 让我们模拟这种情况
                if round_num == 1:  # 只在第一轮模拟这个bug
                    print(f"    ⚠️  模拟bug: {ip} 由于某种原因又被添加回处理列表")
                    # 这里我们不重新添加到remaining_ips，而是模拟其他可能的路径
                    pass
            
            # 如果没有被处理，尝试创建新组
            if not processed:
                print(f"    {ip} 未被处理，尝试创建新组")
                # 模拟创建新组失败
                failed_ips.append({
                    "addr": ip,
                    "desc": "创建地址组失败"
                })
                
                # 从列表中移除
                if ip in type_ips:
                    type_ips.remove(ip)
                if ip in remaining_ips:
                    remaining_ips.remove(ip)
        
        print(f"第 {round_num} 轮处理后:")
        print(f"  remaining_ips: {remaining_ips}")
        print(f"  success_ips: {len(success_ips)} 个")
        print(f"  failed_ips: {len(failed_ips)} 个")
        print(f"  skipped_ips: {len(skipped_ips)} 个")
        
        # 检查是否有进展
        if len(remaining_ips) == initial_count:
            print("  本轮没有进展，停止处理")
            break
        
        round_num += 1
        if round_num > 3:  # 防止无限循环
            break
    
    print(f"\n=== 最终结果 ===")
    print(f"success_ips: {success_ips}")
    print(f"failed_ips: {failed_ips}")
    print(f"skipped_ips: {skipped_ips}")
    
    # 检查重复
    success_addrs = [item['addr'] for item in success_ips]
    failed_addrs = [item['addr'] for item in failed_ips]
    duplicates = set(success_addrs) & set(failed_addrs)
    
    if duplicates:
        print(f"\n⚠️  发现重复处理的IP: {duplicates}")
        print("这表明存在逻辑错误，需要进一步调试")
    else:
        print(f"\n✅ 没有发现重复处理的IP")
    
    print(f"\n=== 可能的原因分析 ===")
    print("1. IP在成功处理后没有被正确从所有相关列表中移除")
    print("2. 存在并发问题或异常处理导致状态不一致")
    print("3. 某个条件分支导致IP被重复添加到处理队列")
    print("4. while循环的逻辑有问题，导致已处理的IP被重新处理")

if __name__ == "__main__":
    simulate_real_issue()
