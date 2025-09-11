#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试重复处理问题的脚本
"""

def analyze_duplicate_processing():
    """分析重复处理问题"""
    
    print("=== 分析重复处理问题 ===")
    
    # 模拟问题场景
    print("\n问题场景：")
    print("- IP 1.1.1.5/32 和 1.1.1.6/32 既出现在 success_ips 中，又出现在 failed_ips 中")
    print("- 这说明同一个IP在一次处理中被处理了多次")
    
    print("\n可能的原因：")
    print("1. 在 for ip in type_ips[:] 循环中，IP被成功处理并从 type_ips 中移除")
    print("2. 但是由于某种原因，同一个IP又被后续的逻辑处理了")
    print("3. 第二次处理时失败，导致IP被添加到 failed_ips")
    
    print("\n需要检查的地方：")
    print("1. type_ips[:] 的使用是否正确")
    print("2. IP移除逻辑是否完整")
    print("3. 是否有其他地方会重复处理同一个IP")
    
    # 模拟代码逻辑
    print("\n=== 模拟代码逻辑 ===")
    
    type_ips = ['1.1.1.5/32', '1.1.1.6/32']
    remaining_ips = ['1.1.1.5/32', '1.1.1.6/32']
    success_ips = []
    failed_ips = []
    
    print(f"初始状态:")
    print(f"  type_ips: {type_ips}")
    print(f"  remaining_ips: {remaining_ips}")
    
    # 模拟第一轮处理
    print(f"\n第一轮处理 (for ip in type_ips[:]):")
    for ip in type_ips[:]:  # 使用副本遍历
        print(f"  处理 {ip}")
        # 模拟成功添加到现有组
        success_ips.append({
            "addr": ip,
            "desc": "封禁成功"
        })
        
        # 从列表中移除
        if ip in type_ips:
            type_ips.remove(ip)
            print(f"    从 type_ips 中移除 {ip}")
        if ip in remaining_ips:
            remaining_ips.remove(ip)
            print(f"    从 remaining_ips 中移除 {ip}")
    
    print(f"\n第一轮处理后:")
    print(f"  type_ips: {type_ips}")
    print(f"  remaining_ips: {remaining_ips}")
    print(f"  success_ips: {len(success_ips)} 个")
    
    # 这里应该没有问题，让我们看看是否有其他逻辑会重复处理
    print(f"\n=== 分析可能的重复处理点 ===")
    print("1. 检查是否有其他循环会处理同样的IP列表")
    print("2. 检查是否有条件分支导致IP被重复添加到失败列表")
    print("3. 检查 remaining_ips 的使用是否一致")

if __name__ == "__main__":
    analyze_duplicate_processing()
