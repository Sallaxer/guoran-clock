const chinese = {
 home:'背光与控制',time:'时间与闹钟',settings:'设置',guide:'使用指南',journal:'日志',
 device:'电子时钟',model:'四只 IN-12 辉光管 · 木质外壳',subtitle:'蓝牙控制',connect:'连接时钟',connected:'时钟已连接',read:'读取设置',
 color:'背光颜色',colorHelp:'辉光管周围的 LED 背光。选择颜色后点击应用。',customColor:'自定义颜色',hue:'色相',applyColor:'应用颜色',colorMode:'背光模式',previous:'上一模式',next:'下一模式',
 remote:'遥控器',remoteHelp:'控制时钟内置菜单的按键。',power:'电源',back:'返回',plus:'增加',minus:'减少',setup:'设置',confirm:'确认',remoteNote:'SET：选择左侧菜单项 → OK：选择右侧参数 → OK：确认。+ / − 修改所选数值。',
 channels:'背光通道',channel:'通道 {n}',channelsNote:'时钟有四只辉光管；应用控制器最多支持六个通道。通道对应关系取决于固件。',
 pcTime:'电脑时间',sync:'设置时钟时间',syncHelp:'发送日期、时间和星期。',alarms:'闹钟',alarm1:'闹钟 1',alarm2:'闹钟 2',alarmsHelp:'设置时间并启用所需闹钟。',set:'设置',
 schedule:'定时开关',scheduleHelp:'自动开启和关闭时钟。',onTime:'开机时间',offTime:'关机时间',scheduleNote:'修改的时间保存在应用中。启用定时开关时，先发送两个时间，再启用定时功能。',scheduleApply:'应用定时设置',scheduleSaved:'所选时段：{on} — {off}',scheduleEmpty:'请设置两个时间。',scheduleSent:'已发送：{on} — {off} · 尚未确认',scheduleRead:'时钟上次回复：{on} — {off}',
 autoSync:'跟随电脑时间',autoSyncHelp:'应用运行且时钟保持连接时，每秒更新时间。',autoSyncNote:'仅对本次连接有效。',
 featureA:'自动亮度',descA:'根据环境光调整亮度。手动模式及 10 级亮度调节位于时钟菜单第 06 项。',
 featureC:'环境光感应',descC:'此开关在 IN12_M4 上的具体作用尚未确定。根据环境光调整亮度请使用“自动亮度”；定期轮换显示所有数字请使用时钟菜单第 16 项“辉光管保护”。',
 featureF:'感应开关',descF:'通过传感器控制的开关。厂家未说明 IN12_M4 的传感器类型和触发条件；不同版本的时钟可能有所不同。',
 featureB:'12 小时制',descB:'关闭后使用 24 小时制。对应时钟菜单第 09 项。',featureD:'整点报时',descD:'每小时整点语音报时。菜单第 12 项的夜间模式可在低亮度时停止报时。',featureE:'英文语音',descE:'时钟语音：开启为英文，关闭为中文。应用界面语言单独设置。',
 protection:'辉光管保护',protectionShort:'定期轮换显示所有数字，是时钟菜单第 16 项的独立功能。建议间隔：5 分钟。',how:'设置方法',
 unread:'尚未读取',unknown:'未知',on:'已开启',off:'已关闭',fromClock:'时钟回复',pending:'已发送，尚未确认',rawUnknown:'回复“{raw}”尚未解析',lastReply:'上次回复',selected:'已选择：{color}',colorValue:'颜色：{color}',readAt:'读取时间：{time}',stale:'连接已关闭',invalidTime:'时钟返回了无效时间：{value}',timeReply:'时钟时间：{value}',timeSent:'已发送：{value} · 尚未确认',
 saveLog:'保存日志',logHelp:'TX 表示发送的命令，RX 表示时钟的回复。密码不会记录。',noEvents:'暂无事件。',saved:'已保存：{path}',sending:'正在发送命令…',failed:'操作失败',runApp:'请运行 Guoran Clock 以连接时钟。',lost:'与应用的连接中断：{error}',
 connectHelp:'请在电脑附近开启时钟。蓝牙名称以 XGGF 开头，例如 XGGF-IN1204240430.4。',connectNote:'如果其他应用已连接此时钟，请先断开。',scan:'查找时钟',enableBt:'开启蓝牙',scanPrompt:'点击“查找时钟”',scanning:'正在搜索…',unnamed:'未命名',password:'连接密码',passwordHint:'原版应用密码：210709',disconnect:'断开连接',connectAction:'连接',close:'关闭',
 lightTheme:'浅色主题',darkTheme:'深色主题',language:'界面语言',amber:'琥珀色',warm:'暖白色',coral:'珊瑚色',lavender:'淡紫色',sky:'天蓝色',teal:'青色',sage:'绿色',white:'白色',
 guideIntro:'IN12_M4 时钟使用指南。可通过电脑蓝牙或机身按键修改设置。',guideMenu:'设置菜单',guideMenuText:'遥控设置分为两步：先在左侧两只辉光管选择菜单项，再在右侧两只辉光管选择参数。在机身上同时按 L 和 R 可进入设置。',
 guideProtection:'辉光管保护会定期轮换显示所有数字，这是正常现象。设置间隔时，按 SET，用 + / − 在左侧选择第 16 项并按 OK。然后在右侧选择 5 至 15 分钟的间隔，按 OK 确认。建议设置为 5 分钟。0 表示关闭保护；厂家建议保持开启。',
 guideTouch:'机身按键',guideTouchText:'L 开关背光，在菜单中增加数值。OK 开关时钟，在菜单中确认。R 显示日期，在菜单中减少数值。同时按 L+R 进入或退出设置；OK+R 启动计时器。',
 guideRead:'读取与发送',guideReadText:'“时钟回复”表示已收到的数值。“已发送，尚未确认”表示命令已发送，但尚未收到新的回复。“读取设置”会请求回复；若无回复，应用会重新连接。异常数值会单独标出，不影响其他功能。',
 guidePower:'供电与保养',guidePowerText:'说明书参数：直流 5 V，电流小于 400 mA，尺寸 132 × 50 × 50 mm。请保持干燥，不要拉扯 USB 接口或拆开外壳。',
 menuTable:'时钟菜单参考表',code:'左侧：菜单项',function:'功能',values:'右侧：参数',quickStart:'首次连接',
 quickStartText:'为时钟接通 5 V 电源并开启电脑蓝牙。点击“连接时钟”→“查找时钟”，选择名称以 XGGF 开头的设备。输入连接密码（默认 210709），点击“连接”。如果其他应用正在使用时钟，请先在该应用中断开连接。连接后打开“背光与控制”。',
 diagramTitle:'示例：选择闹钟 1',diagramItem:'SET · 选择菜单项',diagramValue:'OK · 选择参数',diagramCaption:'显示示意图：带边框的一对表示当前选择。这是示例，并非所连接时钟的实时读数。',menuOpen:'显示菜单参考表',menuClose:'隐藏参考表',menuLeft:'左侧：菜单项',menuRight:'右侧：参数',
 menuStep1:'1. 按 SET。左侧两只管亮起，显示“左侧：菜单项”列中的代码。用 + / − 选择菜单项。',menuStep2:'2. 按 OK。选择移至右侧两只管，对照“右侧：参数”列，用 + / − 修改参数。',menuStep3:'3. 按 OK 确认。有些菜单项会进入进一步设置，例如闹钟时间。“返回”回到上一级，在主菜单中则退出至时间显示。',menuExample:'示例：左侧代码 02 表示“闹钟 1”。按 OK 后选择移至右侧。0 表示关闭，1 表示开启并继续设置闹钟时间。背光指示当前选择的一对辉光管。',menuPrepare:'按 SET 进入菜单。应用先发送“返回”，再发送 SET，使时钟退出当前模式后进入菜单选择。',menuReferenceOnly:'此表仅供参考。显示或隐藏表格不会发送命令。当前菜单位置请查看时钟上的数字。'
};
for (const [key, value] of Object.entries(chinese)) messages[key][2] = value;
const chineseMenu = [
 ['时间设置','0 — 手动；1 — 蓝牙同步'],['闹钟 1 / 2','0 — 关闭；1 — 开启并设置闹钟时间'],['数字切换效果','0–3 — 数字切换效果'],['冒号','0 — 关闭；1 — 开启'],['亮度','0 — 自动；1 — 手动调节，10 级'],['音量','0–7；0 — 静音'],['显示模式','1 — 时/分/秒；2 — 时/分/星期；3 — 月/日/星期；4 — 自定义'],['时间格式','12 或 24 小时制'],['定时开关','1 — 开机时间；2 — 关机时间'],['整点报时','0 — 关闭；1 — 开启'],['夜间模式','0 — 关闭；1 — 亮度低于 2 时停止报时'],['闹钟铃声','1–6 — 选择铃声'],['星期背光颜色','0 — 关闭；1 — 开启（无法手动更改颜色）'],['外部开关','0 / 1 — 为外部设备预留的接口'],['辉光管保护','0 — 关闭；5–15 分钟；建议 5 分钟'],['语音语言','0 — 中文；1 — 英文'],['重置时钟','00 — 保留设置；11 — 恢复出厂设置']
];
menuRows.forEach((row,i)=>{row[1][2]=chineseMenu[i][0];row[2][2]=chineseMenu[i][1]});
