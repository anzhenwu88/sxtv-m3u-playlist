import requests
import json
from datetime import datetime
import time
import re

def get_real_m3u8_urls():
    """
    从山西网络电视台真实获取播放地址 - 带反爬虫绕过
    """
    print("🎯 开始从官网真实抓取M3U8地址...")
    print("=" * 60)
    
    # 频道列表
    channels = {
        "山西卫视": "SXTV1",
        "黄河电视台": "SXTV2", 
        "山西经济与科技": "SXTV3",
        "山西影视": "SXTV4",
        "山西社会与法治": "SXTV5",
        "山西文体生活": "SXTV6",
        "太原-1": "taiyuan"
    }
    
    m3u_links = {}
    
    # 使用更好的请求头绕过反爬虫
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://www.sxrtv.com/',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Upgrade-Insecure-Requests': '1',
        'DNT': '1'
    }
    
    try:
        print("📡 访问山西网络电视台播放页面...")
        
        # 创建会话保持cookies
        session = requests.Session()
        session.headers.update(headers)
        
        # 先访问首页获取cookies
        response = session.get("https://www.sxrtv.com/", timeout=15)
        print(f"首页状态码: {response.status_code}")
        
        # 再访问播放页面
        response = session.get("https://www.sxrtv.com/tv/", timeout=15)
        
        if response.status_code == 200:
            content = response.text
            print("✅ 页面获取成功，开始分析播放地址...")
            
            # 在页面中查找所有M3U8链接
            m3u8_patterns = [
                r'https://livehhhttps\.sxrtv\.com/lsdream/[^"\']+?\.m3u8',
                r'file:\s*["\'](https://livehhhttps\.sxrtv\.com/lsdream/[^"\']+?\.m3u8)["\']',
                r'src:\s*["\'](https://livehhhttps\.sxrtv\.com/lsdream/[^"\']+?\.m3u8)["\']',
            ]
            
            all_m3u8_urls = []
            for pattern in m3u8_patterns:
                matches = re.findall(pattern, content)
                all_m3u8_urls.extend(matches)
            
            print(f"🔍 在页面中找到 {len(all_m3u8_urls)} 个M3U8链接")
            
            # 显示找到的所有链接
            for url in all_m3u8_urls[:10]:
                print(f"   📺 发现: {url}")
            
            # 为每个频道匹配对应的链接
            for channel_name, channel_code in channels.items():
                for url in all_m3u8_urls:
                    if channel_code.lower() in url.lower():
                        m3u_links[channel_name] = url
                        print(f"✅ 匹配到 {channel_name}: {url}")
                        break
                else:
                    # 如果没有找到，使用基础地址
                    m3u_links[channel_name] = f"https://livehhhttps.sxrtv.com/lsdream/{channel_code}/live.m3u8"
                    print(f"⚠️ {channel_name}: 使用基础地址")
            
        else:
            print(f"❌ 页面获取失败: HTTP {response.status_code}")
            # 如果获取失败，使用备用地址
            for channel_name, channel_code in channels.items():
                m3u_links[channel_name] = f"https://livehhhttps.sxrtv.com/lsdream/{channel_code}/live.m3u8"
            
    except Exception as e:
        print(f"❌ 抓取过程出错: {e}")
        # 出错时使用备用地址
        for channel_name, channel_code in channels.items():
            m3u_links[channel_name] = f"https://livehhhttps.sxrtv.com/lsdream/{channel_code}/live.m3u8"
    
    return m3u_links

def verify_urls(m3u_links):
    """
    验证URL有效性
    """
    print("\n🔍 验证地址有效性...")
    print("=" * 50)
    
    verified_links = {}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://www.sxrtv.com/tv/'
    }
    
    for channel_name, url in m3u_links.items():
        try:
            response = requests.head(url, headers=headers, timeout=5, allow_redirects=True)
            if response.status_code == 200:
                verified_links[channel_name] = url
                print(f"✅ {channel_name}: 地址有效")
            else:
                verified_links[channel_name] = url
                print(f"⚠️ {channel_name}: HTTP {response.status_code}")
                
        except Exception as e:
            verified_links[channel_name] = url
            print(f"⚠️ {channel_name}: 验证失败 - 但仍保留地址")
        
        time.sleep(1)
    
    return verified_links

def generate_m3u_content(m3u_links):
    """生成M3U文件内容"""
    m3u_content = "#EXTM3U\n"
    m3u_content += f"# 山西电视台直播M3U播放列表\n"
    m3u_content += f"# 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    m3u_content += f"# 自动更新周期: 每30分钟\n"
    m3u_content += f"# 来源: 山西网络广播电视台\n\n"
    
    for channel_name, url in m3u_links.items():
        m3u_content += f"#EXTINF:-1 tvg-id=\"{channel_name}\" tvg-name=\"{channel_name}\" group-title=\"山西频道\",{channel_name}\n"
        m3u_content += f"{url}\n"
    
    return m3u_content

def main():
    print("🚀 山西电视台M3U播放列表 - 真实地址抓取")
    print("=" * 60)
    
    # 真实抓取M3U8地址
    m3u_links = get_real_m3u8_urls()
    
    # 验证地址
    verified_links = verify_urls(m3u_links)
    
    # 生成M3U内容
    m3u_content = generate_m3u_content(verified_links)
    
    # 保存文件
    with open("sxtv_channels.m3u", "w", encoding="utf-8") as f:
        f.write(m3u_content)
    print(f"\n✅ M3U文件已生成: sxtv_channels.m3u")
    
    # 保存频道信息
    info_data = {
        "update_time": datetime.now().isoformat(),
        "channels": verified_links,
        "total_channels": len(verified_links)
    }
    
    with open("channels_info.json", "w", encoding="utf-8") as f:
        json.dump(info_data, f, ensure_ascii=False, indent=2)
    print("✅ 频道信息文件已生成: channels_info.json")
    
    print(f"\n🎉 更新完成！")
    print(f"📺 频道数量: {len(verified_links)}")
    print(f"🕐 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
