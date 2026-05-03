import json
import os
import re
import sys
import tkinter as tk
import webbrowser
from tkinter import ttk, messagebox, scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# 高DPI适配（Windows）
if sys.platform == 'win32':
    try:
        from ctypes import windll

        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass


# matplotlib全局设置（图表文字保留英文）
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 100
plt.rcParams['savefig.dpi'] = 150
plt.rcParams['figure.autolayout'] = True


# ================== 数据加载与清洗 ==================
def load_and_clean_data(file_path='test-data.json'):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    df['amount'] = df['amount'].astype(float)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['hour'] = df['timestamp'].dt.hour
    df['weekday'] = df['timestamp'].dt.dayofweek  # 0=Monday
    # 过滤异常金额
    df = df[df['amount'] >= 0.5]
    return df


# ================== K-means 聚类 ==================
def cluster_dishes(df):
    dish_stats = df.groupby('window_id').agg({
        'transaction_id': 'count',
        'amount': 'sum'
    }).rename(columns={'transaction_id': 'frequency', 'amount': 'total_amount'})
    dish_stats['avg_price'] = dish_stats['total_amount'] / dish_stats['frequency']

    features = ['frequency', 'total_amount', 'avg_price']
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(dish_stats[features])

    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    dish_stats['cluster'] = kmeans.fit_predict(scaled_data)

    # 根据频率均值排序，确定标签（英文，保持图表一致性）
    order = dish_stats.groupby('cluster')['frequency'].mean().sort_values()
    label_map = {order.index[0]: 'Unpopular', order.index[1]: 'Regular', order.index[2]: 'Popular'}
    dish_stats['category'] = dish_stats['cluster'].map(label_map)
    return dish_stats


def get_dish_name(window_id):
    mapping = {
        'W01': 'Tomato Egg + Braised Pork + Veg',
        'W02': 'Fish with Pickled Cabbage + Mapo Tofu + Rice',
        'W03': 'Beef Noodle / Soybean Paste Noodle',
        'W04': 'Fried Rice Noodle + Fried Egg',
        'W05': 'Steamed Bun + Soy Milk',
        'W06': 'Fruit Platter + Yogurt'
    }
    return mapping.get(window_id, window_id)


