# larch-story-studio

在 [Larch](https://larch.ink) 平台進行專案、白板、故事卡片、角色、素材、AI 生成、版本快照、復原與匯出的完整創作 Skill。支援 Streamable HTTP MCP 與 REST API fallback。

## 這個 skill 涵蓋什麼

- **專案與白板**：專案管理、白板階層、卡片節點（dialogue, choice, scene, event, aiStory, setVariable 等）批次與單張安全 patch。
- **角色與立繪差分**：角色設定、帶透明通道（Alpha）差分立繪上傳與管理、語音音色配置。
- **素材庫與個人素材包**：多媒體資源上傳與管理、全域素材包同步。
- **免登入即時預覽**：取得短效預覽 URL（`url` / `playUrl` / `boardUrl` / 單張 `cardId`），在 Agent 或瀏覽器直接視覺驗證。
- **版本快照與復原**：重大變更版本自動快照與回滾機制。
- **市集發布與分享**：作品上架、版本更新、公開分享連結。

## 安裝

```bash
git clone https://github.com/yazelin/larch-story-studio-skill ~/larch-story-studio-skill
ln -s ~/larch-story-studio-skill ~/.claude/skills/larch-story-studio
ln -s ~/larch-story-studio-skill ~/.agents/skills/larch-story-studio
```

其他 agent 不需要額外安裝，直接讀 `SKILL.md` 照做即可。

## 金鑰與連線配置

金鑰放 `~/.config/larch/key`（`chmod 600`）。**絕對不要寫進專案、卡片、匯出檔或 repo。**

### Antigravity (agy)

```bash
agy mcp add --header "Authorization: Bearer <LARCH_API_KEY>" larch-story-studio https://larch.ink/mcp
```

### Claude Code

```bash
claude mcp add --scope user --transport http larch-story-studio https://larch.ink/mcp --header "Authorization: Bearer <LARCH_API_KEY>"
```

### REST Fallback

若目前環境無法註冊遠端 MCP，可直接使用 REST API 搭配 `~/.config/larch/key`：

```bash
python3 ~/larch-story-studio-skill/bin/larch-api.py projects
```

## 授權

MIT © 林亞澤

---

[GitHub](https://github.com/yazelin) · [Facebook](https://www.facebook.com/yaze.lin.gm) · [請亞澤喝咖啡](https://buymeacoffee.com/yazelin) · [亞澤的部落格](https://yazelin.github.io/)
