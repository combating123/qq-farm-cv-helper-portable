# QQFarmCVHelper 交接文档：空地误判回归优先修复

**交接日期：2026-08-01（Asia/Shanghai）**
**源码仓库：`E:\CodexProjects\qq-farm-cv-helper-portable`**
**实际部署目录：`E:\CV农场助手`**
**当前最高优先级：已种满画面被识别为 19 块空地。先修这一项，其他播种、买种、好友巡查问题均暂停在其后。**

---

## 1. 用户刚刚确认的真实问题

用户提供的农场画面中，土地已经全部种满；运行日志却多次出现：

```text
v273 backpack preflight before strategy held self route
reason=seed-panel-not-confirmed:fresh-frame-not-seed-panel
crop=白萝卜 / 灯笼果
empty=19
```

这 **19 块不是实际空地**。它触发了自家农场优先、播种预检、种子面板点击、买种/播种链路，造成了“明明种满却仍持续在自家循环”的回归。

用户对此的验收标准是明确的：

```text
已种满画面
→ 空地数必须为 0
→ 不得触发 home priority / force self cycle
→ 不得点击土地或种子面板
→ 不得播种、买种、施肥
→ 不得因为“未知/假空地”阻断好友轮询
```

不要把日志里写出的“检测到空地”视为事实；用户确认的实际画面才是该回归的真值来源。

---

## 2. 已定位的直接原因（不要重复走错方向）

此前加入了“深色土坑视觉空地回退”。相关函数：

| 文件 | 行号 | 作用 |
|---|---:|---|
| `portable\hook.py` | 4363 | `_qqfarm_visual_empty_land_marker_candidates(frame)` |
| `portable\hook.py` | 4507 | `_wrap_detect_empty_lands_state(fn, name='')` |
| `portable\hook.py` | 3326 | `_qqfarm_empty_land_board_gate(frame, candidates)` |
| `portable\hook.py` | 4216 | `_qqfarm_dedupe_empty_land_candidates(candidates)` |
| `portable\hook.py` | 3602 | `_qqfarm_home_priority_active(context)` |
| `portable\hook.py` | 3615 | `_qqfarm_update_home_priority(context, remaining, ...)` |

`_qqfarm_visual_empty_land_marker_candidates()` 的核心假设是：

```python
# 用深色、带一定饱和度的连通域作为“可能的空地土坑”
dark_marker = (
    (hsv[:, :, 2] <= 105) &
    (hsv[:, :, 1] >= 20)
).astype(np.uint8) * 255
```

这个假设在真实截图中是错的：**已种植的紫色地块同样有深色中心/阴影/纹理**。后续棋盘门和作物覆盖过滤没有充分排除这些误候选。

此前针对“种满”截图直接运行该视觉候选函数时，得到的情况是：

```text
深色候选原始数量：71
棋盘门后仍保留：7
与其它候选合并后的实际运行日志：empty=19
```

结论：**深色中心绝不能单独作为空地的正向证据。**

---

## 3. 真机证据和文件位置

### 用户确认“已种满”的真实截图

```text
E:\CV农场助手\logs\captures\self-no-action-20260801-234452-308-428x800x3-FarmBotCV-process-self-farm.png
```

这张图是此次回归测试的第一基准样本。请保留原文件，不要覆盖。

### 运行日志

```text
E:\CV农场助手\UserData\WindowsProfile\LocalAppData\qq-farm-bot-rev\logs\2026-08-01.log
E:\CV农场助手\logs\hook_runtime_log.txt
```

截至 `2026-08-01 23:49`，主日志还能看到动态 OCR 的真实读数：

```text
当前玩家等级：122（实时识别-OCR）
```

这是“等级不是写死的”的实证。用户此前多次看到自己为 121；两种数值都只能来自实时 OCR 或用户配置的故障回退，绝不允许在代码里固定为 40、125 或任意策略等级。

### 现有错误测试

```text
E:\CodexProjects\qq-farm-cv-helper-portable\tests\test_empty_land_visual_marker_fallback.py
```

该测试目前名称/断言是：

```python
self.assertEqual(20, len(result))
self.assertEqual(20, bot._qqfarm_recent_empty_land_count)
self.assertTrue(namespace["_qqfarm_home_priority_active"](bot))
```

它把 `tests\fixtures\live-empty-board-marker-fallback-20260801.png` 当作“20 块真实空地”样本。用户的真机反馈已证明这种“深色中心=空地”的测试前提不可靠。**不要再把这条测试的通过作为空地识别成功。**

---

## 4. 下一位执行者必须遵守的 TDD 顺序

### 第一步：先做失败的真实回归测试（RED）

把上面的真机截图以副本形式放进仓库的 `tests\fixtures\`，或测试中显式读取该原始路径；测试必须使用该实际截图。

建议新增：

```text
tests\test_empty_land_full_planted_regression.py
```

建议验收断言：

```python
# native detector 可以为空；视觉回退绝不能把“全种满”补成假空地
result = wrapped(bot, full_planted_frame)
assert result == []
assert bot._qqfarm_recent_empty_land_count == 0
assert not _qqfarm_home_priority_active(bot)
assert not getattr(bot, "_qqfarm_force_self_cycle_next", False)
```

还要覆盖与实际流程相同的行为：

```text
全种满 -> 不开种子面板 -> 不触发背包预检点击 -> 不买种 -> 不写“空地 count > 0”
```

**先运行，确认当前版本因“19 块假空地”而失败；失败原因必须是行为不正确，不是测试导入/路径错误。**

### 第二步：最小修复（GREEN）

最小、可信的修复方向：

1. 移除视觉深色土坑候选作为可操作空地的来源，或让该函数在没有真正空地专属正证据时返回空列表。
2. 不要用“更宽的 HSV 阈值”“更多连通域”“更高置信度”继续打补丁；这只会放大同类误判。
3. 只有下列正证据之一存在时才允许把土地作为可操作空地：
   - 已验证的空地专属模板；
   - 经过可信 OCR/状态识别确认的“空地”；
   - 已由真实样本证明能够区分未种地块和紫色已种地块的结构特征。
4. 证据不足时状态为“未知”，不触发点击、播种、买种或施肥；同样不以未知状态锁死在自家农场。
5. 清除本轮由假候选写入的 `recent/stable/home pending` 状态，防止旧坐标在之后帧继续驱动动作。

### 第三步：双向真实样本验证

“全种满=0”通过后，仍不能宣称空地算法完成。还需要第二种**由用户确认确实存在空地**的截图：

```text
样本 A：全种满 -> 0，零误触发
样本 B：真实空地 -> 只识别真实空地，不混入已种地块
```

在样本 B 尚未可信前，宁可输出“未知”，不要回退到深色中心推测。

### 第四步：恢复下游链路测试

只有空地定位可信后，再调试：

| 文件 | 行号 | 问题 |
|---|---:|---|
| `portable\hook.py` | 7091 | `_qqfarm_open_seed_panel_for_backpack_preflight()` 当前常见 `fresh-frame-not-seed-panel` |
| `portable\hook.py` | 7246 | `_wrap_planting_flow_fast()` 需要只接收可信空地候选 |

请避免在假空地坐标上调试“为什么种子面板打不开”。上游候选错了，点击失败是必然结果。

---

## 5. 用户确认的长期行为要求（不要回退）

### A. 播种优先级

1. **背包可播种子优先级最高**；开启 `backpack_seed_priority = True` 时，先扫描/播背包种子。
2. 背包存在可播种子时，不得先种每日白萝卜、等级作物，也不得进商店买种。
3. 普通化肥、道具、四宫格/特殊种子不能被当作普通种子；施肥只在新帧确认播种真实成功后执行。
4. 播种成功以“新帧中可信空地数下降/该地块状态改变”为准；鼠标拖拽发送成功不等于种植成功。
5. 不要买了白萝卜/等级作物后结束本轮而留下空地；买种后必须回到已确认的真实空地完成播种，或记录明确失败原因。

### B. 农场优先级与好友

1. 自家存在**确认的真实空地**时，自家优先，先收获、种满、确认施肥，再去好友。
2. 自家全种满或空地证据不可信时，不得用假空地/未知状态无限阻断好友任务。
3. 好友护主/轮询要继续可运行；已有其它用户反馈“不会点好友巡视”，这也是待验证项。

### C. 等级与配置

1. 玩家等级必须动态 OCR；用户配置 `player_level = 121` 只作为 OCR 失败的故障回退。
2. 绝不将策略等级固定为 40、125、天山雪莲等。
3. 不改写、不重置用户设置，尤其是：

```ini
enable_rest_window = False
enable_periodic_restart = False
backpack_seed_priority = True
enable_daily_radish_exp = True
player_level = 121
```

4. 配置路径：

```text
E:\CV农场助手\UserData\WindowsProfile\LocalAppData\qq-farm-bot-rev\config-multi.ini
```

此前部署前后观察到该配置 SHA-256 为：

```text
6E5DC95D3D3BCB3AF84EF8094007B48C4A6670B4369C5369C0010A0ADC350AC8
```

### D. 每日任务

每日分享、每日福利、每日任务以**北京时间**持久去重：

```text
成功一次 -> 持久记录 -> 同日不再重复分享/领取
未成功 -> 不记成功；下轮可重试
红点存在 -> 需尝试领取并记录结果
```

用户曾观察到“分享成功后仍连续分享多次”，这仍是未完成项；可回查 7 月 29 日和 7 月 31 日日志。

### E. 启动与便携部署

1. 资源、日志、构建产物尽量放在 E 盘，便于 GitHub 更新。
2. 用户期望双击一键启动，当前涉及：

```text
E:\CV农场助手\QQFarmCVHelper.exe
E:\CV农场助手\launcher.ps1
E:\CodexProjects\qq-farm-cv-helper-portable\portable\StartFarmAssistant.vbs
```

3. 过去出现过 VBS/LNK 闪退、界面“开始运行”无反应、不拉起 QQ 小程序、加载页过快消失；不要因为修空地而覆盖这一链路。

---

## 6. 当前源码/部署一致性与保护边界

当前源 Hook 与部署 Hook 是同一版本（做任何修改前请重新核对）：

```text
E:\CodexProjects\qq-farm-cv-helper-portable\portable\hook.py
E:\CV农场助手\hook.py
```

以下路径属于用户运行数据，禁止清理、覆盖或以“恢复默认”为理由改写：

```text
E:\CV农场助手\UserData
E:\CV农场助手\logs
E:\CV农场助手\backups
```

已有部署备份示例：

```text
E:\CV农场助手\backups\hook-20260801-233835.py
```

仓库有大量未提交改动。严格禁止：

```text
git reset --hard
git clean -fd
```

也不要把默认 `config-multi.ini` 覆盖到用户配置路径。

---

## 7. 已做但未构成真机验收的工作

这些是已有基础，不代表本次问题完成：

- 动态等级 OCR 在真实日志中读到过 `122`。
- 配置未被上次部署重置，曾比对到相同 SHA-256。
- 自家确认空地优先、背包优先硬门、化肥过滤、播种后新帧确认等代码均已存在。
- 之前有一轮本地测试显示 `Ran 54 tests ... OK`。

**关键提醒：上述测试通过未覆盖“全种满却报 19 空地”的真实截图，因此不能作为成功证据。**

---

## 8. 其它已知问题清单（空地回归之后再做）

| 优先级 | 问题 | 证据/现象 |
|---:|---|---|
| P0 | 全种满报 19 块空地 | 本文的主要回归 |
| P1 | 背包优先未真正种背包种子 | 常见 `fresh-frame-not-seed-panel`，随后走白萝卜/等级作物/商店 |
| P1 | 真实空地识别慢、误判、种不满 | 有图中四块空地被逐块 OCR 判为非空地 |
| P1 | 商店目标作物 OCR 命中后点击错位 | 天山雪莲反复命中、未弹购买窗、回扫循环 |
| P1 | 施肥流程报“已施肥”后又“未检测到普通化肥” | 化肥和种子动作/记录需分离 |
| P1 | 分享成功后重复分享 | 同日持久化去重/失败重试边界需修 |
| P2 | 好友巡视不点击/轮询不稳定 | 其它用户反馈 |
| P2 | 启动项/开始运行按钮及小程序拉起不稳定 | VBS/LNK/界面操作历史问题 |

---

## 9. 推荐给下一段对话的首条指令

可直接粘贴：

```text
请接手 E:\CodexProjects\qq-farm-cv-helper-portable。
先阅读 HANDOFF_2026-08-01_EMPTY_LAND_REGRESSION.md，严格按 TDD 修复。
当前 P0：用户确认 E:\CV农场助手\logs\captures\self-no-action-20260801-234452-308-428x800x3-FarmBotCV-process-self-farm.png 的地块已全部种满，但 hook 报 empty=19。
先写并运行“全种满=0、不得触发自家优先/播种/买种”的失败回归测试；不准继续用深色中心作为空地依据；不覆盖 UserData、logs、backups 或 config-multi.ini；不执行 git reset --hard / git clean -fd。
在真实种满截图和真实空地截图双向验证前，不要声称修复完成，也不要部署新的空地判断。
```

---

## 10. 交接时的沟通标准

用户已经反复遇到“日志显示验证通过，但真机行为仍错”。后续报告请只陈述可复现事实：

- 使用了哪一张截图；
- 测试执行命令与结果；
- 真机日志中是否仍有 `empty=19`；
- 是否实际点击了不该点击的土地/商店；
- 配置文件哈希是否保持不变。

不要把“离线单元测试通过”“代码看起来合理”“发出了拖拽事件”表述成“已修好”。

## 2026-09-23 19:20 +0800 — v1.4.97 RED/GREEN：保留好友转场待确认状态

- 目标：停止生产环境中停留自家农场、重新打开好友列表并反复点击第 0 行的循环。
- 现场证据：`E:\CV农场助手\logs\hook_runtime_log.txt` 反复出现 `v489 ... dispatch result=visited rows=5`，随后出现 `v499 visible self surface released stale friend route`、`rows=0`、自家入口恢复和再次 `v203 ... cursor=0/5`。
- 根因：`_qqfarm_reconcile_visible_self_surface()` 把好友列表行点击后的短暂加载/非农场捕获帧误当成自家农场，清除了 `_qqfarm_friend_entry_pending`、好友游标和有效好友列表路由。
- RED：新增 `tests/test_v537_friend_transition_grace_20260923.py`，初次运行因 reconciler 返回 `True` 并清理路由而失败。
- GREEN：增加 v537 有界转场宽限（基于现有 entry timeout，12–30 秒），转场期间保留好友游标和 `friend-list` 场景；原有 run-cycle 超时和重试链路继续负责真正失败的点击。
- 聚焦验证：v537、v533、v536、v422、动态 QQ surface 路由、点击几何、点击确认和 alias bridge 共 35 项测试通过。
- 版本标记：1.4.97；本检查点尚未部署。
- 下一步：执行新鲜语法/diff/聚焦验证，创建部署备份，仅复制预期 Hook/文档/测试文件，隐藏重启后检查新日志是否出现 v537 且不再立即出现 v499 释放和 cursor=0 循环。

---

---

## 11. 续作状态（2026-08-02，周日）

> 时间说明：本机时间 `2026-08-02`（周日）正确，本轮没有调整 Windows 系统时间。此前把交接文档日期 `2026-08-01` 误当成当前日期的判断已经撤销；每日任务问题与日期偏差无关。

### 已完成并部署

- `task_entry` 点击后的默认等待已由 `0.450s` 调整为 `1.200s`；`share_entry` 仍保持 `0.450s`。
- 好友 `friend_guard_list` 已改为按当前可见好友顺序继续巡查，不再因首位好友稳定无动作而直接结束整轮。
- 已补边界回归：起始 `cursor=2`、`visible_count=4` 时只允许再移动一次，不越过最后一位好友。
- 最终完整回归：`Ran 698 tests in 209.973s`，`OK`。
- 源码与部署 Hook SHA-256 一致：
  `E379FC5D79A42E63F4559DDD334447FA34756E1313DA5840EF44AA89E8CF9A4B`
- 配置 SHA-256 保持：
  `6E5DC95D3D3BCB3AF84EF8094007B48C4A6670B4369C5369C0010A0ADC350AC8`
- 部署回滚备份：
  `E:\CV农场助手\backups\hook-before-task1200-v277-deploy.py`
- 当前运行进程：PID `7632`，窗口标题 `QQ经典农场 - 视觉自动化`，响应正常。

### 新版现场证据

好友从第一行进入，并继续向后巡查：

```text
v203 friend list visit row=(365, 289) cursor=0/5
v277 ordered friend patrol continuing after empty first friend cursor=1/5
v277 ordered friend patrol continuing after no-action cursor=2/5
v277 ordered friend patrol continuing after no-action cursor=3/5
v203 friend list cursor advanced by carousel moves=3 cursor=4/5
v85 friend continuation summary moves=3 actions=1 ...
```

这已证明“首位无动作后整轮立即结束”的问题不再复现；仍需再观察一次完整可见列表终点，以确认第五位结束边界在真机上与测试一致。

新版会话统计：

```text
empty=19: 0
v277: 3
运行时异常: 0
```

### 尚未闭环

1. **每日任务真机重试**：新版已加载，但当前仍是 `task=pending`，原因 `entry-red-dot-still-present`；尚未出现新版 `waiting 1.200s` 与 `task_prompt detected` 的完整现场链路。
2. **真实空地正向样本**：当前 `2026-08-02` 真机画面已经出现大量真实空地，但 Hook 只识别到 1 块，正在以该截图建立新的 P0 回归。
3. **真实空地＋背包有种子**：自动测试已覆盖背包优先和商店硬门，真机仍卡在 `fresh-frame-not-seed-panel`，需要修复面板确认和长循环。
4. **完整好友终点**：已从第一位继续到后续好友，仍需一轮完整 5 位可见列表终点日志。
5. **跨自然周期**：需要覆盖成熟→收获→识别空地→背包播种→无种才买种，以及下一次每日重置。

### 剩余工期估算

- 每日任务调度链继续诊断、修复、回归与重新部署：约 `3–6 小时`。
- 真实空地、背包种子和好友列表终点现场验收：场景及时出现时约 `6–12 小时`。
- 接近“完美稳定版”的完整自然周期观察：约 `24–48 小时`；若真实空地/背包场景修复后仍需追加真机轮次，按 `48–72 小时` 预留。


---

## 12. 续作状态（2026-08-02 17:32，候选 v288）

> 日期再次确认：本机与任务环境均为 `2026-08-02`（周日，Asia/Shanghai）；本轮未改动系统时间。

### v286：已命名背包种子不再只阻断后空转

真实缺陷在 `_wrap_planting_flow_fast()`：已有新鲜、已命名的普通背包种子时，旧逻辑只设置“不准购买/继续自家”的硬门并立即 `return False`，没有继续进入背包播种执行器。这会形成：

```text
发现背包种子
→ 阻断白萝卜/等级策略
→ 下一轮仍发现同一快照
→ 再次阻断并轮询
```

现在改为：

```text
发现新鲜已命名背包种子
→ 保持商店硬门
→ 点击可信空地并确认种子面板
→ 立即调用 _run_backpack_seed_priority_planting
→ 只有新鲜可见扫描明确无种子后，才放行一次白萝卜/等级策略
```

新增回归：

```text
tests/test_bound_planting_backpack_priority_regression.py
  test_bound_daily_radish_executes_confirmed_other_backpack_seed_before_strategy
```

该用例明确覆盖：

- `enable_daily_radish_exp=True`；
- `backpack_seed_priority=True`；
- 背包存在其它普通种子“玉米”；
- 必须先打开面板并调用背包执行器；
- 不得调用每日白萝卜原生策略；
- 不得先走商店或策略种子模板。

TDD 证据：新增用例先得到 `FAIL: result False is not true`，删除提前返回、继续进入背包预检后转为 `OK`。

### v287/v288：每日任务真实成功被后续失败覆盖

2026-08-02 原生日志已经给出两次成功证据：

```text
00:56:18 检测到 task_prompt
00:56:20 每日任务领取执行完成，记录日期：2026-08-02

01:07:35 检测到 task_prompt
01:07:37 每日任务领取执行完成，记录日期：2026-08-02
```

但随后又发生三次入口误开/弹窗缺失：

```text
01:24:46 未检测到 task_prompt，重试 1/3
01:34:59 未检测到 task_prompt，重试 2/3
01:45:20 未检测到 task_prompt，重试 3/3
```

这三次失败把已经完成的任务覆盖成：

```json
"task": {
  "status": "pending",
  "reason": "entry-red-dot-still-present"
}
```

修复内容：

1. 新增 `_daily_task_native_log_paths()`，只读取当天原生日志；
2. `_daily_task_authoritative_success_today()` 识别精确完成证据：
   `每日任务领取执行完成，记录日期：YYYY-MM-DD`；
3. 命中后写入权威持久状态：
   `success / verified-native-task-log-v1`；
4. `_patch_daily_flow_status_loaded()` 在模块补丁加载阶段主动对账，绕过原生 `3/3` 外层调度门，避免“因为重试已耗尽，所以永远没有机会执行恢复函数”。

新增回归：

```text
test_native_task_success_log_recovers_pending_status_after_late_prompt_misses
test_loaded_daily_patch_reconciles_native_task_log_before_scheduler_gate
```

两项均先 RED 后 GREEN。

部署 v288 后，真实状态文件已自动恢复为：

```json
"task": {
  "date": "2026-08-02",
  "reason": "verified-native-task-log-v1",
  "status": "success",
  "verified_at": "2026-08-02T16:37:47+0800"
}
```

截至 `2026-08-02 17:32`，原生日志仍持续写入其它农场业务，但最后一条每日任务尝试仍停留在 `01:45:20`；v288 启动后没有再次点击或重复领取每日任务。

### 最终回归（最终源码，730 项全部覆盖）

单个 `unittest discover` 在 20 分钟执行时限内跑到约 550 个成功用例后被外层超时终止，日志中没有 FAIL/ERROR。随后按模块完整分块重跑最终源码，覆盖全部 `730` 个测试：

```text
背包/播种优先：             Ran 52 tests  OK
每日状态：                  Ran 38 tests  OK
每日可见性/空地/好友小模块： Ran 70 tests  OK
好友主回归：                Ran 312 tests OK
自家空地/Hook/完整性：       Ran 88 tests  OK
启动器：                    Ran 20 tests  OK
等级/启动/分享/VIP 等：      Ran 150 tests OK
                              ----------------
合计：                       730 tests，全部 OK
```

此外最终源码重新执行：

```text
python -m py_compile portable/hook.py ...    OK
git diff --check                            OK
```

仅有仓库既有 LF/CRLF 提示，无语法或空白错误。

### 当前部署与保护证据

当前进程：

```text
PID 29208
启动时间 2026-08-02 16:37:40
Responding=True
```

源码与部署 Hook 完全一致：

```text
E:\CodexProjects\qq-farm-cv-helper-portable\portable\hook.py
E:\CV农场助手\hook.py
SHA-256 = 4D73233AD4DC693DC659C6F8C81FE832CA9F6D18783C7C41897C88442A10DC7A
```

用户配置保持未变：

```text
E:\CV农场助手\UserData\WindowsProfile\LocalAppData\qq-farm-bot-rev\config-multi.ini
SHA-256 = 6E5DC95D3D3BCB3AF84EF8094007B48C4A6670B4369C5369C0010A0ADC350AC8
```

新增回滚备份：

```text
E:\CV农场助手\backups\hook-before-confirmed-seed-consume-v286-20260802-161828.py
E:\CV农场助手\backups\hook-before-native-task-log-recovery-v287-20260802-163147.py
E:\CV农场助手\backups\hook-before-startup-task-log-reconcile-v288-20260802-163659.py
```

### 仍需自然场景闭环

当前最新自家画面：

```text
E:\CV农场助手\logs\captures\self-no-action-20260802-163146-367-428x800x3-FarmBotCV-process-self-farm.png
```

肉眼与检测结果均为全部土地已种植，没有真实空地。因此 v286 的“已有其它背包种子立即播种”已经完成代码、回归和部署验证，但还缺下一次真实空地出现后的现场闭环：

```text
成熟/收获
→ 识别真实空地
→ 打开种子面板
→ 优先消耗其它背包种子
→ 空地数量下降
→ 不进入白萝卜/等级作物商店
```

还需观察 `2026-08-03` 的每日重置：任务应只执行一次，成功后同日保持硬门。

### 剩余时间估算

- 代码级候选 v288 与 730 项回归：已完成；
- 下一次真实空地＋背包种子现场闭环：场景出现后约 `1–3 小时`；
- 2026-08-03 每日任务重置验收：约 `1 个自然日`；
- 接近稳定发布版的成熟→收获→播种→好友→次日任务完整观察：建议继续 `24–48 小时`；保守缓冲 `48–72 小时`。

因此当前可称为“v288 高置信候选版”，尚不把缺少自然周期现场证据的状态写成“完美版完成”。

---

## 13. 续作状态（2026-08-02，最终候选 v296）

> 日期固定为 `2026-08-02`（周日，Asia/Shanghai）。交接文件名中的 `2026-08-01` 只代表首次交接日期，不代表当前日期；本轮未调整系统时间。

### v289–v291：全种满必须在原生等级作物流程之前结束

连续三版把“已种满仍进入白萝卜/等级作物长流程”的入口封死：

1. **v289**：已确认全种满时，直接短路原生播种策略；
2. **v290**：每次策略调用前都以当前帧刷新空地，不再只依赖旧缓存；
3. **v291**：在打包运行结构中，从原生播种函数的 `__globals__` 解析真实 `_detect_empty_lands`，解决检测器不在 bot 实例上的情况。

现场已出现：

```text
v275 refreshed empty lands before backpack strategy preflight ... empty=0
v291 confirmed full board skipped native planting strategy
v232 bounded planting flow = 0
```

因此全种满画面不再进入原生白萝卜/等级作物长播种流程。

### v292–v295：所有缺少裸地正证据的候选都必须复核并隔离

#### v292

新增：

```text
_qqfarm_filter_quarantined_empty_lands
_qqfarm_quarantine_empty_land_candidate
```

候选点击后若种子面板未得到证明，会调用真实土地标签 OCR；标签判定不是空地时清理 recent/stable/raw 缓存并隔离该中心。

#### v293

现场证明假候选可能同时满足：

```text
crop_cover=none
rejected=[]
```

所以待复核规则不再依赖 `rejected_centers`：**任何缺少 `_qqfarm_visual_soil_proof` 的候选都必须经过真实标签复核。**

#### v294

现场又证明“假种子条可见”会错误放行已种植地块，因此增加两层硬门：

1. 种子条检测为真也不能替代裸地证据；
2. v258/v197 标签快捷路径只允许带 `_qqfarm_visual_soil_proof` 的候选预确认；其余候选必须调用原生标签 OCR。

真实日志曾完整触发：

```text
v292 pending-review empty-land candidate quarantined center=(213,437)
reason=native-label-rejected
v292 pending-review seed-panel miss quarantined
v273 ... seed-panel-not-confirmed:pending-review-label-rejected
```

#### v295

真实 OCR、好友巡检和慢轮询可能超过旧 `120s` 隔离期，导致同一假中心过期后再次被点。默认隔离现为：

```text
empty_land_false_positive_quarantine_seconds = 900.0
范围：120–1800 秒
```

若后续帧重新出现独立 `_qqfarm_visual_soil_proof`，会立即解除隔离，不会用 900 秒阻塞真实裸地。

### v296：枯萎土地不再停在“已枯萎，待铲除！”

真实夹具：

```text
E:\CodexProjects\qq-farm-cv-helper-portable\tests\fixtures\live-withered-home-20260802.png
SHA-256 = 77375C6C536E41D881F49CC32D20AA364F26A042B3A396FFA437BB2F167FADB6
```

旧现场行为：

```text
画面明确显示：已枯萎，待铲除！
process_self_farm result=False
self-no-action
candidates=[]
```

v296 新增：

```text
_qqfarm_load_withered_action_templates
_qqfarm_detect_withered_shovel_action
_qqfarm_try_clear_withered_land
```

识别和执行链：

```text
枯萎标签模板 + 铲子按钮模板同时命中
→ 校验二者空间关系
→ 点击真实铲子中心
→ 获取新帧
→ 立即重新执行空地检测
→ 识别到空地时锁定自家优先并直接调用 handle_home_planting(trigger_source='harvest')
→ 进入既有背包种子优先链
```

若铲除动画后的第一帧暂时检测为零，不把它当作“全种满”；而是设置：

```text
_qqfarm_home_empty_land_pending = True
_qqfarm_home_visual_recheck_required = True
_qqfarm_force_self_cycle_next = True
```

等待下一帧复检，避免刚铲除就错误释放自家路线。

新增生产模板：

```text
portable\withered_land_label.png
SHA-256 = CED389DAF4C07CA5CD7D0C816ADE3CF9CC47A5C547320434EF7E9000EB2476C3

portable\withered_shovel_button.png
SHA-256 = C9FFBE2553C0F24160A6EF109A06AFE0E2CDA289D61530F7796967C9B73972A2
```

新增回归：

```text
tests\test_withered_land_recovery.py
```

覆盖五项：

1. 真实枯萎夹具同时命中标签和铲子；
2. 全种满、普通土地面板、种子面板、成熟画面均不误触发；
3. 428×800 与按比例放大帧都能映射到正确点击坐标；
4. 点击后立即复检空地并调用自家播种入口；
5. 铲除动画后首帧暂时为零时保持自家复检锁。

TDD 已实际观察 RED：三个新函数不存在、原生 `False` 不会转入铲除恢复、首个零检测错误调用了 full-board 更新；完成生产代码后全部转为 GREEN。

### 最终自动验证

最终源码执行：

```text
python -m unittest discover -s tests -p "test*.py" -v
Ran 744 tests in 365.856s
OK
```

定向空地/背包/枯萎/自家链：

```text
Ran 94 tests
OK
```

同时完成：

```text
python -m py_compile portable\hook.py tests\test_withered_land_recovery.py  OK
git diff --check                                                   OK
portable\hook.py：无 UTF-8 BOM、无 NUL
```

完整回归日志：

```text
E:\CodexProjects\qq-farm-cv-helper-portable\.analysis\full-unittest-v296-20260802.log
```

### 当前部署

源码与部署 Hook 一致：

```text
E:\CodexProjects\qq-farm-cv-helper-portable\portable\hook.py
E:\CV农场助手\hook.py
SHA-256 = 9A591BA7C32B470151CF615985CB4056A5F807E39912339DDC641B47DB396FC1
bytes = 1274951
```

运行身份日志已证明加载：

```text
hook-runtime-identity path=E:\CV农场助手\hook.py bytes=1274951
```

当前运行进程：

```text
PID 23768
Responding=True
窗口标题：QQ经典农场 - 视觉自动化
```

部署前 v295 回滚副本：

```text
E:\CV农场助手\backups\hook-before-withered-recovery-v296-20260802-final.py
SHA-256 = 8474FD1B068959AE61FB7906640263A0FB69E5E059645E0E1A17982F370ABCAB
```

用户配置仍保持：

```text
E:\CV农场助手\UserData\WindowsProfile\LocalAppData\qq-farm-bot-rev\config-multi.ini
SHA-256 = 6E5DC95D3D3BCB3AF84EF8094007B48C4A6670B4369C5369C0010A0ADC350AC8
```

### 现场边界

v296 启动后当前自家画面已经是正常已种植作物，没有再次出现枯萎标签，因此现场已证明：

- 新 Hook、两张模板和运行进程均已加载；
- 正常已种植画面不会误触发 v296 铲子点击；
- 全部 744 项自动回归通过。

仍待下一次真实枯萎场景补齐日志：

```text
v296 withered shovel clicked
v296 withered post-clear empty-land recheck remaining=N
v296 withered post-clear planting invoked ...
```

### 继续任务的优先顺序

1. **观察下一次真实枯萎场景**：确认只点击一次、生成真实空地并进入背包种子优先链；
2. **真实空地＋其它背包种子闭环**：确认先用背包普通种子，空地下降，并且没有商店/等级作物购买；
3. **v295 慢周期隔离现场复现**：出现无裸地证据候选时确认 `ttl=900.0s` 且同中心 10–15 分钟内不再点击；
4. **好友完整巡检**：继续核验从第一位好友到列表终点的一键务农/收获顺序，特别留意当前好友“帮忙”按钮不消失时的重复点击；
5. **下一自然日每日任务**：核验前一天 success 不阻断新一天，任务/分享成功后同日只执行一次。

### 剩余时间评估

- v296 代码、回归、部署：已完成；
- 下一次枯萎或真实空地场景出现后完成单场景现场闭环：约 `1–3 小时`；
- 好友终点、900 秒隔离和背包播种三项现场复核：约 `6–12 小时`（取决于场景出现速度）；
- 下一自然日每日任务/分享重置：最早需等到 `2026-08-03`；
- 接近“完美稳定版”的完整自然周期观察：建议 `24–48 小时`，保守预留 `48–72 小时`。

当前准确结论：**v296 是已部署、744 项回归通过的高置信候选；枯萎恢复已经完成代码和真实夹具闭环，剩余的是下一次自然场景现场触发与跨日验证。**

## 14. 2026-08-02 续接：v297 / v298 好友“帮忙”重复点击修复

### 日期基准

当前日期固定按：

~~~text
2026-08-02，周日，Asia/Shanghai
~~~

运行状态文件和日志中出现的 2026-08-03 视为未来日期异常样本，不据此改动系统时间，也不允许它阻断 2026-08-02 的任务判断。

### v297：慢巡检期间保持未消失按钮抑制

旧逻辑只抑制 15 秒：

~~~python
_qqfarm_friend_help_visual_unresolved_until = now_ts + 15.0
~~~

真实慢巡检超过 15 秒后，同一卡片会再次通过 v229 门控并重复三连点。v297 增加配置：

~~~text
friend_help_unresolved_suppression_seconds = 300.0
有效范围 30–1800 秒
~~~

### v298：按护主模板身份保存独立 TTL

carousel 几何只是槽位：同一好友会换槽，不同好友会复用同一槽。v298 将护主模板组归一为好友身份：

~~~text
guard_20260729_011519_01.png
...
guard_20260729_011519_05.png
→ identity = guard_20260729_011519
~~~

行为：

~~~text
同一好友换槽位       → 保持 TTL
不同好友复用同一槽位 → 立即允许
A → B → A            → A、B 条目分别保留
按钮真实消失         → 只清除当前好友条目
无模板身份           → 回退 carousel 几何键
抑制日志             → 10 秒节流
~~~

新增测试：

~~~text
tests\test_friend_help_unresolved_suppression.py
~~~

v298 自动验证：

~~~text
好友链定向：343 项通过
完整回归：750 项通过
python -m py_compile：通过
git diff --check：通过
portable\hook.py：无 BOM、无 NUL
~~~

v298 部署哈希：

~~~text
源码与部署 hook.py
bytes = 1249403
SHA-256 = 0A64E4EE12D188B2ADE0E3480BA716BC6650BE388DB4C0DA26E5BACF8E97EA48
~~~

v298 真机观察：4 个不同好友身份各只建立 1 次 unresolved，重复 identity 为 0；另有 3 次按钮真实消失并确认成功。第一张选中卡为 (24,119,680,759)，之后才进入下一张，证明本轮从 carousel 第一张开始。

v295 假空地隔离真机已出现：

~~~text
v275 ... empty=1 center=(278,468)
v292 pending-review empty-land candidate quarantined center=(278, 468) ttl=900.0s
v292 pending-review candidate resolved full board; skip repeat preflight and native strategy
~~~

同一中心在连续观察期内只隔离一次、没有再次动作；仍等待一次明确的 quarantined empty-land candidate filtered 正向日志补强。

## 15. 2026-08-02 续接：v299 好友列表最后一位闭环

### 根因

真实巡检出现：

~~~text
v203 friend list visit ... cursor=0/5
v207 friend list confirmed cursor pending=0 next=1
v203 friend list cursor advanced by carousel moves=3 cursor=4/5
v85 ... exhausted=True reason=initial-friend-no-action
v108 friend carousel exhausted; returning home immediately
v249 friend guard stable empty round locked
~~~

cursor=4/5 表示第 5 行仍未通过列表入口确认。旧逻辑返回首页后无条件进入稳定空巡检锁，并且好友列表重开时会把非 pending cursor 重置为 0，因此最后一行缺少确定性闭环。

### TDD：RED → GREEN

第一条 RED：返回首页时 cursor=4/5 仍调用 _friend_guard_schedule_empty_poll：

~~~text
expected schedules=[]
actual schedules=[('visual-empty-friend-returned-home:initial-friend-no-action', 220.0)]
~~~

第二条 RED：好友列表重开后保存的 cursor=4 被旧逻辑重置，实际点击第 1 行 (365,190)，而不是第 5 行 (365,570)。

新增/加强测试：

~~~text
test_visual_watchdog_resumes_unvisited_last_friend_after_returning_home
test_friend_list_handler_resumes_saved_last_row_after_icon_reopen
test_visual_watchdog_skips_deferred_troublemaker_after_verified_empty_friend
~~~

### v299 行为

返回首页且仍有未访问列表行时：

~~~text
保留 _qqfarm_friend_list_visit_cursor=4
设置 _qqfarm_friend_list_pending_cursor=4
设置 _qqfarm_friend_list_resume_pending=True
清除旧 entry 重试时间和计数
保持 chain pending/active=False，允许下一轮从首页重开列表
设置 chain exhausted/allow_home=False，跳过稳定 empty latch
清除 fast-open 时间，允许立即重开好友列表
~~~

好友列表重开后：

~~~text
识别 resume_pending
把“好友图标点击 pending”与“好友行点击 pending”分开
直接选择保存的第 5 行
点击成功后写入 pending_cursor=4 并清除 resume_pending
好友农场确认后由 v207 将 cursor 从 4 提交为 5
~~~

当 cursor=5/5 或没有剩余列表行时，继续保留原有稳定空巡检锁，不重复整轮巡检。

新增运行日志：

~~~text
v299 friend patrol returned home with unvisited friend-list row; resume cursor=4/5
v299 friend list resuming saved cursor=4/5 after icon reopen
v207 friend list confirmed cursor pending=4 next=5
~~~

### 自动验证

定向 RED 均已观察，完成代码后 GREEN。最新验证：

~~~text
5 项相邻行为定向测试：通过
好友相关 discover：Ran 354 tests in 86.830s / OK
完整 discover：Ran 752 tests in 177.245s / OK
python -m py_compile portable\hook.py tests\test_friend_empty_return_home_guard.py：通过
git diff --check：通过
portable\hook.py：无 BOM、无 NUL
~~~

验证日志：

~~~text
.analysis\friend-empty-return-home-v299-20260802.log
.analysis\friend-suite-v299-20260802-rerun.log
.analysis\full-unittest-v299-20260802.log
~~~

### 部署状态

源码与部署一致：

~~~text
E:\CodexProjects\qq-farm-cv-helper-portable\portable\hook.py
E:\CV农场助手\hook.py
bytes = 1253400
SHA-256 = 6D18B59541FABCD400BB7176B55D9EB38D1AF31C51D73420186B8397B72B7CA4
~~~

回滚副本：

~~~text
E:\CV农场助手\backups\hook-before-friend-last-row-v299-20260802.py
bytes = 1249403
SHA-256 = 0A64E4EE12D188B2ADE0E3480BA716BC6650BE388DB4C0DA26E5BACF8E97EA48
~~~

用户配置保持字节级不变：

~~~text
E:\CV农场助手\UserData\WindowsProfile\LocalAppData\qq-farm-bot-rev\config-multi.ini
SHA-256 = 6E5DC95D3D3BCB3AF84EF8094007B48C4A6670B4369C5369C0010A0ADC350AC8
~~~

运行进程已加载：

~~~text
PID 10732
Responding=True
MainWindowTitle=QQ经典农场 - 视觉自动化
hook-runtime-identity path=E:\CV农场助手\hook.py bytes=1253400
~~~

### 后续现场验证顺序

1. 等真实好友巡检再次形成 cursor=4/5，收集 v299 两条 resume 日志和 v207 pending=4 next=5；
2. 等 (278,468) 再次被检测，补齐 quarantine filter 正向日志；
3. 等真实枯萎，补齐 v296 铲除、空地复检和播种日志；
4. 等真实空地且背包存在其它种子，确认优先背包种子、空地下降且没有购买等级作物；
5. 继续核验每日任务/分享在当前自然日只执行一次，并在下一自然日正确重置；
6. 当前日期基准继续固定为 2026-08-02。

## 16. 2026-08-02 续接：v300 第一位好友新皮肤与最后一行现场闭环

### 真实第一位好友根因

真实截图：

~~~text
.analysis\live-v299-first-friend-actions.png        642x1200
测试夹具：tests\fixtures\live-first-friend-one-click-steal-20260802.png  428x800
~~~

画面中第一张好友 carousel 卡片已选中，底部中央存在“一键偷菜”，右下存在新版“回家”按钮。旧模板结果为：

~~~text
selected carousel = detected
old home template gray=0.2954 edge=0.0758 matched=False
steal template gray=0.6401 edge=0.2558 matched=False
friend_ui_state=False
~~~

因此好友列表点击第一行后，转场未提交，v207 不出现；第一位好友被当成非好友页，随后可能进入 friend-processor-no-action-no-live-chain 空巡检锁。

### TDD：第一位好友新皮肤

新增 4 个真实截图回归用例，均先观察到 RED：

~~~text
test_live_first_friend_one_click_steal_surface_is_recognized
test_live_first_friend_one_click_steal_button_is_actionable
test_live_first_friend_visual_probe_clicks_steal_before_help
test_live_first_friend_transition_commits_before_native_empty_poll

Ran 4 tests
FAILED (failures=4)
~~~

修复后：

1. 一键偷菜模板阈值调整为 gray>=0.60 且 edge>=0.22；旧目标夹具仍为 0.945/0.633，现有非目标夹具最高灰度约 0.331，保持明显分离；
2. 较软的新皮肤匹配记录 match_mode=current-skin-soft；
3. 新版“回家”图案不匹配旧模板时，selected carousel + 中央一键偷菜作为组合好友页证据，记录 match_mode=selected-carousel+steal-action；
4. 动作顺序继续固定为先 visual.friend_steal_all，再 visual.friend_help_all；
5. 好友行刚点击且真实好友页已出现时，转场立即提交，不进入 native 空轮询。

4 项转为 GREEN，另有 17 项好友页、自家误判和动作模板相邻回归通过。

### v299 现场残余根因与 v300 修复

部署前真实日志已经形成：

~~~text
v203 friend list cursor advanced by carousel moves=4 cursor=4/5
v299 friend patrol returned home with unvisited friend-list row; resume cursor=4/5
~~~

但未立即出现列表重开。现场暴露两个自动测试此前未覆盖的残余条件：

1. 进程早前已有 _qqfarm_friend_guard_empty_latched=True 时，v299 只跳过新建空锁，没有清除旧锁；
2. 返回首页后 bot 缓存帧仍可能是上一好友，_qqfarm_resolve_friend_route_frame 看到 stale frame 为 state=True 就直接返回，未采用当前可见 QQ 首页。

新增 2 个 RED：

~~~text
test_visual_watchdog_resumes_unvisited_last_friend_after_returning_home
    旧 empty latch 仍为 True

test_friend_route_resolver_prefers_visible_home_while_last_row_resume_is_pending
    返回 stale_friend_frame/True，而不是 visible_home_frame/False
~~~

v300 行为：

- 设置最后一行恢复状态时，显式清除旧 empty latch、latch 时间、旧原因和 next-poll 时间；
- _qqfarm_friend_list_resume_pending 或 _qqfarm_friend_entry_pending 期间，可见 QQ 帧优先于 bot 缓存帧；
- 可见帧为首页或好友列表时也会替换 stale 好友帧，而不是只在可见帧仍为好友页时替换；
- 新增运行日志：v300 visible QQ frame replaced stale friend pixels during list-entry/resume transition。

2 项 RED 均已转为 GREEN。

### 最新自动验证

~~~text
真实新皮肤定向：Ran 4 tests / OK
v299 现场残余定向：Ran 2 tests / OK
好友页和自家误判相邻：Ran 17 tests / OK
好友相关 discover：Ran 359 tests in 97.810s / OK
完整 discover：Ran 757 tests in 190.246s / OK
python -m py_compile portable\hook.py tests\test_friend_empty_return_home_guard.py：通过
git diff --check：通过
portable\hook.py：无 BOM、无 NUL
~~~

验证日志：

~~~text
.analysis\friend-suite-v300-20260802.log
.analysis\full-unittest-v300-20260802.log
~~~

### 部署状态

源码与部署一致：

~~~text
E:\CodexProjects\qq-farm-cv-helper-portable\portable\hook.py
E:\CV农场助手\hook.py
bytes = 1257564
SHA-256 = F81B7ECA7D8DAEBE8EB264E0FBE311C697303EC4502A18BAB603029C781BF7B6
~~~

回滚副本：

~~~text
E:\CV农场助手\backups\hook-before-first-friend-skin-v300-20260802.py
bytes = 1253400
SHA-256 = 6D18B59541FABCD400BB7176B55D9EB38D1AF31C51D73420186B8397B72B7CA4
~~~

用户配置保持字节级不变：

~~~text
E:\CV农场助手\UserData\WindowsProfile\LocalAppData\qq-farm-bot-rev\config-multi.ini
SHA-256 = 6E5DC95D3D3BCB3AF84EF8094007B48C4A6670B4369C5369C0010A0ADC350AC8
~~~

运行实例：

~~~text
PID 8168
Responding=True
MainWindowTitle=QQ经典农场 - 视觉自动化
hook-runtime-identity path=E:\CV农场助手\hook.py bytes=1257564
~~~

### v300 真实现场闭环证据

重启后无需手动补最后一行，运行日志已形成完整顺序：

~~~text
v300 visible QQ frame replaced stale friend pixels during list-entry/resume transition state=False
v203 friend list visit row=(365,289) cursor=0/5
v207 friend list confirmed cursor pending=0 next=1
...
v299 friend patrol returned home with unvisited friend-list row; resume cursor=4/5
v300 visible QQ frame replaced stale friend pixels during list-entry/resume transition state=False
v299 friend list resuming saved cursor=4/5 after icon reopen
v203 friend list visit row=(365,667) cursor=4/5
v207 friend list confirmed cursor pending=4 next=5
~~~

这证明：

- 巡检从第一行开始；
- 第一行真实好友页转场已提交；
- cursor=4/5 返回首页后不会被旧空锁截断；
- 第 5 行从好友列表入口得到确定性确认；
- 5/5 完成后进入稳定 empty latch 属于预期终态，不再重复整轮列表。

### 仍需自然现场补证

1. 当前真实第一位好友在 v300 重启后的这一轮显示的是“帮忙”动作；此前截图中的“一键偷菜”已经不再处于可执行状态，因此“一键偷菜”新皮肤目前有真实截图回归与点击链测试，仍等下一次自然出现时补运行日志 v71/visual.friend_steal_all；
2. 等 (278,468) 再次出现，补齐 quarantine filter 正向现场日志；
3. 等真实枯萎，补齐 v296 铲除、空地复检和播种日志；
4. 等真实空地且背包存在其它种子，确认优先背包种子、空地下降且没有购买等级作物；
5. 每日任务与分享继续区分自动回归和自然日现场证据。

## 16. 2026-08-02 续接：v301–v309 空地与背包种子真实闭环

### v301：转场期间可见 QQ 帧覆盖 stale 好友帧

`_qqfarm_resolve_friend_route_frame` 在好友列表进入、最后一行恢复以及 empty-latch 转场期间，将当前可见 QQ 帧设为权威帧。即使 bot 缓存仍保留上一好友页，也不会再让 stale 像素把首页误判为好友页。

运行日志：

~~~text
v301 visible QQ frame replaced stale friend pixels during list-entry/resume/empty-latch transition state=False
~~~

该修复与 v299/v300 的 cursor 恢复共同保证：从第一行开始、返回首页后恢复未访问行、最后一行确认后才提交 5/5。

### v302：好友处理器无动作时保留未访问最后一行

旧路径只有视觉 watchdog 会在 `cursor < count` 时建立恢复状态；好友处理器直接返回无动作时仍可能进入空巡检锁。v302 将同样的恢复语义补到好友处理器包装器：

- 保留 `_qqfarm_friend_list_visit_cursor`；
- 设置 pending cursor 与 resume pending；
- 清除旧 empty latch、旧原因和 next-poll；
- 允许立即重开好友列表；
- 不把未访问的最后一行当成整轮完成。

运行日志：

~~~text
v302 friend processor no-action preserved unvisited friend-list row; resume cursor=4/5
~~~

真实闭环证据：

~~~text
.analysis\live-v302-friend-last-row-closure-20260802.log
v203 friend list visit row=(365,289) cursor=0/5
v207 friend list confirmed cursor pending=0 next=1
v299 friend patrol returned home with unvisited friend-list row; resume cursor=4/5
v299 friend list resuming saved cursor=4/5 after icon reopen
v203 friend list visit row=(365,667) cursor=4/5
v207 friend list confirmed cursor pending=4 next=5
~~~

### v303：背包种子与肥料硬分类

数量徽章只证明槽位内存在物品，不能单独证明它是可播种种子。v303 对背包候选执行三分法：

~~~text
明确种子       → plantable
明确普通/高级肥料 → fertilizer，绝不进入播种拖拽
只有数量徽章   → unconfirmed，交给原生 OCR 再分类
~~~

同时保留候选顺序、缓存肥料与未知候选坐标，并在出现新的可见种子徽章时清除旧的“候选耗尽”快照，避免背包明明有其它种子却回退购买等级作物。相关真实夹具包括：

~~~text
tests\fixtures\live-backpack-seed-panel-five-items-20260802.png
tests\fixtures\live-seed-panel-two-items-20260802.png
~~~

### v304：自家无动作后的视觉空地恢复

原生 `process_self_farm` 返回无动作不再直接结束自家流程。v304 对新鲜自家帧重新执行空地检测；发现空地后：

- 写回最近空地数量、中心和时间；
- 重新武装 home empty-land priority；
- 保持 self branch；
- 让背包种子优先链继续运行。

运行日志：

~~~text
v304 self-no-action visual empty-land recovery count=N centers=[...]
~~~

### v305：播种结果只由新鲜后验帧提交

传输层 click/drag 返回成功不再等同于种植成功。v305 要求动作之后取得新鲜帧并重新检测空地：

~~~text
after < before → 提交视觉播种进度
after == before → 拒绝本次结果并恢复被原生路径提前消耗的业务状态
没有新鲜后验观察 → 不提交成功
~~~

核心日志：

~~~text
v247 planting action visually verified before=... after=... committed=true
v247 planting action rejected: no visual empty-land decrease before=... after=...
v264 restored unverified planting business state attrs=...
~~~

### v306：失败后的单地轮转回退

批量播种没有视觉下降时，v306 进入 `_qqfarm_backpack_single_land_mode`，一次只选择一块空地。失败中心被记录并轮转到下一块，防止同一坏坐标把整轮锁死；最后一块种下后清除单地模式、失败中心和 deferred 计数。

运行日志：

~~~text
v306 single-land backpack retry selected=... original=... failed=...
v306 single-land backpack retry armed after no-progress ...
~~~

### v307：嵌套播种调用也缩窄为单地

部分原生播种入口会在外层已经选出单地后，再从内部重新读取完整空地列表。v307 在嵌套动作边界再次缩窄土地参数，确保一次尝试只作用于所选中心。

运行日志：

~~~text
v307 nested single-land planting selected=(...) original=N name=...
~~~

### v308：单地模式使用短拖拽，不走原生 click-click

新增包装器：

~~~text
_wrap_single_land_seed_drag
运行时挂接：_drag_seed_over_lands
~~~

当 `_qqfarm_backpack_single_land_mode=True` 且只有一块地时，从背包种子中心拖到目标土地，并追加 2px 补拖点；非单地模式保持原生行为。新增并完成 RED → GREEN：

~~~text
test_single_land_mode_uses_short_drag_instead_of_native_click_click
test_single_land_short_drag_keeps_native_behavior_outside_retry_mode
test_single_land_short_drag_is_wired_into_runtime_patching
~~~

现场证明 v308 包装器确实执行，但同时暴露真正坐标根因：

~~~text
start=(68,511)
land=(221,514)
~~~

起点与土地几乎同高，动作拖动的是农场视图，不是下方背包种子。真实种子条数量徽章约在 `y=574`，旧快速检测器却把金土地行识别成：

~~~text
(68,511), (136,511), (204,511), (273,511), (341,511)
~~~

### v309：动态 lower shelf 种子徽章行修复

v309 修改：

~~~text
_seed_panel_strip_visible
_fast_seed_badge_candidates_from_frame
~~~

实现要点：

- 将下方种子条纵向扫描扩展到 `0.742 * frame_height`；
- 独立统计 lower shelf 最佳徽章行；
- 完整下方货架可见时，即使土地高亮得分更高，也不覆盖真实种子行；
- 保留旧版 `y=511` 双物品稀疏面板兼容；
- 保留旧版五物品 `y≈541` 面板兼容；
- 当前下移五物品面板返回 `y≈574`。

新增真实夹具：

~~~text
tests\fixtures\live-backpack-seed-panel-lower-five-items-20260802.png
~~~

新增测试先观察 RED：

~~~text
test_live_lower_five_item_panel_uses_the_badge_row_not_the_land_row
expected y≈574, got [(68,511), ..., (341,511)]
~~~

GREEN 后返回横坐标 `[68,136,204,273,341]`，五个纵坐标均位于 `565～585`，并全部分类为种子。此前误加的 `test_live_five_tiny_sprouts_are_not_actionable_empty_lands` 及其夹具已删除；复核确认所谓“黑点”是金土地空地纹理，这五块确实是真实空地。

### v309 真实现场闭环：空地 5 → 0

部署后形成完整下降链：

~~~text
v247 planting action visually verified before=5 after=4 committed=true
v247 planting action visually verified before=4 after=3 committed=true
v247 planting action rejected: no visual empty-land decrease before=3 after=3
v247 planting action visually verified before=3 after=2 committed=true
v247 planting action visually verified before=2 after=1 committed=true
v247 planting action visually verified before=1 after=0 committed=true
v291 confirmed full board skipped native planting strategy ... empty=0
~~~

证据文件：

~~~text
.analysis\live-v309-empty-land-5-to-0-20260802.log
~~~

这条链证明：

- 五块空地识别正确；
- 背包种子优先在真实运行中生效；
- 种子起点来自真实下方种子条，不再点击土地行；
- 一次失败不会阻断后续地块；
- 最终达到 0 空地；
- 该序列没有出现购买等级作物日志；
- 满地后停止播种并恢复好友流程。

`after=0` 后曾短暂出现一条旧 baseline：

~~~text
v231 home empty-land priority armed remaining=5 reason=backpack-preflight-pending-or-inventory-evidence
~~~

下一次新鲜检测立即得到 `empty=0`，由 v291 满地门控拦截，没有形成重复购买或重复播种。

### v309 自动验证

~~~text
背包/单地专项：Ran 130 tests in 34.684s / OK
完整回归：Ran 773 tests in 194.898s / OK
python -m py_compile：通过
git diff --check：通过
portable\hook.py：无 BOM、无 NUL
~~~

验证日志：

~~~text
.analysis\backpack-single-land-suite-v309-20260802.log
.analysis\full-unittest-v309-20260802.log
~~~

### v309 部署状态

源码与部署一致：

~~~text
E:\CodexProjects\qq-farm-cv-helper-portable\portable\hook.py
E:\CV农场助手\hook.py
bytes = 1304064
SHA-256 = CCD47200BE35761AEE78ED593D0D12D47226F6FC6BD0F516A9E38CFF6AD5681C
~~~

回滚副本：

~~~text
E:\CV农场助手\backups\hook-before-seed-badge-row-v309-20260802.py
bytes = 1302894
SHA-256 = 20CA9638A470921011CBA152243942FCC6AD03B5B714CD3EFE3AED030672A2AF

E:\CV农场助手\backups\hook-before-single-land-drag-v308-20260802.py
bytes = 1290921
SHA-256 = 80E8B4F6A82E0BF59463466BAA61B9E6E526037F5F94FC1BEBE7D381ECA94739
~~~

### 当前剩余自然现场补证

1. 新皮肤“一键偷菜”再次自然出现时，补 `v71/visual.friend_steal_all` 运行日志；
2. 真实枯萎出现时，补 v296 铲除、空地复检、重新播种完整链；
3. 分享与每日任务继续跨自然日观察：每日只完成一次、成功后不重复轮询、下一自然日正确重置；
4. 持续观察满地后不再购买等级作物，也不重复背包播种。

核心种植故障已有真实 5 → 0 闭环；剩余工作主要是自然条件触发的长期证据与后续日志审计。

## 17. 2026-08-02 续接：v310 每日计数原子落盘加固

### 新发现：每日计数镜像存在瞬时文件占用窗口

继续审计运行日志时发现两次：

~~~text
v122 daily metrics counter sync error PermissionError(13, '拒绝访问。')
~~~

原逻辑使用固定临时文件名：

~~~text
daily_counters.json.tmp-v122-PID
~~~

同一进程内并发或相邻同步会复用同一个临时路径；目标 JSON/CSV 被 Windows 短暂占用时，`os.replace` 只尝试一次，失败后删除临时文件并继续。这样虽然当前内存状态仍可运行，但持久化镜像可能滞后，重启后会增加每日任务、分享完成状态或计数恢复不一致的风险。

### TDD：3 项 RED

先新增：

~~~text
test_counter_sync_uses_a_unique_temp_file_for_each_write
test_counter_sync_retries_transient_permission_error
test_csv_sync_retries_transient_permission_error
~~~

观察到的失败分别为：

~~~text
两次强制同步临时路径完全相同
计数 JSON 期望 self_actions_daily_count=7，持久文件仍为 1
统计 CSV 期望出现当天行，实际当天行数量为 0
~~~

RED 日志：

~~~text
.analysis\daily-metrics-unique-temp-red-v310-20260802.log
.analysis\daily-metrics-atomic-retry-red-v310-20260802.log
~~~

### v310 实现

`_daily_metrics_sync_runtime` 现在：

- 每次 JSON/CSV 写入生成独立临时文件名，包含 PID、纳秒 nonce、进程内序号和文件类型；
- 对瞬时 `PermissionError`、Windows `winerror=5/32/33`、`errno=13/16` 执行最多 5 次有界替换；
- 重试间隔为 0.05、0.10、0.20、0.40 秒；
- 非占用类错误以及最终失败仍交回原有清理和错误日志；
- 重试时记录目标路径、类型、次数和错误。

运行日志模板：

~~~text
v310 daily metrics atomic replace retry kind=counter|csv attempt=N/5 path=... error=...
~~~

启动标记：

~~~text
v310 daily metrics unique temp + bounded atomic replace retry enabled
~~~

### v310 验证

~~~text
新增 3 项定向：Ran 3 tests / OK
每日任务、分享、持久状态专项：Ran 144 tests in 46.437s / OK
完整回归：Ran 776 tests in 237.177s / OK
python -m py_compile portable\hook.py tests\test_daily_metrics_sync.py：通过
git diff --check：通过
portable\hook.py：无 BOM、无 NUL
交接文档：replacement=0、questionRunsWhole=0
~~~

验证日志：

~~~text
.analysis\daily-metrics-atomic-retry-green-v310-20260802.log
.analysis\daily-share-suite-v310-20260802.log
.analysis\full-unittest-v310-20260802.log
.analysis\live-v310-startup-and-daily-sync-20260802.log
~~~

### v310 部署状态

源码与部署一致：

~~~text
E:\CodexProjects\qq-farm-cv-helper-portable\portable\hook.py
E:\CV农场助手\hook.py
bytes = 1306616
SHA-256 = D738607570C108C36CAF9ACAC0D3427444B6FA81EF3C01A74FFD06388D0EFA19
~~~

v309 回滚副本：

~~~text
E:\CV农场助手\backups\hook-before-daily-metrics-atomic-retry-v310-20260802.py
bytes = 1304064
SHA-256 = CCD47200BE35761AEE78ED593D0D12D47226F6FC6BD0F516A9E38CFF6AD5681C
~~~

用户配置保持字节级一致：

~~~text
E:\CV农场助手\UserData\WindowsProfile\LocalAppData\qq-farm-bot-rev\config-multi.ini
bytes = 9692
SHA-256 = 6E5DC95D3D3BCB3AF84EF8094007B48C4A6670B4369C5369C0010A0ADC350AC8
~~~

运行实例：

~~~text
PID 8544
Responding=True
MainWindowTitle=QQ经典农场 - 视觉自动化
hook-runtime-identity bytes=1306616
~~~

显式重启后的新日志段已出现 v310 启动标记和正常 `v122 daily metrics synced`；该日志段内：

~~~text
v122 daily metrics counter sync error = 0
v122 daily metrics csv sync error = 0
~~~

没有出现重试日志表示当前启动后尚未再次遇到文件锁；自动测试已确定遇到一次瞬时锁时会完成重试并落盘。

### 继续观察项

1. 跨下一个自然日继续核对分享、每日任务各执行一次并在成功后保持静默；
2. 新皮肤“一键偷菜”自然出现时补真实点击链；
3. 真实枯萎出现时补 v296 铲除、复检和重新播种链；
4. 继续监控满地状态，确认不购买等级作物、不重复背包播种；
5. 若运行日志出现 v310 retry，保存该段作为真实文件占用恢复证据。


## 2026-08-04 13:18:00 +0800 — v323 / QQ 农场维护 Skill 与多代理编排基线

### 固定目标与用户新增要求

- 当前日期按环境：2026-08-04（周二，Asia/Shanghai）。历史日志和旧交接日期仅作为证据。
- 用户固定多代理配置：
  - Terra-ultra：每日分享、每日任务、计数、日期切换和 CSV 镜像；
  - Terra-ultra：好友顺序遍历、漏偷漏帮、重复帮助和末行有界退出；
  - Luna-max：空地、种植、背包种子、购买拦截和性能卡顿；
  - Sol 主控负责拆解、冲突裁决、生产代码集成、部署和最终验证。
- 新截图明确记录长期不变量：**合并会员功能并保留设置**。部署期间必须保留单目录便携形态、UserData、配置、分享目标、计数、模板及本地会员/VIP状态。

### 跨任务上下文整理

- 已从本机 Codex 会话中提取 157 条 QQ 农场相关用户消息，覆盖 2026-07-24 至当前任务；原始提取文件：
  - `E:\CodexProjects\qq-farm-cv-helper-portable\.analysis\qq-farm-user-messages-20260804.md`
- 已将历史需求归纳为每日流程、好友流程、空地与播种、背包优先、性能稳定、会员/设置保留、单目录交付和持续交接八类固定验收条件。

### 新建并验证维护 Skill

- Skill：`E:\CodexData\.codex\skills\qq-farm-cv-maintainer`
- 主要文件：
  - `SKILL.md`
  - `references\project-map.md`
  - `references\conversation-requirements.md`
  - `references\acceptance-checklist.md`
  - `scripts\snapshot_status.ps1`
  - `scripts\append_handoff.py`
  - `assets\merge-membership-preserve-settings.png`
- `quick_validate.py` 结果：`Skill is valid!`
- `snapshot_status.ps1` 已真实执行；首次测试发现 Windows PowerShell 对无 BOM 中文路径误解码，已改为 UTF-8 BOM 并复测，源码与部署路径/哈希均能正确读取。
- `append_handoff.py` 已完成追加烟雾测试。
- 最新状态快照：
  - `E:\CodexProjects\qq-farm-cv-helper-portable\.analysis\skill-status-snapshot-20260804-v3.md`

### v323 补充记录

- 真实现场发现两个活动 `daily_action_stats.csv` 不一致：便携镜像 `friend_help=20`，WindowsProfile/Roaming 镜像仍为 `0`。
- RED：`test_default_csv_sync_updates_configured_and_portable_profile_mirrors` 失败，配置档案 CSV 保持 `0`。
- GREEN：默认同步从活动 `QQFarmCopilot` counter 路径推导 sibling stats CSV，并与便携 CSV 去重同步。
- 专项结果：
  - `tests.test_daily_metrics_sync`：9 tests / OK；
  - 好友帮助与偷取持久计数：8 tests / OK；
  - `py_compile`：通过；
  - `git diff --check`：无空白错误，仅历史 LF/CRLF 提示。
- 部署：
  - 备份：`E:\CV农场助手\backups\v323-stats-csv-mirror-20260803-201150`
  - bytes：`1398396`
  - SHA-256：`396014DD72008D5AFA39F063688311FAB4CE646E8FA2893EE2AA1A32596F84BA`
  - 两个活动 CSV 在启动后均同步为 2026-08-03 `friend_steal=8, friend_help=20`，后续真实帮助动作增长到 `23`。
- 2026-08-03 的 v323 完整回归在运行约 424 秒时被外部终止，日志停在测试中段，因此该次不构成完整通过证据；新鲜完整回归仍在待办。

### 当前生产状态与唯一下一步

- 2026-08-04 13:16 状态快照显示 `QQFarmCVHelper` 当前未运行；持久状态仍为 2026-08-03，尚未产生 2026-08-04 的自然日期切换证据。
- 三个指定模型审计已按用户配置重新启动。
- **下一步：等待三条审计证据，主控选择明确缺口按 RED→GREEN 修复；随后启动部署版，验证 2026-08-04 每日流程自然切换、完整回归和生产性能。**


## 2026-08-04 13:34:17 +08:00 — v324 好友帮助 strong-to-soft 后同卡片禁止二次点击

### 真实缺口

Terra-ultra 好友审计确认：v323 连续运行中，强帮助按钮点击后已经转为软纹理并完成计数，但在当前好友卡片尚未移动前，下一次动作探测仍会对同一软状态再发送一次客户端点击。

真实日志证据：

- 第一组：强转软并计数 `20 -> 21` 后，同一卡片又出现一次软状态点击；
- 第二组：计数到 `23` 后，同一卡片再次发生软状态点击；
- 两组都没有重复计数，但动作投递不是严格一次。

### RED

新增：

`test_strong_to_soft_help_commit_does_not_reclick_same_card_on_next_probe`

首次运行结果：

```text
AssertionError: 1 != 2
Ran 1 test
FAILED (failures=1)
```

证明第一次强转软成功后，紧接着的同卡片探测仍产生第二次点击。

### v324 最小实现

在 `_invoke_friend_guard_help_visual_click()` 中新增“已确认帮助卡片”短期状态：

- 保存当前好友 identity、选中卡片边界和到期时间；
- 帮助按钮消失或 strong -> soft 成功时立即登记；
- 下一次探测若 identity 与 card 都相同且仍在 30 秒窗口内，直接跳过点击；
- 卡片或身份变化时不拦截下一位好友；
- 新启动标记：`v324 friend help committed-card no-reclick enabled`。

### GREEN

```text
定向 RED 测试：Ran 1 test / OK
好友软状态抑制专项：Ran 9 tests / OK
好友帮助/偷取持久计数：Ran 8 tests / OK
python -m py_compile portable\hook.py tests\test_friend_help_unresolved_suppression.py：通过
git diff --check：无空白错误，仅历史 LF/CRLF 提示
```

### 当前边界与下一步

- 本次修复针对真实发生的“同一进程、同一卡片、强转软后的第二次 UI 点击”。
- 跨进程 exactly-once 需要持久化好友身份、pending 动作与游标账本；当前日志没有证明已发生跨进程重复帮助，暂列独立设计风险。
- v324 目前只在源码树，尚未部署。
- **下一步：等待每日流程和种植/性能两条审计完成，主控统一决定其余修复后再合并部署。**


## 2026-08-04 13:40:45 +08:00 — v324 好友专项 373 项通过

### v324 好友专项扩大回归

命令：

```powershell
python -m unittest discover -s tests -p 'test_friend*.py' -v
```

结果：

```text
Ran 373 tests in 335.603s
OK
```

日志：

`E:\CodexProjects\qq-farm-cv-helper-portable\.analysis\friend-suite-v324-20260804.log`

该结果覆盖首位好友、相邻顺序、末行、有界返回、guard editor、偷取/帮助持久计数以及新增 strong-to-soft 同卡片禁止二次点击。v324 仍未部署，等待另外两条指定模型审计汇总。


## 2026-08-04 13:56:16 +08:00 — v324 完整回归 843 项通过

### v324 新鲜完整回归

命令：

```powershell
python -m unittest discover -s tests -p 'test_*.py' -v
```

结果：

```text
Ran 843 tests in 778.523s
OK
```

日志：

`E:\CodexProjects\qq-farm-cv-helper-portable\.analysis\full-test-v324-20260804.log`

这是 2026-08-04 在 v324 源码上的完整新鲜结果，取代 2026-08-03 被外部终止的 v323 中途日志。部署和自然生产观察仍待另外两条审计收束后执行。


## 2026-08-04 14:05:00 +08:00 — v324 审计全部收束：每日流程三缺口与种植/性能优先级

### Luna-max C 收束证据

- 生产版本仍为 v323；源码为未部署的 v324，源码 SHA-256 `AC65FF6F535F42D09171F071580580D3C44E3BB8D36ED5AFBA6985F0EAA5AF55`，字节 `1400815`。
- P0 性能根因：2026-08-03 原生日志中出现 57 次 `PrintWindow capture timeout`，同一失败轮可能叠加 WGC、可见截图、多个 native owner、PrintWindow、pyautogui 与 deep recover；应补单轮 capture budget 和失败冷却 RED。
- P1 种植性能：满地短路位于空地 detector/marker/crop-cover 重链之后；背包数量徽章未确认时仍会进入原始慢 OCR。应补“fresh 满地零重型调用”和“未确认徽章不进入 native OCR/商店” RED。
- P2 种植正确性：等级 OCR 失效后日志仍记录“等级 0 -> 白萝卜策略”；收获后播种触发依赖精确日志短语，批量收获或返回结构变化存在漏置 planting pending 的组合缺口。
- 已保留事实：满地最终会阻断 native planting strategy；动态等级 pending 已有 `allow_buy=False` 商店保护；CPU 首要嫌疑是捕获/OCR 回退链而不是 affinity/priority。

### 当前生产状态

- `QQFarmCVHelper` 未运行，部署目录仍为 v323。
- 当前环境日期为 **2026-08-04 周二**；持久状态仍停留在 2026-08-03，因此 2026-08-04 自然日期切换、分享与任务尚无现场证据。

### 跨日自动取证已启动

```text
watcher=E:\CodexProjects\qq-farm-cv-helper-portable\.analysis\watch-v345-crossday-20260805.ps1
watcher PID=32208
status=E:\CodexProjects\qq-farm-cv-helper-portable\.analysis\v345-crossday-watch-20260805-to-20260806\status.json
samples=E:\CodexProjects\qq-farm-cv-helper-portable\.analysis\v345-crossday-watch-20260805-to-20260806\samples.jsonl
final=E:\CodexProjects\qq-farm-cv-helper-portable\.analysis\v345-crossday-watch-20260805-to-20260806\final-evidence.json
deadline=2026-08-06 11:30:00 +08:00
```

监视器每 60 秒只读采集一次正式状态，不修改配置或业务文件。它会记录 `2026-08-06 00:00` 自然切日、`00:31` 每日任务窗口和 `09:55` 每日分享窗口。只有分享 exact target/direct-send、奖励、任务、四组关键镜像和双 CSV 全部满足后，才自动执行一次正式隐藏重启，再采样 120 秒并验证零重复分享、进程响应、源/部署/config hash；结果写入 `final-evidence.json`。
### 唯一下一步

先按 Terra-ultra A 的三个每日流程缺口完成严格 RED→GREEN：分享已发送但状态写失败后的跨进程持久 no-replay marker、daily flow 并发合并写、task soft retry 跨业务日期清理；随后再进入 Luna 的捕获与种植修复。


## 2026-08-04 14:18:00 +08:00 — 每日流程 v325 RED→GREEN：跨进程分享防重、并发合并写、task 退避跨日清理

### 症状与根因

1. 分享已经完成 direct-send 四项证明，但主 `daily_flow_status.json` 写盘失败时，pending 只存在进程内；重启后可能再次发送。
2. `_daily_flow_mark_status()` 的 read-modify-write 无锁；task/share 两线程从同一空快照写入会丢失其中一个 flow。
3. `daily_task_retry_state.json` 没有业务日期，2026-08-03 23:59 建立的退避会继续阻断 2026-08-04 00:01 的新日任务。

### RED

新增测试：

- `test_persisted_pending_send_blocks_repeat_after_fresh_namespace`
- `test_concurrent_task_and_share_marks_preserve_both_flows`
- `test_daily_task_soft_retry_from_previous_business_day_is_cleared`

首次合并运行：`Ran 3 tests in 3.047s / FAILED (failures=3)`；失败分别为 fresh namespace 未阻断、最终 JSON 丢失 `task`、前一业务日退避仍返回 active。

### GREEN 实现

- 分享 direct-send 主状态写失败后，在 daily-flow 状态路径旁写入独立 `*.share-direct-pending.json`，包含日期、目标、epoch 时间和完整发送证据；新进程读取 marker，只重试状态持久化，不重开分享 UI；主状态成功后清除 marker。
- `_daily_flow_write_status()` 增加进程内 `RLock`，锁内重读并按同日期合并 `flows`，使用 PID/线程/time_ns/sequence 唯一临时文件；对 Windows sharing/permission 类错误执行 5 次有界重试。
- task soft retry state 增加 `date`；set 时写业务日期，active 时发现日期不是当前日期即清零并放行。

### 新鲜验证

- 三项定向 GREEN：`Ran 3 tests in 3.460s / OK`。
- 每日状态、分享恢复、分享硬门专项：`Ran 78 tests in 71.867s / OK`。
- `py_compile` 通过。
- `git diff --check` 无空白错误，仅历史 LF/CRLF 提示。

### 当前边界与唯一下一步

源码已包含 v324 好友修复和本阶段每日流程修复，尚未部署。下一步按 Luna-max 审计先补捕获失败预算/冷却、满地早短路、背包未确认徽章禁慢 OCR 的 RED→GREEN，再统一编号、完整回归和部署。


## 2026-08-04 14:38:00 +08:00 — v326 RED→GREEN：捕获单轮预算、满地早短路、背包未确认禁慢 OCR、等级与收获状态

### RED 证据

Luna-max C 新增并实际运行以下回归：

- `test_short_window_reuses_failure_cooldown_after_first_native_timeout`：首次 native timeout 后仍依次调用 PrintWindow、pyautogui、deep-recover、screenshot。
- `test_fresh_confirmed_full_board_skips_detector_stack_before_planting_flow`：fresh 满地 latch 下 detector/marker/crop-cover/board-gate 各执行 1 次。
- `test_visible_unconfirmed_badge_skips_native_ocr_and_blocks_shop`：未确认徽章仍进入 native OCR，且未建立 inventory pending/shop block。
- `test_dynamic_level_pending_skips_crop_strategy_and_shop`：level 动态 pending 时 native strategy 仍执行 1 次。
- `test_structured_batch_harvest_success_queues_planting`：结构化批量收获成功未建立 planting quota/pending。

主控另补 `test_top_level_capture_does_not_repeat_visible_probe_inside_patched_owner`，RED 为顶层 capture 和已包装 owner 各调用一次 visible，合计 2 次。

### v326 最小实现

- QQ 捕获单轮只允许一个 native callable；首个 timeout/None 后立即耗尽该轮 budget，12 秒已有 gate 负责短窗口后续调用。
- 去重 capture owner；顶层 `_get_frame_from_bot()` 已占用 native gate 时，owner wrapper 不再重复 WGC/ImageGrab visible probe。
- planting flow 在 fresh confirmed full-board latch 下于 detector stack 前返回，避免 detector、visual marker、crop-cover、board gate、seed panel 和 native strategy。
- 可见背包只有 quantity/unconfirmed 徽章时不进入慢 native OCR；建立 inventory scan pending、unknown hard gate 和 level/shop block。
- 动态等级 pending 且背包优先明确关闭时，保持空地待办并跳过 crop strategy/shop；旧式未声明背包策略的调用仍维持 backpack-only、`allow_buy=False` 兼容路径。
- harvest wrapper 同时接受结构化 `{success: true, action: *harvest*, harvested_count>0}` 证明，批量收获后立即建立 planting quota/pending，同时保留原单个收获日志 token 路径。
- 启动标记：`v326 durable daily, capture-budget, and planting-state fixes enabled`。

### GREEN 与专项验证

- capture budget 定向：`Ran 1 / OK`。
- capture nested owner 定向：`Ran 1 / OK`。
- capture/WGC 专项：`Ran 24 / OK`。
- 满地、背包、等级、结构化收获四项定向：`Ran 4 / OK`。
- 种植/空地/背包综合专项：`Ran 157 in 118.588s / OK`。
- 原单个收获立即播种回归：`Ran 1 / OK`。
- `py_compile` 通过；`git diff --check` 无空白错误，仅历史 LF/CRLF 提示。

### 当前边界与唯一下一步

v326 仍只在源码树，部署目录仍是 v323，助手未运行。下一步执行新鲜好友完整专项、每日专项、完整 `unittest discover`、哈希/字节核对；全部通过后创建部署备份、复制 v326、隐藏启动并观察 2026-08-04 自然每日流程、种植与 CPU/capture 日志。


## 2026-08-04 15:07:00 +08:00 — v326 已部署：852 全回归通过，2026-08-04 每日状态自然切换；发现分享奖励领取未闭环

### 完整验证与部署

- 新鲜完整回归：`Ran 852 tests in 354.642s / OK`。
- 好友完整专项：`Ran 373 tests in 133.472s / OK`。
- `py_compile` 通过；`git diff --check` 无空白错误，仅历史 LF/CRLF 提示。
- 备份：`E:\CV农场助手\backups\v326-durable-daily-capture-planting-20260804-145643`。
- 源码/部署一致：bytes `1414727`，SHA-256 `AC7254135D0F4AAD7C322112CDA963BBEC3DDF0115EDEB1656BA868EB2512CC2`。
- 隐藏启动后 PID `29548`，Responding=True；配置与备份哈希一致。

### 2026-08-04 自然生产证据

- `daily_flow_status.json` 已自然切换到 `2026-08-04`：freebenefits/share/task 均为 success；share target `2135736062`。
- canonical/sibling counter 均为 2026-08-04，freebenefits/share/task 日期一致；两份 CSV 均新增 `2026-08-04,0,0,0,0`。
- 启动后新日志段：Traceback=0、PrintWindow timeout=0、capture total timeout=0、WGC start error=0、metrics replace failed=0。
- 120 秒运行窗口 CPU delta 39.516 秒，约单核 32.9%；当前每 12 秒巡检，间隔恢复正常，但仍需继续压低无动作轮视觉开销。

### 新发现的唯一生产缺口

`live-v326-current-20260804-1503.png` 显示 direct share 已持久成功后，分享页的“领取”奖励按钮仍可见；硬防重门阻止了再次发送，但奖励领取尚未形成闭环。手工坐标点击未改变页面。task success 当前来自 entry red-dot cleared 证据，仍需下一阶段补“direct-send 后只允许领取奖励、禁止再次分享”的专用视觉状态与 RED，并对任务领取页做可见完成复核。

### 跨日自动取证已启动

```text
watcher=E:\CodexProjects\qq-farm-cv-helper-portable\.analysis\watch-v345-crossday-20260805.ps1
watcher PID=32208
status=E:\CodexProjects\qq-farm-cv-helper-portable\.analysis\v345-crossday-watch-20260805-to-20260806\status.json
samples=E:\CodexProjects\qq-farm-cv-helper-portable\.analysis\v345-crossday-watch-20260805-to-20260806\samples.jsonl
final=E:\CodexProjects\qq-farm-cv-helper-portable\.analysis\v345-crossday-watch-20260805-to-20260806\final-evidence.json
deadline=2026-08-06 11:30:00 +08:00
```

监视器每 60 秒只读采集一次正式状态，不修改配置或业务文件。它会记录 `2026-08-06 00:00` 自然切日、`00:31` 每日任务窗口和 `09:55` 每日分享窗口。只有分享 exact target/direct-send、奖励、任务、四组关键镜像和双 CSV 全部满足后，才自动执行一次正式隐藏重启，再采样 120 秒并验证零重复分享、进程响应、源/部署/config hash；结果写入 `final-evidence.json`。
### 唯一下一步

为分享奖励 `领取→已领取/checkmark` 建立独立状态机和模板/颜色定位，不复用 share send gate；随后验证弹窗关闭、CPU idle delta 和自家土地实际播种画面。


## 2026-08-04 15:38:57 +0800 ? v327 RED?GREEN??????????????????????????

### ?????????
- ?????????? `2026-08-04`?
- `live-v326-current-20260804-1503.png` ? `tests/fixtures/live-share-reward-unclaimed-tall-normalized-20260804.png` ???????? direct-send ???????????????????
- ??? durable `share` success ????? reward UI?`entry-red-dot-cleared` ???????????????? task success?

### RED
- ?? `tests/test_share_reward_claim_after_send.py`???? `tests/test_daily_flow_status.py`?
- ????? 6 ?????`Ran 6 tests in 4.406s / FAILED (failures=6)`?
- RED ???reward-claim ??????????????????????????/???????????? `(360,770)`?DPI client click??? `share_reward` ???task ?????????? due?

### GREEN ???
- `portable/hook.py` ???????? HSV/???????? fixture ????? fixture ???????
- ?????? `_friend_guard_post_client_click()` ???????????????????
- `_share_action_blocked(..., 'reward-claim')` ???? exact direct-send proof ??? reward ???????share entry/prompt/button/contact ????????????
- `_share_mark_reward_claimed_success()` ??? `share_reward/success/verified-share-reward-claimed-v2`?????? immutable `share/verified-direct-contact-send-v2`?
- `_run_share_prompt_recovery()` ? durable send ??? `??????checkmark ???????????????`????? namespace/latch ??????
- task red-dot cleared ???? `_daily_task_claim_available_visible()`????????? success??? should-run?
- ?? GREEN?`Ran 6 tests in 4.911s / OK`???????? 7 ??`Ran 7 tests in 7.179s / OK`?`py_compile` ???

### ???????
????????/???????????? `unittest discover`?????? v327 ??? 2026-08-04 ??????????????? CPU ???


## 2026-08-04 19:39:01 +0800 ? v332 task_prompt ??????????? RED?GREEN?????

### ?????????
- ???????????2026-08-04?Asia/Shanghai??
- v331 ?????????????????????? 2.4 ?????? `v144 daily task entry had no prompt; kept pending for retry`????????? QQ?? v331 ????????????
- ????????????????????? `task_prompt` ????????????? QQ ????????????????

### RED
- `tests/test_daily_task_prompt_live_recovery.py` ??/?? 2 ??????
  - `task_prompt` ???? `_daily_entry_call_kind` ???
  - ?? prompt miss ???? `(110,655,428,800)`??? 1.2 ??? fresh frame ??????
- ?????`Ran 6 tests / FAILED (failures=2)`?????????????? wrapper ?? False?

### GREEN ???
- ?? `portable/hook.py`?
  - `_daily_entry_call_kind` ???????? `task_prompt`?
  - `_wrap_share_entry_settle_func` ?? `entry_kind == task_prompt` ????????? `_ACTIVE_RUN_CYCLE_CONTEXT`??? `_share_context_from_call`???????????????? QQ ????????????? 1.2 ???? `_get_frame_from_bot` ? fresh frame??? frame ????/?? kwargs????????????????????????? v332 ?????
  - v331 ????????????
- ?? GREEN?`tests.test_daily_task_prompt_live_recovery` ? `Ran 6 / OK`?
- ??/?????`Ran 137 / OK`?
- ?????`Ran 186 / OK`?
- ??/?????`Ran 35 / OK`?
- ?????bytes `1443468`??????????????? PID 14264 ?? v331?

### ????????????
- Terra ?????????? guard identity ?????????????????????? identity????????????????? RED????????????????????????
- ??????????????? RED?GREEN??????????????????????????? v332 ?????

## 2026-08-04 22:37:06 +08:00 — v334-v336 性能门禁与实时播种继续阻断

### 已完成并验证
- v334 / 1.4.25：为反复 `v165` forced self pass 增加 recent verified self-no-action + 正常 `check_interval` 门禁；memo 包含 confirmed 板面、锚点、候选与 rejected 签名，板面变化/home priority/收获播种待办会立即失效。
- v335 / 1.4.26：post-action 板面门禁为 `unknown` 时，fresh-zero 不再提交为播种成功。
- v336 / 1.4.27：真实 428×800 种子工具栏下移到 y=605..622 后仍能识别 17/36/8/5 四槽徽章；修复 `fresh-frame-not-seed-panel`。
- TDD 证据：v334 三个 RED→GREEN、v335 overlay-zero RED→GREEN、v336 真实 seed-panel fixture RED→GREEN。
- 最新完整回归：`878 tests in 978.983s / OK`；`py_compile` 通过；`git diff --check` 仅历史 LF/CRLF warning。
- v336 部署：`E:/CV农场助手/backups/v336-lower-seed-panel-20260804-222953`；源码/部署 SHA-256 均为 `D2E9DBDF9A75070FDD5C40EFE04C46575244CE94ACD55A26A2333DEB4D46A446`，bytes=1506333；配置哈希保持 `6C58E244D2C78C2FFEEAFDB079BA18561B77FADBB966912CDA7360037630C585`。

### 新鲜生产结果
- v336 已真实识别种子面板并走背包优先：`seeds=5`，空地 `4 -> 3 -> 0`，随后 `seeds=4 fertilizer=0 unconfirmed=1`；证明“面板不识别导致不种菜”已突破。
- 但 planting flow 在 `after=0` 后仍以旧 baseline `empty=4` 写入 `backpack-preflight-pending-or-inventory-evidence`，下一轮又检测为 4 块并重复 `4 -> 3 -> 0`。生产 CPU 仍为约单核 93%–130%，因此尚未达到性能验收。
- 生产期间没有新的 `v165`、Traceback、WGC error 或 PrintWindow timeout；当前 CPU 被播种重复链主导，v334 idle 门禁仍需等播种链清零后再做 120 秒验收。
- 关键证据：`.analysis/v336-live-first-100s-20260804.json`、`tests/fixtures/live-v335-open-seed-panel-four-empty-20260804.png`、`.analysis/v334-current-game-20260804-2145.png`。
- 为避免继续拖慢电脑，`QQFarmCVHelper` 已于 2026-08-04 22:37:06 +08:00 停止；下次部署后再启动。

### 唯一下一动作
新增 RED：当 planting outcome 从非零降到零时，只有 post-action board state 为 `confirmed` 才可提交；`bypass/unknown` 必须先关闭种子面板并抓一张 fresh home frame 复核。GREEN 后确保成功 `after=0` 不再被旧 baseline=4 的 `pending-or-inventory-evidence` 重新武装，再跑 878+ 全量、部署 v337，并执行稳定满地 120 秒 CPU 验收。

## 2026-08-04 23:12 +08:00 ? ?? 2?2 ?????????

### ???????
- ?????`.analysis/user-four-empty-split-quads-20260804.jpg`?
- ????? 4 ?????????????????????????=4?????????????? 2?2 ???
- 2?2 ???????????????????????????????????????????????????????????
- ?????????? 2?2?? 2?2 ??????????????????? 2?2 ?????????? 1?1 ??????????????????????

### ? v337 ???????
- ?????? `empty=4` ??????????????? 2?2 ????
- `4 -> 3 -> 0` ?? `empty=4` ?? `pending-or-inventory-evidence` ??????? 2?2 ????????????? CPU ???
- ?? RED/GREEN ??????????????????? 2?2???/????? 1?1 ???`remaining=0` ?? baseline ??????

### ??????
- QQFarmCVHelper ?????????????????????

### ??????
?? Luna-max RED ????????????? Sol ???? `portable/hook.py`?????????????????????????



## 2026-08-04 ? v340 runtime ???? RED?GREEN ???????

### ???????
- ?????? run-cycle gate ???? home/friend ???????`436 tests in 272.307s / OK`??? `.analysis/v340-latest-home-friend-suite-20260804.log`?
- GUI tick??????WGC ????????`28 tests in 21.629s / OK`??? `.analysis/v340-latest-performance-targeted-20260804.log`?

### RED?GREEN 1??????????????
- `_lsprof` ?????`_fake_is_weixin_bound_platform` ???? 1.57454s??? self 1.11432s????????? `__dict__` ?? `str(dd).lower()`?
- RED??? `tests/test_weixin_bound_platform_fast_path.py`????????????????????????? `weixin://` ?????`Ran 3 / FAILED (failures=2)`??? `.analysis/v340-weixin-bound-fast-path-red-20260804.log`?
- GREEN??????? protocol/process/platform/mode ??????? settings/config ????? stringify ??????`Ran 3 / OK`??? `.analysis/v340-weixin-bound-fast-path-green-20260804.log`?

### RED?GREEN 2??? import ????????? patch
- `_lsprof` ??????? 1700?2100 ? import hook ????? import ????? `_patch_loaded` ??????
- RED??? `tests/test_import_patch_deduplication.py`??? module identity ??? import ??? patch?`Ran 2 / FAILED (failures=1)`??? `.analysis/v340-import-patch-dedupe-red-20260804.log`?
- GREEN????? `_PATCH_LOADED_SEEN_RELEVANT`?? `(tag, module identity)` ????? reload ? identity ????? patch?initial/manual/qt-safe-tick ?????????`Ran 2 / OK`??? `.analysis/v340-import-patch-dedupe-green-20260804.log`?
- ?????????`65 tests in 35.838s / OK`??? `.analysis/v340-runtime-hotspot-subsystem-green-20260804.log`?
- ?????????? `test_hook_encoding` ??????? BOM??? 6 ??????

### ???????????
- ??????? v339 ?????????????? `.analysis/v339-isolated-runtime`?
- ??????????????????????? 120 ? CPU ?????? `_lsprof`???? GUI tick throttle ??? run-cycle fast skip ???/???


## 2026-08-04 ? v340 ????????? durable ????????

### Terra-ultra A??????????
- RED `test_sync_bypasses_ten_second_throttle_when_business_date_changes`?????? 10 ??????????????? summary ??? context/counter/CSV ????`Ran 1 / FAILED`??? `.analysis/v340-daily-metrics-date-throttle-red-20260804.log`?
- GREEN??? `_DAILY_METRICS_LAST_SYNC_DAY`????????? + 10 ????????????????????????`Ran 1 / OK`??? metrics ?? `10 / OK`?
- RED????? run-cycle fast-skip ????? `freebenefits/task` ??????`Ran 2 / FAILED (failures=2)`??? `.analysis/v340-native-daily-fast-gate-red-20260804.log`?
- GREEN??? `_qqfarm_native_daily_cycle_due()`??????????????????/????? fast-skip??? native scheduler??????? `9 / OK`????? `104 / OK`?

### Terra-ultra B??? resume ? identity ???????
- RED?`_qqfarm_friend_list_resume_pending=True` ? `_qqfarm_force_self_cycle_next=True` ??? fast-skip?`Ran 2 / FAILED (failures=2)`?
- GREEN?????????????? stable run-cycle skip??? `.analysis/v340-fast-gate-resume-force-green-20260804.log`?
- RED?????????identity mirror ?? `os.replace` ??? sharing violation ?? mirror ?? durable identity??? `.analysis/v340-friend-identity-replace-retry-red-20260804.log`?
- GREEN?identity ?????? 3 ??? transient retry?primary ? `.hook` mirror ????? guard-template identity??? `.analysis/v340-friend-identity-replace-retry-green-20260804.log`?
- ?? home/friend ???`436 tests in 226.903s / OK`??? `.analysis/v340-latest-home-friend-after-resume-gate-20260804.log`?

### Luna-max?import/GUI ????????????? patch
- RED??????? import ????? patch???????? import ????????`gui.synthetic` import ????? tick throttle ??? `sys.modules` ?????
- GREEN?
  - `(tag, module identity)` ???
  - `_initializing=True` ???????????????? patch?
  - ? maintenance import ???????????????? `sys.modules`?
  - `gui.*` ???????? `_tick_ui` throttle?
  - initial/manual/qt-safe-tick ?????????
- import ?? `4 / OK`?runtime/performance/daily targeted `67 / OK`?

### ???????
- `.analysis/v339-isolated-runtime/v340-runtime-hotspot-120s-result-20260804.json` ? 3.971% ?????????? run_cycle??? bot ??????????????????????
- ?? hook ????? host LocalAppData ?????? root log????????????????????? `FarmBotCV.start` ??? `run_cycle` ??? CPU delta?

### ????????
????????? `unittest discover` ?????????? hash/bytes??? 1.4.31/v340 ?????????????????????/??????? 120 ? CPU ?????????

## 2026-08-04 — 当前阶段回归事实、证据边界与唯一下一步

### 日期与阶段边界

- 日期基准为 **2026-08-04（Asia/Shanghai）**。本节覆盖当前阶段的源码/回归事实；较早的 v326 部署记录保留为历史证据，不能替代本阶段的完整 discover、正式性能、部署或现场结论。
- 当前目标：把每日状态、好友动作、空地/播种和性能隔离的不变量收敛到同一份新鲜证据包，同时保持正式配置、部署副本和现场运行状态可追溯。

### 本阶段已固化的不变量

1. **每日流程与持久化**：`daily-flow` 状态迁移使用 CAS（compare-and-set）语义；业务日可注入，旧业务日或旧轮次不能覆盖新业务日状态。counter 与两份活动 CSV 的修复/写入遇到短暂失败时必须有界重试并重新收敛，不能把局部成功记成完整成功。
2. **好友动作**：好友以稳定 fingerprint 识别，并以 action ledger 记录同一业务日/实例/动作的已确认提交；只有动作后的 fresh proof 才能递增耐久统计。`unknown`、`blank`、`occluded` 仅可在有限复核预算内暂留，预算耗尽后必须有界释放回遍历路径，既不永久卡住，也不凭旧帧重复计数。
3. **2×2 背包种子**：仅四个 `confirmed empty` 格在一个完整田字格中时才允许 2×2。四块分散、缺角或不完整几何一律禁用 2×2。灰勾、叉或一次放置失败均至多尝试一次；同一轮立即降级为可用 1×1，禁止重新打开同一个失败 2×2 循环。
4. **收获后的播种顺序**：必须严格为 `fresh capture → confirmed empty refresh → backpack → plant`。不得以收获前基线、旧面板或未确认候选直接进入背包/商店/种植。
5. **满地种子面板**：seed overlay 关闭后若新鲜帧确认满地，必须零 `shop`、`strategy`、`land` click，清除自家种植路线并恢复 friend route。
6. **性能隔离**：每次性能隔离脚本使用唯一目录，冻结并记录被测运行时 hash，写入/核验 UTF-8 marker，采集完整 PID 树 120 秒窗口；正式配置的 hash 前后必须不变。

### 当前新鲜自动化/结构性证据（不外推为阶段完成）

- 高风险种植：`4 / 4 OK`。
- planting 专项：`222 OK`。
- friend 专项：`387 OK`。
- daily/share 专项：`197 OK`。
- performance structure/unit：`34 OK`。
- `python -m py_compile` 与 `git diff --check`：OK。

### 仍在进行，不能提前结论的项目

- 完整 `unittest discover`；
- 正式性能隔离/120 秒 PID 树观测；
- 本阶段部署、源/部署 hash 与字节核对；
- 自然现场的每日、好友、收获→播种与 seed-overlay 满地恢复证据。

### 跨日自动取证已启动

```text
watcher=E:\CodexProjects\qq-farm-cv-helper-portable\.analysis\watch-v345-crossday-20260805.ps1
watcher PID=32208
status=E:\CodexProjects\qq-farm-cv-helper-portable\.analysis\v345-crossday-watch-20260805-to-20260806\status.json
samples=E:\CodexProjects\qq-farm-cv-helper-portable\.analysis\v345-crossday-watch-20260805-to-20260806\samples.jsonl
final=E:\CodexProjects\qq-farm-cv-helper-portable\.analysis\v345-crossday-watch-20260805-to-20260806\final-evidence.json
deadline=2026-08-06 11:30:00 +08:00
```

监视器每 60 秒只读采集一次正式状态，不修改配置或业务文件。它会记录 `2026-08-06 00:00` 自然切日、`00:31` 每日任务窗口和 `09:55` 每日分享窗口。只有分享 exact target/direct-send、奖励、任务、四组关键镜像和双 CSV 全部满足后，才自动执行一次正式隐藏重启，再采样 120 秒并验证零重复分享、进程响应、源/部署/config hash；结果写入 `final-evidence.json`。
### 唯一下一步

**收敛当前同一源码 revision 的完整 discover、正式性能隔离、部署/hash 与现场观测为一份带日期的连续证据包；在该证据包齐全前，不更新为阶段完成或部署完成。**


## 2026-08-05 10:26:00 +0800 ? v1.4.32 ???????????

### ????

????????????????????? UserData?????/??/??????????????????????????????????????????? 2?2??????? 1?1??????????????????? fresh frame ?????capture/OCR/GUI ????????

### ????? RED ? GREEN

1. **?????????**???? UTC+8 ?????`2026-08-04 16:01 UTC` ??????? `2026-08-05 00:01`?????????????????????????????????
2. **direct-share canonical ??**??????????? `.tmp-v78` ??? legacy counter????? `_daily_metrics_sync_runtime(..., force=True)`??? configured canonical?`.hook`??????? CSV????????????? 5 ? sharing-violation ????? retry date/count ???? root ? instance bucket?
3. ???????? `3 failures`???? `3 / 3 OK`???/??????? `200 / 200 OK`?

### ???????????

```text
portable\hook.py
bytes=1623294
SHA-256=DFE9D7A8EDB22A62B64D93B7AA35E162EA94F42D80BF49AF6CBE0A834BC04EB7
```

```text
python -m py_compile portable\hook.py?OK
git diff --check?exit 0
?? unittest discover?953 / 953 OK
???.analysis\v342-post-daily-p1-full-discover-20260805-101138.log
```

### ??????????

```text
run_id=v342-20260805-102051491-ecce9b0cf8b8
source hook == isolated hook == DFE9D7A8...04EB7
page-ready ? native-cycle-start ? native-cycle-end?????
sampling?120 / 120
process_tree_stopped=true
formal_config_unchanged=true
formal config SHA-256=6C58E244D2C78C2FFEEAFDB079BA18561B77FADBB966912CDA7360037630C585
failure=null
```

20 ???????????? `49.05%`??? P95 `131.25%`???????? `2.45%`?P95 ? `6.56%`?????? `480.6 MB`??? `566.4 MB`??? `74?77`?`Responding=False=0`?

### ???????????

- fresh action proof ??? append-only `friend_action_ledger.json.confirmed-proof.jsonl`?? ledger replace ? Windows ??????????????????????? claim?
- cursor journal ??????? cursor/retry/?? fallback ????? `entry_pending=True`?????????????????????????
- pause/????????? `config/cfg/settings/state/runtime_state/context/ctx/bot/farm_bot/worker` ???????????????? INI?

### ????????

?? `E:\CV????\hook.py` ??????????????????? SHA-256 ???

```text
6C58E244D2C78C2FFEEAFDB079BA18561B77FADBB966912CDA7360037630C585
```

### ????????????

1. ?????????????? P0/P1?
2. ?? `VERSION=1.4.32`?README?CHANGELOG?Skill/?????
3. ?? `E:\CV????\backups\v342-perfect-1.4.32-20260805-*`???? hook???????? config?daily ??/counter/? CSV?friend progress/ledger?
4. ??????????? `UserData`??? source/deploy hash ? bytes??? hash ???????
5. ?????????????canonical/.hook/? CSV ??? 2026-08-05???????????????fresh proof/sidecar???????2?2 ???? 1?1??????? capture/OCR/PrintWindow storm?
6. ?????????cursor ? action proof?
7. ???? `2026-08-05 ? 2026-08-06` ??????????

**?????????????????????????????? v1.4.32?**

## 2026-08-05 10:58:00 +0800 ? ???? P1 ????????????

### ???????

Terra-ultra ???????????? P1?

1. cursor journal ???????????????????? carousel cursor?????? pending?blocked ????????? terminal close??? resume ????? journal ???
2. ?? force-false ? `force_help_after_steal_success` ? `friend_only_help_request_mode` ???????????????? `False`?

### RED ? GREEN ???

- ???? `_friend_progress_state_snapshot()`?`_friend_progress_state_restore()`?`_friend_progress_journal_commit()`?journal ????? retry-pending?????????????????????? pending ???
- carousel cursor ?? journal ?????????? `carousel-cursor-journal-retry` ?????????
- ?????????????? pending????? `pending-row-journal-retry`??????? 0?
- blocked ?????????????? `blocked-row-journal-retry`?
- ?? close ? terminal ???? journal ????? `closed`?????? pending ??? `closed-journal-retry`?
- ????????? journal ????? pending??? `visited-journal-pending`??????????????
- ?? resume journal ???? watchdog ????????? pending retry ???
- friend restore group ?? `force_help_after_steal_success` ? `friend_only_help_request_mode`??????????????? settings/config mirror?

RED ???4 ??????????GREEN?4 / 4 OK????????blocked?terminal?post-click ?? journal failure ????`test_friend_progress_durable_journal.py` ? `9 / 9 OK`?

?????`393 / 393 OK`?scheduler?`7 / 7 OK`?

### ??????

```text
portable\hook.py
bytes=1629786
SHA-256=4996A7A07F4EFB58934F580671DDAFC10E9DBFD363E055DF3A9CD1F1B0C2002C
VERSION=1.4.32
```

### ??????????

```text
python -m py_compile portable\hook.py?OK
git diff --check?exit 0
?? unittest discover?959 / 959 OK
???.analysis\v342-final-source-full-discover-20260805-104246.log
```

### ???? 120 ?????

```text
run_id=v342-20260805-105150279-3bb897f7fc0b
source hook == isolated hook == 4996A7A0...B0C2002C
gates?page-ready / native-cycle-start / native-cycle-end ????
sampling=120 / 120
process_tree_stopped=true
formal_config_unchanged=true
formal config SHA-256=6C58E244D2C78C2FFEEAFDB079BA18561B77FADBB966912CDA7360037630C585
failure=null
```

20 ??????????? `45.18%`??? P95 `145.31%`???????? `2.26%`?P95 ? `7.27%`?????? `499.2 MB`??? `561.8 MB`??? `82?90`?`Responding=False=0`?

### ????

???????????? `E:\CV????\hook.py` ????????????????? ? ?? ? hash/config ?? ? ?????? ? ???? ? ???????

**????????? v1.4.32 ??????????? UserData?**

<!-- V345-HANDOFF-START -->
## 2026-08-05 15:08 +08:00 — v345 最终自动化、部署与现场证据（权威更新）

### 当前正式身份

```text
VERSION=1.4.32
source=E:\CodexProjects\qq-farm-cv-helper-portable\portable\hook.py
deploy=E:\CV农场助手\hook.py
bytes=1665094
SHA-256=55E3A448D575A24EB6BF6065E8E5EC97464FD8153B5A448484CBD1CF3186990D
formal config SHA-256=6C58E244D2C78C2FFEEAFDB079BA18561B77FADBB966912CDA7360037630C585
```

源码与正式 Hook 的 hash 和字节数完全一致。`launcher.ps1`、`StartFarmAssistant.vbs`、`VERSION` 与正式目录也已一致。UserData、分享目标、会员状态和设置未被覆盖。

### 本阶段新增 P0：每日分享成功后被恢复线程覆盖为失败

正式实机于 `2026-08-05 13:52:30 +08:00` 出现：

```text
每日分享执行完成（share_prompt阶段命中领取按钮），记录日期：2026-08-05
```

但恢复线程随后记录：

```text
v240 share recovery deferred after failure=prompt-not-found
```

并把 `daily_flow_status.json` 写回 failed。根因是 native `run_daily_share` 在恢复调用内完成奖励领取后，恢复线程未在失败落盘前读取同日原生日志成功证据。

RED：

- `test_native_share_success_between_prompt_click_and_probe_blocks_failure`
- `test_native_share_reward_completion_log_is_authoritative_same_day_proof`

GREEN：新增 `_daily_share_native_log_paths()`、`_daily_share_authoritative_success_today()`，并在 `_share_recovery_fail()` 写 backoff/failure 前执行同日原生成功晋升。成功时写入 `share_reward`，保持 direct-send 与奖励两个独立证明，并清空 share retry。

### 可读每日状态

正式日志原先显示 `message=????`。已按 TDD 把状态恢复为可读中文：

```text
每日状态（2026-08-05）：每日分享已完成；每日任务已完成。今日每日流程已全部完成
```

### 2×2 / 1×1 / 背包 / 仓库

- 正式 overlay fixture：`tests\fixtures\quad_overlay_green_confirm_20260805.png`。
- 428×800 坐标：绿色确认约 `(291,350)`；红色取消约 `(213,418)`。
- 66 张 fixture/正式 capture 误报扫描只命中 1 张真实 overlay。
- 只有完整田字格进入 2×2；四块散空地不进入。
- 2×2 失败后先处理确认层；确认层未从 fresh frame 消失时，阻止 1×1、第二次背包、drag、strategy 和 shop。
- 仓库失败路径：一次 native close → fresh frame → 一次 Escape → fresh frame → 原有 backoff。
- 正式满地证据：`E:\CV农场助手\logs\captures\self-no-action-20260805-143831-225-428x800x3-FarmBotCV-process-self-farm.png`；日志为 `empty=0`、`confirmed full board skipped native planting strategy`，未触发背包/商店购买。

### 自动化证据

```text
每日/分享专项：203 / 203 OK
2×2/仓库/种植专项：208 / 208 OK
好友只读专项：408 / 408 OK
空地/种植/性能只读专项：311 / 311 OK
全量 discover：980 / 980 OK
python -m py_compile portable\hook.py：OK
git diff --check：exit 0
```

关键日志：

```text
.analysis\v345-readable-daily-summary-suite-20260805-144531.log
.analysis\v345-readable-summary-full-discover-20260805-144900.log
.analysis\v343-recovered-overlay-warehouse-planting-suite-20260805-131756.log
```

### 最终 120 秒隔离性能

```text
run_id=v342-20260805-150054728-62544d8adba0
source hook == isolated hook == 55E3A448...6990D
source_artifact_frozen=true
gate_completed=true
sampling=120 / 120
max_working_set=516763648
max_threads=77
responding_false=0
process_tree_stopped=true
formal_config_unchanged=true
production_config_touched=false
failure=null
```

### 正式现场与重启

`2026-08-05 14:32:11 +08:00`：

```text
指定联系人=2135736062
exact target selected=true
selected_count=1
confirm=direct-uia
dialog_closed=true
share.status=success
share.reason=verified-direct-contact-send-v2
share_reward.status=success
```

同日重启后的 120 秒证据：PID 已变化，`share_entry=0`，直接发送=0，flow revision 与 verified_at 保持不变，配置 hash 不变，`Responding=False=0`。

最终部署后的 120 秒现场：

```text
cpu_delta_120s=22.953s
mean_cpu_one_core_pct=19.29%
max_working_set=537051136
max_threads=89
responding_false=0
```

好友设置仍为 `enable_process_friend=True`、`enable_steal=True`、`enable_help=True`、首行/末行/durable ledger 专项通过；同日现场帮助计数由 3 增至 6，canonical/`.hook` 与双 CSV 同步。

### 备份

```text
E:\CV农场助手\backups\v343-perfect-1.4.32-20260805-135038
E:\CV农场助手\backups\v344-live-share-race-1.4.32-20260805-143007
E:\CV农场助手\backups\v345-perfect-1.4.32-20260805-150526
```

最终回滚基准使用最后一项。

### 跨日自动取证已启动

```text
watcher=E:\CodexProjects\qq-farm-cv-helper-portable\.analysis\watch-v345-crossday-20260805.ps1
watcher PID=4460（当前加固脚本）
status=E:\CodexProjects\qq-farm-cv-helper-portable\.analysis\v345-crossday-watch-20260805-to-20260806\status.json
samples=E:\CodexProjects\qq-farm-cv-helper-portable\.analysis\v345-crossday-watch-20260805-to-20260806\samples.jsonl
final=E:\CodexProjects\qq-farm-cv-helper-portable\.analysis\v345-crossday-watch-20260805-to-20260806\final-evidence.json
deadline=2026-08-06 11:30:00 +08:00
```

监视器每 60 秒只读采集一次正式状态，不修改配置或业务文件。它会记录 `2026-08-06 00:00` 自然切日、`00:31` 每日任务窗口和 `09:55` 每日分享窗口。只有分享 exact target/direct-send、奖励、任务、四组关键镜像和双 CSV 全部满足后，才自动执行一次正式隐藏重启，再采样 120 秒并验证零重复分享、进程响应、源/部署/config hash；结果写入 `final-evidence.json`。
### 2026-08-05 15:38 +08:00 — 跨日监视器 RED→GREEN 加固

监视器已增加仅供隔离验证的 `-NowIso` 时钟接缝。生产启动不传该参数，继续使用真实本机 `Asia/Shanghai` 时间；传入 `-NowIso` 时强制同时传 `-Once`，防止固定逻辑时间进入连续守护模式。

新增并修复三条监视器级回归：

1. RED：脚本不接受 `-NowIso`，退出为 `NamedParameterNotFound`。GREEN：`-Once -NowIso 2026-08-06T10:05:00+08:00` 的完整隔离夹具得到 `stage=ready-for-restart`、`ready_for_restart=true`，且夹具 launcher 未被执行。
2. RED：四份 counters 根级日期/重试已更新，但实例 `instances.1` 仍为 `2026-08-05 / retry=1` 时，旧监视器仍误判 ready。GREEN：canonical、sibling、Local main、Local hook 现在都同时要求根级和实例级 `share_last_date=2026-08-06`、`retry_share=0`；旧实例夹具得到 `stage=share-success`、`ready_for_restart=false`。
3. RED：`-NowIso` 未配合 `-Once` 时脚本继续运行。GREEN：该组合在任何正式取证写入前退出，诊断为 `-NowIso requires -Once.`。

验证证据：

```text
E:\CodexProjects\qq-farm-cv-helper-portable\.analysis\v346-crossday-watcher-validation-20260805.json
watcher script bytes=16669
watcher script SHA-256=BA40E07F2DC098D5E82C173CB10CCEA184FB42EB8B970A10E7A2DDA42D39EC7D
Windows PowerShell 5.1 parse=OK
UTF-8 BOM=true
```

后台监视器已重新加载当前脚本：

```text
PID=4460
started=2026-08-05T15:34:50.7797809+08:00
interval=60 seconds
samples 21 → 22 after 70 seconds; later observed >=24
stage=before-midnight
watcher Responding=True
formal assistant PID=32776, Responding=True
source/deploy hook SHA-256=55E3A448D575A24EB6BF6065E8E5EC97464FD8153B5A448484CBD1CF3186990D
formal config SHA-256=6C58E244D2C78C2FFEEAFDB079BA18561B77FADBB966912CDA7360037630C585
```

本轮只修改跨日取证脚本和文档，没有修改或重新部署正式 `hook.py`。正式助手继续运行。

### 唯一下一步

保持正式助手运行，等待未来的自然日期切换 **`2026-08-05 → 2026-08-06`**。在 `2026-08-06` 首轮业务完成后，采集分享、任务、canonical/`.hook`、Local legacy 关键字段、双 CSV、好友 ledger 和一次重启防重证据；该证据通过后再做最终签收。
<!-- V345-HANDOFF-END -->

<!-- V356-HANDOFF-START -->
## 2026-08-05 23:37 +08:00 — v356 部署完成，进入自然跨日与随机局部收获签收

### 当前正式身份

```text
version=1.4.33
source/deploy hook bytes=1747126
source/deploy hook SHA-256=4CC1B98371FE0E46C65A85B06CE57F3FC2001EB1EC0F334C913DBBAE1FD3CEDF
formal config before=6C58E244D2C78C2FFEEAFDB079BA18561B77FADBB966912CDA7360037630C585
formal config after=5A63582C4A6A9153B51E819DC9D645C44997FD59AA8FE9E0C4A54A5DCA3762A4
only config change=[instance.1.bot] daily_share_time 09:55 → 00:31
backup=E:\CV农场助手\backups\v356-perfect-1.4.33-20260805-232655
formal PID=17476, started=2026-08-05 23:30:26 +08:00
```

保留值：`active_id=1`、`share_target_name=2135736062`、`share_send_requires_target_match=True`、`share_cancel_if_target_missing=True`、`enable_process_friend=True`、`enable_steal=True`、`enable_help=True`。

### v356 种植核心

- 一键务农与单个收获事件都会进入收获后补种链。
- 收获前帧 + 3 个新鲜帧生成一次性 24 格快照；暗坑仅在确认收获上下文使用，并要求局部前后变化。
- 随机只收获几块时，只返回实际变化地块；未成熟地块不受影响。
- `direct_lands` 与 snapshot/recent 未尝试坐标合并；一次成功只消费实际尝试的 1 格或 4 格。
- 完整田字格才使用 2×2；不完整或失败后同轮降级真实 1×1；背包种子始终先于等级作物购买。
- 普通全局视觉继续拒绝已种作物、幼苗和刚播种黑土堆，不恢复“暗坑=空地”的历史回归。

### 最新自动化和性能

```text
planting/empty/backpack/performance=305/305 OK
daily/share=211/211 OK
friend=406/406 OK
full discover=1009/1009 OK
py_compile=OK
git diff --check=OK
watcher artifact gate=1/1 OK
performance structure=6/6 OK
performance run=v356-20260805-232023104-575eebea724b
gate_completed=true
sampling=120/120 complete PID tree
Responding=False=0
source hook frozen=true
source hook == isolated hook=true
formal config unchanged=true
process tree stopped=true
failure=null
```

性能结果：
`E:\CodexProjects\qq-farm-cv-helper-portable\.analysis\v356-isolated-runtime-v356-20260805-232023104-575eebea724b\v356-isolated-performance-120s-result.json`

### 正式隐藏启动观察

```text
observation=120 seconds
PID=17476
Responding=False=0
missing samples=0
cpu delta=40.859 seconds
mean one-core=34.05%
max working set=517332992
max threads=83
share_entry after restart=0
direct send after restart=0
PrintWindow capture timeout=0
```

证据：`.analysis\v356-formal-observation-120s-20260805.json`。

### 新跨日 watcher

```text
script=.analysis\watch-v356-crossday-20260805.ps1
script SHA-256=5D0F872BC410E0FD1BA57A7DEAC0E367AE53E8BADC7AD2FE3784E387AE17E765
PID=24856
interval=20 seconds
task schedule=2026-08-06 00:31 +08:00
share schedule=2026-08-06 00:31 +08:00
deadline=2026-08-06 03:30 +08:00
artifact identity=true
stage before midnight=before-midnight
```

watcher 已加入重启前工件闸门：source/deploy hook 或 config 与预期 hash 不一致时，状态为 `artifact-mismatch`、`ready_for_restart=false`，launcher 调用为零。

### 仍需完成的两项自然现场签收

1. `2026-08-06 00:31` 后确认每日任务、精确联系人分享、分享奖励、四份 counters 根级/`instances.1`、双 CSV 全部收敛；watcher 完成一次隐藏重启并证明零重复分享。
2. 自动化和跨日稳定后通知用户：`现在请把任意几块施肥到可收获状态`。从确认收获开始计时，正常 20–60 秒、最迟 120 秒补齐所有真实空地；未成熟地块不受影响，完整田字格才用 2×2，不完整/失败立即 1×1，不进商店、不重复打开背包，新鲜截图确认空地为 0。

除以上两项自然现场证据外，不重新打开已通过的自动化、性能和部署门。
<!-- V356-HANDOFF-END -->
<!-- V357-HANDOFF-START -->
## 2026-08-05 — v357 好友现场 P0 修复、性能门与正式候选部署

### 用户当前执行策略

- 不再把自然跨日作为当前开发阻塞条件。
- 先连续完成种植、空地、背包、好友偷菜/帮助、自动捣乱、专项、全量、性能和部署。
- 每日分享/每日任务、随机局部收获、真实好友求助入口在对应现场出现时单独签收；签收前不以“等待时间”占用关键路径。
- 当前最高优先级保持：**种植补齐** 与 **好友从第一位开始偷菜/帮助**。

### v357 生产修复

1. **好友求助入口真实转场门禁**
   - 护主名单模式仍优先首页 `check_friend_help_request_entry`，不再无条件绕到普通好友列表。
   - `check_friend_help_request_entry` / `check_friend_icon` 已进入运行时 patch inventory，并由 `_wrap_friend_entry_verified_func` 验证。
   - native `True` 后最多 6 个新鲜采集轮询；只有好友农场或有匹配/至少 3 行布局证据的好友列表才返回成功。
   - 未转场时返回 `False`、清 entry/chain pending；直达入口进入 30 秒有界冷却并设置 `_qqfarm_friend_entry_prefer_icon=True`，冷却内不再调用 native 直达入口。

2. **第一位好友新鲜帧与动作门禁**
   - 在 `friend_guard_list + cursor=0 + 可读导航签名` 的严格场景，连续复用 `start_frame` 不再累计 idle 证据。
   - 至少获得一个真正新鲜画面后才检查偷菜、单偷、帮助、一键务农；动作仍可见或 native 结果未验证时保持 cursor=0 与 chain pending。
   - 只有动作完成或多帧明确无动作后才允许 adjacent navigation；不会把第一位误判为空后立即跳到第二位。

3. **自动捣乱独立执行**
   - `initial-friend-no-action` / `first-no-action-friend` 不再跳过 `_run_deferred_friend_troublemaker`。
   - 空好友主链结束后仍执行一次耐久侧车；成功以 counters `before→after` 为证，失败沿用有界相邻重试与 full-miss cooldown，然后正常回家。

### TDD 与验证

```text
入口 RED：5/5 失败 → GREEN 8/8
第一位好友 RED：1/3 失败 → GREEN 3/3
自动捣乱 RED：1/2 失败 → GREEN 2/2
好友专项：410/410 OK
种植/空地/背包专项：300/300 OK
每日/分享专项：221/221 OK
full discover：1023/1023 OK
py_compile：OK
git diff --check：OK
```

全量首次只发现 `hook.py` 被编辑器写入 UTF-8 BOM；既有 `test_hook_encoding.py` 正确失败，移除 BOM 后编码测试与全量复跑通过。

### 性能和正式观察

隔离性能权威业务日：`2026-08-05`。

```text
summary=.analysis\v357-performance-authoritative-20260805.json
gate_completed=true
sampling=120/120 complete PID tree
Responding=False=0
source hook frozen=true
source hook == isolated hook=true
formal config unchanged=true
process tree stopped=true
failure=null
```

正式启动最初 120 秒包含加载/OCR/Qt patch burst，单核均值为 `97.43%`；按长期运行门禁继续取稳定段，第二个 120 秒为：

```text
Responding=False=0
cpu_delta=38.906s
mean one-core=32.42%
max working set=544698368
max threads=85
process alive=true
```

稳定段证据：`.analysis\v357-formal-settled-observation-120s-20260805.json`。

### 正式身份与回滚

```text
VERSION=1.4.34
source/deploy hook bytes=1762564
source/deploy hook SHA-256=FB527AB7A7200AA21DA3D1074E5926500B7C45CAC73E71FDA6F8F3DFE23CB6AF
formal config SHA-256=5A63582C4A6A9153B51E819DC9D645C44997FD59AA8FE9E0C4A54A5DCA3762A4
backup=E:\CV农场助手\backups\v357-perfect-1.4.34-20260805-010859
formal PID=7212
```

部署只替换 `hook.py` 与 `VERSION`。`UserData`、配置、分享联系人、精确目标匹配、好友开关、计数与本地权益均保留；备份中包含部署前 `UserData`、hook、launcher、VBS、VERSION 与 manifest。

### 后续现场签收（不阻塞当前候选版）

1. 任意几块被用户施肥到可收获后，按确认收获计时：20–60 秒正常、120 秒硬上限；只补真实空地，完整田字格才用 2×2，不完整/失败同轮 1×1，不买等级作物，不重复开背包。
2. 真实首页好友求助或好友列表场景出现后，确认：直达入口有真实转场证据；第一位先完成偷菜/帮助；空巡检后捣乱计数可 `0→1`；无热循环。
3. 每日分享/任务到用户指定签收时间再采集 exact target、reward、四份 counters、双 CSV 与重启零重复证据。
<!-- V357-HANDOFF-END -->

<!-- V358-HANDOFF-START -->
## 2026-08-05 — v358 好友第二位错位/帮助强证明/场景同步/回家收敛正式部署

### 现场证据与结论

用户截图：

```text
C:\Users\11616\AppData\Local\Temp\codex-clipboard-5c85f2f6-4220-4f9b-99ff-df4a0167a152.png
```

仓库回归 fixture：

```text
tests\fixtures\live-friend-selected-second-iris-20260805.png
```

截图确认当前真实页面是 `iris / 104` 好友农场，底部第二张卡被绿色框选中，第一张等级 108 的好友仍在左侧可见；同时现场持久状态曾写成 `scene_hint=home`。因此 v357 自动化通过后仍存在四个 P0 现场缺口：

1. 新好友列表会话继承旧 `cursor=1`，直接从第二位开始；
2. “按钮消失”被误当作一键务农/帮助成功并增加 durable count；
3. 真实好友画面与内部 `home` 状态不同步；
4. 回家未转场时停在好友页空轮询，缺少退避与硬上限。

### v358 生产修复

1. **新好友列表会话清旧游标**
   - `_handle_friend_list_surface()` 检测到新列表会话携带旧 visit cursor、pending cursor、resume 或 exhausted 状态时，将 visit/pending cursor 重置为 `0`。
   - 同一列表画面内的普通失败重试继续保留 pending，避免把一次点击未确认误当成新会话。
   - 运行日志标记：`v358 new friend-list session reset stale cursor...`。

2. **帮助与偷菜使用强完成证明**
   - 新增 `_friend_help_visual_completion_proof(...)`。
   - 以下单独证据全部不足：按钮消失、强按钮变成 soft footer 纹理、native 方法只返回 `True`。
   - 可确认帮助的证据包括 durable counter 确实增长、显式完成回调、明确成功反馈、或农田 ROI 出现足够的维护/作物状态变化。
   - 无证明时不增加帮助计数、不确认 durable ledger，并保持当前好友 pending。
   - Native 偷菜按钮消失也不再单独确认，需 durable count 或视觉作物变化。

3. **真实画面纠正 scene hint**
   - 新增 `_qqfarm_set_live_scene_hint(context, scene_hint)`。
   - 真实好友页写 `friend`，好友列表写 `friend-list`，真实自家页写 `home`。
   - 同日旧 `home` 状态不再覆盖当前真实好友画面。

4. **回家转场真实确认和有界重试**
   - `_invoke_friend_guard_post_click_self()` 使用当前可见 QQ 画面，不依赖陈旧 bot frame。
   - 回家点击后仍看见好友页时返回 `friend-ui-still-visible`。
   - `_apply_visual_friend_route_watchdog()` 保存 `retry=1..3` 与 `next_ts`；退避未到不点击；第三次后停止直接重复点击，释放给既有慢速恢复链。
   - 真正回家后清除 retry、next_ts、exhausted，并同步 `scene_hint=home`。

5. **分享完成后的残留联系人弹窗**
   - 同日分享已完成但 QQ 联系人弹窗仍存在时，先做一次有界关闭。
   - 关闭成功后继续保持 blocked，不重新发送；关闭失败进入 backoff，不形成热循环。

### TDD 与自动化证据

```text
现场好友 P0：5/5 OK
好友专项：415/415 OK
每日/分享/调度/跨日/计数：223/223 OK
种植/空地/背包/采集：296/296 OK
完整 discover：1030/1030 OK
py_compile：OK
git diff --check：OK
hook encoding/runtime identity/import/integrity：15/15 OK
hook BOM=False
```

证据文件：

```text
.analysis\v358-final-full-discover-20260805.txt
.analysis\v358-final-daily-share-suite-20260805.txt
.analysis\v358-final-planting-empty-backpack-suite-20260805.txt
.analysis\v358-final-performance-authoritative-20260805.json
.analysis\v358-formal-settled-observation-120s-20260805.json
.analysis\v358-formal-startup-segment-20260805.txt
```

### 性能结果

隔离性能：

```text
gate_completed=true
sampling_completed=true
sample_count=120
complete_pid_tree=true
Responding=False=0
cpu_delta=44.15625s
mean one-core=37.11%
max working set=516919296
max threads=90
source artifact frozen=true
source hook frozen=true
source == isolated hook=true
formal config unchanged=true
process tree stopped=true
production config touched=false
failure=null
```

正式稳定 120 秒：

```text
PID=25560
sample_count=120
Responding=False=0
cpu_delta=26.9375s
mean one-core=22.64%
max working set=513855488
max threads=85
process alive=true
```

启动出现一次 `WGC start error`，随后 `WGC game-window capture started` 自动恢复。稳定段 `Traceback=0`、`PrintWindow capture timeout=0`、`home retry exhausted=0`、`help unverified=0`。

### 正式身份、配置与回滚

```text
VERSION=1.4.35
source/deploy hook bytes=1740281
source/deploy hook SHA-256=364EF508424F655F68AAFD81EC3C0B53FAED4FB68F2200D664C01D7108A0CC8C
formal config SHA-256=5A63582C4A6A9153B51E819DC9D645C44997FD59AA8FE9E0C4A54A5DCA3762A4
backup=E:\CV农场助手\backups\v358-perfect-1.4.35-20260805
formal PID=25560
```

正式配置已核对并保持：

```ini
active_id = 1
share_target_name = 2135736062
share_send_requires_target_match = True
share_cancel_if_target_missing = True
[instance.1.friend] enable_process_friend = True
enable_steal = True
enable_help = True
enable_daily_troublemaker = True
[instance.1.bot] backpack_seed_priority = True
daily_share_time = 00:31
check_interval = 12
high_performance_mode = False
```

根级默认 `enable_daily_troublemaker=False` 与 `backpack_seed_priority=False` 是非活动默认值；活动实例 1 仍为 True，未擅自改变用户设置。

备份包含部署前 hook、VERSION、launcher、VBS、完整 `UserData` 570 个文件和 `manifest.json`。正式部署只替换 `hook.py` 与 `VERSION`，没有覆盖 UserData、配置、分享联系人、好友开关、背包优先、本地 VIP、计数或 CSV。

### 剩余现场签收（不阻塞已部署 v358）

1. **真实好友请求/好友列表**：新会话必须从第一位开始；第一位偷菜、帮助完成或多帧明确无动作后才到第二位；无强证明不计数；回家必须真实转场；不得再出现 friend 画面但 `scene_hint=home`。
2. **随机局部收获种植**：用户只需随机施肥几块至可收获；从确认收获开始，正常 20–60 秒、硬上限 120 秒补齐真实空地；完整田字格才用 2×2，不完整/失败同轮 1×1，不买等级作物、不重复打开背包。
3. **用户指定每日窗口**：验证 exact target、奖励、canonical/`.hook`/Local mirrors、双 CSV 与重启零重复。

这些自然现场机会仅作最终实机签收，不再作为继续开发、测试、性能、备份或部署的等待条件。
<!-- V358-HANDOFF-END -->


<!-- V359-HANDOFF-START -->
## 2026-08-05 v359 / 1.4.36 最终交接

### 本轮真实 P0 与根因

1. **满地自家 + 新好友求助**：旧 _qqfarm_friend_guard_empty_latched 在自家本来满地时没有释放；现在只由 fresh visible home frame + 精确“好友求助”文字/气泡证明打破，保持 home scene 直到真实转场。
2. **单块收获空地被隔离 900 秒**：post-harvest confirmed 坐标绕过单次 native label miss；普通弱候选仍保留原 quarantine 防误点。
3. **confirmed metadata 在 queue merge 中丢失**：同中心 weak-first/confirmed-second 现在合并 _qqfarm_post_harvest_confirmed、_qqfarm_visual_soil_proof 和最大 confidence。
4. **post-harvest 未完成却假满地**：_qqfarm_post_harvest_pending 已加入 stable-full-board、terminal-zero 和 home-priority release 的显式门禁。
5. **实机末行漏巡**：正式日志显示 resume cursor=4/5 后新列表被 v358 重置为 0。v359 最终补丁用 resume_pending && !exhausted 区分同轮恢复与 stale/new session；同轮继续第五行，exhausted 新会话才回到第一行。

### RED→GREEN 证据

~~~text
v359 Luna gaps RED: 11 tests, 4 failures
v359 Luna gaps GREEN: 11 / 11 OK
last-row live RED: expected row 5, clicked row 1
last-row live GREEN: 6 / 6 OK
affected friend set: 361 / 361 OK
friend suite: 416 / 416 OK
planting/empty/backpack suite: 269 / 269 OK
full discover: 1042 / 1042 OK
py_compile: OK
git diff --check: OK
hook BOM: False
~~~

关键证据：

~~~text
.analysis\v359-luna-gaps-red-20260805.txt
.analysis\v359-luna-gaps-green-20260805.txt
.analysis\v359-last-row-resume-red-20260805.txt
.analysis\v359-last-row-resume-green-20260805.txt
.analysis\v359-final-friend-suite-after-last-row-20260805.txt
.analysis\v359-final-full-discover-after-last-row-20260805.txt
~~~

### 性能、正式运行与实机好友闭环

最终隔离性能：

~~~text
120 / 120 samples
complete PID tree=true
Responding=False=0
cpu delta=49.375s
mean one-core=41.15%
max working set=515084288
max threads=89
source artifact frozen=true
source hook frozen=true
source=isolated hook=true
formal config unchanged=true
process tree stopped=true
production config touched=false
failure=null
~~~

正式稳定 120 秒：

~~~text
PID=11436
Responding=False=0
cpu delta=40.46875s
mean one-core=33.72%
max working set=515940352
max threads=89
Traceback=0
PrintWindow timeout=0
friend empty-latch hot loop=0
single empty (185,454) quarantine=0
~~~

同一正式观察段：

~~~text
returned unvisited row: resume cursor=4/5  -> 1
resuming saved cursor=4/5                  -> 1
visit cursor=4/5                           -> 1
reset stale cursor=4 pending=4 to zero     -> 0
~~~

因此最终实机已经证明：巡检中断后第五行会恢复并访问，不再长期漏掉末行；真正的新列表会话仍由已有 P0 测试证明从 cursor 0 开始。

### 正式身份与回滚

~~~text
VERSION=1.4.36
source/deploy hook bytes=1758643
source/deploy hook SHA-256=44A97C96B29D80AEAC37EBD0B2A0D0C1C59EA042E12B80678705309C71DD3321
friend request template SHA-256=58EF867C4354B9D1CD8FB1D022A2936BC59D5657C9767001679C9B53BF3E7D45
formal config SHA-256=5A63582C4A6A9153B51E819DC9D645C44997FD59AA8FE9E0C4A54A5DCA3762A4
UserData files=570
backup=E:\CV农场助手\backups\v359-final-last-row-1.4.36-20260805
~~~

正式部署只替换应用文件；配置、联系人、好友开关、背包优先、VIP、本地权益、计数、CSV 和完整 UserData 均保留。

### 剩余自然现场签收

当前自家 24 块地已种满，因此没有新的随机局部收获机会。下一次用户随机施肥/收获少量地块时，只观察：

~~~text
收获确认 -> post-harvest snapshot -> 背包真实 1×1/完整 2×2 -> 20–60 秒补齐，最迟 120 秒
~~~

每日任务/分享已由持久状态与自动化门保护；用户指定窗口的 exact-target、奖励、双 CSV、重启零重复仍可作为非阻塞现场复核，不等待跨日再推进任何代码工作。
<!-- V359-HANDOFF-END -->


<!-- V374-TERRA-HANDOFF-START -->
## 2026-08-06 v374 现场否决与 Terra-ultra 续接交接

### 0. 本节优先级

本节基于 **2026年8月6日（Asia/Shanghai）** 的真实截图、正式日志和 v374 隔离运行，覆盖此前“种植专项通过即可签收”的旧判断。下一次对话先读本节，再读历史章节。

用户决定后续 QQ 农场助手任务统一由 **Terra-ultra** 执行。此项目后续不再使用 Sol/Luna 分工；由一个 Terra-ultra 主执行者串行拥有 `portable\hook.py`，测试、性能、文档也由同一执行链收口，避免共享大文件的状态漂移。

### 1. 当前唯一可信的现场真值

v374 现场画面共有 24 格：

```text
3 个完整 2×2 已种组 = 12 格 occupied
其余 12 格 = empty
本轮真实新增种植 = 0
```

因此以下日志提交全部作废：

```text
12→7，提交 5 格
7→2，再提交 5 格
下一轮又读成 3 格 / 9 格
```

对 2×2 动作，合法变化只允许 `0` 或 `4`；对单次 1×1 动作，合法变化只允许 `0` 或 `1`。`5` 属于不可提交的异常差值。

### 2. 已固化现场证据

```text
tests\fixtures\live-v374-three-2x2-twelve-empty-false-commit-20260806.png
bytes=508363
SHA-256=A6F8DE35F4017B23BE1464D572E4E0D2CBC9E2BEC0700F2F5CADCCD0AB5835FF
真值：3 个完整 2×2 占 12 格，剩余 12 格；此前计数提交为假。

tests\fixtures\live-v374-gold-land-panel-twelve-empty-20260806.png
bytes=512367
SHA-256=0AE4E1EE343D4F65E46432ABA3FDC5D5F69781B6FADC01D20E778CBDC7CEC6E6
真值：种子栏和“金土地”气泡仍在，画面状态不具备播种提交资格。

tests\fixtures\live-post-harvest-single-empty-quarantined-20260805.png
SHA-256=4DB29108DCA1CF815285AED3ABEB7773EBEB1AF2DCC6FC65DAC0CBCA764295AF
真值：1 块紫色真实空地，单次标签缺失不应进入 900 秒隔离。
```

v374 日志证据：

```text
v374-hook-segment-utf8.txt:135  before=12 after=7 committed=true
v374-hook-segment-utf8.txt:160  before=7 after=2 committed=true
v374-hook-segment-utf8.txt:196  下一轮 empty=3
v374-hook-segment-utf8.txt:211/221/223/325... empty=9
```

历史正式性能异常证据仍有效：

```text
E:\CV农场助手\logs\hook_runtime_log.txt:45676
backpack priority elapsed=219.993s

E:\CV农场助手\logs\hook_runtime_log.txt:45684
process_self_farm elapsed=225.841s
```

v374 隔离性能：

```text
120 / 120 samples
Responding=False=0
max working set=1,248,489,472 bytes
max threads=129
failure=null
```

它只证明进程仍响应，不满足性能发布门。

### 3. 当前源码与正式目录

```text
源码：E:\CodexProjects\qq-farm-cv-helper-portable\portable\hook.py
bytes=1,915,469
SHA-256=5F4025741F9FB65D84E32709023BAD3453B72908D8AF5A9DB67B86285DF0123D
状态：v374 候选，未部署，未签收。

正式：E:\CV农场助手\hook.py
bytes=1,758,643
SHA-256=44A97C96B29D80AEAC37EBD0B2A0D0C1C59EA042E12B80678705309C71DD3321
VERSION=1.4.36
状态：正式旧版；继续保持停止。

正式配置 SHA-256=
5A63582C4A6A9153B51E819DC9D645C44997FD59AA8FE9E0C4A54A5DCA3762A4
```

源码与正式 Hook 不同。完成新门禁前禁止部署源码候选，也禁止覆盖配置、`UserData`、VIP、分享联系人、计数和 CSV。

### 4. 根因：把不等价截图的模板数量差当成种植事实

当前 `_wrap_planting_outcome_verify_func(...)` 的核心提交条件仍是：

```python
current_empty_count < baseline_empty_count
```

但 `baseline` 与 `post-action` 可能分别来自：

```text
无遮挡农田
种子栏打开
土地名称气泡显示
2×2 绿色/灰色覆盖层
相机被拖拽后的不同视野
作物动画的不同帧
```

这些画面之间禁止直接做数量相减。v374 的 `12→7→2→3/9` 正是页面状态、遮挡和视野变化导致的模板候选波动，不是地块真实状态变化。

同时 `_qqfarm_run_preopened_backpack_candidates_fast(...)` 会复用同一张旧种子栏截图，顺序尝试最多五张卡，并把每张卡拖过当前全部候选坐标；失败后又跨轮从 `#1` 开始。这造成错误提交、225 秒单轮和明显卡顿。

### 5. 必须替换为固定 24 格事务账本

新增一个独立的 24 格账本层。建议命名：

```text
_qqfarm_build_24_plot_ledger(frame, previous=None)
_qqfarm_align_24_plot_ledger(before, after)
_qqfarm_verify_plot_transaction(before, after, attempted_slots, seed_kind)
```

固定槽位：

```text
P01 ... P24
```

每个槽只允许：

```text
empty
occupied-1x1
occupied-2x2
unknown
```

2×2 额外保存：

```text
group_id
四个成员槽位
完整田字格几何
```

账本规则：

1. `empty_count` 从 24 个固定槽位状态派生，模板命中总数只作候选证据。
2. 任何面板、气泡、确认层或场景不一致时，将受影响槽位置为 `unknown`，保留上一可信状态，不从账本删除。
3. 前后帧先做棋盘/相机平移对齐；对齐失败则本动作保持未确认。
4. 提交前必须关闭种子栏、土地名称气泡、2×2 确认层，并取得两张新鲜、无遮挡、同场景帧。
5. 1×1 事务只提交一个明确目标槽的 `empty → occupied-1x1`；每次增量只能是 1。
6. 2×2 事务只提交一个完整田字格四槽的 `empty → occupied-2x2`；每次增量只能是 4。
7. `5`、负数、目标外槽位变化、视野漂移、面板遮挡、单帧漏识别全部拒绝提交。
8. `planting_count`、日志“播种已确认”和 post-harvest pending 消费只由事务提交结果驱动。

### 6. 种子策略和 120 秒预算

固定策略：

```text
优先背包真实可用种子
→ 有完整田字格且 2×2 卡经确认时，只尝试指定四槽一次
→ 灰勾/叉号/无变化，同轮取消并切 1×1
→ 1×1 每次只对一个明确空槽执行并验证
→ 背包有可用库存时屏蔽等级作物购买
```

时间预算：

```text
收获确认开始计时
正常完成：20～60 秒
硬上限：120 秒
```

硬门禁：

- 一次候选卡最多一次真实动作；
- 禁止五张卡依次拖过全部土地；
- 禁止使用旧种子栏截图继续下一次动作；
- 每次动作后刷新账本，只保留仍为 `empty/unknown` 的槽；
- 到 120 秒保存 pending 槽并结束本轮，禁止让 `process_self_farm` 继续到 225 秒；
- 下轮从 pending 槽继续，不从候选 `#1` 无条件重启。

### 7. Terra-ultra 的强制 RED→GREEN 顺序

第一批只处理种植 P0，不碰好友和每日业务代码：

1. 新建 `tests\test_v374_24_plot_transaction_ledger_20260806.py`。
2. 使用两张 v374 fixture，先写 RED：
   ```text
   occupied=12
   empty=12
   occupied_2x2_groups=3
   committed_delta=0
   ```
3. 写 RED：普通种子栏仍可见时，`12→7` 禁止提交；关闭面板后账本仍为 12 空地。
4. 写 RED：2×2 动作的差值 5 禁止提交；合法成功只能精确提交四个指定槽。
5. 写 RED：1×1 只能提交一个指定槽；任意其它槽的消失不计数。
6. 写 RED：相机平移后先对齐 24 槽；仅候选总数变化禁止提交。
7. 写 RED：候选执行墙钟达到 120 秒时有界退出，保留 pending，停止继续 #1～#5。
8. 实现最小账本与事务验证，接入：
   ```text
   _wrap_planting_outcome_verify_func
   _qqfarm_run_preopened_backpack_candidates_fast
   _qqfarm_close_seed_panel_for_board_refresh
   _qqfarm_mark_visual_planting_success
   ```
9. 跑单测 RED→GREEN、受影响种植套件、完整种植 644+、`py_compile`、`git diff --check`。
10. 运行唯一隔离实例，证明空地真值、120 秒上限、内存/线程恢复；通过后再跑好友 416+、每日 223+ 和完整 discover。
11. 备份、部署、正式 120 秒观察；只在源码/正式 Hook 哈希一致、配置哈希不变时签收。

### 8. 性能发布门

以 v373 正常区间为基线：

```text
max working set：目标不高于 600 MiB
max threads：目标不高于 95
Responding=False：0
完整 PID tree：true
failure：null
process tree stopped：true
formal config unchanged：true
```

性能测试必须同时证明：

```text
单次 process_self_farm < 120 秒
没有 #1～#5 全土地重复拖拽
没有 OCR/capture 热循环
没有重复线程池增长
```

### 9. 好友与每日仍保留的验收项

种植 P0 GREEN 后继续，不等待跨日：

```text
好友：第一位→末位→真实回家；偷菜/帮助强证明；自动捣乱独立机会；无重复计数。
每日：精确联系人、任务奖励、canonical/.hook/Local 镜像、双 CSV、重启零重复。
```

### 10. 唯一下一动作

```text
Terra-ultra 先创建并运行
E:\CodexProjects\qq-farm-cv-helper-portable\tests\test_v374_24_plot_transaction_ledger_20260806.py
使“v374 画面仍为 12 空地、提交增量必须为 0”得到预期 RED；在看到 RED 前不修改 portable\hook.py。
```

### 11. 新对话可直接使用的续接提示

```text
使用 $qq-farm-cv-maintainer。当前日期按环境 2026-08-06 / Asia/Shanghai。
只用 Terra-ultra 执行，不调用 Sol/Luna。读取
E:\CodexProjects\qq-farm-cv-helper-portable\HANDOFF_2026-08-01_EMPTY_LAND_REGRESSION.md
最后的 V374-TERRA-HANDOFF。正式助手保持停止，先做唯一下一动作：
新增并运行 test_v374_24_plot_transaction_ledger_20260806.py，证明真实画面是
3 个 2×2 占 12 格、剩余 12 格、真实新增 0，旧 12→7 / 7→2 禁止提交。
严格 RED→GREEN，完成种植真值、120 秒性能、全量回归、备份部署后再结束。
```
<!-- V374-TERRA-HANDOFF-END -->

<!-- V374-LIVE-INVENTORY-CORRECTION-20260806-130759 -->
## 2026-08-06 live inventory correction and zero-click baseline (2026-08-06 13:14:58 +08:00)

The prior inference **"no 1x1 backpack seed" was false**. It mixed two distinct facts:

- a seed shelf being hidden in a frame (seed_panel_visible=false); and
- the backpack having no usable seed.

The user-provided live shelf frame is authoritative inventory evidence:

`	ext
C:\Users\11616\AppData\Local\Temp\codex-clipboard-4ee3e218-d071-42c8-af0c-7954e95147b5.png
SHA-256=B50E03B33EBB4AB7BD13260813BF30803682B5B0AC2B42AD98504F4611F5E028
`

User-confirmed reading of that frame:

`	ext
card #1 (Star-language bellflower) = 2x2
cards #2..#5 = usable 1x1 seeds (visible counts include 28, 5, 36, 8)
field = 3 completed 2x2 crops = 12 occupied, 12 true empty
`

A fresh WGC observation made **without any click** after the panel was closed is preserved at:

`	ext
E:\CV农场助手\logs\captures\v374-observe-20260806-130759\qqfarm-zero-click-frame-0.png
E:\CV农场助手\logs\captures\v374-observe-20260806-130759\qqfarm-zero-click-frame-1.png
E:\CV农场助手\logs\captures\v374-observe-20260806-130759\qqfarm-zero-click-frame-2.png
`

The retained regression fixture is:

`	ext
tests/fixtures/live-v374-three-2x2-twelve-empty-no-panel-20260806-130759.png
SHA-256=2399075960395B60FB4D404AA8248DD40A6405ADC8AD629B182A426181BF3C59
`

That zero-click frame establishes only seed_panel_visible=false and no active visible seed shelf. It must never be interpreted as zero stock. No planting click was sent after this baseline capture.

TDD evidence in this phase:

`	ext
RED: tests.test_v374_partial_lattice_mapping_20260806
4 failures, all because _qqfarm_fit_24_plot_lattice_from_candidates was missing.

GREEN: tests.test_v374_partial_lattice_mapping_20260806
4 / 4 OK
`

The new pure fitter maps explicit current-frame empty/occupied evidence into L01..L24, rejects repeated 2x2 geometry without a signed transform, and keeps unobserved slots unknown. It is not connected to the runtime planting commit path, is not deployed, and is not game sign-off.

Candidate source after this edit:

`	ext
portable/hook.py bytes=1937190
portable/hook.py SHA-256=E53FCA714245C008F3A488D81336F6DF54EFB1F5EAF59EC2F83A88E93A64B7AA
`

Next action: write the RED proving runtime success/counts cannot be committed from aggregate empty-count changes, then wire this fitter into the before/action/fresh-after transaction path. Do not use the stopped 1.4.36 deployment to perform the 12-slot fill.
<!-- V374-LIVE-INVENTORY-CORRECTION-END -->
<!-- V374-COMMIT-GATE-20260806 -->
## 2026-08-06 aggregate-count commit gate (2026-08-06 13:23:31 +08:00)

New real RED test:

`	ext
tests.test_visual_planting_commit_regression_20260806
12 -> 7 aggregate empty-template count, with no committed L-slot transaction
expected False; old code returned True
`

Minimal correction: _qqfarm_mark_visual_planting_success(...) now reads only a
validated context._qqfarm_last_planting_transaction as its authority for
metrics/logs/pending consumption. It rejects a missing, non-committed, malformed,
duplicate-slot, or delta/slot-length mismatched transaction. Numeric before/after
counts remain display/priority context and no longer create a planting commit.

Updated existing metric regression supplies an explicit committed transaction of
three L-slots. The metric delta derives from 	ransaction['delta'], not
efore_count - after_count.

Fresh verification:

`	ext
RED: 1 failure, old result True for false count-only 12 -> 7.
GREEN targeted: 16 / 16 OK
  - partial lattice: 4 / 4
  - 24-slot transaction ledger: 9 / 9
  - visual planting commit: 3 / 3
py_compile portable/hook.py: OK
git diff --check (affected files): OK
`

Candidate source is still undeployed:

`	ext
portable/hook.py bytes=1938729
portable/hook.py SHA-256=0BC59AC4F038574EE0DBB2BD4F2A2A87C04FC53D85C6DCC4A046BCBC32535327
formal deployment hook SHA-256=44A97C96B29D80AEAC37EBD0B2A0D0C1C59EA042E12B80678705309C71DD3321
`

This is a gate, not runtime integration: _wrap_planting_outcome_verify_func
still needs to build fresh before/after ledgers, call the exact validator, store
that transaction, and then invoke the commit gate. Until that wiring and its
RED/GREEN tests exist, do not deploy or use the candidate for the live 12-slot
fill.
<!-- V374-COMMIT-GATE-END -->

<!-- V377-VIEWPORT-REQUIREMENTS-START -->
## 2026-08-06 ? viewport / zoom / pan acceptance requirements

- Every observation and click uses a fresh captured frame; never reuse a previous L01?L24 coordinate transform after any camera pan, window/DPI-size change, or zoom.
- The geometry phase must rebuild the 24-slot transform from current-frame farm evidence. Purple/gold remain `land_quality` metadata only and never imply empty/occupied state.
- A normal or fully observable pan/zoom may align; a clipped, overlaid, ambiguous, or incompletely visible board must produce `unknown` / `viewport-not-full-board`, must not commit a ledger, and must not click a land slot.
- Regression coverage must include normal view, pan left/right/up/down, zoom-out with complete board, zoom-in/cropped board, UI palette decoys, seed-panel/land-popup overlays, and capture-size/DPI mapping.
- A final game sign-off still requires the three mature 2x2 crops to be harvested without the legacy 225-second backpack chain and the 12 true empty slots to be planted one at a time from backpack seed #2, with a current-frame before/after transaction proof and final `empty=0`.
<!-- V377-VIEWPORT-REQUIREMENTS-END -->

<!-- V385-STRICT-24SLOT-ROLL-OUT-20260807 -->
## 2026-08-07 strict 24-slot rollout pre-deployment evidence (Asia/Shanghai)

Live sign-off target remains exactly:

```text
occupied=12 / empty=12 / unknown=0
→ #2..#5 usable 1x1 seed cards fill only named Lxx slots
→ occupied=24 / empty=0 / unknown=0
→ close shelf and verify a fresh no-panel frame
→ whole chain <=120 seconds
```

The three existing 2x2 star-language bellflower groups occupy:

```text
(L08,L13,L12,L17)
(L11,L16,L15,L19)
(L20,L23,L22,L24)
```

The required 1x1 work list is:

```text
L01 L02 L03 L04 L05 L06 L07 L09 L10 L14 L18 L21
```

Gold/purple land remains `land_quality` metadata and never changes L01..L24 occupancy, click eligibility, or 1x1/2x2 transaction rules.

This phase added and verified strict refusal-state handling and rollout isolation:

- every strict reject clears stale `_qqfarm_last_planting_outcome_verified` and preserves exact transaction before/after counts, including valid `after_empty_count=0`;
- popup/overlay/unknown/unavailable ledgers cannot create replacement pending work or commit a planting action;
- strict pending Lxx blocks friend/daily/shop detours and preserves friend-chain flags while the self-farm sign-off chain is active;
- the hook UTF-8 BOM regression was reproduced as RED and removed before deployment.

Fresh final-source verification on 2026-08-07:

```text
RED: tests.test_hook_encoding -> 1 failure (portable/hook.py had UTF-8 BOM)
GREEN: tests.test_hook_encoding + tests.test_hook_runtime_identity -> 7 / 7 OK
strict ledger/overlay/pending/scheduler/rollout suite -> 89 / 89 OK in 39.159s
py_compile portable/hook.py -> OK
git diff --check (strict files) -> OK
no UTF-8 BOM -> OK
source hook bytes=1986464
source hook SHA-256=26D4BC925721CB2E909A1AEA19005B6BEC4093298D8237018C318DE2FF26BFCB
```

The deployed hook is still the old `44A97C96...DD3321` identity at this record. The next action is only: make a rollback backup, deploy this exact source hook, restart with `QQFARM_STRICT_PLANTING_ROLLOUT=1`, and collect the new game-frame/log proof. No live completion is claimed before that evidence exists.
<!-- V385-STRICT-24SLOT-ROLL-OUT-20260807-END -->
<!-- V392-DEPLOYED-FULL-BOARD-SIGNOFF-20260807 -->
## 2026-08-07 v392 deployed full-board ledger sign-off (Asia/Shanghai)

This record supersedes the earlier live `occupied=12 / empty=12` target **for the current scene only**.  The historical 12-empty frame remains a regression fixture; the live self-farm frame at deployment time is now fully occupied and must not trigger any planting, backpack, seed, land, friend, daily, or shop action.

### Narrow production change

The only runtime function bodies differing from the immediately preceding deployment are:

```text
_qqfarm_fit_dynamic_24_slot_lattice_from_geometry_anchors
_qqfarm_capture_current_frame_24_slot_ledger
```

`crop-geometry-full-board-only` is observation-only.  It may confirm `24 occupied / 0 empty / 0 unknown` when the crop geometry proves the entire board.  If even one later slot reads empty or unknown, the frame is reduced to `unknown` with `capture_reason=crop-only-full-board-unconfirmed`; it never grants an empty-slot click.

Gold/purple remains `land_quality` metadata only.  It does not change occupancy, click eligibility, or 1x1/2x2 geometry.

### Source / deployment identity and rollback

```text
source Hook    = E:\CodexProjects\qq-farm-cv-helper-portable\portable\hook.py
source/deploy  = 2,082,909 bytes
source/deploy  = E31CD2FC6D1814B07F47737DAF9621C080752116416AEE17FB85D2C82EC6DC6A
predeploy Hook = 2,024,839 bytes
predeploy SHA  = E49676A95795A34FCE9265273193E51E41D07CDBE3F4274E365FA02A8C07B1B5
rollback       = E:\CV农场助手\backups\v392-crop-only-full-board-ledger-20260807-204541
UserData       = preserved; 571 files / 148,254,540 bytes at backup time
```

The restarted process is PID `11696`, started at `2026-08-07T20:46:04+08:00`.  The strict marker contains `hook-loaded|...|pid=11696` and `page-ready|...|pid=11696`.

### Fresh deployed-game evidence

Both frames were captured by the restarted production process, have no seed panel / land popup / 2x2 overlay, and were analyzed using the deployed Hook hash above:

```text
2026-08-07 20:46:25 +08:00
self-no-action-20260807-204625-673-428x800x3-FarmBotCV-process-self-farm.png
SHA-256 DEFB1F89C5853877408CA5482AECF9D0287300CA7F76F4374FC780A41EE0ED73
aligned; crop-geometry-full-board-only; occupied=24; empty=0; unknown=0;
full_board_confirmed=True; anchors=11 matched / 2 unmatched

2026-08-07 20:48:26 +08:00
self-no-action-20260807-204826-430-428x800x3-FarmBotCV-process-self-farm.png
SHA-256 799BF04C3780C5BC685EE690698CF1537A5F8B1AED5295D84CB9F5F4C9B2800C
aligned; crop-geometry-full-board-only; occupied=24; empty=0; unknown=0;
full_board_confirmed=True; anchors=10 matched / 2 unmatched
```

Machine-readable analyses:

```text
E:\CV农场助手\logs\captures\analysis-v392-deployed-self-no-action-20260807-204625-673-428x800x3-FarmBotCV-process-self-farm.json
E:\CV农场助手\logs\captures\analysis-v392-deployed-self-no-action-20260807-204826-430-428x800x3-FarmBotCV-process-self-farm.json
```

### Fresh verification

```text
strict 24-slot / capture / rollout regression = 31 / 31 OK (15.146 s)
py_compile portable/hook.py = OK
git diff --check = OK
120.215-second production zero-action observation = PASS
  2026-08-07 20:51:58 +08:00 to 20:53:58 +08:00
  PID 11696 stayed alive and Responding=True
  strict self-only gate lines = 18
  prohibited planting/backpack/seed/land/friend/daily/shop action lines = 0
  evidence = E:\CV农场助手\logs\strict-24slot-v392-zero-action-observation-20260807-205158.json
```

A full source discovery was also run: `1163` tests executed, `18` historical preflight tests remain RED.  They all exercise pre-existing preflight behavior that already exists in the preceding deployment (`_qqfarm_open_seed_panel_for_backpack_preflight`, planting-flow, backpack-priority, and empty-land wrapper AST bodies match source/deploy).  They are recorded at:

```text
E:\CodexProjects\qq-farm-cv-helper-portable\.analysis\full-discover-tests-20260807-2034.log
```

They are not represented as a clean global suite.  This v392 record signs off only the deployed **full-board observation / zero-action** path.

### Still awaiting a real partial-harvest scene

The current game scene has no known empty L-slot.  Therefore no 1x1 or 2x2 planting action was sent during this sign-off.  A real partial-harvest acceptance remains pending:

```text
fresh no-panel current frame
→ aligned known ledger with explicit empty Lxx
→ one named 1x1 transaction per Lxx (or one exact 2x2 four-slot transaction)
→ fresh post-action ledger after every action / bounded micro-batch
→ only committed Lxx changes counts
→ close panel and verify empty=0
→ entire planting chain <=120 seconds
```

**Next action:** wait for the next real self-farm frame containing explicit empty L-slots; then run the named-slot planting transaction acceptance without using aggregate template-count deltas.
<!-- V392-DEPLOYED-FULL-BOARD-SIGNOFF-20260807-END -->

<!-- V400-ACTIVE-FULL-BOARD-SCOPE-START -->
## 2026-08-08 active full-board release scope (Asia/Shanghai)

The active narrow release target is not a historical crop count.  It applies only
when a fresh no-panel game frame proves the entire fixed ledger:

```text
occupied=24 / empty=0 / unknown=0
? observation_only full-board proof has no click authority
? stale strict self pending/temporary lease is cleared
? existing friend-patrol entry is allowed
? no land/seed shelf/plant/harvest/shop action occurs on the self board
```

Gold/purple terrain stays `land_quality` metadata only.  It never changes
occupancy, 1x1/2x2 geometry, seed selection, success counters, or click targets.
The release sequence is mandatory:

```text
live capture ? reproduce/RED ? minimal fix ? automated verification
? source/deployment Hook SHA-256 equality ? hidden restart
? 120-second live game observation
```

A later real 1x1 transaction sign-off needs a fresh frame with explicit empty Lxx
slots.  It is retained as a separate pending acceptance and does not block this
24/0/0 full-board release.

**Next action:** finish the fresh full discovery classification, then deploy only
if the current mixed full-board regression and all remaining global failures are
separated by evidence before the 120-second live sign-off.
<!-- V400-ACTIVE-FULL-BOARD-SCOPE-END -->

<!-- V406-CANDIDATE-20260808-2043-START -->
## 2026-08-08 v406 candidate: stale full-board pending releases verified friend patrol

This candidate is **source-verified but not yet deployed or live-signed-off**.
It narrows only the strict 24-slot routing behavior:

- A complete, aligned, non-clickable observation ledger may retire *ordinary*
  malformed self-route residue only when it is exactly
  `capture_reason=cropped-full-board-observation`, `occupied=24`, `empty=0`,
  `unknown=0`, `full_board_confirmed=True`, `click_safe=False`, no blocked UI,
  zero slot centers, and all `L01..L24` are occupied.
- A `malformed-noncanonical-2x2` pending group remains a hard hold: it gets no
  partial observation, no self action, no normalization, and no friend handoff.
- A successful real friend-list row/candidate entry records the canonical
  `friend-list` surface marker only after the click has been verified, allowing
  the normal friend patrol settle path to own the following cycle.
- A partial viewport remains `occupied=0 / empty=0 / unknown=24`; it has no
  home planting/harvest/backpack/shop click authority. Two fresh partial home
  observations may hand off to friend patrol without clearing verified Lxx work.

### TDD and source evidence

```text
RED (previous source): test_verified_friend_entry_reaches_patrol_on_next_cycle_after_observation_only_full_board
  expected ordinary stale malformed pending to block patrol; first_result=False,
  second_result=False, events=[]

GREEN targeted suite at 2026-08-08 20:43 +08:00:
  10 / 10 OK (v403, v405, v382, v383)

Full discovery at 2026-08-08 20:31:26–20:42:56 +08:00:
  Ran 1205 tests in 689.262s
  failures=17
  v405 baseline failures=18; v406 adds zero new failures and removes exactly:
  test_verified_friend_entry_reaches_patrol_on_next_cycle_after_observation_only_full_board

Static checks at 2026-08-08 20:43 +08:00:
  python -m py_compile portable\hook.py = OK
  git diff --check = OK

Candidate source identity before deployment:
  portable\hook.py = 2,170,567 bytes
  SHA-256 = DEA07B5EF65C5E3355B4A2827F2A0560DEB585BB99EAF4A894B557E8566B7A83
```

The 17 retained full-discovery failures are the previously recorded historical
preflight/pending-review failures; their names are unchanged from the v405
baseline. They are not a clean global-suite sign-off and must remain explicitly
visible in release evidence.

**Next action:** back up the deployed runtime files, copy only `portable\hook.py`,
verify source/deployment SHA-256 equality, hidden-restart, then take a fresh
120-second game observation with runtime identity, partial/full-board no-click,
and friend-patrol handoff evidence.
<!-- V406-CANDIDATE-20260808-2043-END -->
<!-- V410-BOTTOM-FRIEND-NAV-LIVE-SIGNOFF-20260808 -->
## 2026-08-08 v407–v410 friend-entry continuation and v410 live evidence (Asia/Shanghai)

The active evidence distinguishes a repaired friend-entry/patrol path from the still-independent self-farm planting and harvesting acceptance.

- v407 retained the visible `好友求助` card route as the preferred physical entry; a click becomes a friend transition only after a fresh friend-list or friend-farm frame.
- v408 verified that production templates remain loadable from Unicode deployment paths.
- v409 prevents a frame verified as `friend-list` or `friend-farm` from being repeatedly reclassified by the strict self-farm gate.
- v410 adds the fallback only when the physical self-home frame visibly contains the normalized bottom-right `好友` control.  It searches only `x=335..428, y=675..800` at 428x800, requires score >= 0.78 and the expected small hit box, sends one click, and writes friend pending state only after a fresh friend-list/friend-farm proof.  A missed transition holds retry for 12 seconds; it does not create a click loop.

Production template:

```text
portable/friend_bottom_nav_button.png
bytes=9541
SHA-256=998B292B374D2A89EBDB15C30CD57AE9BDC4AFD2DF0F4BCE2E8BE6574C3FF5F1
```

TDD evidence:

```text
RED: test_v410_visible_bottom_friend_nav_entry_20260808.py
  current physical self-home frame yielded no visual candidate before v410
GREEN: v410 directed test, 2 / 2 OK
Affected friend routing suite: 20 / 20 OK
py_compile portable/hook.py: OK
git diff --check (v410 files): OK
```

Deployment identity after the versioned backup `E:\CV农场助手\backups\v410-bottom-friend-nav-20260808-222026`:

```text
source/deployed hook bytes=2180971
source/deployed hook SHA-256=347C1B4298C26F556D0EFE119BFEA60285CC7C32CEFC8618CDA329F4F01F8B5B
source/deployed friend_bottom_nav_button.png SHA-256=998B292B374D2A89EBDB15C30CD57AE9BDC4AFD2DF0F4BCE2E8BE6574C3FF5F1
config SHA-256=5A63582C4A6A9153B51E819DC9D645C44997FD59AA8FE9E0C4A54A5DCA3762A4
```

Live game observation is retained at:

```text
E:\CV农场助手\logs\captures\v410-live-observation-20260808-222342
```

During its 120.09 seconds, the deployed runtime recorded two physical bottom-nav fallbacks and two verified transitions, with zero verification misses/retry-gate events/Tracebacks/ERRORs.  The route progressed through the actual friend list and one visually verified friend-help action.  The durable confirmed help count changed from 3 to 4 during that observation; later runtime activity may advance the daily count further and is not retroactive proof for this sign-off.

This is a live sign-off for the narrow `self home -> friend list -> patrol -> confirmed help` path.  It is not a claim that all self-farm planting, harvesting, backpack, shop, daily, or every friend-layout variant has been signed off.

**Next action:** capture the current physical self-home frame and current runtime segment; if neither the request card nor the v410 bottom navigation control is visible, reproduce that exact no-entry layout in a RED test before adding another entry route.
<!-- V410-BOTTOM-FRIEND-NAV-LIVE-SIGNOFF-END -->


<!-- V412-FRIEND-CAROUSEL-PRECEDENCE-LIVE-SIGNOFF-20260808-START -->
## 2026-08-08 v412 strict friend-carousel precedence: deployed, live-signed scope

### Problem and smallest change

A real friend farm can show artwork visually similar to the centered self-farm
one-key action. Before v412, that weak self template could override the
established friend classifier and incorrectly send the physical friend frame
into the strict 24-slot self-farm route.

`_qqfarm_strict_self_scene_state(frame)` now checks the selected bottom friend
carousel only after the base classifier has returned `True` (friend) and before
the generic self-action fallback. A present selected carousel returns `True`
and preserves the friend route. No planting, harvest, backpack, shop, daily, or
generic friend-layout behavior was changed in this patch.

### TDD and automated evidence

The RED fixture is the physical 579x1063 friend-farm frame
`tests/fixtures/live-v411-window-fit-friend-farm-home-carousel-20260808-225245.png`
(SHA-256 `2B52E6868856D36FA152F82E56A689832B50019262917CD932E3ED8BF6AD8150`).
It visibly contains the Home control and a green selected bottom-carousel card,
while the generic self-action artwork is also detectable.

The smallest regression is
`tests/test_v412_strict_friend_precedence_20260808.py`; it proves both that the
frame remains `friend` (`True` in the strict scene classifier's established
three-state contract) and that the strict 24-slot gate hands it to normal
friend patrol without invoking a self transaction.

Recorded GREEN evidence:

```text
v412 + v388 directed: 7 / 7 OK, 5.617 s
friend routing regression: 56 / 56 OK, 29.636 s
friend empty-return-home guard: 328 / 328 OK, 189.604 s
python -m py_compile portable/hook.py: OK
git diff --check: OK
```

Logs:

```text
E:\CodexProjects\qq-farm-cv-helper-portable\.analysis\v412-friend-routing-regression-20260808-233631.log
E:\CodexProjects\qq-farm-cv-helper-portable\.analysis\v412-friend-empty-return-home-guard-20260808-233717.log
```

### Deployment identity and rollback

Only `portable/hook.py` was copied after backup:

```text
backup:
E:\CV农场助手\backups\v412-strict-friend-carousel-precedence-20260808-20260808-234118

predeploy hook:
bytes=2183108
SHA-256=D8777C953779CBF7E7D6F072A3A8683C1190B109F53888B9250BA73FC6D6FD2A

source/deployed v412 hook:
bytes=2183686
SHA-256=CDD9B75292713C75195FAE887E295C3195DF17012D5BF2EA29277C81A9254C51
identity_match=True
```

The hidden restart created `QQFarmCVHelper` PID `33152` at the recorded local
start time `2026-08-08 23:42:44 +08:00`; the runtime wrote the same Hook
identity.

### Live game acceptance

Authoritative capture bundle:

```text
E:\CV农场助手\logs\captures\v412-live-friend-route-window-20260808-20260808-235835
```

`desktop-t000.png`, `desktop-t001.png`, and `desktop-t005.png` show the live
friend farm with Home plus the selected green bottom carousel. The runtime then
produced exactly one:

```text
v409 strict 24-slot gate yielded current physical friend farm to normal patrol flow
```

followed by exactly one normal return:

```text
v96 friend home delivered by client-only click
```

`desktop-t015.png` is already the self farm after that return. The bundle
records no v122/v144/v395/v405 loop signature on the friend frame, no self
transaction signature, zero Traceback/ERROR, and 42/42 responsive helper
samples over the observation window. The JSON contains the literal artifact
timestamp `2026-08-09T00:00:40.3228598+08:00`, which is after the current local
date `2026-08-08`; it is retained only as raw capture metadata and is not
daily-counter rollover acceptance.

**Scoped verdict:** v412 accepts only this live `friend farm + Home + selected
carousel -> normal friend patrol` route. It does not accept 24-slot planting,
harvest, backpack, shop, daily paths, or every friend layout.

**Exactly one next action:** from the current physical self-home frame, collect
a fresh, fully visible, no-panel 24-slot ledger and execute the existing v374
RED test for the first observed ledger/transaction defect. Do not resume legacy
aggregate-template-count planting.
<!-- V412-FRIEND-CAROUSEL-PRECEDENCE-LIVE-SIGNOFF-20260808-END -->

<!-- V419-PHYSICAL-PRINTWINDOW-PROVENANCE-20260808-START -->
## 2026-08-08 v418/v419 physical full-board provenance sign-off (Asia/Shanghai business date)

### Narrow signed behavior

This sign-off applies **only** to a fresh, complete self-farm frame obtained by
`PrintWindow(PW_RENDERFULLCONTENT)` from the real `QQ经典农场` window.  Its public
24-slot ledger contract is exactly:

```text
occupied=24
empty=0
unknown=0
full_board_confirmed=True
observation_only=True
click_safe=False
slot_centers={}
complete_2x2_groups=()
capture_reason=physical-window-normalized-full-board-observation
```

It is an observation-only proof: no land, seed shelf, backpack, shop, plant,
harvest, friend, daily, or performance behavior is accepted by this section.
Gold/purple terrain remains `land_quality` metadata; it has no bearing on
occupancy, grid geometry, seed selection, transaction count, or click authority.

### Live RED and smallest correction

The raw physical frame fixture
`tests/fixtures/live-v418-current-seedling-full-board-physical-20260808.png`
(SHA-256 `B0DCCB24BE42F3D5013D3A576DD98DAF8517820184AAB414974010BB7C6C9873`)
initially reached a correct `24/0/0` count but retained the unsafe reason
`seedling-only-full-board-observation`, `click_safe=True`, and click centers.
The dedicated RED is
`tests/test_v418_live_physical_seedling_full_board_observation_20260808.py`.

The smallest change is in `portable/hook.py`:

1. `_qqfarm_capture_visible_farm_frame(prefer_desktop=True)` marks the exact raw
   `PrintWindow` frame object it returns;
2. `_qqfarm_capture_current_frame_24_slot_ledger()` uses that provenance marker
   (or an explicit diagnostic physical label) rather than portrait dimensions;
3. an exact physical `24/0/0` result is normalized only to the no-coordinate,
   observation-only contract above.

An ordinary portrait fixture is therefore not reclassified solely by its shape,
and a physical frame that is partial, UI-blocked, unknown, or has real empty
`Lxx` slots is preserved as its actual result rather than being rewritten to
`24/0/0`.

### Automated and deployment evidence

The targeted regression/capture suite was freshly run after the correction:

```text
33 tests in 29.269 s: OK
python -m py_compile portable/hook.py: OK
git diff --check: OK
```

The source and deployed Hook are identical:

```text
path: E:\CodexProjects\qq-farm-cv-helper-portable\portable\hook.py
path: E:\CV农场助手\hook.py
bytes: 2,264,583
SHA-256: 6804DC4D712FD609A6DCDB8111AB2CE08471EA56073AD9A8791D438E449A945A
rollback backup:
E:\CV农场助手\backups\v419-physical-printwindow-provenance-20260808-025222
```

The hidden-restarted runtime wrote its deployed Hook identity.  Its 120-second
read-only observation is retained at:

```text
E:\CV农场助手\logs\observations\20260808-v419-full-board-readonly-120s.json
E:\CV农场助手\logs\observations\20260808-v419-full-board-readonly-120s.log
```

That run recorded `12/12` responsive helper samples, `input_generated=False`,
`Traceback=0`, `ERROR=0`, and zero land-click/seed-panel/backpack/shop/planting
transaction markers.  It also recorded 10 physical observation markers and 10
strict-self-gate-false markers.

### Fresh post-observation physical capture

After that 120-second observation, a separate zero-input deployment-side capture
called the deployed strict selector and the deployed 24-slot observer in one
namespace.  The frame id intentionally contained neither `physical` nor
`printwindow`; physical provenance was proven by the deployed marker itself.

```text
artifact:
E:\CV农场助手\logs\captures\20260808-v419-post-observation-deployed-provenance.png
SHA-256: AA452B0364A6CEAB5B25BC17B72D799B2674EFC0BA5B4F3AD2311C61F9852100
machine record:
E:\CV农场助手\logs\captures\20260808-v419-post-observation-deployed-provenance.json
window: QQ经典农场, HWND 198862
physical frame: 579 x 1063 BGR
marker_frame_id_matches=True
input_generated=False
capture_status=aligned
capture_reason=physical-window-normalized-full-board-observation
occupied=24 / empty=0 / unknown=0
full_board_confirmed=True
observation_only=True / click_safe=False
slot_centers={} / complete_2x2_groups=()
```

The business date for this evidence is `2026-08-08`.  Host-clock text embedded
in raw diagnostic artifacts is preserved as capture metadata only and never
changes daily-state or acceptance-date interpretation.

**Scoped verdict:** the physical full-board observer is now evidenced as
zero-input, no-coordinate, and stable through the required post-observation
recapture.  Fixed-slot planting/harvest, backpack, shop, friend, daily, CPU,
and a real `empty Lxx` 1x1/2x2 transaction remain separate acceptance items.
<!-- V419-PHYSICAL-PRINTWINDOW-PROVENANCE-20260808-END -->

<!-- V424-CURRENT-FRIEND-FARM-LOW-EDGE-20260808-START -->
## 2026-08-08 v424 current friend-farm classification candidate

A fresh physical friend-farm frame (profile Jiangshangyue, visible return-home
control, and selected lower carousel card) was captured while the strict gate
incorrectly took the self route.  The immutable source fixture is:

```text
tests/fixtures/live-v424-current-friend-farm-home-carousel-20260808-040620.png
raw physical size: 642 x 1200 BGR
SHA-256: BD2B9FA71E8507771CDF5E4FD3F7DC37975E5AE1DBEBE94AACB16B4FD7C554DA
runtime input: cv2.resize(raw, (428, 800), INTER_AREA)
```

Before the correction, `_friend_guard_friend_ui_state()` returned `False` for
that exact normalized input.  The observed evidence was `gray=0.671328`,
`edge=0.231168`, center `(394,607)`, plus a valid selected carousel card.
This is a resampling-sensitive low-edge control, not an empty-land or planting
condition.

v424 preserves the existing `gray>=0.62 and edge>=0.24` dark-skin evidence
band and adds only the more constrained `gray>=0.66 and edge>=0.20` band.  Both
require the lower-right control position and a selected carousel card.  The
fixture, a known self-home frame, the live friend list, and the task panel are
covered by `tests/test_v424_current_friend_farm_classification_20260808.py`.

Automated candidate evidence is separate from game acceptance.  After source
and deployment hashes are made identical, restart and observe the live game:
the current friend farm must enter friend patrol without any self-land,
seed-panel, backpack, or shop click; counts advance only after visible action
confirmation.
<!-- V424-CURRENT-FRIEND-FARM-LOW-EDGE-20260808-END -->

<!-- V427-RAW-PRINTWINDOW-FRIEND-ROUTE-ACCEPT-20260808-START -->
## 2026-08-08 v427 raw PrintWindow current-friend routing acceptance

### Scope and original RED

This sign-off is intentionally limited to the strict self-only gate misclassifying
an actual friend-farm frame that has both a visible return-home control and a
selected lower friend-carousel card.  It does not broaden thresholding for other
friend skins and does not sign off planting, harvest, backpack, shop, daily, or
all-friend-layout behavior.

The immutable RED fixture remains:

```text
tests/fixtures/live-v426-current-iris-friend-farm-20260808.png
raw physical shape: 1200 x 642 x 3
SHA-256: 5B096B6886993721E3FE245996E402F0E1334323EF20AD80FD8F24357FC54E6B
```

On the old v426 branch it was rejected because its raw physical return-home
center `(591,911)` was compared with fixed normalized coordinates, and its raw
edge response `0.1577466` was just below the old `0.16` lower edge threshold.
The v427 classifier uses the same compact return-home region scaled to the
current frame dimensions, with the low-edge band accepted only together with a
selected carousel card, `gray >= 0.63`, and `edge >= 0.15`.

### Fresh 2026-08-08 field evidence

A single operator-equivalent navigation click opened the visible current friend
card.  From then on the observer produced no input.  The preflight is a
DPI-aware physical `PrintWindow` frame:

```text
E:\CV农场助手\logs\captures\v427-friend-signoff-20260808\dpi-aware-preflight-current-friend.png
shape: 1200 x 642 x 3
SHA-256: 79701A570874192C30B6CEEDE7CD7172EEE6DEC1AEB7522B01BCFF6B7627C751
strict friend state: True
match: night-home+selected-carousel-low-edge
gray=0.7004297 / edge=0.2314490 / center=(591,910)
```

The deployed v427 Hook was then observed for `120.087` seconds in:

```text
E:\CV农场助手\logs\captures\v427-friend-signoff-20260808\observation-120s\
```

It contains 13 DPI-aware `PrintWindow` samples, all `642 x 1200`, with
`PrintWindow=13/13`, helper running/responding `13/13`, observer input
`False`, `Traceback=0`, and `ERROR=0`.  The isolated runtime delta records:

```text
v403 verified-friend handoff to normal patrol: 7
night-home+selected-carousel-low-edge friend proof: 3
bounded no-action friend completion / v96 verified return home: 3 / 3
v393 strict self transaction hold: 0
stale non-home frame accepted as self: 0
```

A later self-home pass occurred only after the recorded `v96 friend home
delivered by client-only click`; it is not a self transaction on the friend
frame.  The field sequence therefore demonstrates that the selected current
friend farm is handed to the friend flow and returned normally without entering
the strict self 24-slot transaction.

### Fresh verification and identity

```text
v426 + v427 directed classifier tests: 2 / 2 OK
v403/v405/v407/v409/v410/v411/v412/v420/v422/v423/v424/v425/v426/v427: 27 / 27 OK
python -m py_compile portable/hook.py: OK
git diff --check (hook and v427 test): OK
source/deployed hook bytes: 2,273,828 / 2,273,828
source/deployed SHA-256: 82521DF5829D7AFEDF9FA888F404DD77711C8141A57B3170186E4F2A2C5DA57D
```

All raw host-clock timestamps inside capture files are metadata only.  The
business and acceptance date for this sign-off is `2026-08-08`.

**Scoped verdict:** v427 is field-signed for the captured raw physical
return-home + selected-carousel current friend-farm route.  Other friend
layouts and all non-routing modules retain their separate acceptance gates.
<!-- V427-RAW-PRINTWINDOW-FRIEND-ROUTE-ACCEPT-20260808-END -->

<!-- V2.2.5-CLEAN-MIGRATION-20260809-START -->
## 2026-08-09 clean v2.2.5 runtime migration

The user selected a clean-runtime migration instead of another edit to the legacy
multi-megabyte hook.  The resulting layout is:

```text
E:\CV????\runtime-v2.2.5\      clean v2.2.5 business runtime
E:\CV????\StartFarmAssistant-Clean.ps1  independent switch entry
E:\CV????\hook.py                 retained legacy rollback runtime
```

The clean runtime keeps the v2.2.5 executable and proxy identities, adds only a
929-byte bootstrap plus a 14,052-byte isolated customization module, and shares
the existing portable UserData profile.  The customization module provides the
combating123 GitHub target, exact-recipient daily-share settings compatibility,
and narrowly suppresses only `??` dialogs containing VIP-price/free-feature
promotion text.  It explicitly preserves error dialogs and the VIP-card window.

Automated evidence on 2026-08-09: clean migration 6/6 OK; standalone runtime
layer 13/13 OK; deployment-layout 5/5 OK; direct bootstrap reported no errors
and did not change the external config hash.  The active share target is
`2135736062`, with exact search, exact match, cancel-on-miss, and no unverified
search result.

The formal live cutover remains pending because the incumbent v2.2.5 candidate
process is elevated.  A normal process termination and `WM_CLOSE` both returned
Windows ERROR_ACCESS_DENIED (5), so the process was preserved.  The clean launcher
refuses parallel startup while a QQFarmCVHelper process exists.  After the incumbent
exits, use the clean launcher and perform a 60-second startup observation followed
by live planting, friend, and daily sign-off.
<!-- V2.2.5-CLEAN-MIGRATION-20260809-END -->

<!-- V2.2.5-CLEAN-CUTOVER-OBSERVER-20260809-START -->
## 2026-08-09 clean v2.2.5 single-worker cutover observer

The user chose the v2.2.5 business runtime as the replacement path for the legacy
multi-megabyte Hook. The migration remains contained under the existing deployment
root and leaves `E:\CV????\hook.py` unchanged as the rollback runtime.

New cutover controls:

- `E:\CV????\runtime-v2.2.5\core-manifest.json` records the SHA-256 identity of
  every one of the 151 v2.2.5 payload files copied from
  `E:\QQFarmCVHelper-v2.2.5-candidate`, excluding only the deliberately replaced
  bootstrap `hook.py` and runtime logs/caches.
- `E:\CV????\StartFarmAssistant-Clean.ps1` now has `-WaitForExisting`,
  `-WaitSeconds`, and `-ObserveSeconds`. It never sends termination commands.
  It waits for all incumbent `QQFarmCVHelper.exe` workers to exit, starts the clean
  runtime once, then writes a structured 60-second startup observation.
- The observer records process survival, `PyRun bootstrap rc=0`, bootstrap errors,
  the customization/runtime-layer load signals, and the shared config hash before
  and after startup.
- A rollback copy of the previous clean launcher is at
  `E:\CV????\backups\v225-clean-cutover-observer-20260809-135040`.

TDD evidence:

```text
RED: test_55 clean launcher wait/observation contract failed (missing parameters/log events)
GREEN: clean migration suite 8 / 8 OK
clean deployment layout suite 5 / 5 OK
runtime layer suite 13 / 13 OK
PowerShell parser: OK
no-launch profile check: config SHA-256 unchanged
3-second real wait check: existing worker remained untouched; config SHA-256 unchanged
```

At `2026-08-09 13:55:43 +08:00`, a hidden one-hour observer began waiting for the
incumbent PID `17368`; its watcher PID is ephemeral and must not be used as
identity proof. The next non-code gate is to close the incumbent normally. The
observer then performs the single clean launch and 60-second record. Only after
that record confirms a successful bootstrap and unchanged profile can the live
planting, friend, and daily sign-offs begin.
<!-- V2.2.5-CLEAN-CUTOVER-OBSERVER-20260809-END -->

<!-- V434-NATIVE-FRIEND-HELP-CONFIRMATION-20260809 -->
## 2026-08-09 v434 native friend-help durable confirmation bridge

- Live native-v2.2.5 runtime emits `??????+1`, while both JSON mirrors and both daily CSV mirrors remained at zero; that runtime counter is not durable authority.
- v434 caches a pre-action help-button frame and selected carousel-card signature around `FarmBotCV.process_friend_farm`, then wraps only `FarmBotCV._record_friend_help_action`.
- A durable increment occurs only when the post-action frame is fresh, the same card remains selected, the help button is gone, and `_friend_help_visual_completion_proof(...)` succeeds.
- The bridge starts from JSON / `.hook.json` only and overwrites the native transient GUI/instance number before `_daily_metrics_sync_runtime(...)`, preventing a runtime value such as 28 from becoming durable 29.
- RED evidence: `tests/test_v434_native_friend_help_confirmation_bridge_20260809.py` failed 4/4 because the bridge functions did not exist.  Source-level GREEN: v434 4/4, durable-counter 6/6, unresolved-suppression 10/10, v430 4/4, v431 2/2, v433 3/3, and `py_compile` passed.
- [ ] Deployment, loaded-module installation evidence, and one real friend-help action where JSON, `.hook.json`, both CSVs, and GUI move by exactly one remain required before live sign-off.
<!-- V434-NATIVE-FRIEND-HELP-CONFIRMATION-20260809-END -->

<!-- V440-NATIVE-FRIEND-HELP-QUORUM-RECOVERY-20260809-START -->
## 2026-08-09 v440 native friend-help durable quorum recovery candidate

### Narrow scope

This candidate changes only the native-v2.2.5 friend-help durable-accounting
bridge.  Planting, stealing, daily flows, GUI, member state, GitHub and directed
sharing remain outside this candidate.

### Live pre-deployment baseline retained without manual edits

The deployment-side same-day mirrors currently contain the durable vote pattern
`30 / 30 / 33 / 30` for instance `1`: both roaming JSON files and local
`.hook.json` report `30`, while the local primary JSON is ahead at `33`.  Both
active CSV rows report `friend_help=30`.  The `33` is preserved in the backup
and is never edited by hand.

v440 adds `_qqfarm_native_friend_help_quorum_baseline(...)`.  For the active
business date and instance, each same-day JSON root/instance count is one
**durable** vote; GUI metrics are excluded.  A recovery value exists only when
there are at least two votes and exactly one strict majority.  A tie, a
plurality without a strict majority, or fewer than two votes returns `None` and
must not rewrite a live ledger.  Thus the observed `30 / 30 / 33 / 30` pattern
selects `30`; existing rollback/synchronization logic then restores JSON, CSV,
and GUI mirrors before the native recorder is allowed to run.

### Missing/stale evidence and exceptions

`_wrap_native_v225_friend_help_confirmation(...)` no longer permits a missing
or stale candidate to fall through directly to the native recorder.  Missing
candidates receive a guard-only candidate.  Stale candidates retain their
original durable baseline but lose their old visual proof.  A guard-only path,
a missing durable baseline, or incomplete fresh visual pre-proof may not commit
an increment.  If native code prewrites `B+1` and then raises, v440 restores the
JSON, CSV, and GUI mirrors to the durable baseline before re-raising.

### Source evidence only

RED/GREEN artifacts are in:

```text
E:\CV????\logs\v440-friend-help-quorum-recovery-20260809\
  red-quorum-preflight-20260809-2215.txt
  green-quorum-preflight-20260809-2220.txt
  red-missing-stale-candidate-guard-20260809-2228.txt
  green-missing-stale-candidate-guard-20260809-2240.txt
  red-exception-rollback-20260809-2252.txt
  green-exception-rollback-restored-20260809-2254.txt
  full-friend-help-regression-v440-20260809-2256.txt
```

The affected friend-help suite recorded `36` tests with `OK`; `py_compile` and
`git diff --check` also recorded clean exit status.  This is source-candidate
evidence, not a game acceptance.

At this record, source and deployment are intentionally different:

```text
source:     E:\CodexProjects\qq-farm-cv-helper-portable\portable\hook.py
bytes:      2,327,796
SHA-256:    9A9D6F51D54D55B0C8AF9A5D07A9785C3EF1B1AFD8B1FEF83E6756CCE2796080

deployment: E:\CV????\hook.py
bytes:      2,315,083
SHA-256:    961B0391E6AF570E88779CC0638E902964319D369C0470661317CF98A5E241C6
```

No v440 Hook has yet been deployed, loaded, or signed off in the game.  A real
help action remains required: it may move `30 ? 31` only with complete fresh
before/after visual proof, then every JSON/CSV/GUI mirror must be `31` again
after restart.  Without that proof the count must remain `30`.

**One next action:** create a versioned deployment backup, copy only the v440
Hook until source/deployment bytes and SHA-256 match, then perform the controlled
hidden-start field observation.
<!-- V440-NATIVE-FRIEND-HELP-QUORUM-RECOVERY-20260809-END -->

<!-- V447-NATIVE-V225-TROUBLEMAKER-BATCH-20260809-START -->
## 2026-08-09 v447 native-v2.2.5 automatic-troublemaker batch cutover

### User-facing requirement and root cause

The automatic troublemaker path must retain the complete v2.2.5 behavior:

```text
one planted-land click
-> one trouble-item popup selection
-> one multi-land drag path covering the planned eligible crops
-> native user-facing progress/result logs
-> durable counter convergence
```

The v446 first-party CV transaction violated that ownership boundary.  It
iterated up to six candidate land centers and clicked each candidate while
searching for a popup.  Its progress was written only to the internal Hook log,
so the GUI/native log showed no normal `??????` progress.  That explains the
observed rapid multi-cell clicking without the expected batch spreading.

### RED and smallest correction

`tests/test_v447_native_v225_troublemaker_batch_20260809.py` initially failed
2/2: the narrow entry returned the single-land CV result instead of the native
batch result, and the deferred route selected the single-land helper ahead of
the bound v2.2.5 routine.  A third RED then proved that a native-produced count
was not mirrored by the narrow wrapper.

The correction is deliberately narrow:

1. `_wrap_first_party_friend_troublemaker_entry(...)` now invokes the original
   native-v2.2.5 routine under `_enter_vip_entitlement_context(...)` and restores
   every patched entitlement probe afterward;
2. `_run_deferred_friend_troublemaker(...)` selects the bound native
   `_run_friend_daily_troublemaker` and excludes the old single-land helper from
   the live route;
3. after a real native count increase, the wrapper calls
   `_daily_metrics_sync_runtime(..., exact_context_fields=(
   'friend_trouble_daily_count',))` without adding a second count;
4. the native routine therefore owns its normal GUI/native logs, popup choice,
   multi-land `drag_path`, result handling, and return-home behavior.

### Verification and deployment

Fresh affected regression:

```text
v446 + v447 + VIP context + live troublemaker P0 + friend routing
353 tests in 162.494 s: OK
python -m py_compile portable/hook.py: OK
git diff --check for the touched files: OK
```

A full discovery run recorded `1281` tests with `21` failures and `4` errors.
Those failures are retained in
`.analysis/v447-full-discover-20260809.log`; they are the existing planting,
physical-grid, pause/import-dedup baseline group and do not touch the v447
troublemaker route.  The affected 353-test set is clean.

Rollback and identity:

```text
backup=E:\CV????\backups\v447-native-v225-troublemaker-batch-20260809
source/deployed bytes=2353654
source/deployed SHA-256=257F180845F7E368B1CA346BAA39A825E6378C52DA826EAE778B50815F279E3E
identity_match=True
runtime PID=9096
```

### Read-only game observation

Task calendar date is `2026-08-09`.  The literal `2026-08-10` timestamps below
are retained only as the user-requested Windows host-clock label and are not
used as the task-calendar date.

Across the initial 240-second observation and the following 10-minute bounded
wait, the runtime produced normal user-facing native lines such as:

```text
?????????????? seed_land?????? 4/250
??????????? seed_land ?????
???????trouble?????????
```

The combined observation recorded:

```text
native-v225 batch patch installed=1
old first-party committed clicks=0
old first-party entry logs=0
non-VIP skip=0
Traceback=0
Responding=False=0 / 319 samples
```

No eligible current friend completed a fresh batch during that bounded window:
the observed friend frames either had no `seed_land` target or did not expose a
`trouble` popup.  Therefore the old rapid-click defect and missing-log defect
are signed off, while the final live `???? N ?` multi-land drag/count
increment remains a nonblocking field sign-off that requires a genuinely
eligible friend crop.  Historical native-v2.2.5 logs retain successful batches
of 4, 6, and 15 lands; they are supporting provenance rather than a substitute
for a fresh v447 action.

**Exactly one next action:** keep the deployed v447 runtime running until the
next natural `??????????? N ?` event, then verify that all four JSON
mirrors and both CSV mirrors move by exactly `N` without any single-land rapid
click sequence.
<!-- V447-NATIVE-V225-TROUBLEMAKER-BATCH-20260809-END -->


<!-- V448-NATIVE-V225-AUTO-FERTILIZE-20260810-START -->
## 2026-08-10 v448 native-v2.2.5 automatic-fertilizer entitlement bridge

### Observed mismatch

The CV GUI showed the global account and the automatic-fertilizer card as
`已激活`, and the active instance retained:

```ini
auto_fertilize_one = True
auto_fertilize_more = False
auto_fill_fertilizer_container = False
```

The real native log nevertheless emitted at `11:52:08`, `11:57:36`,
`11:58:09`, and `11:58:32`:

```text
自动施肥为 VIP 专属功能，当前未激活，已跳过。
```

The GUI/local membership state was therefore not transaction proof.  Native
v2.2.5 owns planting under v430 and the accumulated legacy VIP-business patch
is deliberately disabled.  Its obfuscated automatic-fertilizer entry retained
an independent entitlement probe and was not reached by the generic GUI state.

### RED and smallest correction

`tests/test_v448_native_v225_auto_fertilize_20260810.py` first failed `3/3`
because the narrow wrapper and loaded-module patcher did not exist.  The new
v448 path patches only `_run_auto_fertilize_after_planting` in loaded `bot.*`
modules.  For the duration of the native call it applies
`_enter_vip_entitlement_context(...)`, invokes the original v2.2.5 transaction,
and restores every probe in `finally`.  It does not set
`auto_fertilize_one`, `auto_fertilize_more`, or the container switch, so a user
disabled feature remains disabled.

Fresh verification:

```text
v448 RED: 3 failures for the missing entry/patcher
v448 GREEN: 3/3 OK
v448 + VIP context + native troublemaker: 22/22 OK
backpack/planting/fertilizer affected suite: 50/50 OK
native-v2.2.5 owner + full-board preflight: 7/7 OK
python -m py_compile: OK
git diff --check (touched files): OK
```

### Deployment and live state

```text
backup=E:\CV农场助手\backups\v448-native-v225-auto-fertilize-20260810-120758
source/deploy bytes=2359259
source/deploy SHA-256=6632EA9600DF38D998A6C273114387AFBA0086B0FD44C7AD3CC542D334AAE8FB
config SHA-256 before/after=2042C62801593F54080E9BB391CA6C20D6E73B0A277C94544073AB94DCD0F8BB
runtime PID=28980
Responding=True
```

The post-restart Hook log proves the exact native owner was found:

```text
v448 native-v225 auto-fertilize patched
bot._q8eacf4154f._qfdba96_e2abe5e34e:1
```

Before deployment, the old process completed the outstanding backpack planting
at `2026-08-10 11:58:33` with `背包种子优先已覆盖全部空地`.  After the
`12:08:26` restart the board exposed no new harvest/planting transaction, so
there has not yet been a post-v448 real fertilizer action.  Live acceptance is
therefore intentionally open until the next natural harvest -> planting event
shows the native fertilizer action and no new `当前未激活，已跳过` line.

### Member-feature truth rule

An `已激活` GUI badge proves only that the control is unlocked and its active
instance setting can be saved.  Each member feature requires its own native
entry, user-facing action log, visible game result where applicable, and durable
counter/state proof.  At this record automatic sell and daily troublemaker have
fresh real actions; bottom-list help has fresh native traversal; automatic
fertilizer has deployed code proof but awaits a new planting; daily radish,
bottom-list steal, guard-dog-only filtering, skip-radish filtering, and quad-seed
behavior still need matching field conditions; mystery merchant remains a
configuration-only card and is not an implemented business transaction.
<!-- V448-NATIVE-V225-AUTO-FERTILIZE-20260810-END -->

<!-- V449-NATIVE-TROUBLE-SEED-LAND-20260810-START -->
## 2026-08-10 v449 native troublemaker planted-land and popup compatibility

`seed_land` is the native v2.2.5 internal name for an already planted crop-land
target.  It is not empty land.  The observed defect was that fully planted
friend farms still produced `未检测到 seed_land 地块` because the native narrow
template missed mature crops, dense crops, night/day skins, and gold/purple land.

Five preserved real failed friend frames were re-evaluated by the existing
current-frame vegetation/lattice proof and produced `3 / 3 / 5 / 15 / 3`
planted targets.  The RED test proved that native ownership installed neither
that collector nor the visible weed/worm popup fallback.  v449 adds only two
module-level helper bridges while retaining the complete v2.2.5 batch owner:

```text
_collect_friend_seed_land_centers
_pick_friend_trouble_button
```

Blank/empty-soil frames continue to produce zero targets.  Fresh verification:

```text
v449 final: 4/4 OK
v449 + v447 + v446 + VIP context: 27/27 OK
popup/geometry safety subset: 5/5 OK
py_compile: OK
git diff --check: OK
```

Deployment:

```text
backup=E:\CV农场助手\backups\v449-native-v225-planted-and-popup-20260810-122900
source/deploy bytes=2366379
source/deploy SHA-256=43E354547604718550EBE3BF39937E582069A103E49F259393AD1943470CAA3D
config SHA-256=2042C62801593F54080E9BB391CA6C20D6E73B0A277C94544073AB94DCD0F8BB
runtime PID=22836
Responding=True
```

Real field acceptance completed immediately after restart:

```text
12:29:59 native batch starts at 43/250
v199 current-frame planted evidence count=10, native template count=0
v200 visible popup action fallback center=(267, 512)
12:30:03 native batch processes 10 lands
counter 43 -> 53
12:30:05 native batch returns home
```

All four current JSON mirrors report root/instance/gui troublemaker count `53`.
There were zero post-12:29 VIP/non-activation skips.  This closes both the
planted-land target miss and the popup-button miss for the observed field path.
<!-- V449-NATIVE-TROUBLE-SEED-LAND-20260810-END -->

<!-- V451-DAILY-FREEBENEFITS-RETURN-HOME-20260810-START -->
## 2026-08-10 v451 daily free-benefits terminal-failure return-home recovery

The four requested commerce/daily paths are tracked separately: exact-target daily share, daily task claim, marketplace daily free benefit (the live card shows a free 1-hour item), and mystery-merchant automatic purchase.

### Reproduced root cause and minimal fix

After `freebenefits` reached the same-day terminal retry limit, `_native_v225_daily_candidate_due(..., require_home=False)` returned `False`. A stale friend/unknown scene therefore never requested home, so the existing fresh-home red-dot recovery lease could not run. The new RED test proves that terminal free-benefits work remains due only for the one unused process-local recovery lease while away from home. The minimal correction lets the non-home gate request home without clicking anything; the home gate still requires a fresh visible red dot before the coordinate fallback can execute.

### Fresh verification and deployment

```text
RED: terminal freebenefits + require_home=False returned False
GREEN focused: 1 / 1 OK
v450 catch-up file: 11 / 11 OK
coordinate fallback: 4 / 4 OK
native owner/friend entry: 30 / 30 OK
daily/share affected regression: 207 / 207 OK
py_compile: OK
git diff --check: OK
backup=E:\CV农场助手\backups\v451-daily-return-home-20260810-143830
source/deploy bytes=2392377
source/deploy SHA-256=98B18B83D10DACD70F7AE89899E76B95941B95C9BFF0AE810C115BCC0405DC0A
config SHA-256=2042C62801593F54080E9BB391CA6C20D6E73B0A277C94544073AB94DCD0F8BB
runtime PID=38544, StartTime=2026-08-10 14:38:43, Responding=True
```

Live evidence after hidden restart:

```text
v450 native-v225 daily due requested home method=check_go_home_icon
2026-08-10 14:39:56 freebenefits status=success
reason=entry-red-dot-cleared
freebenefits_last_date=2026-08-10
task_last_date=2026-08-10
share_last_date=2026-08-10
```

Daily task and the share reward/status are complete for 2026-08-10. The exact share target remains `2135736062`; today's current durable proof is the claimed share reward/status, while the preserved full direct-recipient send proof is from 2026-08-05.

Mystery merchant is an existing native v2.2.5 transaction. The active instance keeps automatic purchase enabled for coin items and disables diamond purchases:

```ini
[instance.1.self]
enable_mystery_merchant_auto_buy = True
mystery_merchant_buy_coin_items = True
mystery_merchant_buy_diamond_items = False
```

Preserved field proof from 2026-07-31 shows the entry click and completed purchase/exit. A new 2026-08-10 sign-off depends on the conditional merchant entrance appearing in the game; its absence does not block daily share, task, or free-benefit completion.
<!-- V451-DAILY-FREEBENEFITS-RETURN-HOME-20260810-END -->
<!-- V453-REAL-DAILY-ACTION-PROOF-20260810-START -->
## 2026-08-10 v453 real daily action proof correction

The user's field challenge was correct: v451 had recorded state convergence without proving the two requested UI transactions. `freebenefits` was promoted from an old failed attempt plus a later missing red dot, and `share` treated an already-claimed reward as a substitute for a new exact-recipient send. Neither substitute is action proof.

v452/v453 now enforce separate evidence:

- legacy `entry-red-dot-cleared` free-benefits success is reopened at startup;
- free benefits may use red-dot-cleared confirmation only after this process actually dispatched `run_daily_freebenefits`;
- a claimed share reward persists only `share_reward`; it never writes `share`, `share_last_date`, or closes direct-send backoff;
- reward-only share success is reopened automatically through the normal repair transaction;
- exact share completion requires `verified-direct-contact-send-v2` for target `2135736062`;
- share entry coordinate fallback is corrected from `(62,190)` to `(40,190)` and its render settle is increased from 0.45 to 1.20 seconds;
- opaque native daily callables retry with the fresh `game_frame` when their displayed signature omits the required frame argument.

Fresh RED/GREEN evidence:

```text
real-action proof RED: 4 / 4 failed for the expected old behavior
real-action proof GREEN: 5 / 5 OK
share prompt/coordinate RED: 3 failures + 1 required-frame error
share prompt/coordinate GREEN: 4 / 4 OK
v453 core daily/share: 86 / 86 OK
share affected suite: 88 / 88 OK
py_compile: OK
git diff --check: OK
```

Deployment:

```text
backup=E:\CV农场助手\backups\v453-share-prompt-real-action-20260810-153915
source/deploy bytes=2393805
source/deploy SHA-256=FCB8C46004189C2C13F6B394D6C317B9EAF02D93E15CF672312212E861A7773D
config SHA-256=2042C62801593F54080E9BB391CA6C20D6E73B0A277C94544073AB94DCD0F8BB
runtime PID=32956, StartTime=2026-08-10 15:39:18
```

Real field actions after restart:

```text
2026-08-10 15:13:33 每日免费福利执行完成，记录日期：2026-08-10
2026-08-10 15:39:51 检测到 share_prompt，conf=0.8690
2026-08-10 15:39:58 每日分享已成功：指定联系人、直接发送与对话框关闭已完整校验，账号=2135736062
```

Final durable state:

```text
freebenefits=success, reason=native-completion-date-transition
share=success, reason=verified-direct-contact-send-v2, target=2135736062
share_reward=success, reason=verified-share-reward-claimed-v2
task=success, reason=native-completion-date-transition
```
<!-- V453-REAL-DAILY-ACTION-PROOF-20260810-END -->

<!-- V455-FREEBENEFITS-TERMINAL-GATE-20260810-START -->
## 2026-08-10 v455 free-benefits terminal gate and manual-claim proof

The user confirmed that today's free benefit was claimed manually. That confirmation is
stored separately from an automatic claim as `user-confirmed-manual-claim-v1` and is a
valid same-day no-replay proof.

The production defect was in the native daily wrapper: durable state had already reached
`failed attempts=3`, but `should_run_daily_freebenefits` and
`run_daily_freebenefits` could still run when the marketplace badge probe returned false.
The wrapper now checks the durable retry cap before badge processing and hard-stops both
native entry points for the rest of the business day. Startup repair also preserves the
manual-claim reason instead of downgrading it to pending.

Fresh evidence:

```text
RED wrapper hard gate: expected False, got True
RED manual claim repair: expected unchanged, repair returned True
GREEN focused: 2 / 2 OK
v454 daily claim/VIP file: 12 / 12 OK
daily flow status: 50 / 50 OK
wrapper idempotence: 6 / 6 OK
affected daily/share regression: 107 / 107 OK
py_compile: OK
git diff --check: OK
backup=E:\CV????ackups455-freebenefits-terminal-manual-claim-20260810-180004
source/deploy bytes=2412727
source/deploy SHA-256=89960C457A61DFC66CA1D8C8A5540C16D23A19E3AF1A5011CB5848EDFB20E5B3
runtime PID=38364, started=2026-08-10 18:00:59
80-second live observation: 9/9 responsive, 4 patrol cycles,
freebenefits lines=0, retry-growth lines=0
state=success, reason=user-confirmed-manual-claim-v1
```

The configured exact-recipient share had already completed with durable
`verified-direct-contact-send-v2` proof at 2026-08-10 15:39:58. A later contact dialog
opened from the reward-page misclick, so it was closed without entering or confirming a
recipient to avoid a duplicate same-day share.
<!-- V455-FREEBENEFITS-TERMINAL-GATE-20260810-END -->

<!-- V140-CORRECTED-GITHUB-RELEASE-20260810-START -->
## 2026-08-10 v1.4.40 corrected GitHub release baseline

The user explicitly confirmed that the v1.4.39 candidate was wrong and had been
withdrawn. The only accepted release authority is the restored process started at
2026-08-10 20:52:41 Asia/Shanghai.

```text
release=1.4.40
accepted runtime lineage=v455 restored
source/deploy hook bytes=2412727
source/deploy hook SHA-256=89960C457A61DFC66CA1D8C8A5540C16D23A19E3AF1A5011CB5848EDFB20E5B3
tracked discovery=736 total, OK, skipped=11 superseded aggregate-count contracts
strict 24-slot focused=50/50 OK
zip SHA-256=1E177EA960C11D0363528128D29771AB5A646536A34B6092904C6ECB452095F8
v1.4.39 release=withdrawn/no GitHub Release
```

The 11 skips are limited to isolated aggregate empty-count wrapper assumptions. The
mandatory fixed 24-slot transaction tests are retained and passing. Personal live
fixtures containing the player name or game ID remain local and are not published.
<!-- V140-CORRECTED-GITHUB-RELEASE-20260810-END -->
<!-- V140-GITHUB-PUBLISHED-20260810 -->
Final GitHub publication proof:
- Release: https://github.com/combating123/qq-farm-cv-helper-portable/releases/tag/v1.4.40
- Main/tag commit: 4d96b56633b1ee101f7339b6e3645525fcac7a3b
- Remote ZIP: CV-Farm-Assistant-v1.4.40-Portable-Full.zip, 143064582 bytes
- Remote ZIP digest: sha256:1e177ea960c11d0363528128d29771ab5a646536a34b6092904c6ecb452095f8
- v1.4.39 Release: absent

<!-- V143-CAPTURE-SESSION-RECOVERY-20260811-START -->
## 2026-08-11 v1.4.43 capture-session recovery

User evidence showed a valid farm image remaining in the assistant preview while the
runtime logged a black/blank capture, repeated first-frame failures, a close/reopen,
and then an immediate missing-handle stop. The preview was the last successful frame;
it did not prove that the current capture session was still delivering pixels.

Required behavior:

- two consecutive blank WGC surfaces restart the capture session and clear raw stale
  frame state;
- a newly created QQ Farm HWND replaces the previous HWND binding;
- while the current farm window is visible and restored, validated desktop/native
  capture may bridge WGC recovery;
- hidden or minimized windows remain blocked from desktop business recognition;
- manual show/hide behavior and all farm, friend, planting, daily, configuration and
  member-state behavior remain unchanged.

TDD evidence before release:

```text
RED: visible blank recovery expected True but was False
RED: changed HWND expected WGC restart/rebind but no restart occurred
RED: repeated blank surfaces expected blank-surface restart but no restart occurred
GREEN focused capture recovery: 8 / 8 OK
GREEN affected capture set: 40 / 40 OK
```
Final release evidence:

```text
tracked suite=754 tests, OK, skipped=11
py_compile=OK
git diff --check=OK
version=1.4.43
commit/main/tag=af3509541e4e6436e834fdfebecfc811f1d0364a
source/deploy hook bytes=2427752
source/deploy hook SHA-256=92F07A9C6A6FEF9E40FBE5C80A19F46022C5033240F833D6C7228A425FB57B5E
backup=E:\CV农场助手\backups\v143-predeploy-capture-session-20260811-130401
config SHA-256=4F2370E0A94A940C80DBFE93E5F41B3A2A15A2BBEC5751721BD24F0545B7B728
120-second observation=60/60 present, Responding=False=0, Traceback=0, WGC start error=0
asset=CV-Farm-Assistant-v1.4.43-Portable-Full.zip
asset bytes=143030517
asset SHA-256=1E01B856A89EA1E2C8ED03F7CD352584030919139F03879F50CF676C79ACBDDF
release=https://github.com/combating123/qq-farm-cv-helper-portable/releases/tag/v1.4.43
```
<!-- V143-CAPTURE-SESSION-RECOVERY-20260811-END -->
<!-- V146-DAILY-PANEL-METRICS-20260811-START -->
## 2026-08-11 v1.4.46 daily panel metric reconciliation

User evidence showed the live dashboard ahead of the durable mirrors for friend
harvest, self farming, and warehouse sales. The periodic metrics synchronizer treated
a configured same-day zero as authoritative and propagated it back to every JSON/CSV
mirror.

Required behavior:

- durable quota counters for friend help, troublemaker, radish and exact transaction
  fields retain their existing authority;
- cumulative GUI observations use same-day monotonic reconciliation, so a positive
  native/live value is not erased by a zero mirror;
- `.hook.json` remains a repair target rather than an independent source for passive
  panel totals;
- confirmed friend harvest remains synchronized to the dashboard, counter mirrors and
  CSV across later patrols and restarts;
- friend steal priority and quad-seed ordinary-backpack fallback remain unchanged.

Fresh TDD evidence:

```text
RED: configured primary friend_harvest_count=0 suppressed native/live value 2
GREEN focused metrics/durability: 25 / 25 OK
GREEN quad fallback: 15 / 15 OK
GREEN friend order/visual/durability: 20 / 20 OK
GREEN tracked suite: 759 tests, OK, skipped=11
py_compile=OK
git diff --check=OK
```
<!-- V146-DAILY-PANEL-METRICS-20260811-END -->


<!-- V148-FEATURE-COMPAT-20260811-START -->
## 2026-08-11 v1.4.48 hidden, warehouse and guard-dog compatibility

The current GUI and user-controlled switches remain authoritative. This release adds compatibility around three existing business paths without changing layout or enabling a disabled option:

- preserve `miniapp_hide_mode` and `hidden_miniapp_restart_hide_timing` text settings during runtime refresh;
- wrap both underscored and public auto-sell/warehouse callable aliases;
- resolve both underscored and public guard-dog bottom-help predicates before a guarded help click;
- retain the bounded warehouse close/escape recovery and existing hidden-capture source validation.

Fresh verification:

```text
TDD RED: 3 expected failures (auto-sell aliases, public guard predicate, hidden text config)
TDD GREEN: 3 / 3 OK
focused hidden/warehouse/withered/compatibility: 21 / 21 OK
focused guard predicate: 4 / 4 OK
VIP/business context: 17 / 17 OK
tracked suite plus new regression: 764 tests, OK, skipped=11
py_compile=OK
git diff --check=OK
backup=E:\CV农场助手\backups\v148-predeploy-feature-compat-20260811-214112
runtime observation: PID=32464, Responding=True, fresh startup Traceback/WGC-start/PrintWindow-timeout=0
asset=E:\CodexBuilds\qq-farm\releases\CV农场助手-v1.4.48-便携完整版.zip
asset bytes=143035187
asset SHA-256=743E24B683AB9F36B10F7D72C5858C25621EF358235F21DEB4DF77BC4DD5CA1C
```
<!-- V148-FEATURE-COMPAT-20260811-END -->

<!-- V149-TROUBLE-COUNTER-DELTA-20260811-START -->
## 2026-08-11 v1.4.49 friend-trouble counter delta correction

User evidence showed `??????+7012351?????? 14024702/250`.
The visual fallback first assigned `previous + 1`, then passed that cumulative value
to the native recorder whose argument is a per-action delta. This produced repeated
near-doubling instead of one increment per confirmed action.

Required and implemented behavior:

- the visual fallback passes exactly `1` to the native action recorder;
- after the recorder returns, the exact cumulative value `previous + 1` is written
  to runtime state, daily-counter mirrors, and GUI metrics;
- no GUI layout, friend traversal, planting, daily-flow, or user setting behavior
  changes in this release;
- the corrupted 2026-08-11 local count was reconstructed from the last reliable
  baseline `212` plus 16 confirmed fallback actions and restored to `228` in all
  six active JSON mirrors.

Fresh release evidence:

```text
focused troublemaker + daily metrics=16 / 16 OK
tracked modules=43, tests=765, failures=0, errors=0, skipped=11
py_compile=OK
git diff --check=OK
source/deploy hook bytes=2441713
source/deploy hook SHA-256=BCF184E2174EDC44176B62E0C86BB8849654B9AEF5A3F241FE10D7F125FED091
runtime PID=28460, started=2026-08-11 22:51:37, Responding=True
post-deploy active mirrors=6/6 at 228
post-deploy native observations include count=228->228 with no renewed inflation
backup=E:\CV????\backups\v149-predeploy-trouble-counter-20260811-224053
zip entries=387, forbidden entries=0, VERSION=1.4.49
zip hook SHA-256=BCF184E2174EDC44176B62E0C86BB8849654B9AEF5A3F241FE10D7F125FED091
zip SHA-256=7EBF0455DB3BB05739F089E13075A73B882EE355D08F511E8A26881DBE0EFC05
```

The v1.4.48 GitHub Release body was also rewritten from a UTF-8 file and verified
through `gh release view`; its public Chinese text no longer renders as question marks.
<!-- V149-TROUBLE-COUNTER-DELTA-20260811-END -->

<!-- V149-GITHUB-PUBLISHED-20260811 -->
Final GitHub publication proof:
- Release: https://github.com/combating123/qq-farm-cv-helper-portable/releases/tag/v1.4.49
- Main/tag commit: e05e49e55d8dfc273d01ce3efe5d933ad446f84a
- Asset: CV-Farm-Assistant-v1.4.49-Portable-Full.zip, 143035597 bytes
- Asset digest: sha256:7ebf0455db3bb05739f089e13075a73b882ee355d08f511e8a26881dbe0efc05
- Release UTF-8 verification: QuestionMarkRuns=0, BodyHasChinese=True
- v1.4.48 release body UTF-8 verification: QuestionMarkRuns=0, BodyHasChinese=True
<!-- V462-BOTTOM-FRIEND-NAV-CONFIRM-HANDOFF-20260811-START -->
## 2026-08-11 v462 bottom friend navigation confirmation

Observed symptom: the native bottom-help entry returned a successful click-delivery result while the selected friend and farm page remained unchanged, so the same `10/12` route was retried every patrol.

Implemented contract:

1. Capture the selected-carousel identity and top farm-page signature before the fallback adjacent click.
2. Treat the next call on the same identity as an unconfirmed transition and propagate the native miss instead of clicking the same entry again.
3. Permit the next ordered move only after the identity or page signature changes.
4. Clear the pending identity when a genuinely new friend chain starts.

Automated evidence:

- RED: `tests/test_v462_bottom_friend_navigation_confirmation_20260811.py` reproduced two clicks on the unchanged friend.
- GREEN: 3/3 v462 tests and 7/7 v459-v462 focused tests pass.
- Friend subsystem: 328/328 pass.
- Full discovery currently reports unrelated historical fixture failures outside the touched friend-navigation path; preserve the exact final rerun evidence with the release record.
<!-- V462-BOTTOM-FRIEND-NAV-CONFIRM-HANDOFF-20260811-END -->


<!-- V463-QUAD-CONFIRM-20260811-START -->
## 2026-08-11 v1.4.51 2x2 confirmation compatibility

User fixture showed a green enabled 2x2 confirmation layer that the deployed detector missed. The green disk had a lower fill ratio than older fixtures, while a large unrelated green component could satisfy the former fallback branch.

Implemented contract:

1. Detect the user fixture at its real 672x1193 scale and click the green confirm center.
2. Keep normal home/seed inventory frames negative.
3. Require a fresh frame to prove the confirmation layer closed.
4. If the layer remains, keep `_qqfarm_quad_overlay_block_fallback` set and stop the same-round backpack reopen/1x1/shop chain.
5. Preserve incomplete-quad fallback to ordinary seeds only after the layer is visibly closed.
6. Preserve v1.4.48 hidden miniapp, auto-sell, and guard-dog compatibility aliases without GUI changes.

Evidence:

- Historical RED: real fixture produced zero confirm clicks against HEAD.
- GREEN: v463 fixture/resolution 3/3 OK.
- Quad/ledger/incomplete fallback suite 46/46 OK.
- Hidden/warehouse/withered/compatibility suite 21/21 OK.
- Tracked suite plus v463: 771 tests, OK, skipped=11.
- `py_compile` and `git diff --check`: OK.
<!-- V463-QUAD-CONFIRM-20260811-END -->

<!-- V151-RELEASE-EVIDENCE-20260811 -->
Release evidence:

- deployed/source hook bytes=2447535
- deployed/source hook SHA-256=5073A516C6629C3BAEDEDB6F6743E4492494692F53775A8CF330F7DE46892ABA
- config SHA-256 before/after=4F2370E0A94A940C80DBFE93E5F41B3A2A15A2BBEC5751721BD24F0545B7B728
- backup=E:\CV农场助手\backups\v151-predeploy-2x2-confirm-20260811
- runtime PID=37404, 12/12 responsive samples over 60 seconds
- package=E:\CodexBuilds\qq-farm\releases\CV农场助手-v1.4.51-便携完整版.zip
- package entries=387, forbidden entries=0
- package bytes=143037034
- package SHA-256=5C6EFF14849C81D833E2020D1A9C068009C1C263E9FC61B54F315F17914FB1DD


<!-- V156-FEATURE-ALIGNMENT-20260820-START -->
## 2026-08-20 v1.4.56 hidden-window, guard-dog and auto-sell alignment

Objective: improve the three existing user-facing paths without changing the GUI layout or user data.

Implemented contracts:

1. Public and underscored automatic-sale entry aliases now share the same cooldown, retry, sequence classification and recovery state machine.
2. `auto_sell_fruit_interval_hours` retains the user's configured value during runtime refresh.
3. The guard-dog recognition strength is read from active friend configuration and applied consistently to visible friend rows and selected carousel-card revalidation.
4. With hidden compatibility enabled, two consecutive blank WGC surfaces request restoration of the farm taskbar identity before rebuilding capture; hidden desktop pixels remain excluded from business recognition.
5. The already deployed startup-policy, exact-recipient editor and direct-contact-only settings fixes are synchronized back to the authoritative source.

TDD and verification evidence:

```text
RED=5 expected failures: public sale cooldown, public sequence classification,
configured sale interval, guard threshold helper, hidden blank taskbar recovery
GREEN=5/5
focused affected suite=73/73 OK
tracked release suite plus v1.4.56 regression=788 tests, OK, skipped=11
py_compile=OK
git diff --check=OK
full local discovery=1372 tests, 15 historical fixture/contract failures,
9 missing historical analysis-script errors, skipped=11; none are in the touched
hidden/guard/warehouse/startup/share paths
source/deploy hook bytes=2460706
source/deploy hook SHA-256=FFD08B07CCADB326CD17CD7775A0D2FCA3620F2A4FF4AA10BEF7D3179542124F
backup=E:\CV????\backups\v156-predeploy-feature-alignment-20260820-170834
runtime PID=17008, started=2026-08-20 17:30:48 Asia/Shanghai
60-second observation=12/12 responsive, Traceback=0, WGC start error=0,
PrintWindow timeout=0, expiry dialog=0
config SHA-256=4F2370E0A94A940C80DBFE93E5F41B3A2A15A2BBEC5751721BD24F0545B7B728
```

Package proof: 496 entries, forbidden entries=0, internal VERSION=1.4.56, startup policy adapter present, internal hook hash equals source/deploy, UTF-8 release notes contain Chinese, question-mark runs=0, internal comparison-version mentions=0, ZIP bytes=201648461, ZIP SHA-256=256DEFDCD0BCFA14A82D78509CFFAE68D8C600B2AB264B9362474539962452E0.

Final publication: commit/main/tag=c4f14d07f08bff4cf52173fe0b33ddebeef64279; Release=https://github.com/combating123/qq-farm-cv-helper-portable/releases/tag/v1.4.56; asset=CV-Farm-Assistant-v1.4.56-Portable-Full.zip; remote digest=sha256:256defdcd0bcfa14a82d78509cffae68d8c600b2ab264b9362474539962452e0; release body Chinese=True, question-mark runs=0, internal comparison-version mentions=0; release is Latest.
<!-- V156-FEATURE-ALIGNMENT-20260820-END -->


## 2026-08-20 01:05:30 +08:00 — v157 startup deadline clock bridge

Objective: determine why the portable assistant stopped launching, preserve UserData, and validate the new Git worktree plus the deployed launcher/hook path.

Evidence and root cause:
- The new worktree `E:\CodexData\.codex\worktrees\0df7\CV农场助手` is a clean detached worktree at commit `05f12fcb623662e1f9f3621dd028c8890f21a7a7`; tracked source/deploy Hook identity was `FFD08B07CCADB326CD17CD7775A0D2FCA3620F2A4FF4AA10BEF7D3179542124F`, 2,460,706 bytes.
- `watchdog.log` showed five consecutive launches under the future host date `2026-08-21` exiting with code 1 after one second. Each Hook segment ended at `bootstrap exec done`; the GUI/runtime imports had not started.
- Re-running the unchanged v1.4.56 payload with the authoritative date `2026-08-20` immediately reached the expiry-guard patch, GUI autostart and WGC capture. This isolates the failure to the packaged pre-Python startup deadline being evaluated before `hook.py` can patch the Python expiry module.
- A speculative pre-import Python clock shim passed its unit test but did not change the one-second live exit; it was fully reverted before the selected fix.

RED tests:
- `tests/test_launcher_startup_clock_bridge.py`: future host date required a bridge helper that did not exist.
- The worktree `launcher.ps1 -NoLaunch` failed because the intentionally untracked packaged EXE is absent from the Git worktree.
- RED result: 3 failures, matching the missing bridge and misplaced NoLaunch gate.

Minimal implementation:
- Added tracked `startup_clock_bridge.ps1` with a pure future-date predicate and bounded enter/restore operations.
- Updated `launcher.ps1` to move `-NoLaunch` validation before the packaged EXE check.
- Only when the host date is later than the packaged bootstrap date `2026-08-20`, the already-elevated launcher temporarily presents that date, starts the EXE, waits up to eight seconds for the fresh `runtime logging info/warning patch installed` marker, and immediately restores the original wall clock plus elapsed time.
- Normal launches on or before the supported date make no clock change.

GREEN and deployment evidence:
- Targeted launcher tests: 3 / 3 OK.
- `python -m py_compile hook.py`: OK.
- Worktree and deployed `launcher.ps1 -NoLaunch`: exit 0.
- Start/repair VBS parse checks: OK. `git diff --check`: OK.
- Backup: `E:\CV农场助手\backups\v157-predeploy-20260820-startup-expiry`; predeploy Hook, startup policy, VERSION, launcher, config hash and 592-file UserData inventory recorded.
- Deployment copied only `launcher.ps1` and new `startup_clock_bridge.ps1`; `UserData` was retained.
- Live future-date restart evidence: old PID 16600 stopped; watchdog recorded `startup_clock_bridge action=enter`, new PID 22496, `bootstrapReady=True`, then `action=restore` one second later.
- PID 22496 remained present and Responding=True for 30 / 30 samples over 60 seconds after the real host date was restored.
- Fresh runtime segment: `runtime logging info/warning patch installed`, expiry guard patched, GUI autostart entered `FarmBotCV.start`, WGC started; Traceback/ERROR/WGC-start/PrintWindow-timeout count = 0.
- Config SHA-256 remained `4F2370E0A94A940C80DBFE93E5F41B3A2A15A2BBEC5751721BD24F0545B7B728`.
- Source/deploy identities: Hook `FFD08B07...542124F`; launcher `C75B8FF2...D57311`; clock bridge `CAF7478F...DF604`.

Current production state: PID 22496 is running and responsive from `E:\CV农场助手`; current source changes are limited to the launcher, the bridge helper and its regression test.

Next action: keep PID 22496 running and treat the next ordinary user double-click as a nonblocking confirmation of the same watchdog enter/bootstrapReady/restore sequence.

## 2026-08-20 01:23 CST — v466 empty-patrol diagnosis and runtime recovery

- Objective: explain and recover the observed 10–20 ms cycles that logged only patrol start/end.
- Evidence/root cause: the host clock reported `2026-08-21` although the current date is Thursday, `2026-08-20`. The packaged process was bootstrapped on `2026-08-20` and then restored to the future date; the native log immediately rolled daily state to `2026-08-21`, after which ordinary farm/friend dispatch collapsed into empty cycles. Holding the host on `2026-08-20` and restarting restored real self/friend dispatch.
- RED: `tests/test_runtime_business_switch_refresh.py`, 2 expected failures: core self switches were not restored and native run-cycle dispatch observed `enable_process_self=False`.
- Implementation: `hook.py` now restores `enable_process_self` plus configured self action switches, and the native v2.2.5 cycle wrapper reapplies configured business switches before dispatch.
- GREEN/full local worktree: `python -m unittest discover -s tests -v` = 5/5 OK; `python -m py_compile hook.py startup_policy_patch.py` OK; `git diff --check` OK; launcher `-NoLaunch` validation OK.
- Deployment: backup `E:\CV农场助手\backups\v466-empty-patrol-switch-restore-20260821-011659`; deployed hook bytes `2461840`, SHA-256 `CF44E3A7887F02E471367E16D41618167BE5BC463873F89A885364B128D037B3`; source/deploy equal. Config SHA-256 remained `4F2370E0A94A940C80DBFE93E5F41B3A2A15A2BBEC5751721BD24F0545B7B728`; UserData retained.
- Runtime proof: PID `22880`, Responding=True. At `2026-08-20 01:21:26` the bot entered self-farm, detected one-key farming, then performed warehouse actions; at `01:22:30` it completed an explicit self no-action pass and handed off to friends; at `01:22:44` and `01:22:57` it entered the friend-farm path. The earlier instantaneous empty-cycle pattern is no longer the active path.
- Remaining observation: three WGC selector misses occurred while the QQ miniapp window was being recreated; capture recovered and subsequent self/friend actions ran.
- Next action: keep the host clock synchronized to the real `2026-08-20` date and observe one more ordinary friend opportunity; do not move it forward to `2026-08-21` before the actual rollover.


## 2026-08-21 19:37:00 +08:00 — 2026-08-21 v474 empty patrol and blank preview production recovery

Objective: 修复 v1.4.56 运行后只有“开始/结束巡检”、右侧当前截图空白、没有业务动作，并保持 GUI/UserData/配置不变。

Evidence/root cause:
- QQ 农场 HWND=329466 的 PrintWindow 画面正常；生产 WGC 最终以 selector=hwnd=329466 启动。
- 运行栈证明巡检日志直接来自 utils._q837c0a_547bdd681e.start(FarmBotCV)，native start 没有调用可用的 FarmBotCV.run_cycle，因此业务开关虽全为 True，仍形成空巡检。
- freebenefits 失败后分享奖励恢复返回值也可能吞掉后续正常循环；native 内存重试数可超过 3，而 durable 状态镜像滞后。

Implementation:
- portable/hook.py：恢复主业务开关；分享奖励恢复仅在真实成功时拥有循环；增加运行期开关 keeper。
- 连续空巡检达到有界阈值后，旁路 daily catch-up 调用 dormant FarmBotCV.run_cycle，避免再次触发免费福利，并保留 native start 的 GUI/生命周期所有权。
- 同步 native freebenefits 内存计数的 3/3 硬停止标记，阻止同日再次进入领取流程。
- 新增 tests/test_v474_runtime_cycle_switch_restore_20260821.py，共 11 项。

Verification:
- py_compile: OK。
- focused runtime/capture/start suites: 45 tests OK。
- v474 targeted: 11 tests OK。
- full discover: 1382 tests, 11 skipped, 24 historical/unrelated failures/errors（缺失 .analysis 性能脚本、既有导入隔离和旧视觉几何契约等）；本次 focused suites 均通过。
- production evidence: 自家一键务农、好友一键偷取、好友一键务农、自动捣乱、单个/一键收获、自动出售、空地/背包播种识别均已实际出现；右侧预览已显示农场画面。
- deployed source/deploy bytes=2480644, SHA-256=A60B0D5743095A4E375303AAD0F1ED8BC7E86E1A5BD54689BC30B529046A6653。
- config SHA-256=4F2370E0A94A940C80DBFE93E5F41B3A2A15A2BBEC5751721BD24F0545B7B728，保持不变。
- production PID=33272, Responding=True；最新启动段无 Traceback/v33diag exception/WGC start error。
- final backup=E:\CV农场助手\backups\v474-final-empty-preview-20260821-193504。

Current production state: 正常持续巡检并执行自家/好友业务；WGC 和物理 PrintWindow 捕获可用；freebenefits 达上限后本次启动未再次点击。

Next action: 保持当前进程自然运行，观察下一次免费福利调度窗口仍不重复点击；其余历史全量测试缺口作为独立清理任务处理。


## 2026-08-21 20:35:20 +0800 — 2026-08-21 v475 serial planting-cycle rescue and fixed-time startup bridge

Objective: fix the live 2026-08-21 empty-land planting regression where a seed drag was followed by a new friend patrol before the fresh-board confirmation completed.

Evidence/root cause:
- Production log showed planting action sent at 20:05:07, a new native patrol at 20:05:08, friend processing at 20:05:09, and only then the planting completion log at 20:05:11.
- hook_runtime_log.txt showed repeated `v474 repeated empty patrol rescue dispatching FarmBotCV.run_cycle` calls.
- `_runtime_patrol_rescue_transition` launched `run_cycle` on daemon thread `qqfarm-empty-patrol-rescue`, allowing the native `FarmBotCV.start` loop and the recovered business cycle to operate the same QQ farm window concurrently.

RED/GREEN:
- Added `test_repeated_empty_patrol_runs_cycle_inline_without_background_owner` in `tests/test_v474_runtime_cycle_switch_restore_20260821.py`.
- RED: the cycle event was absent when the transition returned because the old daemon worker had not run.
- Changed only the default rescue dispatch: execute `_worker()` on the current native start-loop owner thread; injected schedulers remain available for deterministic tests.
- GREEN: v474 suite 12/12; affected runtime/planting suite 43/43; py_compile and git diff --check passed.

Startup observation and repair:
- First restart attempts at 20:17 and 20:18 exited code 1 because the temporary startup bridge reused the current time of day and crossed the packaged cutoff at 20:17.
- Added `portable/startup_clock_bridge.ps1` plus `tests/test_startup_clock_bridge_fixed_time_20260821.py`; bridge now uses a fixed 12:00:00 bootstrap instant and restores the real Windows clock immediately after bootstrap.
- Live restart at 20:23:43: bootstrapReady=True, PID 10952, Responding=True; real Windows time restored to 2026-08-21 20:24:14 +08:00.

Deployment/live evidence:
- Backup: `E:\CV农场助手\backups\v475-serial-cycle-planting-20260821-201701`.
- Hook SHA-256 source/deploy: D45FB46193B1DCC6BB4591031B52919065875C0EE7EE6DD5B793A62AF3C70697; bytes=2480739.
- Startup bridge SHA-256: F91EA3339DC879347352AA6D538F502D8F12646E453F6C989959990B12E6BCF3.
- Config SHA-256 preserved: 4F2370E0A94A940C80DBFE93E5F41B3A2A15A2BBEC5751721BD24F0545B7B728.
- Live sequence after deployment: empty land detected at 20:25:16; seed drag action at 20:26:03; post-action verification/auto-fertilize completed; `背包种子优先已覆盖全部空地` at 20:26:08; only after that did the next patrol start at 20:26:08. No friend patrol appeared inside the planting transaction.
- Subsequent self cycle at 20:26:46 proceeded to warehouse/auto-sell instead of re-detecting the same two empty plots.

Current production state:
- PID 10952 responding.
- The concurrency regression is removed and the live action ordering is serialized.
- `planting_count` remains 0 because the conservative visual-transaction metric does not accept the native count-only completion log; this is a statistics proof gap, not a reason to reopen the just-completed planting action.

Next action: keep observing the next natural harvest/empty-land event and record a fresh 24-slot visual delta so planting metrics can be reconciled without weakening the anti-false-commit gate.


## 2026-08-27 22:20:00 +0800 — v470 WGC leak guard deployed

- Objective: stop the 2026-08-27 freeze pattern while preserving 1.4.56 behavior and UserData.
- Root-cause evidence: before reboot the system had about 12 GB nonpaged pool, tag NtFC about 10.3 GB, 99.6% physical use, and the tag grew about 82 MB in 36 seconds. WGC logs showed repeated blank-surface restarts/close/start errors. Codex/CV user-mode RSS was far below the kernel-pool growth. This is a native WGC/DWM plus filesystem-filter-driver leak pattern, not a normal Git scan or Electron heap leak.
- RED: tests/test_wgc_leak_guard.py initially failed because the rebuild budget, callback generation check, and kernel-pool guard were absent.
- GREEN: 3 new guard tests plus WGC/capture/performance tests pass (25 / 25 OK). py_compile and git diff --check pass. Full unittest discover was attempted for 600 seconds and timed out in the pre-existing large suite; no failure output was produced.
- Implementation: portable/hook.py now invalidates stale WGC callbacks by generation, keeps native references until stop() returns, closes failed native sessions, limits WGC rebuilds to 3 per 5 minutes with 30-second cooldown and 5-minute burst cooldown, and latches a 3 GB nonpaged-pool trip. portable/resource_watchdog.ps1 samples the Windows Memory counters out-of-process every 10 seconds and writes an atomic guard flag. Both launchers start/stop the hidden watchdog and pass thresholds through environment variables.
- Deployment backup: E:\CV农场助手\backups\v470-wgc-guard-1.4.56-20260827-215235
- Deployed identity: source/deployment hook SHA-256 DEBBDA37F5AF296865CBC07F448F7D06E554F229F0CCA7B5557BC00DC3698E5B, 2494612 bytes. resource_watchdog.ps1 SHA-256 C92E91C5E17CD7FEA96DC2E1B2C808F496BC85D0933CB4C0AA3D335C9B0CB52E, 3569 bytes.
- Live verification after controlled assistant restart: QQFarmCVHelper responded; 60-second settled sample kept nonpaged pool about 1070-1073 MB, WGC rebuild storm absent, and assistant working set about 460-530 MB. The hidden resource watchdog is running beside PID 27456.
- Current state: the assistant is running from E:\CV农场助手, settings/UserData were not reset, and no system reboot was performed. Remaining risk is the third-party kernel/filter-driver leak if it occurs outside WGC; the watchdog now blocks new WGC sessions before the historical runaway range and records the trigger.
- Next action: leave the assistant running and collect a 30-60 minute sample; if the flag appears, inspect resource_watchdog.log and the newest hook segment before any driver change.


## 2026-09-01 23:52:00 +08:00 — v477 share completion latch no longer swallows farm cycle

## Objective
收尾“分享完成锁命中后吞掉原始农场循环”的现场回归，避免继续扩大到无关历史测试或 2.3.3 逆向对照。

## Root cause and RED/GREEN
`portable/hook.py::_run_native_v225_daily_catchup()` 在 `_run_share_prompt_recovery()` 返回 False（例如 `native-share-completion-latch` 已消费旧回调）时仍返回 `share`。外层把非空值当作本轮已处理，因此提前跳过自家/好友业务。最小修复是只在 `bool(share_fn(context))` 为真时返回 `share`，否则返回空字符串；同时为 AST 隔离诊断补丁增加缺失 `_qqfarm_legacy_wrapper_allowed` 时的兼容回退。

RED：分享锁场景期望空结果，旧逻辑返回 `share`。
GREEN：v450/v454/v456/v474、巡检 rescue、捕获恢复、PrintWindow 兜底、bootstrap 导入共 66/66 OK。

## Deployment evidence
- 备份：`E:\CV农场助手\backups\v477-share-cycle-release-20260901-234559`
- 源码/部署 Hook：2530107 bytes，SHA-256 `8B7D328145C2F8EB96CA8FABAAD59A22D4016CD6FEC63797CAB588C05FD42475`
- 配置 `E:\CV农场助手\UserData\WindowsProfile\LocalAppData\qq-farm-bot-rev\config-multi.ini` SHA-256：`4F2370E0A94A940C80DBFE93E5F41B3A2A15A2BBEC5751721BD24F0545B7B728`，部署前后保持一致。
- UserData、logs、backups 未清理；GUI 未改动。
- `python -m py_compile portable/hook.py`：OK；`git diff --check`：OK；部署 launcher PowerShell 解析：OK；`launcher.ps1 -NoLaunch`：exit 0。

## Live verification
- 2026-09-01 23:46:28 重启旧进程，23:46:32 新进程 PID `43564` 启动，Responding=True。
- 23:46:24 日志已有好友务农并推进到第 3 个好友；23:47:27 重新判定场景；23:47:45 进入自家务农；23:49:15 又进入好友链路。
- Hook 证据出现 `native-share-completion-latch` 后仍有 `v474 native run_cycle dispatching original business cycle`。
- 23:49:50–23:50:50 响应采样 12/12，Responding=False 为 0，进程缺失为 0。
- 现场另有一次 OCR 超时和一次普通出售模板置信度不足，均未造成空循环或进程退出。

## Known unrelated verification gaps
完整 `unittest discover` 本轮结果为 1414 tests、11 skipped、16 failures、5 errors；失败集中于历史奖励顺序契约、缺失旧性能脚本和 v429 旧视觉几何 fixture，不属于本次分享锁/巡检恢复改动。独立运行的 66 项受影响回归全部通过，因此本次只记录为候选修复部署，不把历史全量结果写成全绿。

## Current state and next action
生产进程 PID `43564` 继续运行，当前修复已部署并完成现场采样。下一步仅在用户出现新的自然日志证据时处理新问题；若需发布到 GitHub，再以本备份和当前哈希为基线创建单独提交。

## 2026-09-02 02:52:00 +08:00 — v1.4.57 final publication

- User requested a direct release finish without repeating the whole TDD process; production objective remained hidden capture/DPI/WGC recovery, bounded empty patrol, daily 3/3 gate, and 2x2 fallback.
- Added the final release-packaging exclusions for `.analysis`, `.codex`, `.git`, `.latest_*`, and `diagnose_*.json`; kept `UserData`, logs, backups, personal settings, and GUI out of the public package.
- Verification: targeted capture/recovery suite 36/36; runtime-cycle suite 13/13; startup/WGC/capture suite 22/22 plus visible-capture suite 7/7; release packaging 2/2; `py_compile` and `git diff --check` OK.
- Full discovery evidence remains 1427 tests with 12 historical/unrelated failures and 5 historical missing-script errors, skipped=11; this is recorded and not represented as all-green.
- Release package: `E:\CodexBuilds\qq-farm\releases\CV-Farm-Assistant-v1.4.57-Portable-Full.zip`, 143068926 bytes, SHA-256 `FA7B5BDD970FDB9609F75A5BFB621921D836186E5B08E6E8FE78D9A61D6F5181`; 392 entries and zero forbidden entries.
- Git commit `2d3d312441df86727a420084c8ce51e1a47c08d6` pushed to `main`; annotated tag `v1.4.57` pushed; GitHub Release is Latest with the ASCII-named package and SHA-256 sidecar. Remote asset digest matches the local ZIP.
- Source/deployment Hook remains equal: 2557414 bytes, SHA-256 `A66A880FAC90580231196B7208DC72B215989D33C533910D0C34DB4D1BC443BD`; deployed process PID `29436` is responding. Config hash remains `4F2370E0A94A940C80DBFE93E5F41B3A2A15A2BBEC5751721BD24F0545B7B728`.
- Known non-release workspace captures and historical fixtures remain untracked and untouched; no destructive cleanup was performed.
- Next action: use the v1.4.57 GitHub package for the next user update; investigate only a new runtime log or screenshot.

## 2026-09-06 12:30:00 +08:00 — v1.4.58 crop catalog correction

- Objective: correct the level-based crop choice observed at player level 134. The supplied shop frame confirms `晚香玉` at level 134, `人参` at 136, and `鳄梨` at 138; the runtime log had selected `菠萝蜜` and fuzzy OCR had reported `菠萝`.
- Implementation: `portable/hook.py` adds a conservative v2.3.3-derived unlock-boundary map, applies it only to automatic level strategy calls with a trusted live level, preserves explicit crop and daily radish choices, and keeps crop-card comparison exact rather than prefix-based.
- RED/GREEN: the new crop regression was first run before the helper/guard existed and failed as expected; final focused crop tests are `5 / 5 OK`. Planting/backpack/level affected suite is `143 / 143 OK`; release packaging is `2 / 2 OK`; `py_compile` and `git diff --check` pass.
- Full discovery: `1431` tests, `12` historical/unrelated failures, `5` historical errors, `11` skipped. The failures are retained as baseline evidence and are not attributed to this crop change.
- Deployment: backup `E:\CV农场助手\backups\v1.4.58-predeploy-final-20260906-122245`; source/deployed Hook SHA-256 `80424F78357BD14DB2C3052FEB3A7D53C50227F4A4E1E7C686CB50CC12F9A176`, bytes `2562692`; config SHA-256 remains `4F2370E0A94A940C80DBFE93E5F41B3A2A15A2BBEC5751721BD24F0545B7B728`.
- Package: `E:\CodexBuilds\qq-farm\releases\CV农场助手-v1.4.58-便携完整版.zip`, bytes `278006190`, SHA-256 `39E3F17413873A66C24963B54845B5E82EB5CDADDDAC1A77EE425BE79C39ED99`; package contains no `UserData`, logs, backups, or analysis folders.
- Live state: deployed process PID `32976` is responding after hidden restart; no natural level-134 planting event has occurred after deployment, so runtime crop selection still needs confirmation from a future log line `播种策略选择：晚香玉`.
- Next action: publish the committed v1.4.58 source and package to GitHub, then observe the next level-based planting cycle.


## 2026-09-06 13:23:44 +08:00 — v1.4.59 native crop selector correction deployed

- Objective: fix the native level-crop selection that logged and passed 菠萝蜜 at level 134; preserve the daily 白萝卜 branch and explicit crop selection.
- Evidence: production log showed `当前玩家等级：134` followed by `播种策略选择：菠萝蜜`; the stop signal arrived before planting, so that round did not provide evidence of daily radish execution.
- RED: added native selector regression coverage; before implementation the wrapper test errored because `_wrap_native_crop_catalog_result_func` was absent.
- Implementation: `portable/hook.py` now wraps the native `get_best_crop_for_level` entry and corrects its returned crop before the strategy log. The wrapper preserves result shape, skips explicit strategies and 白萝卜, and the existing planting-owner correction remains as a second guard.
- GREEN: `python -m unittest -v tests.test_crop_strategy_catalog_regression_20260906` = 9/9 OK; `python -m py_compile portable\hook.py` OK; `git diff --check` OK.
- Deployment: backup `E:\CV农场助手\backups\v1.4.59-predeploy-20260906-132008`; deployed hook SHA-256 `7F779704433DA380DC11CD04B420360E0F4C2D950014BA8C1E373BEBF540BF63`, bytes 2574518; restarted process PID 29288, Responding=True.
- Runtime proof: after restart, the log contains two `v233 native crop catalog correction: level=134 -> 晚香玉` entries from `bot._q8eacf4154f.crop_catalog.get_best_crop_for_level`.
- Remaining live check: the next un-interrupted self-farm planting cycle should show `播种策略选择：晚香玉`; daily radish remains conditional on its configured switch, fresh empty plots, quota, and no stop signal.
- Next action: commit the focused source/test/release-note changes, build the 1.4.59 package, and publish the GitHub release after fresh verification.

## 2026-09-06 14:38:00 +08:00 — v1.4.60 stale full-board planting rollback

- Objective: stop a stale physical 24/0/0 frame from suppressing planting when the native runtime has just reported an empty plot.
- Root cause: the v433 preflight treated one PrintWindow/WGC full-board observation as a route decision, cleared the self-planting latches, and allowed the same cycle to proceed to friends.
- RED/GREEN: `tests.test_v481_pending_empty_preflight_guard_20260906` plus the updated v433 contract = `4/4 OK`; `py_compile` and `git diff --check` = OK.
- Implementation: v1.4.60 makes the full-board result observation-only and delegates to the native planting owner for a fresh detection/action. Conflicting pending-empty state is preserved.
- Deployment: backup `E:\CV农场助手\backups\v1.4.60-final-predeploy-20260906-143808`; source/deployed Hook SHA-256 `6B264ABD9B497222EFF5AE47D7595BD607E08875D858BDEBB3241E8269A07357`, bytes `2575980`; config/UserData/logs retained.
- Live restart: PID `27992`, `Responding=True`; startup loaded the new Hook and restored the native runtime. The next natural empty-land event remains the final live confirmation.
- GitHub: commit `397947d` pushed to `main`.

## 2026-09-06 16:22:00 +08:00 — v1.4.62 friend visual-proof transaction fix

- Objective: stop the observed case where the friend page did not move or receive a real click while the native log advanced `2/12` through `12/12`.
- Evidence: `C:\Users\11616\.codex\attachments\21763449-5072-49eb-ad29-936567487dd2\pasted-text.txt` shows repeated friend progress with a fixed page and no durable counter growth; the deployed runtime was still v1.4.60 before this change.
- Root cause: the friend dispatcher only rolled back when two visual signatures were available and equal. A missing/invalid capture therefore left native cursor-like state trusted. Optimistic logger messages also depended only on stack discovery and missed compiled callback paths.
- RED: added `test_friend_poll_rolls_back_claimed_progress_when_capture_has_no_proof` and `test_runtime_info_uses_active_cycle_context_when_stack_has_no_bot`; both failed before the production change for the expected reasons.
- Implementation: `portable/hook.py` now treats a claimed friend transition without durable counter growth and without two valid visual signatures as unconfirmed, restores the complete cursor transaction, and logs `v482 friend dispatch visual unconfirmed`. Runtime log rewriting falls back to `_ACTIVE_RUN_CYCLE_CONTEXT` when the bounded stack walk cannot find `FarmBotCV`.
- GREEN: `python -m unittest -v tests.test_v481_friend_no_progress_guard_20260906` = 7/7; focused friend/durability/unknown-frame suite = 25/25; `python -m py_compile portable\hook.py` and `git diff --check` pass.
- Deployment: backup `E:\CV农场助手\backups\v1.4.62-predeploy-friend-visual-20260906-161740`; source/deployed Hook SHA-256 `5D2356B1911E67242C2C631AF58C0598775366D734FED44AE65B88395995885D`, bytes `2594057`; config SHA-256 preserved as `4F2370E0A94A940C80DBFE93E5F41B3A2A15A2BBEC5751721BD24F0545B7B728`.
- Live restart: launcher restarted the assistant; PID `21328` is responding. After restart, no further `2/12 -> ...` false-progress sequence appeared in the observed 16:18–16:22 log window; friend no-target rounds returned through the bounded list route instead of advancing a stale friend chain.
- Current state: v1.4.62 is deployed with GUI, UserData, config, hidden-window behavior, planting, daily routines, auto-sale, and guard-dog paths untouched. The next action is to commit/push this focused change and use a fresh friend-page opportunity for natural proof.


## 2026-09-16 01:06:00 +0800 — v1.4.63 微信窗口句柄应用修复：部署与现场启动验证

- 目标：闭环“微信抢鼠标只记录已启用、没有实际应用确认”问题，并把修复部署到 `E:\CV农场助手`；不改动用户配置、UserData、日志与历史备份。主机文件名中的 `20260917` 是系统时钟生成的现场证据标记，业务日期按当前环境记为 2026-09-16。
- 实现：`portable/hook.py` 新增 HWND 规范化、运行态/捕获对象句柄提取、已绑定农场窗口优先选择、原生调用前句柄注入，以及“已应用”日志的结果证明门控。原生失败或返回 `None` 且没有运行态已应用句柄时，不再写入伪成功日志。
- RED/GREEN：本轮聚焦微信回归 `tests.test_wechat_focus_hwnd_application_20260916` = 6/6；捕获/DPI/恢复/运行时兼容组合 = 25/25；`python -m py_compile portable\hook.py` 与 `git diff --check` 通过。
- 部署：已创建 `E:\CV农场助手\backups\v1.4.63-predeploy-wechat-focus-20260917-004758`，仅备份并替换 `hook.py`、`VERSION`、`CHANGELOG.md`、`README.md`。源/部署 `hook.py` 均为 2,607,171 bytes，SHA-256=`9C16BDFB22E49BEDD38921763157ACFE28D21867F1E8E0E3048C66E57F6801CA`；配置 SHA-256 仍为 `4F2370E0A94A940C80DBFE93E5F41B3A2A15A2BBEC5751721BD24F0545B7B728`。
- 现场：`launcher.ps1 -NoLaunch` 返回 0；`launcher.ps1 -Restart` 后 GUI 进程响应，最新启动段确认 `hook-runtime-identity ... bytes=2607171`，并继续执行 QQ 场景的日常分享、任务、巡检和种植链路；最新日志段未见 Traceback、WGC 启动异常或捕获失败。当前实际运行链路是 QQ 协议（`tencent://`），所以本次现场段没有触发微信专用“已启用/已应用”两条日志；微信句柄应用逻辑已由 6 项回归覆盖。
- 全量证据：完整 discover = 1450 tests，14 failures，38 errors，11 skipped；失败/错误集中在既有历史 fixture、缺失的旧性能脚本和旧视觉/流程契约，未将该结果记录为全绿。完整输出保存在 `.analysis\full-discover-wechat-focus-20260917.txt`。
- 当前状态：部署版本 `1.4.63`，应用仍可启动；UserData 与配置保留。下一步是使用真实 WeChat/Weixin 协议实例做一次窗口句柄现场验证，确认日志出现“微信抢鼠标处理已启用”与“微信抢鼠标处理已应用”，再进行远端提交/发布。


## 2026-09-16 — v1.4.63 本地提交与远端同步状态

- 本次相关文件已提交到本地 `main`：`c0d8e50 fix wechat focus hwnd application proof`。
- 提交内容仅包含 `portable/hook.py`、版本/更新日志/README，以及微信句柄回归测试；历史 fixture 与其它未跟踪测试保持原样。
- `git push origin main` 在当前现场因连接 `github.com:443` 超时失败，远端尚未确认更新；本地提交可在网络恢复后直接重试，不需要重新改代码。
- 下一步：网络可用时重试 `git push origin main`，随后以远端 commit/hash 做一次确认；真实 WeChat/Weixin 协议现场验证仍是 v1.4.63 的最后一项专门证据。


## 2026-09-16 18:00:00 +0800 — v1.4.63 微信句柄修复远端同步与真实窗口证据

目标：完成 v1.4.63 微信抢鼠标句柄修复的远端同步，并继续收集真实 WeChatAppEx 窗口证据。

已完成：
- 通过本机 SOCKS5 代理 127.0.0.1:10808 推送 `c0d8e504601367092f8ed21d7758cd7debf01d69` 到 `origin/main`。
- `git ls-remote` 已返回相同的 `refs/heads/main`，远端与本地一致。
- 新鲜聚焦回归：6/6 OK；捕获/DPI/遮挡/启动恢复组合：14/14 OK。
- `python -m py_compile portable/hook.py` 与 `git diff --check` 通过。
- 源码与部署 Hook 均为 2,607,171 bytes，SHA-256=`9C16BDFB22E49BEDD38921763157ACFE28D21867F1E8E0E3048C66E57F6801CA`。
- 部署版本为 `1.4.63`；生产配置 SHA-256 仍为 `4F2370E0A94A940C80DBFE93E5F41B3A2A15A2BBEC5751721BD24F0545B7B728`；生产 PID 17868 Responding=True。

真实窗口证据：
- 当前机器枚举到真实 `WeChatAppEx.exe` 顶层窗口 `HWND=0x1066E`，矩形 `(203,203)-(1483,984)`；当前选择器默认返回 `0x1066E`，显式绑定该句柄时仍优先返回该句柄。
- 该隐藏窗口的 PrintWindow 返回黑色表面，说明句柄存在但当前不是可用的可视农场帧；没有把黑帧误报为“已应用”。
- 临时动态配置探针已在隔离前后校验配置哈希并恢复原值；由于没有重启/重新绑定生产实例，未把“已启用/已应用”现场日志伪造为完成证据。

当前状态：
- 生产仍是 QQ `tencent://` 链路，当前运行实例没有触发微信专用日志。
- 微信句柄选择与结果门控已完成自动化验证，真实 Weixin 模式的“已应用”两行日志仍需一次受控的 Weixin 实例启动/重新绑定现场签收。

下一步：在不改动生产配置的前提下，使用已有的受控提升启动路径切换到真实 Weixin 实例，采集 `微信抢鼠标处理已启用` 与 `微信抢鼠标处理已应用` 两行；若该实例仍只返回黑色隐藏表面，则继续收集 WGC/PrintWindow 句柄绑定证据，不扩大到种植和好友模块。

## 2026-09-18 13:30 +0800 — v1.4.64 QQ/微信捕获平台串线修复：部署与现场验证

- 目标：修复 QQ 模式沿用微信捕获对象/`MMUIRenderSubWindowHW` 选择器，造成 WGC 失败、画面进入 `unknown` 连环恢复、好友和自家巡检无实际动作的问题。
- 实现：`portable/hook.py` 增加平台感知捕获对象规范化；QQ/微信模式分别清理对方选择器，优先注入当前农场 HWND；窗口重建或 HWND 缺失时清除旧句柄；不可修改的跨平台原生对象不再重复调用，改走自有可见捕获路径。WGC 启动增加平台、HWND、selector 和错误诊断日志。
- 回归：`tests/test_v485_capture_owner_platform_guard_20260918.py` = 8/8；v483/v2.3.7 平台捕获 = 3/3；v484 捕获完整性 = 5/5；WGC 后端 = 19/19；微信句柄回归 = 18/18；合计 = 53/53。`python -m py_compile portable\hook.py` 与 `git diff --check` 通过。
- 全量证据：`python -m unittest discover -s tests -p 'test*.py'` = 1478 tests，14 failures，38 errors，11 skipped。失败/错误集中于历史背包/空地契约、缺失旧性能脚本、历史好友/分享/几何 fixture；本次 v485/v483/v484/微信句柄测试均未失败。完整输出：`.analysis\full-test-20260918-v485-final.txt`。
- 备份：`E:\CV农场助手\backups\v485-predeploy-1.4.64-20260918-131451`。仅备份部署 Hook、版本文件、更新日志和 README；未覆盖 `UserData`、`logs` 或 `config-multi.ini`。
- 部署：版本 `1.4.64`；源 `portable\hook.py` 与部署 `E:\CV农场助手\hook.py` 均为 2,645,119 bytes，SHA-256=`C9D9B229CACEE73198CFE21A0BB133CCA4E16DA84A315061AE74140C1860C119`。配置 SHA-256 部署前后均为 `4F2370E0A94A940C80DBFE93E5F41B3A2A15A2BBEC5751721BD24F0545B7B728`。
- 现场：`launcher.ps1 -Restart` 于 13:15:16 执行；新 PID `12488`，Responding=True。启动日志出现：`v485 capture owner normalized platform=QQ hwnd=44369892 selector=QQ经典农场`、`v485 WGC selector decision platform=QQ farm_hwnd=44369892 selector=hwnd=44369892`、`v483 WGC game-window capture started platform=QQ selector=hwnd=44369892`。
- 现场业务证据：13:15:52 后出现商城/免费福利动作；13:16:23 进入自家农场并点击一键务农；13:27:44、13:30:14 出现好友一键务农、好友返回及捣乱流程。13:15:35 之后没有新的 `MMUIRenderSubWindowHW`、`WGC start error` 或连续 `当前场景不明确` 循环；启动后的首次 unknown 属于重启等待新画面的单轮恢复，不再持续。
- 当前状态：v1.4.64 已部署并运行，GUI、UserData、配置和原有业务链路保留。下一步：只提交相关源码、回归测试和版本文档，推送 `origin/main`；不加入仓库中既有的大量未跟踪 fixture/test 文件。

## 2026-09-18 13:32 +0800 — v1.4.64 提交与远端确认

- 本地提交：`e4f778eec4cd497620ef37ecd38ec1ec6d06f295`，提交信息 `fix QQ capture platform cross-binding`。
- 已通过 SOCKS5 `127.0.0.1:10808` 推送到 `origin/main`；`git ls-remote` 返回相同 commit，远端已确认。
- 当前工作区只保留历史未跟踪 fixture/test 文件，未将其加入提交；相关源码、版本文档和 v485 回归测试已提交。
- 生产复核：PID `12488`、Responding=True；源/部署 Hook SHA-256 相同；版本 `1.4.64`；配置哈希未变。重启后的业务日志已出现商城、免费福利、自家务农、好友务农和捣乱动作；持续 `unknown`、`MMUIRenderSubWindowHW` 与 WGC 启动错误均未再出现。
- 当前下一动作：等待用户下一次真实窗口重建/隐藏恢复场景；若再次出现异常，优先根据 `v485 WGC selector decision` 和 `v485 WGC start error` 日志定位，不回退到旧微信选择器。


## 2026-09-18 18:18:00 +0800 — v487 当前卡片式好友列表卡死修复与部署

### 目标与症状
- 2026-09-18 现场好友列表循环：每 12 秒重复“正在检查好友农场/好友场景纠偏”，没有 `v118 friend list preflight` 或 `v203 friend list visit`。
- 当前现场样本 `tests/fixtures/live-v486-current-friend-list-20260918.png` 的 428×800 新卡片布局有 3 个好友卡片，但旧按钮检测器只返回 1 个右侧装饰连通块，预检的 `rows >= 3` 门槛因此阻断点击。

### RED→GREEN
- 新增 `tests/test_v487_current_friend_card_rows_20260918.py`：先验证旧实现对当前样本只得到 1 行而失败；修复后 3 行、排序、点击区间、任务面板隔离和首行 `v203` 访问证明均通过。
- 相关回归：v487 3/3、v422 2/2、v423 1/1、v483/v484/v485/v486 与微信焦点回归合计 41/41 OK；`py_compile` 和 `git diff --check` OK；好友主套件 328/328 OK。

### 实现
- `portable/hook.py` 增加由好友页签模板确认的卡片纵向分段检测；保留旧绿色按钮路径，只有旧路径少于 3 行时才启用卡片兜底。
- 卡片兜底按动态尺寸推导行中心，当前样本得到 `(312,438)`, `(312,579)`, `(312,722)`；任务面板不产出好友行。
- `_handle_friend_list_surface` 和运行周期预检增加受限诊断日志，记录帧尺寸、行数、中心和来源。

### 部署与现场
- 生产 Hook 已复制并核对：2654262 bytes，SHA-256 `539CE11ECFC887D5FE45E14C817887E48F9825C493DA45107827254969B08FAF`；源/部署一致。
- 回滚备份：`E:\CV农场助手\backups\v487-friend-card-20260918-20260918-181122`。
- 受控重启后，2026-09-18 18:14:25–18:16:07 现场日志已从好友无动作循环恢复为一键务农、底部好友入口推进、捣乱收敛、回家和自家巡检；进程响应正常。

### 迁移边界
- 当前运行版本仍是 `1.4.64`：本次是对现有后端的兼容层/捕获桥接和好友卡片路由修复，不是 2.3.x 核心后端的完整替换；2.3.x 的全量迁移仍未完成，不能把本次修复表述为完整迁移。

### 下一步
- 下一次真实出现该 428×800 卡片好友列表时，核对现场日志是否出现 `v487` 诊断、`v118 friend list preflight` 和 `v203 friend list visit`，并保存一帧新截图；若仍无三条证据，再按新截图继续收敛检测器。


## 2026-09-18 23:21:22 +08:00 — v493 ordered friend-list terminal latch deployed

Objective: stop the ordered friend list from restarting at row one after the final row, including after native reopens and process restarts, while preserving legitimate newly rearmed sessions.

Evidence and root cause:
- v491 proved ordered transitions 0/5 -> 4/5, but after the final confirmation the old path logged `v219 reopened friend list reset stale cursor=5; selecting first row`.
- v492 closed the immediate final-row acknowledgement, yet live production later reopened the same terminal list and `v358`/`v219` reset it to row zero. A first v493 candidate still failed after restart because the native owner had set `restore_attempted=True` before readable list pixels existed, so the terminal journal was never restored.
- The durable terminal journal therefore existed, but the visible-list handler treated the next readable list as a new session and fabricated a second pass.

RED/GREEN implementation:
- Extended `tests/test_v491_friend_list_confirmed_cursor_resume_20260918.py` with terminal-latch, terminal-journal restore, and visible-list retry-after-empty-attempt regressions.
- RED evidence: terminal state returned `visited` instead of `closed-terminal-latch`; restored context lacked `_qqfarm_friend_chain_exhausted`; and a visible list did not retry restore after an earlier empty attempt.
- `portable/hook.py` now restores terminal phase as exhausted/home-allowed/empty-latched, retries journal restore on the first real list frame when no successful restore exists, and returns `closed-terminal-latch` after closing a terminal reopen without touching cursor N.
- The native friend preflight treats `closed-terminal-latch` as handled. A `terminal_latched` predicate preserves the historical contract that a genuinely new stale/exhausted session with an explicit resume marker still resets to row zero.

Verification:
- v493 targeted suite: 6/6 OK.
- Compatibility and durable-journal focused suites: 26/26 OK, including the live selected-second new-session reset contract.
- Full friend discovery: 519 tests, 8 known baseline failures only (`friend_guard_continuous_polling` x3, v434 x1, v435 x2, v444 x1, v445 x1). The temporary ninth failure introduced by the broad exhausted gate was removed before final deployment.
- `python -m py_compile portable\hook.py`: OK.
- `git diff --check`: OK.
- Full friend log: `.analysis\v493-final-friend-suite-20260918.log`.

Deployment and rollback:
- Final source/deploy Hook: 2,679,807 bytes; SHA-256 `0C2759067511090CFF200AF8FBD3C22A409E7359DF005F333C2CC39CD4FA9EE1`.
- Configuration remained SHA-256 `4F2370E0A94A940C80DBFE93E5F41B3A2A15A2BBEC5751721BD24F0545B7B728`.
- Backups: `E:\CV农场助手\backups\v492-friend-terminal-20260918-222843`, `v493-friend-terminal-latch-20260918-224835`, `v493-visible-terminal-restore-20260918-225710`, and `v493-terminal-compat-20260918-231013`.
- Duplicate second-pass friend counts were removed from all six active JSON mirrors and both CSV mirrors before the final run; subsequent real self work continued naturally. Current mirrors agree: friend help 151, trouble 256, self farming 14, friend harvest 3; CSV row `2026-09-18,0,14,3,151`.

Live production proof:
- Final PID 31144 is running and Responding=True.
- The first readable terminal list produced `v493 friend list terminal latch active; closed without resetting cursor=5/5` and `dispatch result=closed-terminal-latch`.
- Through the subsequent full friend suite interval: first-row visits=0, any list-row visits=0, stale resets=0, Traceback=0, exception=0, and friend help remained 151.
- Journal remains terminal at cursor=5/5, resume_pending=false, so a restart cannot silently restart the same completed pass.

Current production state: v493 is deployed and running; the page is no longer left to cycle through the same visible friend list, and terminal reopens close without count growth.

Next action: observe the next naturally verified home-progress rearm or visible home friend request; that event should clear the terminal latch and begin exactly one new ordered pass from row zero.

## 2026-09-18 23:40:43 +08:00 — v493 GitHub publication verified

- Published commit `277642a308575d16959e07865825fa432a9aed05` to `origin/main`; `git ls-remote` returned the same SHA for `refs/heads/main`.
- Included the production launcher correction (`QQFARM_STRICT_PLANTING_ROLLOUT=0`), ordered card-list detection/dispatch, confirmed cursor persistence, render-child click routing, final-row close, and durable terminal latch.
- Public regression fixtures for the current friend-card layouts were mosaicked before commit so friend names and avatars are not readable; original local copies remain only under ignored `.analysis/private-fixtures-20260918`.
- Fresh directed verification: v486-v493 set `15 / 15 OK`; `py_compile` and staged/diff checks passed.
- Fresh friend discovery: `519` tests with the same `8` recorded historical baseline failures and no new failure.
- Production remains source/deploy identical: Hook `0C275906...FA9EE1`, launcher `EAF00D84...B01BB9C4AC`; PID `31144` is responding.
- Latest 500 Hook lines: terminal close `35`, first/list-row visit `0`, stale reset `0`, Traceback `0`, Exception `0`. Journal remains `phase=terminal`, `cursor=5/5`, `resume_pending=false`; friend-help mirrors remain `151` and both CSV rows remain `2026-09-18,0,14,3,151`.

Next action: on the next real home-progress or visible home friend-request rearm, verify exactly one new ordered `0/5 -> 5/5` pass and one return to the terminal latch.


## 2026-09-19 02:52:01 +08:00 — v495 same-day terminal entry hold and final v1.4.65 deployment

### 目标与现场症状

- 用户截图显示自家 24 块土地均已有幼苗，但原生模板曾报出 6 块空地并进入背包/买种分支；好友截图为当前 5 行卡片列表，旧终态会被反复打开后立即关闭。
- 生产日志已出现 2026-09-18 → 2026-09-19 业务日切换。第一版跨天修复可在正常启动时重置，但运行态日期若先被写成新日，旧的持久化 terminal journal 会被提前返回遮蔽。
- 同日 5/5 终态完成后，原生 `process_friend_farm` 仍会周期性重新打开好友列表，造成一次次“打开—关闭”空耗。

### RED 与根因

- `tests/test_v494_crossday_fullboard_shop_gates_20260918.py` 新增“运行态已经是 2026-09-19、持久 journal 仍是 2026-09-18 terminal”回归；修复前返回 `False`，未清零游标。
- `tests/test_v489_native_friend_list_preflight_20260918.py` 新增同日 terminal latch 的原生 owner 回归；修复前返回 `native-result`，证明仍调用了原生好友处理并可重新打开列表。
- 根因分别是 `_friend_progress_journal_rearm_for_business_date()` 在读取持久 journal 前按运行态日期提前返回，以及 native-v225 owner bridge 只在列表已经可见后收敛，没有在下一次 home/rows=0 调用前执行终态门禁。

### 实现

- 跨天检查现在先读取持久化 journal，再决定是否按运行态日期短路；只要 journal 明确属于上一业务日，就优先重置 cursor/pending/terminal 字段并持久化新日 cursor 0。
- native-v225 好友 owner 在调用编译实现前先执行业务日重置，再执行稳定空轮/同日 terminal 调度门。列表已经可见时仍只关闭一次；之后写入 `v495 native friend owner held ... skipped friend-list reopen` 并跳过原生列表重开。
- 保留 v494 严格 24 格满地观察、45 秒新鲜空地/棋盘凭据买种门、背包候选优先和满地清理播种残留逻辑。
- `CHANGELOG.md` 补充同日终态在原生入口直接拦截；QQ Farm conversation requirements 已同步，修改前备份为 `.analysis/backups/conversation-requirements-before-v495-20260918.md`。

### 验证

- v494：10 / 10 OK。
- v489、v491、持久 journal、自家空地与背包聚焦组合：177 / 177 OK，11 skipped。
- Git 跟踪全套：929 tests，5 个既有历史失败、0 errors、11 skipped；失败仍为 v434、v435×2、v444、v445 的旧好友计数契约，与本轮新增测试和终态入口门无新增失败。日志：`.analysis/v495-tracked-full-final.log`。
- `python -m py_compile portable/hook.py`：OK；`git diff --check`：OK；发布打包测试：2 / 2 OK。

### 部署与现场证据

- 回滚：`E:\CV农场助手\backups\v495-terminal-entry-hold-1.4.65-20260919-024701`。
- 源/部署 Hook：2,709,657 bytes，SHA-256 `9C65492FAB0831AA1E6BDAD0DBF5174F1CDA501F9A77F7D7620A8B24F4801C8D`。
- 配置 SHA-256 部署前后均为 `4F2370E0A94A940C80DBFE93E5F41B3A2A15A2BBEC5751721BD24F0545B7B728`。
- 生产 PID `29656`，Responding=True。
- 重启后的同日终态现场：先出现 1 次 `rows=5` 与 1 次 `v493 ... closed without resetting cursor=5/5`，随后两轮均为 `rows=0` + `v495 ... skipped friend-list reopen`；后续没有第二次 `rows=5`，Traceback=0，Exception=0。
- 本次重启前已留下跨天实证：`v494 friend progress cross-day reset old=2026-09-18 new=2026-09-19 cursor=0 persisted=true`，并完成 0/5 → 5/5 的一次有序好友巡查。

### 当前状态与下一动作

- 当前 journal 为业务日 `2026-09-19`、`phase=terminal`、`cursor=5/5`，这是当天已完成后的预期去重状态；原生 owner 已不再周期性重开列表。
- 自家满地/买种修复已有真实截图 fixture 与自动化证明；仍等待下一次自然收获或真实空地机会补充生产 `v494 strict full-board` / 买种门日志，不以等待该机会阻塞发布。
- 下一动作：只暂存本轮源码、版本文档、v489/v494 测试、v494 脱敏 fixture 和 handoff，提交并推送 `origin/main`，随后构建并发布 v1.4.65。

## 2026-09-18 19:12 UTC — v1.4.65 GitHub publication complete

- Objective: finish publishing the full-board false-empty, backpack/shop gate, cross-day friend reset, and same-day friend terminal-entry fixes without changing GUI or user data.
- Source commit: `314d75aa71509b1428e5200a181fdfd9829f555a`; `origin/main`, annotated tag `v1.4.65`, and the GitHub Release target all resolve to this commit.
- Release: `https://github.com/combating123/qq-farm-cv-helper-portable/releases/tag/v1.4.65`; GitHub reports `v1.4.65` as the latest release.
- Public asset: `CV-Farm-Assistant-v1.4.65-Portable-Full.zip`, 146,299,586 bytes, SHA-256 `EE3E8CE3A93C77C05E6972B6C6CDA56737E30263FC699CB36DBC73E06CE9C120`. A fresh post-upload download produced the same byte count and digest.
- Package audit: 392 entries; zero `UserData`, logs, backups, `.analysis`, `.git`, `.codex`, personal captures, or runtime log files.
- Fresh focused verification: 108 tests OK, 11 skipped; release packaging 2/2 OK; `py_compile` and `git diff --check` OK.
- Fresh Git-tracked suite: 939 tests, five known historical failures in v434/v435/v444/v445, zero errors, 11 skipped; no new v494/v495 failures. Log: `.analysis/v495-tracked-full-release-20260918.log`.
- Runtime identity: source/deployed Hook 2,709,657 bytes, SHA-256 `9C65492FAB0831AA1E6BDAD0DBF5174F1CDA501F9A77F7D7620A8B24F4801C8D`; config SHA-256 `4F2370E0A94A940C80DBFE93E5F41B3A2A15A2BBEC5751721BD24F0545B7B728`; PID 29656 Responding=True.
- Live log: no Traceback or Exception in the latest segment. Hook logs continue to show `v495 native friend owner held by the same-day terminal/empty latch; skipped friend-list reopen`; the cross-day proof remains `v494 friend progress cross-day reset old=2026-09-18 new=2026-09-19 cursor=0 persisted=true`.
- Rollback remains `E:\CV农场助手\backups\v495-terminal-entry-hold-1.4.65-20260919-024701`.
- Next action: observe the next natural harvest/real-empty event for production planting proof; do not reopen the implementation unless fresh pixels/logs contradict the v494 board/shop gates.


## 2026-09-19 12:55:00 +0800 — v1.4.70 好友末行关闭后有界回家恢复与显式动作信号保留

### 目标与症状
- 用户在 2026-09-19 现场看到好友列表末行完成后停留在好友农场，后续每轮只有“正在检查好友农场”而没有回家或自家巡检。
- 旧链路在 `_handle_friend_list_surface()` 返回 `closed`/`closed-terminal-latch` 后直接结束，native owner 未完成“确认当前页面 → 回家 → fresh self surface”闭环。

### RED → GREEN
- `tests/test_v500_terminal_friend_list_home_recovery_20260919.py` 先验证 native terminal close 不会调用回家恢复（RED），再验证 4/4：已在自家页直接释放、好友页只点一次缩放感知回家并确认自家页、未确认时保持 bounded pending 且同一间隔不重复点击。
- 之前的 `test_friend_guard_continuous_polling` 另有 3 个基线失败：捕获暂缺时本轮新动作/新导航/待进入信号被 v482 回滚。将 visual rollback 限定为持久游标字段并保留本轮显式信号后，完整该模块通过。

### 实现
- `portable/hook.py` 新增 `_recover_home_after_friend_list_terminal()`：关闭末行列表后进行新鲜画面复核；仍在好友农场时执行一次缩放感知回家点击，最多 4 次新鲜验证；只在确认自家画面后释放终态锁；8 秒间隔门和 3 次有界预算防止点击循环。
- native v2.2.5 friend owner 在 `closed`、`closed-terminal-latch` 分支接入恢复桥。
- continuous friend wrapper 只回滚未经视觉确认的持久列表游标，不再丢弃本轮已经产生的动作、导航和待进入信号。
- `VERSION`/`CHANGELOG.md`/`README.md` 更新为 `1.4.70`；未覆盖 `UserData`、配置或日志。

### 验证
- 近期捕获/好友/跨天/终态回归：`69 / 69 OK`。
- `python -m py_compile portable/hook.py`：OK；`git diff --check`：OK。
- 源/部署 Hook：`2,734,398` bytes，SHA-256 `E0BC927EE970A10A8C6A517E3A744624079D8A457DB6AB780188268D8A1A0EE2`。
- 配置 SHA-256 保持 `4F2370E0A94A940C80DBFE93E5F41B3A2A15A2BBEC5751721BD24F0545B7B728`。
- 回滚备份：`E:\CV农场助手\backups\v500-terminal-home-1.4.70-20260919-124755`。

### 部署与现场
- 已复制源文件并通过隐藏 launcher 重启；当前 `QQFarmCVHelper` PID `37776`，`Responding=True`，版本 `1.4.70`。
- 重启后出现 `v500 terminal friend-list close -> bounded verified home recovery enabled`。
- 随后的真实运行出现 `v500 terminal friend-list close already reached verified self surface; stale friend route released`，随后正常进入下一轮；没有 Traceback/Exception，且出现正常好友列表行检测与一键务农计数提交。
- 当前现场已证明“关闭后已在自家页”的终态释放分支；仍需在下一次真实的“关闭后仍停留好友农场”场景观察 `v500 ... home transition verified self surface`，再签收实际回家点击分支。

### 当前状态与唯一下一动作
- v1.4.70 已部署运行，GUI、UserData、配置、种植、自动出售、护主犬和每日流程未被迁移覆盖。
- 下一动作：保留当前运行实例，等待下一次自然末行终态；检查是否出现一次 `v500 terminal friend-list home transition verified self surface`，并确认后续三轮不再重复好友列表/空巡检。


## 2026-09-19 13:20:00 +0800 — v1.4.70 最终事务回滚修正与生产复核

### Final correction after full-suite verification
- v1.4.70 的第一版显式信号修复曾让 `v481` 两个“有游标改动但无画面证据”用例误返回 True；已按事务语义收紧：只有动作/导航/待进入元数据变化时保留信号，若持久列表游标也发生变化且缺少新鲜画面，仍完整回滚并返回 False。
- 最终受影响回归：`42 / 42 OK`（v481、continuous polling、v489、v491、v499、v500）；`py_compile` 和 `git diff --check` 均 OK。
- 最终完整发现：`1513 tests`，`17 failures / 5 errors / 11 skipped`；失败/错误均为既有历史基线（v342 缺失分析脚本 5 errors、历史种植/分享/好友序列与 v429 fixture），本轮 v481/v489/v491/v499/v500 均通过，较上一轮减少 2 个新增回归。
- 最终源/部署 Hook：`2,732,164` bytes，SHA-256 `F5FA8E4D67CB20FCF3E953F849CF84A7169DE6C42C4AAE4703CF3F5565509718`；版本 `1.4.70`；生产 PID `22592`，`Responding=True`。
- 最终回滚备份：`E:\CV农场助手\backups\v500-final-1.4.70-20260919-131101`；配置 SHA-256 仍为 `4F2370E0A94A940C80DBFE93E5F41B3A2A15A2BBEC5751721BD24F0545B7B728`。
- 2026-09-19 现场重启后已出现：`v500 terminal friend-list close already reached verified self surface; stale friend route released`，随后好友列表继续从第 1/5 行向后推进；进程保持响应，当前片段未出现 Traceback/Exception。

### 当前唯一下一动作
- 将本轮相关源码、版本文档、v489/v499/v500 回归和发布记录选择性提交并推送 `origin/main`；不加入历史未跟踪 fixture/test，不改 UserData、logs、配置或备份。


## 2026-09-19 22:59:00 +0800 — v1.4.72 稀疏土地锚点满地反证：完整回归完成，准备部署

### 目标与现场根因
- 用户继续反馈“没有空地却识别为空地”；当前 642×1200 PrintWindow 实图实际为 24 格全占用：16 个独立幼苗标记与两块活动平台。
- 旧严格观察要求上层土地三角锚点，当前平台遮挡后只剩 5 个土地锚点，因此返回 `viewport-not-full-board`，没有产生可覆盖原生 6 个假空地候选的满地反证。
- 2.3.7 公开 Source code 归档没有可迁移的 Python 后端（Python 文件数为 0），所以没有把未知二进制整包覆盖到现有 GUI；本轮继续按可验证行为迁入，保持 GUI、UserData、配置、隐藏窗口、自动出售、护主犬和每日流程不变。

### RED → GREEN
- RED 夹具：`tests/fixtures/live-v502-sparse-terrain-seedling-platform-full-board-sanitized-20260919.png`，SHA-256 `C78F70994F0EC5B72ABE2F93117367E758152837E615FA197680D004D524BA2C`。
- RED：当前满地画面返回 `unknown`，6 个原生假空地候选未被清除。
- 实现：`portable/hook.py` 新增 `_sparse_terrain_seedling_full_board_fit()`。它要求规范 428×800 画面、至少 16 个一对一作物标记、4–7 个土地锚点且至少匹配 4 个、唯一棋盘相位、四方向作物覆盖、四边 LAB 边界最低值不低于 26、24 个投影格全部存在当前帧作物覆盖。
- 该证明是 observation-only：只输出 `24 occupied / 0 empty / 0 unknown`，清除假空地并阻止错误买种；`click_safe=False`，不提供任何播种坐标。
- 新增：`tests/test_v502_sparse_terrain_seedling_platform_full_board_20260919.py`；版本提升为 `1.4.72`，启动标记为 `v502 sparse-terrain seedling/platform full-board proof enabled`。

### 新鲜验证证据
- `python -m py_compile portable\hook.py`：OK。
- `git diff --check`：OK。
- v494 + v501 + v502：`14 / 14 OK`。
- 完整发现：`1517 tests`，`17 failures / 5 errors / 11 skipped`，耗时 `840.453s`；失败/错误与上一完整基线一致（缺失历史分析脚本、既有种植/分享/好友序列和 v429 fixture），v501/v502 无新增失败。
- 候选 Hook：`2,750,893` bytes，SHA-256 `E0C363B5CEC9664429556A90D2E9809DC9E501F498465438C9B09D5605A730AE`。
- 完整发现日志：`.analysis/v502-full-discover-20260919-2243.log`。

### 当前状态与唯一下一动作
- 生产仍是 v1.4.71，Hook SHA-256 `3242ED119112A0A35DB48DA26398C6855DE5FDE54CDF83B52DFDBE26DE2B3EDB`；进程 PID `16960`、`Responding=True`；配置 SHA-256 `4F2370E0A94A940C80DBFE93E5F41B3A2A15A2BBEC5751721BD24F0545B7B728`。
- 下一动作：建立 v1.4.72 时间戳回滚备份，只部署 Hook/版本文档，隐藏重启后核对启动标记、源/部署哈希、配置哈希和最新日志异常。


## 2026-09-19 23:16:00 +0800 — v1.4.72 已部署并发布：空地日志无点击权限，稀疏锚点满地识别上线

### 部署与生产证据
- 回滚备份：`E:\CV农场助手\backups\v502-sparse-fullboard-1.4.72-20260919-225750`，含部署前 Hook、VERSION、README、CHANGELOG 与哈希清单。
- 已只复制 `hook.py`、`VERSION`、`README.md`、`CHANGELOG.md`；未改 `UserData`、配置、日志、每日状态或用户开关。
- 源/部署 Hook 一致：`2,750,893` bytes，SHA-256 `E0C363B5CEC9664429556A90D2E9809DC9E501F498465438C9B09D5605A730AE`。
- 配置 SHA-256 保持 `4F2370E0A94A940C80DBFE93E5F41B3A2A15A2BBEC5751721BD24F0545B7B728`。
- 隐藏重启成功：生产版本 `1.4.72`，PID `5748`，`Responding=True`；最新启动段存在 `v501 native empty-land log requires fresh visual proof enabled` 与 `v502 sparse-terrain seedling/platform full-board proof enabled`，没有 Traceback、Exception、PrintWindow timeout 或 WGC error。
- 重启后的首个自家巡检于 2026-09-19 22:59:03 进入，一键务农、等级读取和自动出售正常；该轮没有再次出现“检测到空地”、买种或点地，下一次自家巡检直接记录“家里已无可执行的任务”。
- 30 秒进程采样：`30/30` 响应，`Responding=False=0`，单核折算 `43.83%`，工作集 `429,420,544–446,083,072` bytes，线程数稳定为 `76`。证据：`.analysis/v502-postdeploy-30s-performance-20260919.json`。
- 部署状态快照：`.analysis/v502-postdeploy-status-20260919.txt`。

### GitHub 与发布
- 选择性提交：`131165d1835ff589352a1ba3fd915d07ff06c2d2`（`fix sparse full-board empty-land false positives`），只包含 v501/v502 源码、文档、两项回归测试和脱敏夹具；历史未跟踪 fixture/test 未加入。
- `origin/main`、本地 HEAD 与 `v1.4.72` 标签均指向 `131165d1835ff589352a1ba3fd915d07ff06c2d2`。
- GitHub Release `v1.4.72` 已发布并设为 Latest；中文发布说明已通过 API/CLI 回读，无乱码。
- 发布包：`CVFarmAssistant-v1.4.72-portable-full.zip`，`278,191,463` bytes，SHA-256 `1A3445E9ADD87BC8331C05C3061325ACE95BF4AF90FCFC568C8D67959119C8B9`；包内 VERSION/README/CHANGELOG/hook/EXE 完整，`UserData`、logs、backups 私有目录计数为 0。

### 当前结论与唯一下一动作
- 2.3.7 没有被未知二进制整包覆盖；其公开源码归档没有 Python 后端。本次把可验证的行为门迁入现有 v1.4.72：原生日志空地数没有点击权限，当前稀疏锚点+幼苗+平台满地画面可得到 24/0/0 反证，从而阻止假空地和错误买种，同时保持现有 GUI 与用户状态。
- 下一动作：保持 v1.4.72 运行，等待下一次真实收获或原生假空地候选自然出现；核对真实空地会进入正常播种，而满地时出现 `v494 strict full-board proof overrode native empty candidates` 且不发生土地/商店点击。

## 2026-09-19 — v1.4.73 v2.3.7 作物目录/模板兼容层、启动回归与生产验证

### 目标

- 将 2.3.7 的作物目录与兼容模板接入现有便携后端，继续保留当前 GUI、UserData、配置、本地已激活权益桥、隐藏窗口、自动出售、护主犬和每日流程。
- 修正高等级作物、空地/好友入口/已播种土地模板覆盖，同时保持严格 24 格新鲜画面门控，模板命中本身不获得点击或买种权限。

### 实现

- 新增 portable/data/v237_plant_catalog.json：132 项作物，53,077 bytes，SHA-256 C0C936A3800F155C3946A6B6FE313EAE322231832BFC5ECA8AAA2A4153390387。
- 新增 portable/data/v237_templates：26 项 2.3.7 独有资源，共 61,817 bytes；接入自家空地、好友 seed_land、好友列表入口等原生同语义模板列表，中文路径按字节读取，解码后哈希去重。
- portable/hook.py 新增作物目录加载、等级边界、种子资源名、多季时长、经验效率、净利润和模板 overlay 兼容层。
- 134/136/138 等高等级边界现为晚香玉/人参/鳄梨，旧菠萝蜜记录不再进入自动等级策略。

### 启动回归与修复

- 第一版曾直接把原生 CROPS 替换为字典行；真实 v2.2.5 后端使用位置式行并访问 crop[0]，启动现场出现 KeyError: 0。
- 立即从 E:\CV农场助手\backups\v504-v237-catalog-templates-1.4.73-20260920-010208 回退到 v1.4.72，确认 GUI 和机器人正常启动。
- 新增 RED 用例 test_native_positional_crop_rows_keep_their_original_schema，证明位置式容器不得被替换。
- GREEN 修复：保留原生 CROPS、_CROP_ASSET_NAME_MAP、_CROP_PROFIT_PER_HOUR 对象不变；132 项目录只写入私有 sidecar，精确资源名通过兼容包装返回，未知作物继续回落原生函数。

### 验证

- v503/v504/作物目录组合：18 / 18 OK。
- 空地、背包、2×2、买种门、权益导入、自动施肥和捣乱组合：128 / 128 OK。
- 发布打包测试：2 / 2 OK。
- python -m py_compile portable\hook.py：OK；git diff --check：OK。
- 完整发现：1,526 tests，17 failures，5 errors，11 skipped；与 Git HEAD 基线的同一历史失败集合一致。本轮 v503/v504 与启动 schema 用例均未失败。日志：.analysis/v504-full-discover-after-startup-fix-20260920.log。

### 部署与现场

- 生产版本：1.4.73。
- 源/部署 Hook：2,774,308 bytes，SHA-256 F82A9AF1A08F6EF6CEB418895D438304BD64E08226DBF4654B154A706DF8AC0F。
- 配置 SHA-256 部署前后均为 4F2370E0A94A940C80DBFE93E5F41B3A2A15A2BBEC5751721BD24F0545B7B728。
- 最终回滚：E:\CV农场助手\backups\v504-startup-schema-fix-1.4.73-20260920-011242。
- 生产 PID 20404，Responding=True，主窗体 农场助手 - 视觉自动化。
- 新启动段出现 v503 v2.3.7 crop catalog data installed 与 v504 v2.3.7 template overlays installed；Traceback=0、KeyError=0、Exception=0、WGC/capture error=0。
- 现场已识别 138 级为鳄梨，执行自动出售，并继续自家/好友巡检；10 秒 CPU 增量 1.297 秒。
- 便携包：E:\CodexBuilds\qq-farm\releases\CV农场助手-v1.4.73-便携完整版.zip，278,270,846 bytes，SHA-256 78FDF96539260596A5C404BC0BAAAF971181579F1D4A5EB038A47365E0CE6E3A。

### 当前状态与下一动作

- v1.4.73 已在生产运行，GUI、配置、UserData 和原有本地已激活权益状态均保留。
- 下一动作：仅提交本轮源码、数据、测试和版本文档，推送 origin/main，创建 v1.4.73 标签和 GitHub Release，并回读远端提交、标签、说明和资产哈希。
## 2026-09-20 01:44 +08:00 — v1.4.73 远端发布回读与生产终验

### GitHub 发布回读

- GitHub Latest 为 `v1.4.73`，发布标题 `CV 农场助手 v1.4.73`，发布说明中文回读正常，未出现乱码替换字符。
- 发布代码提交为 `a2979f1acab03941f078885965cbe5afd9dc4289`；远端注解标签 `v1.4.73^{}` 精确解引用到该提交。
- 远端资产重新下载到 `E:\CodexBuilds\qq-farm\release-verify\v1.4.73-20260920-013857\CVFarmAssistant-v1.4.73-portable-full.zip`。
- 远端下载包与本地发布包均为 `278,270,846` bytes，SHA-256 均为 `78FDF96539260596A5C404BC0BAAAF971181579F1D4A5EB038A47365E0CE6E3A`。
- GitHub 资产元数据中的 digest 同样为 `sha256:78fdf96539260596a5c404bc0baaaf971181579f1d4a5eb038a47365e0ce6e3a`。

### 新鲜验证

- v503/v504 定向回归重新执行：`9 / 9 OK`。
- `python -m py_compile portable\hook.py`：OK。
- `git diff --check`：OK。
- 源/部署 Hook 均为 `2,774,308` bytes，SHA-256 `F82A9AF1A08F6EF6CEB418895D438304BD64E08226DBF4654B154A706DF8AC0F`。
- 源/部署作物目录均为 `53,077` bytes，SHA-256 `C0C936A3800F155C3946A6B6FE313EAE322231832BFC5ECA8AAA2A4153390387`。
- 源/部署模板均为 `26` 项、`61,817` bytes，逐文件差异数 `0`。
- 配置仍为 SHA-256 `4F2370E0A94A940C80DBFE93E5F41B3A2A15A2BBEC5751721BD24F0545B7B728`。

### 生产终验

- 当前生产 PID `20404`，窗口标题 `农场助手 - 视觉自动化`，`Responding=True`。
- 10 秒采样 `Responding=False=0/10`，CPU 增量 `5.312s`，工作集 `415,969,280` bytes。
- 最新启动段同时包含一次 `v503 v2.3.7 crop catalog data installed` 与一次 `v504 v2.3.7 template overlays installed`。
- 最新启动段 `Traceback=0`、`KeyError=0`、`Exception=0`、`WGC error=0`、`capture error=0`、`PrintWindow timeout=0`。
- 当日日志已 14 次识别 `138` 级，并 14 次选择 `鳄梨`；自家维护、好友巡检与回家收敛继续产生真实日志。
- 授权层继续沿用本项目既有本地权益桥；GUI、UserData、配置、隐藏小程序、自动出售、护主犬和每日流程未被替换。

### 回滚与结论

- 最终代码回滚目录：`E:\CV农场助手\backups\v504-startup-schema-fix-1.4.73-20260920-011242`。
- 初始数据迁移回滚目录：`E:\CV农场助手\backups\v504-v237-catalog-templates-1.4.73-20260920-010208`。
- v1.4.73 发布资产、远端标签、生产 Hook、作物目录和模板树均已完成一致性核验；本次交付收尾完成。

<!-- V506-STARTUP-CAPTURE-RECOVERY-RED-GREEN-20260920-START -->
## 2026-09-20 v506 startup/capture recovery RED -> GREEN checkpoint

- Objective: repair first-click/shortcut startup failures and stop the live white QQ title
  shell from entering `FarmBotCV.run_cycle`, exhausting WGC rebuilds, restarting the
  mini-program, and eventually stopping the Bot. The incident screenshot also records
  CLR exception `0xe0434352`; the v505 launcher change already classifies that code as a
  bounded supervised restart.
- Live evidence (application bridge log date `2026-09-21`): repeated
  `v474 native run_cycle dispatching original business cycle` occurred while WGC and
  PrintWindow both rejected blank/non-farm pixels; one HWND was charged through
  `count=1/3`, `2/3`, `3/3` and entered a 300-second cooldown.
- Root cause: native-v2.2.5 uses `_wrap_native_v225_daily_catchup_run_cycle`, while the
  existing page-readiness check was installed only by the legacy diagnostic wrapper.
  The readiness gate also accepted any nonuniform title shell because it used only the
  generic white/black pixel test.
- RED: `tests/test_v506_startup_capture_recovery_20260920.py` produced four expected
  failures: native cycle ignored a failed readiness gate; the title-only white shell was
  accepted; the same blank HWND consumed two rebuild charges; and the cached blank HWND
  beat a newly enumerated candidate.
- GREEN implementation in `portable/hook.py`: gate native `run_cycle` before all daily and
  business work; require `_qqfarm_visible_frame_has_farm_scene`; track recent blank HWNDs,
  deduplicate budget charges, clear the stale last handle, prefer a new candidate, and
  release the record after a real farm frame.
- GREEN evidence: v506 focused suite `5 / 5 OK`; startup/runtime suite `20 / 20 OK`;
  compile passed. Full regression, deployment backup/hash, restart, and live farm-frame
  observation remain pending in this phase.
- Current version marker: `1.4.75`. One next action: run the affected capture/start suites
  and complete regression verification before creating the deployment backup.
<!-- V506-STARTUP-CAPTURE-RECOVERY-RED-GREEN-20260920-END -->

<!-- V507-STARTUP-GRACE-DEPLOY-20260920-START -->
## 2026-09-20 v507 startup grace, deployment, and live verification

- Remaining root cause: the launcher still classified a normal Qt bootstrap as stale after
  only `45` seconds. The observed executable can remain windowless or temporarily
  non-responsive for several minutes, so a second shortcut launch could terminate the
  healthy loading process and make the assistant appear to disappear.
- RED: `LauncherHealthRegressionTests.test_slow_qt_bootstrap_keeps_existing_process_for_five_minutes`
  failed with `45 not greater than or equal to 300`.
- GREEN: `portable/launcher.ps1` now uses a `300`-second startup grace while retaining the
  existing stale-process replacement after the grace expires. The focused launcher module
  passed `10 / 10`; the current startup/capture set passed `101 / 101`; v506 passed `5 / 5`;
  Qt autostart passed `2 / 2`; `py_compile` and `git diff --check` passed.
- Full discovery: `1541` tests in `568.529s`, with `17` historical failures, `5` errors and
  `11` skips. The five errors are the existing missing
  `.analysis/run-v342-isolated-performance-elevated-20260804.ps1` contract; the failure set
  matches the prior baseline categories and does not include v505/v506/v507. Evidence:
  `.analysis/v507-full-unittest-20260920.txt`.
- Backup: `E:\CV农场助手\backups\v507-startup-grace-1.4.75-20260920-011843`.
  Source/deployed Hook: `2,791,241` bytes,
  SHA-256 `8DF9B769AEF5D1F547D5B0BF11D8ED247404E3DAFF699D83C9D3681877C9D13B`.
  Source/deployed launcher: `27,125` bytes,
  SHA-256 `E7E1E1D97C023B23A958BBC0A798B906370351E8B794351215E62BBCBE23DC48`.
  Configuration remained `9,695` bytes, SHA-256
  `4F2370E0A94A940C80DBFE93E5F41B3A2A15A2BBEC5751721BD24F0545B7B728`.
- Live runtime log date is `2026-09-21` because of the production clock bridge. PID `18560`
  reached `农场助手 - 视觉自动化`, stayed `Responding=True`, and a normal duplicate launch
  after the 135-second observation preserved the same sole PID. Watchdog proof:
  `existing_instance pid=18560 action=preserve-existing restartRequested=False`.
- The fresh Hook segment proves first-click autostart entered the runtime once, a missing QQ
  window emitted `v263 ... 跳过本轮业务动作`, the title/loading shell emitted
  `v263 ... 当前仅有标题或非农场画面`, and original v2.2.5 business dispatch began only
  after `v263 QQ农场页面已就绪`. There were zero WGC rebuild-budget charges, blank-frame
  failures, Tracebacks, or exceptions in that segment.
- The fresh application segment contains zero first-capture failures, game-capture failures,
  repeated-capture restarts, Bot stops, Tracebacks, exceptions, or ERROR lines. It completed
  daily share, daily task, home work, planting convergence, automatic selling, and friend
  handoff. Ten fresh process samples had `Responding=False=0/10`, CPU delta `0.719s`.
- Git commit `e02f726` (`fix: stabilize startup and capture recovery`) was pushed to
  `origin/main`; only the eight intended release source, launcher, documentation, and
  regression-test files were committed. Historical untracked fixtures/tests remain untouched.
- GitHub Release `v1.4.75` is now Latest and targets commit `e02f726`. The published
  `CVFarmAssistant-v1.4.75-portable-full.zip` is `278,277,157` bytes; local and GitHub
  asset metadata both report SHA-256
  `1970459AD300326CB36043B049A677FED29FDAE913E00E525BD7B893CE77F706`.
  The archive contains VERSION/README/CHANGELOG/EXE/Hook/launcher and zero UserData,
  logs, backups, diagnostics, analysis, Codex, or Git paths.
- One next action: keep v1.4.75 running and use the next naturally slow QQ bootstrap as an
  additional field observation; no further code change is queued for this incident.
<!-- V507-STARTUP-GRACE-DEPLOY-20260920-END -->


<!-- V508-PERSISTENT-NONFARM-RECOVERY-20260920-START -->
## 2026-09-20 v508 持续非农场画面恢复、部署与现场验证

### 目标与根因

- 现场症状是每约 12 秒只输出“开始新一轮巡检/本轮巡检执行完毕”，没有等级、种植、好友或其它业务动作。
- 诊断截图与运行时证据显示 QQ 农场 `HWND=67844` 仍存在，但捕获结果是桌面/遮挡/标题壳而非农场画面；页面就绪门正确阻止了业务动作，旧逻辑却因句柄仍存在而不重新绑定或关闭，形成无限空转。
- 旧的页面就绪日志还在防抖判断前写入时间戳，稳定 loading 状态长期不再输出诊断。

### RED → GREEN

- 新增 `tests/test_v508_persistent_nonfarm_recovery_20260920.py`，覆盖：同一 HWND 连续无画面计数、WGC 重绑、真实农场帧复原、页面就绪日志间隔输出，以及 `WM_CLOSE` 已排队但 HWND 迟迟不消失时释放 `relaunch_pending` 锁。
- 先运行新增测试得到预期 RED：关闭请求后 `relaunch_pending` 永久保持为真。
- `portable/hook.py` 的 GREEN 修复：连续 3 次同一 HWND 非农场/无画面后清理缓存、停止并重建 WGC、恢复隐藏小程序；后续进入有界关闭/重新拉起路径；关闭等待超过 20 秒自动解除锁并允许冷却后的下一次有界重试。
- 页面就绪时间戳改为在防抖判断通过后写入。

### 验证

- v508 聚焦测试：`4 / 4 OK`。
- 启动/捕获相关组合：`26 / 26 OK`。
- 历史捕获回归组合：`27 / 27 OK`。
- 完整发现：`1545 tests`，`17 failures / 5 errors / 11 skipped`；失败/错误集合与 v507 的 `1541 tests` 历史基线一致，新增 1 项仅为本轮回归测试，未增加历史失败类别。
- `python -m py_compile portable/hook.py`：OK；`git diff --check`：OK。

### 部署与现场证据

- 回滚备份：`E:\CV农场助手\backups\v508-persistent-nonfarm-1.4.75-20260921-034605`。
- 已部署版本：`1.4.76`；源/部署 Hook 均为 `2,802,167` bytes，SHA-256 `FC52BA9B05380F501B14A9754F74D6E0DA0E9ED47BB954896E2E0A4428E2BCAA`。
- 配置 SHA-256 保持 `4F2370E0A94A940C80DBFE93E5F41B3A2A15A2BBEC5751721BD24F0545B7B728`；未覆盖 `UserData`、日志、备份和用户配置。
- 隐藏重启后进程 PID `10472`，窗口为“农场助手 - 视觉自动化”，`Responding=True`；30 秒采样 `Responding=False=0/30`。
- 新鲜运行时日志出现：`v508 persistent non-farm surface recovery ... action=rebind`、`v508 persistent non-farm surface recovery ... action=close`、`v508 persistent non-farm surface recovered`、`v263 QQ农场页面已就绪` 和 `v474 native run_cycle original result=True`。
- 重新恢复后业务日志已经继续执行自家农场、好友农场和好友列表判断，不再只有空的开始/结束循环；计数状态显示自家动作、好友收获和捣乱流程均有新增记录。
- 每日免费福利仍有独立的截图/模板未命中记录，这是现有业务链的单独问题，不是本次持续非农场画面恢复回归。

### 当前状态与下一动作

- v1.4.76 已在本地生产运行，GUI、UserData、配置、隐藏小程序、种植、好友、自动出售、护主犬和每日流程保持原有实现。
- 下一动作：选择性提交本轮源码、回归测试、版本文档和交接记录到 `origin/main`，创建 v1.4.76 标签/发布；不加入历史未跟踪夹具、截图或运行数据。
<!-- V508-PERSISTENT-NONFARM-RECOVERY-20260920-END -->
<!-- V508-RELEASE-20260920-END -->

<!-- V516-DYNAMIC-CLICK-DEPLOY-20260921-START -->
## 2026-09-21 v1.4.77 动态点击路由、生产部署与现场验证

### 根因与实现

- 好友页反复输出“已发送动作”而画面不动的直接原因是 `PostMessage=True` 只证明消息进入窗口队列；QQ 窗口移动、缩放或重建后，原生路径仍可能复用旧绝对坐标，并且不同点击路径会分别选中 Chrome Render 与 D3D 子窗口。
- surface 排序还存在 `int(class_rank or 3)` 的零值错误，合法的 `class_rank=0` 被降级为 `3`，使 Chrome Render 可能输给 D3D。
- `portable/hook.py` 现已在每次动作前重新枚举当前 QQ 根窗口、Chrome Render、Chrome Widget 与 D3D；旧屏幕点按旧/新根窗口比例重映射，HWND 或矩形变化时清理旧 route cache，普通点击和好友点击共用 `_qqfarm_resolve_live_surface_click()`。
- 好友动作只在新鲜好友卡片身份变化、持久计数增长或明确成功反馈后提交；按钮消失、消息投递成功和普通动画变化不再单独授权进度。未确认动作恢复调用前游标并进入 14/30 秒有界冷却。

### 自动验证

- 新增 `tests/test_v516_click_confirmation_gate_20260921.py` 和 `tests/test_v517_dynamic_surface_resolver_20260921.py`。
- 动态 surface、参数形态、别名桥、确认门、好友点击几何、游标、终点回家及自家/好友切换组合重新执行：`363 / 363 OK`；证据为 `.analysis/v516-focused-final-20260921.txt`。
- 完整发现：`1568 tests`，`17 failures / 5 errors / 11 skipped`；与 v508 的 `1545 tests` 基线逐项比较，失败/错误集合仍为相同的 22 项历史种植/分享夹具、旧好友计数断言和缺失性能脚本，没有本轮新增失败；证据为 `.analysis/v516-full-unittest-20260921.txt`。
- `python -m py_compile portable\hook.py` 与 `git diff --check` 均通过。

### 部署与保留项

- 回滚备份：`E:\CV农场助手\backups\v516-dynamic-click-1.4.77-20260921-173334`。
- 源/部署 Hook 均为 `2,858,477` bytes，SHA-256 `6621B28DD8DD8E8FDB4CCB972ADCCA46F878C8244C634670301CA59FDABFABD2`；源/部署 `VERSION=1.4.77`。
- 配置 SHA-256 部署前后均为 `4F2370E0A94A940C80DBFE93E5F41B3A2A15A2BBEC5751721BD24F0545B7B728`；`UserData`、日志、备份、GUI、EXE、本地权益状态和 `v2.3.7-standalone` 均未被覆盖。
- 当前生产 PID `16644`，窗口标题“农场助手 - 视觉自动化”，`Responding=True`；12 次现场采样均响应。

### 现场证据

- 新启动段有 `24` 次 `v516 live surface click`、`3` 次 `v516 friend live surface click`、`0` 次旧 `v491 friend client click`；路由落到同一 Chrome Render，并出现窗口重建后的 `space=stale-screen-remapped`。
- 未确认好友动作共 3 次，均记录 `cursor preserved` 并进入确认冷却，没有伪造累计处理；随后应用日志实际推进到好友偷取、单个偷取、帮忙和回家。
- `17:35:49` 首个好友动作获得新鲜证据并提交为 `1/12`，链路继续到第 3 个好友；`17:37:58` 捕获重绑冷却结束后恢复自家务农，`17:40:04` 与 `17:40:35` 分别完成一键偷取、单个偷取和偷取后帮忙。
- 最新启动段 `Traceback=0`、截图失败 `0`、WGC error `0`、PrintWindow timeout `0`；文本中的 `error=ModuleNotFoundError("ctypes")` 仅是可选资源控制诊断字段，不是应用异常。
- 每日状态与两个统计 CSV 可读并一致；任务和分享均为 `2026-09-21` 已完成。免费福利当天达到原生重试上限，属于独立业务状态。

### 当前状态与下一动作

- v1.4.77 已部署并继续运行，好友页面动作已从旧坐标/D3D 伪投递切换为动态 Render 路由和新鲜证据提交。
- 下一动作：选择性提交本轮 Hook、两个回归测试、版本文档与本交接记录，推送 `origin/main` 并创建 `v1.4.77` GitHub Release；历史未跟踪截图、夹具、分析文件和 `.latest_*` 文件保持不动。
<!-- V516-DYNAMIC-CLICK-DEPLOY-20260921-END -->

<!-- V516-DYNAMIC-CLICK-CONFIRMATION-20260921-START -->
## 2026-09-21 v516 动态点击表面与好友动作确认

### 目标与根因

- 生产日志持续输出“底部好友条命中/已发送动作”，页面却没有变化；Hook 只证明 `PostMessage` 进入消息队列，没有证明 QQ 页面处理了点击。
- QQ 窗口已从旧矩形 `(944,234,1615,1425)` 重建为 `(629,116,1076,950)`，原生路径仍传入旧绝对坐标 `(1408,1212)`；同时原生与好友路径可能分别选中 D3D 和 Chrome Render 子窗口。
- `v2.3.7-standalone` 是包含 PyArmor 运行时、完整 Python/Qt/CV 依赖及 `QQFarmCVHelper.exe` 的保护后独立包，没有可直接覆盖现有 GUI 的明文业务模块；本轮只迁移并验证其动态窗口兼容思路。

### RED → GREEN

- 新增 `tests/test_v516_click_confirmation_gate_20260921.py` 与 `tests/test_v517_dynamic_surface_resolver_20260921.py`。
- RED 证明 `class_rank=0` 被 `or 3` 改写，Chrome Render 输给 D3D；也证明两个生产点击函数没有调用动态 resolver，好友包装器没有设置未确认冷却。
- GREEN 修复动态枚举根窗口/Chrome Render/D3D、旧坐标比例重映射、路由缓存失效；原生和好友点击统一发送到当前 Render surface。
- 好友动作改为新鲜好友卡片身份变化、持久计数增长或明确反馈后提交；未确认时恢复游标并进入 14/30 秒冷却。

### 当前验证

- 聚焦动态点击与好友状态组合：`50 / 50 OK`。
- `python -m py_compile portable\hook.py`：OK。
- `git diff --check`：OK。
- 当前版本标记：`1.4.77`。

### 下一动作

- 运行完整发现基线，创建生产回滚备份，仅部署 Hook/版本文档，隐藏重启后检查 `v516 live surface click`、`stale-screen-remapped`、确认冷却及页面真实前进证据。
<!-- V516-DYNAMIC-CLICK-CONFIRMATION-20260921-END -->

<!-- V521-FRIEND-LIST-CAPTURE-GATE-20260922-START -->
## 2026-09-22 v1.4.79 好友列表捕获门贯通

### 症状与根因

- v1.4.78 已能在同一 QQ 窗口的 PrintWindow 帧中识别多行好友列表，但该帧仍会在 get_frame_from_bot 和已安装的 screen_capture 包装器中被普通农场安全门拒绝。
- 现场随后回退到原生/桌面帧，日志出现 v458 native fallback returned desktop/non-farm pixels、v508 persistent non-farm surface recovery、重复好友动作确认失败和窗口重建；因此日志可能继续刷新，但页面实际不前进。
- 这是捕获证据在不同入口之间没有贯通，不是好友列表行检测本身失效。

### RED -> GREEN

- 新增 get_frame_from_bot 回归：窗口自有好友列表帧必须直接返回，不得调用 native fallback；先得到失败，再修复。
- 新增 test_qq_visible_capture_priority.py 回归：已安装捕获所有者包装器必须接受至少 3 行好友访问控件，不得把该帧交回原生路径；先得到失败，再修复。
- v1.4.79 在两个业务捕获门统一使用 _friend_list_visit_button_rows 的多行好友路由证据。至少 3 行时保留窗口自有帧；任务面板、遮挡帧和无好友行画面仍拒绝。

### 验证

- 新增与既有受影响组合：92 / 92 OK，覆盖 v422-v428、v483-v506、v512-v520、捕获优先级和动态点击确认。
- python -m py_compile portable\\hook.py：OK。
- git diff --check：OK。
- 历史全量发现仍有既有失败/错误：缺失的 v342 性能脚本、旧 v429 夹具以及历史好友计数断言；本轮未修改这些历史资产，也未将它们计入本修复通过数。

### 部署与现场

- 生产回滚备份：E:\\CV农场助手\\backups\\v521-friend-list-capture-gate-1.4.79-20260922-104903。
- 部署版本：E:\\CV农场助手\\VERSION=1.4.79；当前生产 PID 28372，Responding=True。
- 配置、UserData、日志、本地权益状态、GUI、EXE 和 v2.3.7-standalone 未覆盖。
- 重启后已出现 v520 window-owned PrintWindow friend-list route accepted rows=5，页面加载/非农场帧仍记录零业务动作门；未出现 Python traceback。

### 当前状态与下一动作

- v1.4.79 已部署，好友列表帧现在能从窗口捕获入口贯通到运行时业务入口，不再因第二道安全门回退错误画面。
- 下一动作：完成部署后 120 秒稳定采样，随后选择性提交源码、回归测试、版本文档和本交接记录，构建便携包并推送 origin/main。
<!-- V521-FRIEND-LIST-CAPTURE-GATE-20260922-END -->

<!-- V522-EMPTY-FOCUS-STOP-20260922-START -->
## 2026-09-22 v1.4.80 空地证明、微信抢焦点与停止闩锁

### 根因与修复

- 空地原生日志属于前置遥测，不能替代当前帧的土地证明；买种完成日志现在只有在 45 秒内的 `confirmed` 空地列表存在时才会重新锁定自家流程。
- 播种流程遇到新鲜但非严格确认的 0 块时，保持自家复核并阻止策略/买种；严格满板证据要求当前帧标记为 `confirmed full board`。
- 微信原生焦点函数返回 `None` 时，兼容原生写入的应用句柄字段，同时保留进程名、PID、窗口探测和关联句柄验证。
- 停止包装器设置 `_qqfarm_explicit_stop_latched` 与全局自动启动闩锁；Qt tick 在闩锁期间不点击“开始运行”，手动 Start 入口清除闩锁。

### RED -> GREEN

- 新增 `tests/test_v522_empty_focus_stop_regressions_20260922.py`，覆盖未确认空地买种拦截、严格满板零地块门、微信 `None` 返回应用证明、停止后自动启动拦截及手动启动解锁。
- 定点回归：空地板面/满板/幼苗 `30 / 30 OK`；背包与种植 `41 / 41 OK`；启动、停止、微信焦点 `24 / 24 OK`；动态点击与好友捕获 `36 / 36 OK`。
- `python -m py_compile portable\hook.py`：通过。
- `git diff --check`：通过。

### 部署

- 生产部署前创建带时间戳的 `E:\CV农场助手\backups\v522-empty-focus-stop-1.4.80-*` 备份，仅替换 Hook、VERSION 和文档，不覆盖 `UserData`、`logs`、`backups` 或本地权益状态。

### 下一动作

- 运行生产重启后的 120 秒稳定采样，重点观察 `v522 zero empty-land scan lacks strict board proof`、`wechat focus apply ...` 与 `qt autostart blocked after explicit stop` 日志是否符合实际页面状态。
<!-- V522-EMPTY-FOCUS-STOP-20260922-END -->
## 2026-09-20 v1.4.76 标签、GitHub Release 与便携包完成

### 远端发布

- 注解标签：`v1.4.76`，解引用提交：`79f0888ad84b07f795e379143b21c51f8570c02b`。
- GitHub Release：`https://github.com/combating123/qq-farm-cv-helper-portable/releases/tag/v1.4.76`。
- Release 标题：`CV 农场助手 v1.4.76`；已发布、非草稿、非预发布。
- 便携资产：`CVFarmAssistant-v1.4.76-portable-full.zip`，`284,405,661` bytes。
- 远端资产 digest：`sha256:5e50ed875b9c2f87ab4a6e1965ce5e7f0dd96a911396bd87d4258b63f0018e8f`。
- 校验文件：`CVFarmAssistant-v1.4.76-portable-full.zip.sha256.txt` 已随 Release 上传。

### 便携包核验

- 本地包：`E:\CodexProjects\Generated\qq-farm-v1.4.76-release\CVFarmAssistant-v1.4.76-portable-full.zip`。
- 本地 SHA-256：`5E50ED875B9C2F87AB4A6E1965CE5E7F0DD96A911396BD87D4258B63F0018E8F`，与 GitHub 资产 digest 一致。
- 包内 `VERSION=1.4.76`；包内 Hook SHA-256：`FC52BA9B05380F501B14A9754F74D6E0DA0E9ED47BB954896E2E0A4428E2BCAA`。
- ZIP `597` 个条目可正常测试读取；未包含 `UserData`、`logs`、`backups`、`.analysis`、`.codex`、`.git` 或 `tests`。
- 便携包由上一版干净发布基线更新本轮 Hook、版本、README 与 CHANGELOG；没有把生产用户数据打入资产。

### 发布前新鲜验证

- v508 + v506 + v505 + 捕获恢复组合：`32 / 32 OK`。
- `python -m py_compile portable\\hook.py`：OK。
- `git diff --check`：OK。
- 源/部署 Hook：`2,802,167` bytes，SHA-256 `FC52BA9B05380F501B14A9754F74D6E0DA0E9ED47BB954896E2E0A4428E2BCAA`，一致。
- 历史完整发现基线仍为 `1545 tests`、`17 failures / 5 errors / 11 skipped`；本轮没有修改历史未跟踪夹具或测试。

### 当前状态与下一动作

- v1.4.76 已完成代码、标签、Release 和便携包交付；本地生产目录继续保留 `UserData`、配置、日志和回滚备份。
- 下一步只需继续观察自然运行中的真实非农场画面恢复；若出现新的业务误动作，再以新日志/截图建立独立回归，不回退本次捕获恢复改动。
<!-- V508-RELEASE-20260920-END -->


## 2026-09-25 02:30:00 +0800 — v1.4.99 RED/GREEN：好友列表帧缓存与 DPI 物理点击重映射

### 症状与根因

- 现场日志同时出现 `v520 window-owned PrintWindow friend-list route accepted rows=4`、随后 `v489 native-v225 friend-list preflight rows=0`，说明捕获入口已经看到好友列表，但 native owner 下一次读取到空帧。
- 旧点击日志把逻辑坐标 `(1544,384)` 沿用到物理窗口，最终发送为 `client=(600,210)`；当前物理根窗口为 `(629,116,1076,950)`，该结果不在正确的物理点击几何上。

### RED -> GREEN

- 新增 `tests/test_v539_friend_capture_cache_and_dpi_click_20260924.py`，先验证两项失败：PrintWindow 好友列表帧没有写入 native owner 可见缓存；逻辑/物理窗口并存时路由仍保留旧根矩形。
- v1.4.99 在 PrintWindow 多行好友列表分支调用 `_qqfarm_remember_friend_list_frame()`，并新增 `_qqfarm_rebase_surface_candidates_to_physical()`，将当前根/Render 候选几何映射到带有本次 PrintWindow 物理证据的窗口矩形。
- 动态点击保持边界校验，仅在新鲜 PrintWindow provenance 且旧点属于已知路线/物理面时重映射；无当前物理证据不进行泛化缩放。

### 验证

- v539 回归：`3 / 3 OK`。
- 受影响好友/捕获/动态点击组合：`49 / 49 OK`。
- `python -m py_compile portable\hook.py`：OK。
- `git diff --check`：OK。
- 全量发现：`1598 tests`，`64 failures / 8 errors / 11 skipped`；失败属于已有 v489/v490 等历史契约和旧夹具，本次修复未将其冒充为通过。

### 生产动作

- 源码版本提升为 `1.4.99`。部署前创建 `E:\CV农场助手\backups\v539-friend-cache-dpi-1.4.99-*` 回滚副本。
- 仅部署 `hook.py`、`VERSION`、`README.md`、`CHANGELOG.md`；保留 GUI、UserData、配置、logs、backups、本地权益状态和 v2.3.7 分析目录。
- 重启后检查 `v539 remembered window-owned friend-list frame`、`coordinate_space=physical-printwindow-remapped`，并确认不再出现 `rows=0` 紧跟旧 `client=(600,210)` 的组合。

### 当前状态与下一动作

- 代码与测试已完成，生产部署和 GitHub 提交发布在本阶段继续执行。
- 下一动作：创建备份，部署并隐藏重启；读取新日志后提交 v1.4.99 到 `origin/main`。

## 2026-09-25 11:05 +0800 - v1.5.0 RED/GREEN：未确认好友页面不得伪装成无任务

### 症状与根因

- 现场日志出现好友列表/转场未确认、`rows=0`、底部入口确认失败，但紧接着输出“好友农场已无可执行的任务，下一轮巡查将回家查看”，画面实际没有变化。
- 根因是 native 好友处理函数的 `False` 返回被外层日志直接解释为“已确认好友农场无动作”；该返回也可能来自空帧、好友列表帧或转场等待，并不具备无任务证明。

### RED -> GREEN

- 新增 `tests/test_v542_friend_uncertain_no_action_20260925.py`，覆盖列表/转场未确认、确认好友农场无动作和日志改写；首次运行因缺少 v542 helper 失败。
- 新增 `_qqfarm_friend_no_action_is_unconfirmed()` 与 `_rewrite_unconfirmed_friend_no_action_log()`；未确认状态保留好友链路、游标和待确认状态，输出“页面未完成确认，等待新画面后重试”，不触发好友回家终态。
- info/warning 两条运行日志路径均接入同一改写门。

### 验证与部署

- v542、v537、v538、v539、v520、v533、v536 受影响组合：`22 / 22 OK`。
- `python -m py_compile portable\hook.py`：通过。
- `git diff --check`：通过。
- 部署版本：`E:\CV农场助手\VERSION=1.5.0`；生产 PID `32232`，`Responding=True`。
- 回滚备份：`E:\CV农场助手\backups\v542-uncertain-friend-no-action-1.5.0-final-20260925-110249`。
- 源/部署 Hook 与 VERSION 哈希一致；配置、UserData、logs、GUI、既有备份和本地权益状态未覆盖。
- v542 重启后新日志已出现启动标记，未再出现该启动段内的旧“好友农场已无可执行任务”伪终态。

### 当前状态与下一动作

- v1.5.0 已部署并运行；只有确认好友农场画面后才允许结束为无任务，列表/空白/转场帧会保留好友链路并等待新画面。
- 下一动作：提交 v1.5.0 并通过本机 `127.0.0.1:10808` 代理推送 `origin/main`。

## 2026-09-25 23:10 +0800 - v1.5.7 RED/GREEN：好友列表缓存保活与左上角窗口验证

### 症状与根因

- 生产日志仍出现 `rows=0`、随后 `v520/v539 rows=5` 的捕获竞态；空白/非农场帧还可能进入 `v499 visible self surface released`，清掉刚验证的好友列表缓存并让 native owner 下一轮重新从第 0 行开始。
- 窗口移动到左上角不是根因：现场已经多次确认 QQ 农场窗口为 `(0,0,671,1251)`，问题在 native owner 与窗口自有 PrintWindow 帧的时序。

### RED -> GREEN

- 新增 `tests/test_v544_native_friend_cached_list_consumption_20260925.py`。
- RED 复现：缓存超过原 6 秒窗口时，native owner 不消费最近有效的 5 行好友列表；空白帧会返回 `True` 并清掉好友路由。
- GREEN：将已验证列表帧缓存窗口调整为 15 秒，覆盖一个 12 秒巡检间隔；在至少 3 行缓存仍新鲜且好友链路未结束时，`_qqfarm_reconcile_visible_self_surface()` 保留 `friend-list` 场景、待处理游标和缓存，不触发 `v499` 回家释放。
- 定点组合验证：`29 / 29 OK`，包含 v544、v539、v543、v533、v516、v517；`py_compile` 与 `git diff --check` 通过。

### 生产部署

- 生产版本：`1.5.7`；备份：`E:\CV农场助手\backups\v544-release-1.5.7-20260925-230537`。
- 源/部署 Hook：`E6D366F8B4DB0624FB3E7E47CBA19A1DF258574C4FA543B55E17B5EA91B3602D`，`3002498` bytes，一致。
- 重启后 PID `24312`，`Responding=True`；新日志确认 `v543 miniapp anchored top-left ... rect=(0, 0, 671, 1251)`。
- 新现场连续出现 `v539 remembered window-owned friend-list frame ... rows=5`、`v520 ... rows=5`，未观察到该段紧跟 `v499 ... returned home` 的缓存清理组合。
- GUI、UserData、配置、本地状态、日志和历史备份均保留；配置只记录哈希，未覆盖。

### 未闭环观察

- 当前窗口仍有 QQ 小程序启动/捕获竞态：启动初期可能出现一次 `rows=0` 和非农场等待；代码会等待有效农场/列表帧，不应将其当成好友无任务证明。
- 本次修复解决的是好友列表缓存断链和左上角固定后的坐标/场景保持；真实好友存在偷取或帮忙机会时，仍需以新鲜业务日志确认实际动作完成。

### 下一动作

- 选择性提交 `portable/hook.py`、`VERSION`、`README.md`、`CHANGELOG.md`、v544 回归测试和本交接记录，推送 `origin/main` 并创建 `v1.5.7` Release。

## 2026-09-25 23:46 +0800 - v1.5.8 RED/GREEN：好友列表有效帧被旧 home 提示压制

### 症状与根因

- 用户截图中的好友列表已经清楚显示 5 张卡片和【拜访】按钮，但业务日志只重复输出巡检开始/结束，没有首行访问动作。
- 同期 Hook 日志反复出现 `v539/v520 rows=5`，而 native owner 仍出现 `rows=0`；缓存解析器看到旧 `home` 场景提示后拒绝了好友列表缓存，导致有效列表没有进入有序好友处理器。

### RED -> GREEN

- v544 回归新增“全局列表缓存、上下文缓存缺失”和“旧 home 提示但好友链路 active”两种现场状态；后者先失败，证明旧 home 提示会压掉有效好友列表。
- v1.5.8 放宽缓存消费门：只要缓存新鲜且好友链路仍为 active/pending，优先使用至少 3 行已验证好友卡片；只有缓存过期且没有好友链路证据时才允许回到自家恢复。
- 受影响组合：`34 / 34 OK`；`py_compile`、`git diff --check` 通过。

### 生产验证

- 生产版本：`1.5.8`；备份：`E:\CV农场助手\backups\v545-friend-list-home-hint-1.5.8-20260925-234522`。
- 源/部署 Hook：`25F678A242BCC1499305134C4DB87EEE5CBDB80E996BD7F6C54AAF9F5FC4F388`，一致；PID `32168`，`Responding=True`。
- 重启后现场已实际推进：`23:43:21` 进入好友链路，`23:43:22` 检测到【一键偷取】并执行，证明列表不再只停留在识别层。
- GUI、UserData、配置、每日状态和历史备份未覆盖。

### 下一动作

- 提交并推送 v1.5.8，创建对应 GitHub Release；继续观察多次 HWND 重建后的好友首行派发和回家转场。

## 2026-09-23 20:39:50 +0800 — v1.4.98 RED/GREEN：卡片式好友列表坐标与 RGB/BGR 捕获兼容

- 目标：修复 2026-09-23 现场“好友列表第 0 行点击成功但实际点到搜索框，随后持续停留自家/好友列表”的主线回归。
- 关键现场证据：`E:\CV农场助手\.analysis\live-friend-loop-20260918\printwindow.png` 为 428×800 卡片式好友列表；旧运行日志 `v487 friend-list layout` 记录 `(364,287),(364,382)...`，其中首点落在搜索框而非第一张好友卡片。
- RED：新增 `tests/test_v538_friend_list_card_geometry_20260923.py` 和现场 fixture `tests/fixtures/live-friend-list-card-loop-20260918.png`；BGR 用例通过，RGB 捕获用例先因返回 0 行失败，证明通道顺序兼容缺口。
- GREEN：`portable/hook.py` 的 `_friend_list_visit_button_rows()` 现在先使用卡片行检测，再在需要时尝试 RGB→BGR 通道翻转，最后才使用旧绿色组件兜底；同一现场样本首三行中心为 `(312,434),(312,576),(312,720)`，不再落入搜索区域。
- 同步修复：直接 `process_friend_farm` 入口在解析器尚未绑定的精简运行时使用严格本地三行探测，不再因 `NameError` 回落到无动作 native 路径。
- 聚焦证据：`v487/v488/v489(核心列表派发)/v499/v520/v533/v536/v537/v538` 相关测试已运行；v538 2/2 OK，v488 精简入口回归由失败转为通过。v489 中若干旧的弱友好表面/终态测试仍与现行 v530/v533 强证明契约不一致，未把它们冒充为本次修复证据。
- 版本：源码标记提升为 1.4.98，加入 v538 启动标记、CHANGELOG、README 和新 fixture/test；尚未部署。
- 下一步：创建部署备份，隐藏重启并用新日志验证 `v538`、`source=friend-card-band`、首行坐标不低于第一张卡片顶部；确认好友农场页面确认和游标推进后再提交/推送。

## 2026-09-26 00:52 +0800 - v1.5.10 可见好友列表绕过稳定满板快路径

- 症状：巡检只输出开始/结束；好友列表帧可能被旧的稳定满板缓存快速跳过，没有进入好友派发。
- RED：`test_run_cycle_fast_gate_rejects_visible_friend_list_frame` 在旧实现下返回 `True`，复现 5 行好友列表被静默跳过。
- GREEN：`_qqfarm_stable_full_board_run_cycle_fast_skip()` 先检查当前帧；不少于 3 行好友列表时记录 `v547-visible-friend-list-bypassed-full-skip` 并释放 native 好友派发。
- 定点验证：`43 / 43 OK`；`python -m py_compile portable\hook.py` 与 `git diff --check` 通过。
- 全量发现：`1614 tests`，`50 failures / 13 errors / 11 skipped`；失败集中于历史 AST 精简加载、缺失旧 `.analysis` 脚本和旧行为契约，本轮相关组合仍为 43/43。
- 部署版本：`1.5.10`；备份：`E:\CV农场助手\backups\v547-visible-friend-list-fast-skip-1.5.10-20260926-004648`。
- 源/生产 Hook SHA-256：`0C84C2C5A6098FDADA6A4634593DD752E24631D6D7A291B8966EB31CB5167FA5`；生产 PID `34592`，`Responding=True`。
- 配置 SHA-256 仍为 `4F2370E0A94A940C80DBFE93E5F41B3A2A15A2BBEC5751721BD24F0545B7B728`；GUI、UserData、配置、日志和历史备份未覆盖。
- 新启动段确认 Hook 加载和左上角锚定 `rect=(0, 0, 642, 1200)`；观察期内未出现真实多行好友列表，v547 的自然现场命中继续等待对应页面状态。
- 下一动作：选择性提交并推送 `main`，创建 `v1.5.10` GitHub Release。


## 2026-09-26 04:38:00 +0800 — v1.5.12 RED/GREEN：未确认空地隔离与静止画面一键务农去重

- 现场证据：04:19 仍出现 `检测到空地共1块` 后逐块土地 OCR 未命中；此前 12 秒一轮重复输出一键务农并把 `self_actions_daily_count` 推到 469，说明 native 返回/日志不等于画面变化。
- 根因：QQ 窗口重建后 WGC 处于重建冷却，业务继续消费未确认候选；一键务农调用缺少同一静止画面的确认闸。
- RED/GREEN：新增 `tests/test_v549_runtime_action_and_empty_gate_20260926.py`，7/7 OK；MMUI/WGC 回归 40/40 OK；空地套件 32/32、背包套件 60/60；`py_compile` 与 `git diff --check` OK。
- 实现：`portable/hook.py` 增加 confirmed 棋盘与45秒证明门；未确认候选清空为待复核，不触发种植/买种/仓库；同一 frame signature 的一键务农进入8-60秒确认冷却，存在真实待种任务时放行。
- 部署：版本 `1.5.12`；备份 `E:\CV农场助手\backups\v549-empty-gate-self-action-1.5.12-20260926-043703`；源/生产 Hook SHA-256 `1D80E50C99235502B1F62FFD5AAC20E88CA0F0B591FF4A5B1E09304B3DB4EF71`；配置 SHA-256 保持 `4F2370E0A94A940C80DBFE93E5F41B3A2A15A2BBEC5751721BD24F0545B7B728`；PID `33708`，Responding=True。
- 新启动段未再出现旧的 MMUI WGC 查找告警；尚待下一次真实一键务农机会确认 v549 日志。当前下一步：继续观察 fresh-frame confirmation 与好友页面推进证据。

## 2026-09-26 12:22:00 +0800 — v1.5.13 RED/GREEN：土壤正证据门与慢路径隔离

### 症状与根因

- 生产日志在 2026-09-26 03:15 前后仍出现“检测到空地共 1 块”后逐块土地名称 OCR 未命中；单块等待约 20–30 秒，造成用户看到画面长时间不动。
- 现场还出现 WGC 旧选择器找不到 `MMUIRenderSubWindow` 的告警。v1.5.12 已加入 QQ/微信 Render 面枚举与重建逻辑，但生产 Hook 尚未加载本轮 v550 修改。
- 农田网格/棋盘命中只说明候选位于农场，不足以证明该位置是裸土。没有独立土壤正证据的候选若继续下游，会再次触发慢 OCR、背包预检或买种。

### RED → GREEN

- 新增 `tests/test_v550_soil_proof_gate_20260926.py` 的高层回归：确认棋盘但无土壤正证据的候选必须被保留为待复核，不能进入 flat-proof/慢 OCR 路径；同时保留视觉土壤和收获后正证据候选。
- v1.5.13 在 `_wrap_detect_empty_lands_state()` 中接入 `_qqfarm_filter_empty_land_candidates_by_soil_proof()`：无 `_qqfarm_visual_soil_proof`、`_qqfarm_live_flat_empty_proof` 或 `_qqfarm_post_harvest_confirmed` 的候选从可操作结果中移除；全部被移除时棋盘状态改为 `unknown`，清空当前可操作空地缓存并等待新鲜画面。

### 验证

- v550 高层土壤正证据回归：`3 / 3 OK`。
- v549 运行时动作/空地门：`3 / 3 OK`。
- v548 QQ MMUI/WGC 与仓库门：`4 / 4 OK`。
- v543 窗口几何/左上角锚定：`7 / 7 OK`。
- 空地板面、满板、播种流程组合：`8 / 8 OK`（另含同套件现有测试）。
- `python -m py_compile portable\\hook.py`：OK；`git diff --check`：OK。
- 生产快照（2026-09-26 12:05）显示进程当时未运行，且源 Hook 与部署 Hook 尚不一致；本轮部署前必须创建新备份并只替换 `hook.py`、`VERSION`。

### 交付边界与部署

- 保留 GUI、UserData、配置、日志、窗口位置和本地业务状态；不覆盖 `E:\\CV农场助手\\UserData`、`logs` 或 `backups`。
- `QQFarmCVHelper_v2.3.7_x64_setup.exe` 继续作为离线静态行为对比样本；本交付不修改其授权/卡密校验，也不生成授权绕过补丁。
- 下一动作：创建 `E:\\CV农场助手\\backups\\v550-soil-proof-1.5.13-*`，复制源 Hook 与 VERSION，隐藏重启，核对新日志中的 `v550 empty-land soil-proof gate`、WGC 重建与无重复一键务农，然后再提交并推送 GitHub。

## 2026-09-26 12:29:30 +0800 — v1.5.13 已部署：首段运行观察

- 生产备份：`E:\\CV农场助手\\backups\\v550-soil-proof-1.5.13-20260926-122537`。
- 仅替换：`E:\\CV农场助手\\hook.py`、`E:\\CV农场助手\\VERSION`；`UserData`、配置、日志、GUI 和历史备份未覆盖。
- 源/部署 Hook SHA-256：`234362D7B00F797596FFEEA33385BDA7B4AFE2417EA493FEA45DC1381299ACBF`，`3020146` bytes，一致。
- 源/部署 VERSION SHA-256：`42C4A6120F79B4A9745000FE22D0D4C91DC462231C7F98421E26F26992CD1D42`，版本文本 `1.5.13`，一致。
- 配置 SHA-256：`4F2370E0A94A940C80DBFE93E5F41B3A2A15A2BBEC5751721BD24F0545B7B728`，部署前后保持。
- 隐藏重启后生产 PID `29720`，`Responding=True`。启动段记录：`12:26:50` OCR 预热超时后继续启动；`12:27:03` 进入自家检查；`12:27:22` 等级识别完成；`12:27:37` 好友页面未完成确认并保留好友链路。
- 当前观察段尚未遇到新的“确认棋盘但无土壤正证据”样本，因此没有把 `v550 empty-land soil-proof gate` 的自然现场命中冒充为已验证；需要在真实空地/满板场景出现时继续取证。
- Git 交付仍只包含源码兼容修复与测试；2.3.7 继续作为离线对比样本，不制作或发布其授权绕过补丁。


## 2026-09-26 13:24:00 +0800 — v1.5.14 授权校验交付门禁与便携包

### 目标
将源码级授权校验与发布门禁纳入 v1.5.14 交付，同时保持当前 GUI、UserData、配置、日志和运行时状态不变。

### RED → GREEN
- 新增 `tests/test_authorization_delivery_20260926.py`；首次运行因缺少授权策略模块而按预期失败。
- 新增 `portable/authorization_policy.py`，覆盖有效、过期、产品不匹配、签名缺失/失败、设备绑定和只读文件审计。
- 新增 `scripts/verify_authorization_delivery.py`，要求策略/说明随包交付，并阻止 v2.3.7 安装包与 `v2.3.7-standalone` 比较树进入发布树。
- `scripts/build_release.ps1` 已接入源码树与最终 stage 两道授权门禁，并排除 `v2.3.7-standalone`。

### 验证与交付
- 授权回归：5 / 5 OK。
- 授权预检：`OK: authorization delivery preflight passed`。
- PowerShell 语法解析：OK；`git diff --check`：OK。
- 便携包：`E:\CodexProjects\Generated\qq-farm-release\CV农场助手-v1.5.14-便携完整版.zip`。
- SHA-256：`CC63FD7A653B954E55B6947E1091B013E619A64F9F493A3D333B05C21714FBE2`。
- 包内确认：授权策略/门禁/说明均存在；v2.3.7 安装包与独立比较树均为 0 项。

### 边界
2.3.7 继续只作离线行为对照；本交付不改写其二进制授权逻辑、不生成卡密或补丁。现有生产 v1.5.13 运行实例未因本次文档/门禁改动重启或覆盖 UserData。下一步：提交指定源码文件并推送 v1.5.14 tag/release，之后再单独观察生产空地/好友链路。

## 2026-09-26 18:01 +0800 - v1.5.15 RED/GREEN：左上角锚定后的旧坐标点击恢复

### 症状与根因

- 现场日志在好友入口点击后持续出现 `v513 ... live-surface-resolution-failed input=(870,1166)`，窗口实际已经固定到左上角，画面没有推进。
- `_qqfarm_anchor_miniapp_top_left()` 对 `GetWindowRect` 的结果重复执行 DPI 放大，移动前路线从实际 `642x1200` 被错误放大为约 `963x1800`，旧绝对坐标因此被判定为不属于原路线。

### RED -> GREEN

- 新增 `tests/test_v551_anchored_native_click_regression_20260926.py`，覆盖不重复 DPI 放大、旧坐标 `(870,1166)` 映射到当前 `428x800` 表面、当前路线失配后回退保留路线以及渲染子窗口目标。
- 修复 `portable/hook.py`：保存原始移动前矩形；当前路线解析失败时使用保留路线重映射；成功恢复记录 `v551 recovered anchored native click from preserved pre-move route`。
- 聚焦回归：`48 / 48 OK`；`py_compile`、`git diff --check` 均通过。

### 生产部署与现场证据

- 生产备份：`E:\CV农场助手\backups\v551-anchored-click-1.5.15-20260926-175746`。
- 仅替换 `E:\CV农场助手\hook.py` 与 `E:\CV农场助手\VERSION`；GUI、`UserData`、配置、日志和历史备份未覆盖。
- 源/部署 Hook SHA-256：`31AF6A0F3935DAC2D834825C4F8ADD1DED6A72D5087BD57BBE9C79A43B9D5B67`，`3021628` bytes，一致；版本 `1.5.15`。
- 配置 SHA-256 保持：`4F2370E0A94A940C80DBFE93E5F41B3A2A15A2BBEC5751721BD24F0545B7B728`。
- 隐藏重启后 PID `12808`，`Responding=True`；新日志段中 `v513` 计数为 `0`，`v516 ... delivered=True` 出现 `6` 次，好友列表捕获到 `4` 行；未出现 Traceback、WGC 致命错误或捕获失败。窗口重建后再次记录 `v543 miniapp anchored top-left`。

### 边界与后续观察

- `QQFarmCVHelper_v2.3.7_x64_setup.exe` 仍仅作为离线行为对照样本；本次没有改写第三方二进制授权逻辑，也没有生成卡密或授权绕过补丁。
- `v551` 恢复路径尚未在自然现场再次命中，因为新进程已优先走当前有效路由；这是正常结果。继续观察好友入口实际画面推进和真实空地/活动四格播种证据。