# ================== 增强的 Markdown 渲染器 ==================
class MarkdownRenderer:
    def __init__(self, text_widget):
        self.text = text_widget
        # 标题样式（更醒目）
        self.text.tag_configure('heading1', font=('微软雅黑', 18, 'bold'), foreground='#2c3e50', spacing3=12)
        self.text.tag_configure('heading2', font=('微软雅黑', 15, 'bold'), foreground='#34495e', spacing3=10)
        self.text.tag_configure('heading3', font=('微软雅黑', 13, 'bold'), foreground='#7f8c8d', spacing3=8)
        # 文本样式
        self.text.tag_configure('bold', font=('微软雅黑', 10, 'bold'))
        self.text.tag_configure('italic', font=('微软雅黑', 10, 'italic'))
        self.text.tag_configure('code', font=('Consolas', 9), background='#f0f0f0', lmargin1=10, lmargin2=10)
        self.text.tag_configure('code_inline', font=('Consolas', 9), background='#f0f0f0')
        self.text.tag_configure('list_item', lmargin1=20, lmargin2=35)
        self.text.tag_configure('link', foreground='blue', underline=True)
        # 链接点击事件
        self.text.tag_bind('link', '<Enter>', lambda e: self.text.config(cursor='hand2'))
        self.text.tag_bind('link', '<Leave>', lambda e: self.text.config(cursor=''))
        self.text.tag_bind('link', '<Button-1>', self._link_click)

    def _link_click(self, event):
        index = self.text.index(f"@{event.x},{event.y}")
        tags = self.text.tag_names(index)
        for tag in tags:
            if tag.startswith('link_url:'):
                url = tag.replace('link_url:', '')
                webbrowser.open(url)
                return

    def render(self, markdown_text):
        self.text.delete(1.0, tk.END)
        lines = markdown_text.split('\n')
        in_code_block = False
        code_block_lines = []

        for line in lines:
            if line.strip().startswith('```'):
                if not in_code_block:
                    in_code_block = True
                    code_block_lines = []
                else:
                    in_code_block = False
                    code_content = '\n'.join(code_block_lines)
                    self.text.insert(tk.END, code_content + '\n', 'code')
                continue

            if in_code_block:
                code_block_lines.append(line)
                continue

            # 支持三级标题
            if line.startswith('# '):
                self.text.insert(tk.END, line[2:] + '\n', 'heading1')
                continue
            if line.startswith('## '):
                self.text.insert(tk.END, line[3:] + '\n', 'heading2')
                continue
            if line.startswith('### '):
                self.text.insert(tk.END, line[4:] + '\n', 'heading3')
                continue

            if re.match(r'^[-*] ', line):
                content = line[2:]
                self._insert_inline(content, 'list_item')
                self.text.insert(tk.END, '\n')
                continue

            self._insert_inline(line)
            self.text.insert(tk.END, '\n')

    def _insert_inline(self, text, base_tag=None):
        pattern = r'(\*\*(.*?)\*\*)|(\*(.*?)\*)|(`(.*?)`)|(\[(.*?)\]\((.*?)\))'
        last_end = 0
        for match in re.finditer(pattern, text):
            start, end = match.span()
            if start > last_end:
                self._insert_plain(text[last_end:start], base_tag)
            if match.group(1):  # **bold**
                self._insert_plain(match.group(2), base_tag, extra_tag='bold')
            elif match.group(3):  # *italic*
                self._insert_plain(match.group(4), base_tag, extra_tag='italic')
            elif match.group(5):  # `code`
                self._insert_plain(match.group(6), base_tag, extra_tag='code_inline')
            elif match.group(7):  # [text](url)
                link_text = match.group(8)
                link_url = match.group(9)
                self.text.insert(tk.END, link_text, (base_tag, 'link', f'link_url:{link_url}') if base_tag else (
                    'link', f'link_url:{link_url}'))
            last_end = end
        if last_end < len(text):
            self._insert_plain(text[last_end:], base_tag)

    def _insert_plain(self, text, base_tag=None, extra_tag=None):
        if not text:
            return
        tags = []
        if base_tag:
            tags.append(base_tag)
        if extra_tag:
            tags.append(extra_tag)
        if tags:
            self.text.insert(tk.END, text, tuple(tags))
        else:
            self.text.insert(tk.END, text)


