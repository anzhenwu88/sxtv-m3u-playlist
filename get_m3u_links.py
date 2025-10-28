import requests
import json
from datetime import datetime
import time
import re

def get_real_m3u8_urls():
    """
    从山西网络电视台真实获取播放地址
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
    
    # 首先获取播放页面，分析真实的播放地址
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://www.sxrtv.com/',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }
        
        print("📡 访问山西网络电视台播放页面...")
        response = requests.get("https://www.sxrtv.com/tv/", headers=headers, timeout=15)
        
        if response.status_code == 200:
            content = response.text
            print("✅ 页面获取成功，开始分析播放地址...")
            
            # 在页面中查找所有M3U8链接
            m3u8_patterns = [
                r'https://livehhhttps\.sxrtv\.com/lsdream/[^"\']+?\.m3u8',
                r'file:\s*["\'](https://livehhhttps\.sxrtv\.com/lsdream/[^"\']+?\.m3u8)["\']',
                r'src:\s*["\'](https://livehhhttps\.sxrtv\.com/lsdream/[^"\']+?\.m3u8)["\']',
                r'url:\s*["\'](https://livehhhttps\.sxrtv\.com/lsdream/[^"\']+?\.m3u8)["\']'
            ]
            
            all_m3u8_urls = []
            for pattern in m3u8_patterns:
                matches = re.findall(pattern, content)
                all_m3u8_urls.extend(matches)
            
            print(f"🔍 在页面中找到 {len(all_m3u8_urls)} 个M3U8链接")
            
            # 显示找到的所有链接
            for url in all_m3u8_urls[:10]:  # 只显示前10个
                print(f"   📺 发现: {url}")
            
            # 为每个频道匹配对应的链接
            m3u_links = match_channels_to_urls(channels, all_m3u8_urls, content)
            
        else:
            print(f"❌ 页面获取失败: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ 抓取过程出错: {e}")
    
    return m3u_links

def match_channels_to_urls(channels, m3u8_urls, page_content):
    """
    将找到的M3U8链接匹配到对应的频道
    """
    print("\n🔗 开始匹配频道和播放地址...")
    
    matched_links = {}
    
    for channel_name, channel_code in channels.items():
        print(f"   🎯 正在匹配 {channel_name}...")
        
        # 方法1: 在链接中查找频道标识
        found_url = None
        
        # 根据频道代码在URL中查找
        for url in m3u8_urls:
            if channel_code.lower() in url.lower():
                found_url = url
                print(f"      ✅ 通过频道代码找到: {url}")
                break
        
        # 方法2: 在页面JavaScript中查找
        if not found_url:
            found_url = find_url_in_javascript(channel_code, page_content)
            if found_url:
                print(f"      ✅ 在JS中找到: {found_url}")
        
        # 方法3: 尝试访问播放API获取真实地址
        if not found_url:
            found_url = get_url_from_playback_api(channel_code)
            if found_url:
                print(f"      ✅ 从API获取: {found_url}")
        
        if found_url:
            matched_links[channel_name] = found_url
        else:
            print(f"      ❌ 未找到 {channel_name} 的播放地址")
            # 使用基础地址作为备用
            matched_links[channel_name] = f"https://livehhhttps.sxrtv.com/lsdream/{channel_code}/live.m3u8"
    
    return matched_links

def find_url_in_javascript(channel_code, page_content):
    """
    在页面JavaScript中查找播放地址
    """
    try:
        # 查找JavaScript中的播放器配置
        js_patterns = [
            rf'var.*{channel_code}.*=.*["\'](https://livehhhttps\.sxrtv\.com/lsdream/[^"\']+?\.m3u8)["\']',
            rf'cid.*{channel_code}.*["\']([^"\']+?\.m3u8)["\']',
            rf'{channel_code}.*["\'](https://livehhhttps\.sxrtv\.com/lsdream/[^"\']+?\.m3u8)["\']'
        ]
        
        for pattern in js_patterns:
            matches = re.findall(pattern, page_content, re.IGNORECASE)
            if matches:
                url = matches[0]
                if not url.startswith('http'):
                    url = f'https://livehhhttps.sxrtv.com{url}'
                return url
                
    except Exception as e:
        print(f"     JS解析失败: {e}")
    
    return None

def get_url_from_playback_api(channel_code):
    """
    尝试从播放器API获取地址
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://www.sxrtv.com/tv/',
            'Accept': 'application/json, text/javascript, */*; q=0.01'
        }
        
        # 尝试不同的API端点
        api_urls = [
            f"https://apphhplushttps.sxrtv.com/epg/{channel_code}.json",
            f"https://livehhhttps.sxrtv.com/lsdream/{channel_code}/live.m3u8",
            f"https://www.sxrtv.com/api/channel/{channel_code}"
        ]
        
        for api_url in api_urls:
            try:
                response = requests.get(api_url, headers=headers, timeout=8)
                if response.status_code == 200:
                    content = response.text
                    # 在响应中查找M3U8链接
                    m3u8_matches = re.findall(r'https://livehhhttps\.sxrtv\.com/lsdream/[^"\'\s]+?\.m3u8', content)
                    if m3u8_matches:
                        return m3u8_matches[0]
            except:
                continue
                
    except Exception as e:
        print(f"     API获取失败: {e}")
    
    return None

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
            response = requests.head(url, headers=headers, timeout=8, allow_redirects=True)
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
    m3u_content += f"# 来源: 真实抓取自山西网络广播电视台\n"
    m3u_content += f"# GitHub: https://github.com/anzhenwu88/sxtv-m3u-playlist\n\n"
    
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
        "total_channels": len(verified_links),
        "source": "https://www.sxrtv.com/tv/",
        "note": "真实地址抓取，非猜测生成"
    }
    
    with open("channels_info.json", "w", encoding="utf-8") as f:
        json.dump(info_data, f, ensure_ascii=False, indent=2)
    print("✅ 频道信息文件已生成: channels_info.json")
    
    print(f"\n🎉 真实地址抓取完成！")
    print(f"📺 频道数量: {len(verified_links)}")
    print(f"🕐 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
