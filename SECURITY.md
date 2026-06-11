# 安全说明

## Cookie 与账号安全

本项目需要抖音 Cookie 才能下载收藏夹内容。Cookie 等同于你的**登录凭证**，泄露后他人可能访问你的账号。

### 请勿上传以下文件

| 文件 | 说明 |
|------|------|
| `config.yml` | 含 Cookie 的主配置文件 |
| `cookies.txt` | Cookie 字符串备份 |
| `cookies_backup_*.json` | 带时间戳的 Cookie 备份 |
| `cookies.pkl` | Cookie 缓存 |
| `Downloaded/` | 已下载的私人视频 |

以上路径已在 `.gitignore` 中配置，但提交前请用 `git status` 再次确认。

### 若 Cookie 已泄露

1. 立即在浏览器退出抖音网页版
2. 重新登录，使旧 Cookie 失效
3. 若已推送到 GitHub，删除含 Cookie 的提交或重建仓库
4. 重新生成 Cookie 并更新本地 `config.yml`

### 使用建议

- 不要将 Cookie 分享给他人
- 不要在公开场合截图含 Cookie 的配置文件
- 定期更新 Cookie（通常 7–30 天过期）
- 使用本项目仅供个人学习，遵守平台服务条款

## 报告安全问题

如发现安全相关问题，请通过 [GitHub Issues](https://github.com/luxinzhang28-creator/Douyin-collect-downloader/issues) 私下说明，勿在公开 Issue 中粘贴真实 Cookie。
