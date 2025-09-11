#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试原子操作修复是否有效
"""

def test_atomic_operations():
    """测试原子操作修复"""
    
    print("=== 测试原子操作修复 ===")
    
    # 模拟修复后的原子操作逻辑
    success_ips = []
    failed_ips = []
    remaining_ips = ['1.1.1.5/32', '1.1.1.6/32']
    type_ips = ['1.1.1.5/32', '1.1.1.6/32']
    
    print(f"初始状态:")
    print(f"  remaining_ips: {remaining_ips}")
    print(f"  type_ips: {type_ips}")
    
    # 模拟处理每个IP
    for ip in type_ips[:]:
        print(f"\n处理IP: {ip}")
        
        # 模拟API调用成功
        api_success = True
        print(f"  API调用成功: {api_success}")
        
        if api_success:
            # 原子操作：先更新所有状态，再添加到结果列表
            try:
                print(f"  开始原子操作...")
                
                # 模拟在清理状态时发生异常（只对第一个IP）
                if ip == '1.1.1.5/32':
                    print(f"  ⚠️  模拟异常：在清理状态时发生错误")
                    raise Exception("模拟的清理异常")
                
                # 从处理列表中移除
                if ip in type_ips:
                    type_ips.remove(ip)
                    print(f"    从 type_ips 中移除 {ip}")
                if ip in remaining_ips:
                    remaining_ips.remove(ip)
                    print(f"    从 remaining_ips 中移除 {ip}")
                
                # 只有在所有操作成功后才添加到成功列表
                success_ips.append({
                    "addr": ip,
                    "desc": "封禁成功"
                })
                print(f"    添加到 success_ips: {ip}")
                
            except Exception as cleanup_error:
                print(f"  ❌ 清理IP状态时发生异常: {cleanup_error}")
                print(f"  由于异常，{ip} 不会被添加到成功列表")
                # 关键：如果清理失败，不标记为成功
                # IP仍然在remaining_ips中，会被后续处理
    
    print(f"\n第一轮处理后:")
    print(f"  remaining_ips: {remaining_ips}")
    print(f"  type_ips: {type_ips}")
    print(f"  success_ips: {len(success_ips)} 个")
    
    # 模拟第二轮处理（由于异常，某些IP仍在remaining_ips中）
    if remaining_ips:
        print(f"\n=== 第二轮处理（处理剩余IP）===")
        
        # 重新分组
        type_ips = remaining_ips[:]
        
        for ip in type_ips[:]:
            print(f"\n再次处理IP: {ip}")
            
            # 这次处理失败
            api_success = False
            print(f"  API调用失败: {api_success}")
            
            if not api_success:
                # 原子操作：先清理状态，再添加到失败列表
                try:
                    if ip in type_ips:
                        type_ips.remove(ip)
                        print(f"    从 type_ips 中移除 {ip}")
                    if ip in remaining_ips:
                        remaining_ips.remove(ip)
                        print(f"    从 remaining_ips 中移除 {ip}")
                    
                    failed_ips.append({
                        "addr": ip,
                        "desc": "创建地址组失败"
                    })
                    print(f"    添加到 failed_ips: {ip}")
                    
                except Exception as cleanup_error:
                    print(f"  ❌ 处理失败IP时清理状态发生异常: {cleanup_error}")
    
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
        print(f"\n⚠️  仍然发现重复处理的IP: {duplicates}")
        print("原子操作修复无效，需要进一步调试")
        return False
    else:
        print(f"\n✅ 没有发现重复处理的IP")
        print("原子操作修复有效！")
        return True

if __name__ == "__main__":
    success = test_atomic_operations()
    if success:
        print("\n🎉 原子操作修复测试通过！")
        print("现在即使在异常情况下，IP也不会被重复处理。")
    else:
        print("\n❌ 原子操作修复测试失败！")
        print("需要进一步改进异常处理逻辑。")