# ================== 增强的 README 查看器（带行号+同步滚动） ==================
class EnhancedReadmeViewer:
    def __init__(self, parent, file_path):
        self.parent = parent
        self.file_path = file_path

        # 1. 创建顶层窗口
        self.win = tk.Toplevel(parent)
        self.win.title("关于 / 帮助 - 食堂消费分析系统")
        self.win.geometry("950x700")
        self.win.minsize(800, 550)

        # 2. 读取文件内容（兼容 UTF-8/GBK）
        self.content = self._read_file()
        if not self.content:
            return

        # 3. 显示文件基本信息
        self._create_file_info_bar()

        # 4. 创建带行号的文本区域
        self._create_text_area_with_line_numbers()

        # 5. 渲染 Markdown 内容
        self._render_markdown_content()

    def _read_file(self):
        """读取文件，自动处理编码"""
        if not os.path.exists(self.file_path):
            messagebox.showerror("错误", f"找不到 README.md 文件：{self.file_path}")
            self.win.destroy()
            return None

        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            try:
                with open(self.file_path, 'r', encoding='gbk') as f:
                    return f.read()
            except Exception as e:
                messagebox.showerror("错误", f"读取文件失败（GBK 也失败）：{e}")
                self.win.destroy()
                return None
        except Exception as e:
            messagebox.showerror("错误", f"读取文件失败：{e}")
            self.win.destroy()
            return None

    def _create_file_info_bar(self):
        """顶部文件信息栏"""
        info_bar = ttk.Frame(self.win, padding="12 8 12 5")
        info_bar.pack(fill=tk.X, side=tk.TOP)

        # 计算文件信息
        file_size_kb = os.path.getsize(self.file_path) / 1024
        total_lines = len(self.content.split('\n'))

        # 显示信息
        info_text = (
            f"📄 文件路径：{self.file_path}    "
            f"📏 大小：{file_size_kb:.2f} KB    "
            f"📝 总行数：{total_lines}"
        )
        ttk.Label(
            info_bar,
            text=info_text,
            font=("微软雅黑", 9),
            foreground="#555555"
        ).pack(side=tk.LEFT)

    def _create_text_area_with_line_numbers(self):
        """创建带行号的双文本区域（行号+内容同步滚动）"""
        text_container = ttk.Frame(self.win)
        text_container.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)

        # --- 左侧：行号显示 ---
        self.line_num_text = tk.Text(
            text_container,
            width=6,
            padx=5,
            takefocus=0,
            border=0,
            background="#f5f5f5",
            foreground="#666666",
            font=("Consolas", 10),
            state=tk.DISABLED
        )
        self.line_num_text.pack(side=tk.LEFT, fill=tk.Y)

        # --- 右侧：内容显示（带滚动条）---
        self.content_text = scrolledtext.ScrolledText(
            text_container,
            wrap=tk.WORD,
            font=("微软雅黑", 10),
            undo=True
        )
        self.content_text.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # --- 同步滚动绑定 ---
        self.content_text.vbar.config(command=self._sync_scroll_both)
        self.content_text.bind("<MouseWheel>", self._on_mouse_wheel)
        self.content_text.bind("<KeyPress>", self._on_key_press)

        # 初始更新行号
        self._update_line_numbers()

    def _sync_scroll_both(self, *args):
        """同步滚动行号和内容"""
        self.content_text.yview(*args)
        self.line_num_text.yview(*args)
        self._update_line_numbers()

    def _on_mouse_wheel(self, event):
        """鼠标滚轮滚动"""
        self.content_text.yview_scroll(int(-1 * (event.delta / 120)), "units")
        self._sync_scroll_both()
        return "break"

    def _on_key_press(self, event):
        """键盘按键滚动（如上下键、PageUp/PageDown）"""
        self.win.after_idle(self._update_line_numbers)

    def _update_line_numbers(self):
        """动态更新行号显示"""
        # 获取内容区域的可见行范围
        start_line = int(self.content_text.index("@0,0").split('.')[0])
        end_line = int(self.content_text.index("end-1c").split('.')[0])

        # 重新生成行号
        self.line_num_text.config(state=tk.NORMAL)
        self.line_num_text.delete(1.0, tk.END)
        line_numbers_str = "\n".join(str(i) for i in range(start_line, end_line + 1))
        self.line_num_text.insert(1.0, line_numbers_str)

        # 同步行号的滚动位置
        self.line_num_text.yview_moveto(self.content_text.yview()[0])
        self.line_num_text.config(state=tk.DISABLED)

    def _render_markdown_content(self):
        """使用增强的 MarkdownRenderer 渲染内容"""
        renderer = MarkdownRenderer(self.content_text)
        renderer.render(self.content)
        self.content_text.config(state=tk.DISABLED)  # 禁用编辑
        self._update_line_numbers()  # 渲染后再次更新行号


