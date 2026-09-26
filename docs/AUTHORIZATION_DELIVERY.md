# 授权校验交付说明

日期：2026-09-26（Asia/Shanghai）
当前行为版本：1.5.14

Delivery scope: **source-owned validation**; **offline comparison only**.

## 本次纳入交付的内容

1. `portable/authorization_policy.py`
   - 对应用自己的授权文档执行只读校验；
   - 校验产品标识、状态、有效期、设备绑定和功能标志；
   - 支持由调用方注入签名验证器；
   - 不生成密钥、不改写授权文件、不修改二进制。
2. `scripts/verify_authorization_delivery.py`
   - 发布前检查授权策略文件和本说明是否进入交付树；
   - 防止把 `QQFarmCVHelper_v2.3.7_x64_setup.exe` 或绿色版样本复制进发布树；
   - 全程离线、只读。
3. 本说明与测试 `tests/test_authorization_delivery_20260926.py`
   - 固化有效、过期、产品不匹配、签名缺失/失败、文件只读审计和发布树门禁。

## v2.3.7 样本边界

`E:\浏览器下载\QQFarmCVHelper_v2.3.7_x64_setup.exe` 仍作为离线行为对照样本。已记录的安装包 SHA-256 为：

```text
35F56282A447A90C8F8D7DF2D2010C9A888D6E850AA20D7C57E966BBE282D889
```

样本的授权入口、刷新协调、过期/可信时间、完整性和资源签名边界保存在本地分析报告中；样本本身、卡密生成材料和二进制改写产物不进入当前发布树。

## 与现有 GUI 和运行数据的关系

- 保留现有 GUI、窗口左上角锚定、QQ/微信捕获切换、种植、好友巡检和每日流程；
- 不覆盖 `UserData`、配置、日志、计数、历史备份或本地运行状态；
- 授权策略模块是源码级校验与交付门禁，不替换当前业务流程，不改变界面尺寸和布局。

## 发布前检查

在仓库根目录执行：

```powershell
python scripts/verify_authorization_delivery.py --root .
python -m unittest tests.test_authorization_delivery_20260926 -v
```

通过条件：策略文件可解析、说明文件标记齐全、发布树不含 2.3.7 安装包样本，且授权文档读取不会写回文件。
