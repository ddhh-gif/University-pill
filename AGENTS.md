# AGENTS.md — 本仓库的自动提交与双端同步

本仓库有一套自动 commit / 同步机制，了解它能避免误操作（例如以为改动没被提交，或不知道提交被自动推到了 GitHub）。

## 1. 原理

本地工作副本在 zihan 机器的 NTFS 盘上：

```
/media/zihan/Data/linux保存在此/university-pill
```

一个 `systemd --user` 定时器每 10 分钟触发一次性脚本，执行：

1. 加锁，防止两轮并发；
2. 把本地所有改动 `git add -A` 并提交；
3. 探测 fzh 是否可达；
4. 从 fzh 拉取并合并它的提交（双向同步）；
5. 先推 fzh（局域网），再尽力推 GitHub（origin）。

即：**本地 → fzh 是主通道，GitHub 是尽力而为的备份，fzh → 本地也会被拉回合并。**

## 2. 每次运行的完整流程

脚本：`/home/zihan/.local/bin/upill-autocommit.sh`

| 步骤 | 行为 | 关键命令/参数 |
|---|---|---|
| 0 | 进入仓库；失败（未挂载）则退出 | `cd "$REPO" \|\| exit 1` |
| 1 | 抢 flock 非阻塞锁；拿不到说明上一轮在跑，退出 | `exec 9>"$REPO/.git/autocommit.lock"; flock -n 9 \|\| exit 0` |
| 2 | 若存在 `\.git/index.lock`（有别的 git 操作），跳过本轮 | 写日志 `skip: index.lock exists` |
| 3 | 暂存所有改动并提交 | `git add -A`；有差异则 `git commit -m "auto: $(date '+%F %T')"` |
| 4 | 探测 fzh（8 秒超时）；不通则**只保留本地 commit**，后续全部跳过 | `ssh -o BatchMode=yes -o ConnectTimeout=5 fzh true` |
| 5 | 从 fzh 拷 LFS 对象到本地（只补缺） | `rsync -a --ignore-existing "$FZH/.git/lfs/objects/" "$REPO/.git/lfs/objects/"` |
| 6 | 拉取 fzh 的 main 并合并 | `git fetch fzh main` → `git merge --no-edit --allow-unrelated-histories FETCH_HEAD` |
| 7 | 合并失败则中止并标记冲突，本轮不推 fzh | `git merge --abort`，日志 `MERGE CONFLICT with fzh; aborted` |
| 8 | 合并成功则补齐 LFS 工作区文件 | `git lfs checkout` |
| 9 | 再 rsync 一次 LFS 对象，然后推 fzh | `GIT_LFS_SKIP_PUSH=1 git push fzh main`，最多 2 次，间隔 5s / 10s |
| 10 | 推 origin（GitHub），失败只记日志 | `git push origin main` |

注意第 9 步的 `GIT_LFS_SKIP_PUSH=1`：LFS 大文件不走 push，而是靠 rsync 直接把 `.git/lfs/objects` 拷到 fzh。

## 3. 详细配置

### 脚本

`/home/zihan/.local/bin/upill-autocommit.sh`

关键变量：

```bash
REPO="/media/zihan/Data/linux保存在此/university-pill"
FZH="fzh:/home/fzh/University-pill"
LOG="$HOME/.local/state/upill-autocommit.log"
```

### systemd 服务

`~/.config/systemd/user/upill-autocommit.service`

```ini
[Unit]
Description=Auto commit and push university-pill

[Service]
Type=oneshot
ExecStart=/home/zihan/.local/bin/upill-autocommit.sh
Nice=10
IOSchedulingClass=idle
```

### systemd 定时器

`~/.config/systemd/user/upill-autocommit.timer`

```ini
[Unit]
Description=Run university-pill autocommit every 10 minutes

[Timer]
OnBootSec=3min
OnUnitActiveSec=10min
Persistent=true
Unit=upill-autocommit.service

[Install]
WantedBy=timers.target
```

说明：`OnUnitActiveSec` 是从上一次启动时刻算 10 分钟，属于单调计时；这里的 `Persistent=true` 对单调定时器不起作用（只对 `OnCalendar` 有意义），补跑靠下一轮 `fetch/merge`。

### 仓库配置

