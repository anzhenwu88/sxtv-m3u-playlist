# 山西电视台直播 M3U 播放列表

自动获取和更新山西广播电视台各频道的M3U8播放地址。

## 📺 频道列表

- 山西卫视
- 黄河电视台
- 山西经济与科技
- 山西影视
- 山西社会与法治
- 山西文体生活
- 太原-1

## 🚀 使用方法

在支持M3U的播放器中输入以下地址：
https://raw.githubusercontent.com/anzhenwu88/sxtv-live-m3u/main/sxtv_channels.m3u

### 推荐播放器
- VLC Media Player
- PotPlayer
- Kodi
- IPTV Smarters
- Tivimate

## ⚡ 自动更新

- 🔄 **每30分钟自动更新**一次播放地址
- 🎯 **基于真实地址模式**生成有效链接
- ✅ **自动验证**地址有效性
- 📊 **实时监控**播放状态

## 📁 文件说明

- `sxtv_channels.m3u` - 主播放列表文件
- `channels_info.json` - 频道信息和更新时间
- `get_m3u_links.py` - 自动更新脚本
- `.github/workflows/update-m3u.yml` - GitHub Actions工作流

## 🔗 来源

官方直播源：https://www.sxrtv.com/tv/

## 📄 许可证

MIT License
