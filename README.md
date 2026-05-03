# 校园食堂消费智能分析系统

## 项目信息

|项目维度|详情|
|---|---|
|项目名称|校园食堂消费智能分析系统|
|制作人员|阳子誉、岑冠霖、丁萌嘉|
|指导老师|张彬辉|
|完成日期|2026 年 5 月|
|所属课程|信息技术（必修）|
|版本号|v1\.1\.0（2026\-05\-03 更新）|

## 程序说明

本程序是基于 Python 开发的桌面应用，用于分析校园食堂一卡通消费数据（JSON 格式）。核心能力为：利用 **K\-means 聚类算法（k=3）**，将食堂窗口按受欢迎程度自动划分为三类：

- Popular（爆款）

- Regular（常规）

- Unpopular（冷门）

同时配套**独立的命令行随机数据生成工具**，可快速生成符合格式要求的测试数据；并对帮助文档查看功能进行了全面增强，提升使用体验。

### 核心功能

程序内置图形用户界面（GUI），支持以下操作：

1. 加载并展示核心数据统计：总交易数、营业额、平均消费、参与人数；

2. 执行 K\-means 聚类分析，输出各窗口所属热度类别；

3. 可视化图表生成：

    - 各窗口消费次数柱状图

    - 消费时段热力图（按小时 / 星期维度）

4. **增强的帮助文档查看器**：

    - 左侧显示行号，与内容同步滚动

    - 顶部展示文件路径、大小、总行数信息

    - 支持三级标题高亮、代码块格式化、链接可点击

    - 自动兼容 UTF\-8/GBK 编码文件

5. **独立命令行随机数据生成工具**：支持自定义生成条数和输出文件名

> 界面交互（按钮 / 提示）为中文，图表文字 / 聚类类别名为英文，兼顾国内用户使用习惯与专业表达。
> 
> 

## 技术栈

|类别|库 / 工具|核心用途|
|---|---|---|
|GUI 开发|tkinter（Python 内置）|桌面窗口界面搭建|
|数据处理|pandas、numpy|数据清洗、聚合、数值计算|
|机器学习|scikit\-learn|K\-means 聚类、数据标准化|
|数据可视化|matplotlib|柱状图、热力图绘制|
|Markdown 渲染|自定义正则解析器|弹窗内格式化展示帮助文档|
|随机数据生成|Python 内置库（random、json、datetime）|生成符合格式的测试数据|

## 数据格式要求

程序需读取同目录下的 `test\-data\.json` 文件，格式需严格遵循以下规范。**可使用配套的 ****`generate\_data\.py`**** 工具自动生成符合该格式的测试数据**。

### JSON 结构示例

```json
[
  {
    "transaction_id": "T001",
    "student_id": "S1001",
    "timestamp": "2026-05-12 11:45:23",
    "window_id": "W01",
    "amount": 12.50
  }
]
```

### 字段说明

|字段名|类型|描述|
|---|---|---|
|transaction\_id|字符串|交易唯一编号|
|student\_id|字符串|学生匿名 ID（示例：S1001）|
|timestamp|字符串|交易时间，格式：YYYY\-MM\-DD HH:MM:SS|
|window\_id|字符串|窗口编号（范围：W01\~W06）|
|amount|数字|交易金额（单位：元），程序自动过滤 \&lt; 0\.5 元的异常记录|

### 窗口 \- 菜品对应表（辅助分析）

|窗口编号|菜品组合（英文）|
|---|---|
|W01|Tomato Egg \+ Braised Pork \+ Vegetables|
|W02|Fish \+ Mapo Tofu \+ Rice|
|W03|Beef Noodle / Noodle with Soybean Paste|
|W04|Fried Rice Noodle \+ Fried Egg|
|W05|Steamed Bun \+ Soy Milk|
|W06|Fruit Platter \+ Yogurt|

## 运行环境与依赖

### 环境要求

- Python 版本：3\.9 及以上

### 依赖安装

执行以下命令安装主程序所需的第三方库（随机数据生成工具无需额外依赖）：

```bash
pip install pandas numpy matplotlib scikit-learn
```

## 使用方法

### 1\. 生成测试数据（可选）

如果没有现成的消费数据，可使用配套的 `generate\_data\.py` 工具生成随机测试数据：

```bash
# 生成 200 条数据（默认保存为 test-data.json）
python generate_data.py -c 200

# 生成 500 条数据，保存为自定义文件名
python generate_data.py -c 500 -o my_canteen_data.json
```

### 2\. 基础运行

1. 文件准备：将 `canteen\_analyzer\.py`、`test\-data\.json`、`README\.md` 放在同一文件夹；

2. 命令行执行：

    ```bash
    cd 目标文件夹路径
    python canteen_analyzer.py
    ```

3. 操作流程：

    - ① 加载数据 → 查看总体统计数据；

    - ② K\-means 聚类分析 → 查看窗口热度分类结果；

    - ③ 显示统计图表 → 查看柱状图 / 热力图可视化结果；

    - ④ 关于 / 帮助 → 查看增强版格式化帮助文档。

### 3\. 打包为独立 EXE（可选）

如需生成无需 Python 环境的可执行文件，步骤如下：

1. 安装打包工具：

    ```bash
    pip install pyinstaller
    ```

2. 打包主程序：

    ```bash
    pyinstaller --onefile --windowed --add-data "test-data.json;." --add-data "README.md;." canteen_analyzer.py
    ```

3. 打包随机数据生成工具（可选）：

    ```bash
    pyinstaller --onefile --console generate_data.py
    ```

4. 注意：生成的 `canteen\_analyzer\.exe` 需与 `test\-data\.json`、`README\.md` 同目录运行。

## 注意事项

1. 数据安全：程序全程本地处理数据，无网络请求，保护用户隐私；

2. 结果参考：聚类结果为算法自动划分，仅作为决策参考，不建议作为唯一依据；

3. 界面适配：高分辨率屏幕下若界面过小（Windows 系统），可将 “设置→系统→显示→缩放与布局” 调整至 125% 及以上（程序已启用 DPI 感知）；

4. 随机数据：`generate\_data\.py` 生成的数据为模拟数据，仅供测试使用，不代表真实消费情况；

5. 文件编码：帮助文档查看器自动兼容 UTF\-8 和 GBK 编码，若出现乱码请检查文件编码格式。

## 开发者与致谢

### 开发分工

- 阳子誉：算法实现、GUI 架构设计、Markdown 渲染器开发；

- 岑冠霖：数据清洗、统计计算、功能测试、随机数据生成工具开发；

- 丁萌嘉：图表设计、项目文档撰写、帮助文档查看器增强。

- 指导老师：张彬辉

### 致谢

感谢学校提供脱敏后的真实数据样本（测试数据基于真实格式模拟生成）。

> （注：文档部分内容可能由 AI 生成）
