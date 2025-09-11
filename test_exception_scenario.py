#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试异常场景下的重复处理问题
"""

def test_exception_scenario():
    """测试异常场景下的重复处理问题"""
    
    print("=== 测试异常场景下的重复处理问题 ===")
    
    # 模拟一个可能导致重复处理的场景：
    # 1. IP成功添加到success_ips
    # 2. 在从remaining_ips中移除IP时发生异常
    # 3. IP仍然在remaining_ips中，会被重复处理
    
    remaining_ips = ['1.1.1.5/32', '1.1.1.6/32']
    success_ips = []
    failed_ips = []
    
    print(f"初始 remaining_ips: {remaining_ips}")
    
    # 模拟处理过程
    for ip in remaining_ips[:]:
        print(f"\n处理IP: {ip}")
        
        try:
            # 模拟成功的API调用
            print(f"  API调用成功")
            success_ips.append({
                "addr": ip,
                "desc": "封禁成功"
            })
            print(f"  添加到success_ips: {ip}")
            
            # 模拟在移除IP时发生异常
            if ip == '1.1.1.5/32':
                print(f"  ⚠️  模拟异常：在移除IP时发生错误")
                raise Exception("模拟的网络错误")
            
            # 正常移除IP
            remaining_ips.remove(ip)
            print(f"  从remaining_ips中移除: {ip}")
            
        except Exception as e:
            print(f"  ❌ 处理异常: {e}")
            # 异常处理：IP已经在success_ips中，但仍在remaining_ips中
            # 这可能导致重复处理
    
    print(f"\n第一轮处理后:")
    print(f"  remaining_ips: {remaining_ips}")
    print(f"  success_ips: {len(success_ips)} 个")
    
    # 模拟第二轮处理（由于remaining_ips不为空）
    if remaining_ips:
        print(f"\n=== 第二轮处理（由于异常，remaining_ips不为空）===")
        
        for ip in remaining_ips[:]:
            print(f"\n再次处理IP: {ip}")
            
            # 这次处理失败
            print(f"  这次API调用失败")
            failed_ips.append({
                "addr": ip,
                "desc": "创建地址组失败"
            })
            print(f"  添加到failed_ips: {ip}")
            
            # 移除IP
            remaining_ips.remove(ip)
            print(f"  从remaining_ips中移除: {ip}")
    
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
        print("这就是导致问题的原因：异常处理不当导致IP状态不一致")
        return False
    else:
        print(f"\n✅ 没有发现重复处理的IP")
        return True

if __name__ == "__main__":
    success = test_exception_scenario()
    if not success:
        print("\n💡 解决方案：")
        print("1. 使用更细粒度的异常处理")
        print("2. 确保IP状态的原子性操作")
        print("3. 在异常发生时正确清理状态")
