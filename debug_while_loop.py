#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试while循环中的重复处理问题
"""

def simulate_while_loop_issue():
    """模拟while循环中的问题"""
    
    print("=== 模拟while循环处理逻辑 ===")
    
    # 初始状态
    remaining_ips = ['1.1.1.1/32', '1.1.1.2/32', '1.1.1.5/32', '1.1.1.6/32']
    success_ips = []
    failed_ips = []
    consecutive_failures = 0
    
    print(f"初始 remaining_ips: {remaining_ips}")
    
    round_num = 1
    
    # 模拟while循环
    while remaining_ips:
        print(f"\n=== 第 {round_num} 轮处理 ===")
        initial_count = len(remaining_ips)
        print(f"本轮开始时 remaining_ips 数量: {initial_count}")
        print(f"remaining_ips: {remaining_ips}")
        
        # 按地址类型分组处理
        ip_groups = {"ipv4": [], "network": [], "domain": []}
        
        # 模拟分组逻辑
        for ip in remaining_ips[:]:  # 使用副本遍历
            ip_groups["ipv4"].append(ip)
        
        print(f"分组后 ip_groups['ipv4']: {ip_groups['ipv4']}")
        
        # 处理每种地址类型
        for addr_type, type_ips in ip_groups.items():
            if not type_ips:
                continue
                
            print(f"\n处理 {addr_type} 类型的IP: {type_ips}")
            
            # 模拟检查已存在的IP
            existing_ips = ['1.1.1.1/32', '1.1.1.2/32']  # 假设这些已存在
            
            for ip in type_ips[:]:
                if ip in existing_ips:
                    print(f"  {ip} 已存在，跳过")
                    # 从列表中移除
                    if ip in type_ips:
                        type_ips.remove(ip)
                    if ip in remaining_ips:
                        remaining_ips.remove(ip)
                        print(f"    从 remaining_ips 中移除 {ip}")
            
            print(f"  跳过已存在IP后，剩余 type_ips: {type_ips}")
            
            # 处理剩余的IP
            for ip in type_ips[:]:
                print(f"  处理新IP: {ip}")
                
                # 模拟成功添加到现有组
                if round_num == 1:  # 第一轮成功
                    success_ips.append({
                        "addr": ip,
                        "desc": "封禁成功"
                    })
                    print(f"    {ip} 成功添加到现有组")
                    
                    # 从列表中移除
                    if ip in type_ips:
                        type_ips.remove(ip)
                        print(f"    从 type_ips 中移除 {ip}")
                    if ip in remaining_ips:
                        remaining_ips.remove(ip)
                        print(f"    从 remaining_ips 中移除 {ip}")
                else:  # 后续轮次可能失败
                    failed_ips.append({
                        "addr": ip,
                        "desc": "创建地址组失败"
                    })
                    print(f"    {ip} 处理失败")
                    
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
        
        # 检查处理进展
        if len(remaining_ips) == initial_count:
            consecutive_failures += 1
            print(f"  本轮未处理任何IP，连续失败次数: {consecutive_failures}")
            
            if consecutive_failures >= 3:
                print("  连续3轮未能处理任何IP，停止处理")
                for ip in remaining_ips:
                    failed_ips.append({
                        "addr": ip,
                        "desc": "处理失败（达到最大重试次数）"
                    })
                break
        else:
            consecutive_failures = 0
        
        round_num += 1
        
        # 防止无限循环
        if round_num > 5:
            print("  达到最大轮次，停止处理")
            break
    
    print(f"\n=== 最终结果 ===")
    print(f"success_ips: {success_ips}")
    print(f"failed_ips: {failed_ips}")
    
    # 检查重复
    success_addrs = [item['addr'] for item in success_ips]
    failed_addrs = [item['addr'] for item in failed_ips]
    duplicates = set(success_addrs) & set(failed_addrs)
    
    if duplicates:
        print(f"\n⚠️  发现重复处理的IP: {duplicates}")
    else:
        print(f"\n✅ 没有发现重复处理的IP")

if __name__ == "__main__":
    simulate_while_loop_issue()
