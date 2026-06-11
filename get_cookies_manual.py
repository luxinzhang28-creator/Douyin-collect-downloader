#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
抖音Cookie获取助手（手动版）
无需安装Playwright，通过浏览器开发者工具手动获取
"""

import json
import yaml
import os
import sys
from datetime import datetime
from typing import Dict

def print_instructions():
    """打印获取Cookie的详细说明"""
    print("\n" + "="*60)
    print("抖音Cookie获取教程")
    print("="*60)
    print("\n📝 获取步骤：\n")
    print("1. 打开浏览器（推荐Chrome/Edge）")
    print("2. 访问抖音网页版：https://www.douyin.com")
    print("3. 登录您的账号（扫码/手机号/第三方登录）")
    print("4. 登录成功后，按 F12 打开开发者工具")
    print("5. 切换到 Network（网络）标签")
    print("6. 刷新页面（F5）")
    print("7. 在请求列表中找到任意一个 douyin.com 的请求")
    print("8. 点击该请求，在右侧找到 Request Headers（请求标头）")
    print("9. 找到 Cookie 字段，复制整个Cookie值")
    print("\n" + "="*60)
    
    print("\n⚠️ 重要提示：")
    print("• Cookie包含您的登录信息，请勿分享给他人")
    print("• Cookie有效期通常为7-30天，过期需重新获取")
    print("• 建议定期更新Cookie以保证下载成功率")
    print("\n" + "="*60)

def parse_cookie_string(cookie_str: str) -> Dict[str, str]:
    """解析Cookie字符串为字典"""
    cookies = {}
    
    # 清理输入
    cookie_str = cookie_str.strip()
    if cookie_str.startswith('"') and cookie_str.endswith('"'):
        cookie_str = cookie_str[1:-1]
    
    # 分割Cookie
    for item in cookie_str.split(';'):
        item = item.strip()
        if '=' in item:
            key, value = item.split('=', 1)
            cookies[key.strip()] = value.strip()
    
    return cookies

def validate_cookies(cookies: Dict[str, str]) -> bool:
    """验证Cookie是否包含必要字段"""
    # 必要的Cookie字段
    required_fields = ['ttwid']  # 最少需要ttwid
    important_fields = ['sessionid', 'sessionid_ss', 'passport_csrf_token', 'msToken']
    
    # 检查必要字段
    missing_required = []
    for field in required_fields:
        if field not in cookies:
            missing_required.append(field)
    
    if missing_required:
        print(f"\n❌ 缺少必要的Cookie字段: {', '.join(missing_required)}")
        return False
    
    # 检查重要字段
    missing_important = []
    for field in important_fields:
        if field not in cookies:
            missing_important.append(field)
    
    if missing_important:
        print(f"\n⚠️ 缺少部分重要Cookie字段: {', '.join(missing_important)}")
        print("可能会影响某些功能，但可以尝试使用")
    
    return True

def save_cookies(cookies: Dict[str, str], config_path: str = "config.yml"):
    """保存Cookie到配置文件"""
    # 读取现有配置
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f) or {}
    else:
        config = {}
    
    # 更新Cookie配置
    config['cookies'] = cookies
    
    # 保存配置
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    
    print(f"\n✅ Cookie已保存到 {config_path}")
    
    # 同时保存完整Cookie字符串
    cookie_string = '; '.join([f'{k}={v}' for k, v in cookies.items()])
    with open('cookies.txt', 'w', encoding='utf-8') as f:
        f.write(cookie_string)
    print(f"✅ 完整Cookie字符串已保存到 cookies.txt")
    
    # 保存带时间戳的备份
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f'cookies_backup_{timestamp}.json'
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump({
            'cookies': cookies,
            'cookie_string': cookie_string,
            'timestamp': timestamp,
            'note': '抖音Cookie备份'
        }, f, ensure_ascii=False, indent=2)
    print(f"✅ Cookie备份已保存到 {backup_file}")

def load_existing_cookies(config_path: str = "config.yml") -> Dict[str, str]:
    """加载现有的Cookie"""
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f) or {}
            return config.get('cookies', {})
    return {}

def main():
    """主函数"""
    print("\n🍪 抖音Cookie配置助手")
    print("-" * 40)
    
    # 显示选项
    print("\n请选择操作：")
    print("1. 获取新的Cookie")
    print("2. 查看当前Cookie")
    print("3. 验证Cookie有效性")
    print("4. 显示获取教程")
    
    choice = input("\n请输入选项 (1-4): ").strip()
    
    if choice == '1':
        # 获取新Cookie
        print_instructions()
        
        print("\n请粘贴您复制的Cookie内容：")
        print("（提示：粘贴后按Enter确认）")
        print("-" * 40)
        
        # 支持多行输入
        lines = []
        while True:
            line = input()
            if line:
                lines.append(line)
            else:
                break
        
        cookie_str = ' '.join(lines)
        
        if not cookie_str:
            print("\n❌ 未输入Cookie")
            return
        
        # 解析Cookie
        cookies = parse_cookie_string(cookie_str)
        
        if not cookies:
            print("\n❌ Cookie解析失败，请检查格式")
            return
        
        print(f"\n✅ 成功解析 {len(cookies)} 个Cookie字段")
        
        # 显示重要Cookie
        print("\n📋 解析到的关键Cookie：")
        important_fields = ['sessionid', 'sessionid_ss', 'ttwid', 'passport_csrf_token', 'msToken']
        for field in important_fields:
            if field in cookies:
                value = cookies[field]
                display_value = f"{value[:20]}..." if len(value) > 20 else value
                print(f"  • {field}: {display_value}")
        
        # 验证Cookie
        if validate_cookies(cookies):
            # 询问是否保存
            save_choice = input("\n是否保存Cookie到配置文件？(y/n): ").strip().lower()
            if save_choice == 'y':
                save_cookies(cookies)
                print("\n🎉 配置完成！您现在可以运行下载器了：")
                print("python download_collects.py --all")
            else:
                print("\n已取消保存")
        
    elif choice == '2':
        # 查看当前Cookie
        cookies = load_existing_cookies()
        if cookies:
            print("\n📋 当前配置的Cookie：")
            for key, value in cookies.items():
                display_value = f"{value[:30]}..." if len(value) > 30 else value
                print(f"  • {key}: {display_value}")
        else:
            print("\n❌ 未找到配置的Cookie")
    
    elif choice == '3':
        # 验证Cookie
        cookies = load_existing_cookies()
        if cookies:
            print("\n🔍 验证Cookie...")
            if validate_cookies(cookies):
                print("✅ Cookie格式正确")
                print("\n注意：这只是格式验证，实际是否有效需要测试下载功能")
        else:
            print("\n❌ 未找到配置的Cookie")
    
    elif choice == '4':
        # 显示教程
        print_instructions()
    
    else:
        print("\n❌ 无效的选项")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 已退出")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()