| 项 | 值 |
|---|---|
| 分支 | 仅 `main` |
| remote `fzh` | `fzh:/home/fzh/University-pill`（局域网，主） |
| remote `origin` | `git@github.com:ddhh-gif/University-pill.git`（GitHub，备份） |
| LFS | 大 PDF 由 `.gitattributes` 指定，git-lfs 3.4.1 |
| 日志 | `~/.local/state/upill-autocommit.log` |
| 锁 | `<repo>/.git/autocommit.lock`（flock），非锁文件 |
| `.gitignore` | `*.log`、`.DS_Store`、`Thumbs.db`、`*.swp`、`__pycache__/`、`.obsidian/workspace*` 等 |

## 4. 适用条件

- **仅 zihan 本机生效**。fzh 上没有 timer、没有该脚本，只是被动接收 push 和提供 LFS 对象。
- 用户 linger 已开启（`Linger=yes`），未登录时定时器也运行。
- `/media/zihan/Data` 必须已挂载（NTFS，`ntfs3`，`uid=1000,gid=1000`）；未挂载时脚本直接退出。
- 需要到 `fzh` 的免密 SSH：`~/.ssh/config` 里有 `Host fzh`，使用 key 认证（`BatchMode=yes` 不允许交互输入密码）。
- 需要本机具备 `git`、`git-lfs`（≥3.4.1）、`rsync`、`flock`、`ssh`、`timeout`。
- 假设仓库使用 LFS 保存大文件；若新增其他大文件，应先加进 `.gitattributes`，否则会进普通 git 对象，push 体积会暴涨。

## 5. 触发条件

- **自动**：开机 3 分钟后第一次；之后每约 10 分钟一次。
- **手动**：
  ```bash
  systemctl --user start upill-autocommit.service
  ```
- **本轮跳过的情况**：
  - 上一轮还没跑完（flock 拿不到锁）；
  - 仓库里存在 `.git/index.lock`（有别的 git 命令正在执行，例如你正在手工 commit/rebase）；
  - fzh 不可达：只做本地 commit，不 fetch / 不推 fzh（但会尝试推 origin）。
- **没有改动时**：不产生提交，仍然会 fetch/merge fzh 并做两次空 push。

## 6. 已知限制与注意事项

- 提交信息只有时间戳（`auto: 2026-11-27 06:15:29`），看不出改了什么；重要改动请自己写清晰的手工提交信息（下一轮不会再改它）。
- **遇到冲突不自动解决**：直接 `merge --abort` 并写日志，需要人工合并；未解决期间 fzh 不会被推送。
- 使用 merge（`--allow-unrelated-histories`），历史里会出现合并节点，没有 rebase，也**不会 force push**。
- 该机制会**自动把本地所有未被 `.gitignore` 忽略的改动提交并推送到 GitHub**。不要在仓库根目录放临时垃圾文件；需要在本地保留的中间文件请写进 `.gitignore`。
- 新增的 `AGENTS.md` 本身也会在下一轮被 `git add -A` 自动提交。
- 只处理 `main` 分支；在其他分支上的改动不会按预期同步。
- `cd` 失败（盘未挂载）会静默退出，日志里可能只有一次失败记录，注意确认盘是否挂载。
- NTFS 上文件权限/属主由挂载参数决定，`chmod` 无效。

## 7. 运维命令

```bash
systemctl --user status upill-autocommit.timer
systemctl --user list-timers upill-autocommit.timer
systemctl --user cat upill-autocommit.service upill-autocommit.timer
systemctl --user start upill-autocommit.service        # 立即跑一次
journalctl --user -u upill-autocommit.service -n 50    # 服务输出
tail -n 50 ~/.local/state/upill-autocommit.log         # 详细日志
```

修改 unit 文件后需要：

```bash
systemctl --user daemon-reload
systemctl --user restart upill-autocommit.timer
```

只改脚本不需要 daemon-reload。

## 8. 迁移到新机器

1. 复制脚本到 `~/.local/bin/upill-autocommit.sh`（`chmod +x`），修改其中的 `REPO`、`FZH`（以及日志路径）。
2. 复制两个 unit 到 `~/.config/systemd/user/`，同步修改 `ExecStart`。
3. 配好到 fzh 的免密 SSH 和 origin 的 SSH key。
4. 启用：
   ```bash
   systemctl --user daemon-reload
   systemctl --user enable --now upill-autocommit.timer
   loginctl enable-linger "$USER"
   ```
5. 在一台机器上保留定时器即可，**不要两台同时启用**：两边都用 `git add -A` + merge 容易产生反复冲突。