# ================== GUI 应用程序 ==================
class CanteenAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("校园食堂消费智能分析系统")
        self.root.geometry("1100x750")
        self.root.minsize(900, 600)

        # 【新增】绑定窗口关闭事件：点击 X 按钮时调用 on_close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.df = None
        self.dish_stats = None
        self.create_widgets()

        try:
            self.load_data()
        except FileNotFoundError:
            messagebox.showwarning("警告", "未找到 test-data.json 文件，请将其放在程序同目录下。")

    # 【新增】窗口关闭时的处理方法
    def on_close(self):
        """点击窗口关闭按钮时：销毁窗口 + 彻底结束程序"""
        self.root.destroy()  # 销毁 Tkinter 主窗口
        sys.exit(0)  # 退出 Python 进程（确保程序彻底结束）

        try:
            self.load_data()
        except FileNotFoundError:
            messagebox.showwarning("警告", "未找到 test-data.json 文件，请将其放在程序同目录下。")

    def create_widgets(self):
        top_frame = ttk.Frame(self.root)
        top_frame.pack(pady=10)

        ttk.Button(top_frame, text="① 加载数据", command=self.load_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="② K-means 聚类分析", command=self.run_kmeans).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="③ 显示统计图表", command=self.show_charts).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="关于 / 帮助", command=self.show_readme).pack(side=tk.LEFT, padx=5)

        text_frame = ttk.Frame(self.root)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.result_text = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, font=("微软雅黑", 10))
        self.result_text.pack(fill=tk.BOTH, expand=True)

        self.figure_frame = ttk.Frame(self.root)
        self.figure_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.result_text.insert(tk.END, "欢迎使用食堂消费分析系统！\n请点击「加载数据」开始。\n")

    def load_data(self):
        try:
            self.df = load_and_clean_data('test-data.json')
            total_sales = len(self.df)
            total_revenue = self.df['amount'].sum()
            avg_price = self.df['amount'].mean()
            unique_students = self.df['student_id'].nunique()

            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "✅ 数据加载成功！\n")
            self.result_text.insert(tk.END, f"总交易笔数     ：{total_sales}\n")
            self.result_text.insert(tk.END, f"总营业额       ：{total_revenue:.2f} 元\n")
            self.result_text.insert(tk.END, f"平均每笔消费   ：{avg_price:.2f} 元\n")
            self.result_text.insert(tk.END, f"参与消费学生数 ：{unique_students}\n\n")
            self.result_text.insert(tk.END, "请点击「K-means 聚类分析」查看菜品人气分类（爆款/常规/冷门）。\n")
        except Exception as e:
            messagebox.showerror("错误", f"加载失败：{str(e)}")

    def run_kmeans(self):
        if self.df is None:
            messagebox.showwarning("警告", "请先加载数据！")
            return

        self.dish_stats = cluster_dishes(self.df)
        popular = self.dish_stats[self.dish_stats['category'] == 'Popular'].index.tolist()
        unpopular = self.dish_stats[self.dish_stats['category'] == 'Unpopular'].index.tolist()
        regular = self.dish_stats[self.dish_stats['category'] == 'Regular'].index.tolist()

        self.result_text.insert(tk.END, "\n========== K-means 聚类结果（k=3） ==========\n")
        self.result_text.insert(tk.END, "【特征维度】：消费次数、总金额、客单价\n")
        self.result_text.insert(tk.END,
                                f"🔥 爆款窗口 (Popular) ：{', '.join([f'{w}({get_dish_name(w)})' for w in popular])}\n")
        self.result_text.insert(tk.END,
                                f"📊 常规窗口 (Regular) ：{', '.join([f'{w}({get_dish_name(w)})' for w in regular])}\n")
        self.result_text.insert(tk.END,
                                f"❄️ 冷门窗口 (Unpopular) ：{', '.join([f'{w}({get_dish_name(w)})' for w in unpopular])}\n")
        messagebox.showinfo("完成", "聚类分析已完成，结果如上所示。")

    def show_charts(self):
        if self.df is None:
            messagebox.showwarning("警告", "请先加载数据！")
            return

        for widget in self.figure_frame.winfo_children():
            widget.destroy()

        fig = plt.figure(figsize=(8, 6), dpi=110)
        fig.subplots_adjust(hspace=0.4)

        ax1 = fig.add_subplot(211)
        dish_counts = self.df.groupby('window_id')['transaction_id'].count().sort_values(ascending=False)
        windows = [f"{w}\n{get_dish_name(w)[:8]}" for w in dish_counts.index]
        ax1.bar(windows, dish_counts.values, color='#da7756')
        ax1.set_title('Transaction Count per Window', fontsize=12)
        ax1.set_ylabel('Number of Transactions')
        ax1.tick_params(axis='x', labelsize=8)

        ax2 = fig.add_subplot(212)
        df_copy = self.df.copy()
        pivot = df_copy.groupby(['hour', 'weekday']).size().unstack(fill_value=0)
        im = ax2.imshow(pivot.values, cmap='YlOrRd', aspect='auto')
        ax2.set_xticks(range(7))
        ax2.set_xticklabels(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])
        ax2.set_yticks(range(0, 24, 2))
        ax2.set_yticklabels(range(0, 24, 2))
        ax2.set_xlabel('Weekday')
        ax2.set_ylabel('Hour of Day')
        ax2.set_title('Transaction Heatmap (Darker = More Popular)')
        plt.colorbar(im, ax=ax2, label='Transaction Count')

        canvas = FigureCanvasTkAgg(fig, master=self.figure_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def show_readme(self):
        readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
        # 直接使用增强的查看器打开 README
        EnhancedReadmeViewer(self.root, readme_path)


if __name__ == "__main__":
    root = tk.Tk()
    app = CanteenAnalyzerApp(root)
    root.mainloop()
