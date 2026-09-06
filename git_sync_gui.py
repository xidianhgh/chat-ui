# -*- coding: utf-8 -*-
"""
Git 分支同步工具

功能：
    - 界面提供输入框：目标 Git 地址、本地 Git 仓库目录，以及两个可选的
      分支输入框（本地分支、目标分支）
    - 点击“同步”按钮后，根据分支输入框的填写情况决定推送行为：
        * 两个分支都留空：推送本地所有分支到目标地址（分支名保持一致）
        * 只填目标分支：把本地仓库“当前分支”推送到目标仓库的目标分支
        * 两个都填：把本地仓库所填分支推送到目标仓库的目标分支
        * 只填本地分支：把该本地分支推送到目标仓库的同名分支
    - 同步过程统一采用“直接推送到 URL”方式（`git push <url> ...`），
      不会新增/修改本地仓库的 remote 配置，也不会改动本地分支，
      因此同步完成后本地仓库的远程地址与分支保持原样不变。

仅依赖 Python 标准库（tkinter + subprocess），无需安装第三方包。
"""

import os
import queue
import shutil
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


# ---------------------------------------------------------------------------
# 绿色主题配色方案
# ---------------------------------------------------------------------------
COLOR_BG         = "#eef6ee"   # 主窗口背景（浅绿）
COLOR_CARD       = "#ffffff"   # 卡片背景
COLOR_BORDER     = "#c8e6c9"   # 边框 / 分隔线（浅绿）
COLOR_HEADER_BG  = "#2e7d32"   # 顶部横幅（深绿）
COLOR_HEADER_FG  = "#ffffff"   # 顶部标题文字
COLOR_HEADER_SUB = "#d3ecd5"   # 顶部副标题文字
COLOR_ACCENT     = "#43a047"   # 主色（绿）
COLOR_ACCENT_HV  = "#388e3c"   # 主色 hover
COLOR_ACCENT_DK  = "#1b5e20"   # 深绿（强调文字）
COLOR_TEXT       = "#1f3d22"   # 正文（深绿黑）
COLOR_MUTED      = "#5f7d62"   # 次要文字
COLOR_LOG_BG     = "#0e2417"   # 日志区背景（深绿黑，终端风）
COLOR_LOG_FG     = "#c8e6c9"   # 日志默认文字
COLOR_LOG_TITLE  = "#388e3c"   # 日志区标题栏

FONT_FAMILY = "Microsoft YaHei UI"
FONT_MONO   = "Consolas"


class GitSyncApp:
    """Git 分支同步图形界面应用"""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Git 分支同步工具")
        self.root.geometry("1060x660")
        self.root.minsize(940, 600)
        self.root.configure(bg=COLOR_BG)

        # 用于工作线程与主线程之间安全地传递日志/状态
        self.log_queue = queue.Queue()
        self.is_running = False

        self._setup_style()
        self._build_widgets()
        # 定时从队列中取出日志刷新到界面
        self.root.after(100, self._process_log_queue)

    # ------------------------------------------------------------------ #
    # 样式配置（绿色主题）
    # ------------------------------------------------------------------ #
    def _setup_style(self):
        """基于 clam 主题定制绿色主题样式"""
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        base_font = (FONT_FAMILY, 10)
        style.configure(".", background=COLOR_BG, foreground=COLOR_TEXT,
                        font=base_font, bordercolor=COLOR_BORDER)

        # 容器
        style.configure("TFrame", background=COLOR_BG)
        style.configure("Card.TFrame", background=COLOR_CARD, borderwidth=1,
                        relief="solid", bordercolor=COLOR_BORDER)
        style.configure("CardFlat.TFrame", background=COLOR_CARD, borderwidth=0)
        style.configure("Header.TFrame", background=COLOR_HEADER_BG)
        style.configure("LogTitle.TFrame", background=COLOR_LOG_TITLE)

        # 标签
        style.configure("TLabel", background=COLOR_BG, foreground=COLOR_TEXT, font=base_font)
        style.configure("Card.TLabel", background=COLOR_CARD, foreground=COLOR_MUTED,
                        font=(FONT_FAMILY, 9))
        style.configure("CardTitle.TLabel", background=COLOR_CARD, foreground=COLOR_ACCENT_DK,
                        font=(FONT_FAMILY, 11, "bold"))
        style.configure("HeaderTitle.TLabel", background=COLOR_HEADER_BG, foreground=COLOR_HEADER_FG,
                        font=(FONT_FAMILY, 17, "bold"))
        style.configure("HeaderSub.TLabel", background=COLOR_HEADER_BG, foreground=COLOR_HEADER_SUB,
                        font=(FONT_FAMILY, 9))
        style.configure("LogTitle.TLabel", background=COLOR_LOG_TITLE, foreground="#ffffff",
                        font=(FONT_FAMILY, 10, "bold"))
        style.configure("Status.TLabel", background=COLOR_BG, foreground=COLOR_MUTED,
                        font=(FONT_FAMILY, 9))

        # 输入框
        style.configure("TEntry", fieldbackground="#ffffff", foreground=COLOR_TEXT,
                        insertcolor=COLOR_TEXT, bordercolor=COLOR_BORDER, lightcolor=COLOR_BORDER,
                        darkcolor=COLOR_BORDER, padding=6, font=base_font)
        style.map("TEntry", bordercolor=[("focus", COLOR_ACCENT)],
                  lightcolor=[("focus", COLOR_ACCENT)], darkcolor=[("focus", COLOR_ACCENT)])

        # 主按钮（绿色实心）
        style.configure("Accent.TButton", background=COLOR_ACCENT, foreground="#ffffff",
                        borderwidth=0, focuscolor=COLOR_ACCENT, font=(FONT_FAMILY, 11, "bold"),
                        padding=(24, 9))
        style.map("Accent.TButton",
                  background=[("active", COLOR_ACCENT_HV), ("pressed", COLOR_ACCENT_DK),
                              ("disabled", "#a5d6a7")],
                  foreground=[("disabled", "#eef6ee")])

        # 次要按钮（白底绿边）
        style.configure("TButton", background="#ffffff", foreground=COLOR_ACCENT_DK,
                        bordercolor=COLOR_BORDER, borderwidth=1, focuscolor=COLOR_CARD,
                        font=base_font, padding=(14, 7))
        style.map("TButton",
                  background=[("active", "#e8f5e9"), ("pressed", "#dcedc8"), ("disabled", "#f4f4f4")],
                  foreground=[("disabled", "#a8a8a8")],
                  bordercolor=[("active", COLOR_ACCENT)])

        # 复选框
        style.configure("TCheckbutton", background=COLOR_CARD, foreground=COLOR_TEXT,
                        font=base_font, focuscolor=COLOR_CARD)
        style.map("TCheckbutton", background=[("active", COLOR_CARD)])
        # 用自绘图标替换 clam 主题默认的 “×”：选中时显示绿色对勾
        self._setup_checkbutton_icons(style)

        # 进度条
        style.configure("Horizontal.TProgressbar", troughcolor="#dcedc8", background=COLOR_ACCENT,
                        bordercolor=COLOR_BORDER, lightcolor=COLOR_ACCENT, darkcolor=COLOR_ACCENT,
                        thickness=12)

        # 滚动条
        style.configure("Vertical.TScrollbar", troughcolor="#e8f5e9", background="#a5d6a7",
                        bordercolor=COLOR_BG, arrowcolor=COLOR_ACCENT_DK, relief="flat")
        style.map("Vertical.TScrollbar", background=[("active", COLOR_ACCENT)])

    # ------------------------------------------------------------------ #
    # 复选框图标（自绘对勾，替换 clam 主题的 “×”）
    # ------------------------------------------------------------------ #
    def _setup_checkbutton_icons(self, style):
        """用标准库 PhotoImage 自绘复选框图标：
        未选中 = 白底浅绿边框空框；选中 = 绿底白色对勾。
        然后注册为 ttk image 元素并重定义 TCheckbutton 布局，
        以此替换 clam 主题默认的 “×” 选中符号。
        """
        S = 16   # 方框边长（像素）
        W = 20   # 图标总宽（右侧 4px 留白，作为图标与文字的间距）
        white = "#ffffff"
        green_bg = COLOR_ACCENT       # 选中背景（绿）
        dark_green = COLOR_ACCENT_DK  # 选中边框（深绿）
        light_border = "#a5d6a7"      # 未选中边框（浅绿）

        # 计算对勾覆盖的像素：两段折线，约 2px 粗
        check_pixels = set()

        def mark_line(x0, y0, x1, y1):
            steps = max(abs(x1 - x0), abs(y1 - y0))
            for i in range(steps + 1):
                t = i / steps if steps else 0
                x = round(x0 + (x1 - x0) * t)
                y = round(y0 + (y1 - y0) * t)
                for dx in (0, 1):
                    for dy in (0, 1):
                        if 0 <= x + dx < S and 0 <= y + dy < S:
                            check_pixels.add((x + dx, y + dy))

        mark_line(3, 8, 6, 11)
        mark_line(6, 11, 12, 4)

        def build_rows(draw_check):
            rows = []
            for y in range(S):
                row = []
                for x in range(W):
                    if x >= S:
                        row.append(COLOR_CARD)  # 右侧留白，与卡片背景一致
                        continue
                    edge = (x == 0 or y == 0 or x == S - 1 or y == S - 1)
                    if draw_check:
                        if (x, y) in check_pixels:
                            row.append(white)
                        elif edge:
                            row.append(dark_green)
                        else:
                            row.append(green_bg)
                    else:
                        row.append(light_border if edge else white)
                rows.append(row)
            return rows

        def to_image(rows):
            data = " ".join("{" + " ".join(r) + "}" for r in rows)
            img = tk.PhotoImage(width=W, height=S, master=self.root)
            img.put(data)
            return img

        # 必须保持引用，否则会被垃圾回收导致图标消失
        self._cb_unchecked_img = to_image(build_rows(draw_check=False))
        self._cb_checked_img = to_image(build_rows(draw_check=True))

        # 注册 image 元素（新名字，避免与主题内置元素冲突）并重定义布局
        style.element_create("GreenCheck.indicator", "image",
                             self._cb_unchecked_img,
                             ("selected", self._cb_checked_img),
                             sticky="")
        style.layout("TCheckbutton", [
            ("Checkbutton.padding", {"sticky": "nswe", "children": [
                ("GreenCheck.indicator", {"side": "left", "sticky": ""}),
                ("Checkbutton.focus", {"sticky": "", "children": [
                    ("Checkbutton.label", {"side": "left", "sticky": ""})
                ]})
            ]})
        ])

    # ------------------------------------------------------------------ #
    # 界面构建
    # ------------------------------------------------------------------ #
    def _build_widgets(self):
        # ---------- 顶部标题横幅 ----------
        header = ttk.Frame(self.root, style="Header.TFrame")
        header.pack(fill="x")
        ttk.Label(header, text="Git 分支同步工具", style="HeaderTitle.TLabel").pack(
            anchor="w", padx=22, pady=(16, 2))
        ttk.Label(header, text="把本地仓库分支同步到目标 Git 地址（可指定分支），且不改动本地远程配置与分支",
                  style="HeaderSub.TLabel").pack(anchor="w", padx=22, pady=(0, 16))

        # ---------- 主体区域（左右两栏：左配置 / 右日志） ----------
        body = ttk.Frame(self.root)
        body.pack(fill="both", expand=True, padx=18, pady=16)

        LEFT_WIDTH = 430
        left = ttk.Frame(body, width=LEFT_WIDTH)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)  # 固定左栏宽度，内部卡片 fill=x 自动撑满

        # 卡片一：仓库配置
        card1 = ttk.Frame(left, style="Card.TFrame", padding=18)
        card1.pack(fill="x")
        ttk.Label(card1, text="仓库配置", style="CardTitle.TLabel").pack(anchor="w", pady=(0, 10))

        ttk.Label(card1, text="目标 Git 地址", style="Card.TLabel").pack(anchor="w")
        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(card1, textvariable=self.url_var)
        self.url_entry.pack(fill="x", pady=(4, 12))

        ttk.Label(card1, text="本地仓库目录", style="Card.TLabel").pack(anchor="w")
        dir_row = ttk.Frame(card1, style="CardFlat.TFrame")
        dir_row.pack(fill="x", pady=(4, 0))
        self.dir_var = tk.StringVar()
        self.dir_entry = ttk.Entry(dir_row, textvariable=self.dir_var)
        self.dir_entry.pack(side="left", fill="x", expand=True)
        self.browse_btn = ttk.Button(dir_row, text="浏览...", command=self._choose_dir)
        self.browse_btn.pack(side="left", padx=(8, 0))

        # 分支设置（两个输入框均为可选）
        ttk.Label(card1, text="分支设置（均可留空）", style="Card.TLabel").pack(
            anchor="w", pady=(14, 0))
        branch_row = ttk.Frame(card1, style="CardFlat.TFrame")
        branch_row.pack(fill="x", pady=(4, 0))

        left_col = ttk.Frame(branch_row, style="CardFlat.TFrame")
        left_col.pack(side="left", fill="x", expand=True)
        ttk.Label(left_col, text="本地分支", style="Card.TLabel").pack(anchor="w")
        self.local_branch_var = tk.StringVar()
        self.local_branch_entry = ttk.Entry(left_col, textvariable=self.local_branch_var)
        self.local_branch_entry.pack(fill="x", pady=(2, 0))

        right_col = ttk.Frame(branch_row, style="CardFlat.TFrame")
        right_col.pack(side="left", fill="x", expand=True, padx=(12, 0))
        ttk.Label(right_col, text="目标分支", style="Card.TLabel").pack(anchor="w")
        self.target_branch_var = tk.StringVar()
        self.target_branch_entry = ttk.Entry(right_col, textvariable=self.target_branch_var)
        self.target_branch_entry.pack(fill="x", pady=(2, 0))

        ttk.Label(
            card1,
            text="规则：都留空→推送全部分支；仅填目标→当前分支推送到目标分支；"
                 "都填→本地分支推送到目标分支；仅填本地→推送到目标同名分支。",
            style="Card.TLabel", wraplength=LEFT_WIDTH - 40, justify="left").pack(
            anchor="w", pady=(8, 0))

        # 卡片二：同步选项
        card2 = ttk.Frame(left, style="Card.TFrame", padding=18)
        card2.pack(fill="x", pady=(14, 0))
        ttk.Label(card2, text="同步选项", style="CardTitle.TLabel").pack(anchor="w", pady=(0, 8))
        self.force_var = tk.BooleanVar(value=False)
        self.tags_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            card2, text="强制推送 (--force)",
            variable=self.force_var).pack(anchor="w", pady=(2, 2))
        ttk.Checkbutton(
            card2, text="同时同步标签 (--tags)", variable=self.tags_var).pack(anchor="w", pady=2)
        ttk.Label(
            card2,
            text="提示：强制推送会覆盖目标端冲突分支，可能导致目标端数据丢失。",
            style="Card.TLabel", wraplength=LEFT_WIDTH - 40, justify="left").pack(
            anchor="w", pady=(6, 0))

        # 操作区：按钮 + 状态（固定左栏底部）
        action = ttk.Frame(left)
        action.pack(side="bottom", fill="x")
        self.sync_btn = ttk.Button(action, text="同 步", style="Accent.TButton",
                                   command=self._on_sync_clicked)
        self.sync_btn.pack(side="left")
        self.clear_btn = ttk.Button(action, text="清空日志", command=self._clear_log)
        self.clear_btn.pack(side="left", padx=(10, 0))
        self.status_var = tk.StringVar(value="就绪")
        ttk.Label(action, textvariable=self.status_var, style="Status.TLabel").pack(side="right")

        # 进度条（位于按钮上方，固定左栏底部）
        self.progress = ttk.Progressbar(left, mode="indeterminate",
                                        style="Horizontal.TProgressbar")
        self.progress.pack(side="bottom", fill="x", pady=(0, 12))

        # ===== 右栏：日志面板 =====
        right = ttk.Frame(body)
        right.pack(side="left", fill="both", expand=True, padx=(16, 0))

        # 日志卡片（终端风格）
        log_card = ttk.Frame(right, style="Card.TFrame")
        log_card.pack(fill="both", expand=True)
        log_title = ttk.Frame(log_card, style="LogTitle.TFrame")
        log_title.pack(fill="x")
        ttk.Label(log_title, text="同步日志", style="LogTitle.TLabel").pack(
            side="left", padx=12, pady=6)

        log_body = tk.Frame(log_card, bg=COLOR_LOG_BG)
        log_body.pack(fill="both", expand=True)
        self.log_text = tk.Text(log_body, wrap="word", state="disabled", bg=COLOR_LOG_BG,
                                fg=COLOR_LOG_FG, insertbackground=COLOR_LOG_FG, relief="flat",
                                padx=12, pady=10, font=(FONT_MONO, 10), spacing1=1, spacing3=1)
        scrollbar = ttk.Scrollbar(log_body, command=self.log_text.yview,
                                  style="Vertical.TScrollbar")
        self.log_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.log_text.pack(side="left", fill="both", expand=True)

        # 日志着色标签
        self.log_text.tag_configure("plain", foreground=COLOR_LOG_FG)
        self.log_text.tag_configure("cmd", foreground="#4dd0b1")
        self.log_text.tag_configure("error", foreground="#ff6b6b")
        self.log_text.tag_configure("warn", foreground="#ffca6b")
        self.log_text.tag_configure("success", foreground="#69f0ae")
        self.log_text.tag_configure("info", foreground="#a5d6a7")
        self.log_text.tag_configure("sep", foreground="#66bb6a")

    # ------------------------------------------------------------------ #
    # 事件处理
    # ------------------------------------------------------------------ #
    def _choose_dir(self):
        """弹出目录选择框"""
        initial = self.dir_var.get() or os.getcwd()
        chosen = filedialog.askdirectory(title="选择本地 Git 仓库目录", initialdir=initial)
        if chosen:
            self.dir_var.set(chosen)

    def _on_sync_clicked(self):
        """点击同步按钮"""
        if self.is_running:
            messagebox.showinfo("提示", "正在同步中，请稍候...")
            return

        url = self.url_var.get().strip()
        local_dir = self.dir_var.get().strip()
        local_branch = self.local_branch_var.get().strip()
        target_branch = self.target_branch_var.get().strip()

        # 基本校验
        if not url:
            messagebox.showwarning("输入有误", "请填写目标 Git 地址。")
            return
        if not local_dir:
            messagebox.showwarning("输入有误", "请填写本地 Git 仓库目录。")
            return
        if not os.path.isdir(local_dir):
            messagebox.showerror("目录不存在", f"本地目录不存在：\n{local_dir}")
            return

        # 确认强制推送风险
        if self.force_var.get():
            if not messagebox.askyesno(
                "确认强制推送",
                "强制推送 (--force) 会覆盖目标仓库中冲突的分支内容，可能导致目标端数据丢失。\n\n确定继续吗？",
            ):
                return

        self._clear_log()
        self._set_running(True)

        # 在后台线程执行，避免界面卡死
        worker = threading.Thread(
            target=self._sync_worker,
            args=(url, local_dir, self.force_var.get(), self.tags_var.get(),
                  local_branch, target_branch),
            daemon=True,
        )
        worker.start()

    # ------------------------------------------------------------------ #
    # 后台同步逻辑
    # ------------------------------------------------------------------ #
    def _sync_worker(self, url: str, local_dir: str, force: bool, sync_tags: bool,
                     local_branch: str = "", target_branch: str = ""):
        try:
            self._log("=" * 60)
            self._log("开始同步...")
            self._log(f"目标 Git 地址 : {url}")
            self._log(f"本地仓库目录 : {local_dir}")
            self._log(f"本地分支     : {local_branch or '(未指定)'}")
            self._log(f"目标分支     : {target_branch or '(未指定)'}")
            self._log(f"强制推送     : {'是' if force else '否'}")
            self._log(f"同步标签     : {'是' if sync_tags else '否'}")
            self._log("=" * 60)

            # 0. 检查 git 是否可用
            if shutil.which("git") is None:
                self._log("[错误] 未检测到 git 命令，请先安装 Git 并配置到系统 PATH。")
                self._finish(False)
                return

            # 1. 校验是否为 git 仓库
            ok, out = self._run_git(["rev-parse", "--is-inside-work-tree"], local_dir)
            if not ok or out.strip() != "true":
                self._log(f"[错误] 该目录不是有效的 Git 仓库：\n{out}")
                self._finish(False)
                return

            # 2. 记录同步前的 remote 配置与本地分支（用于同步后核对“保持原样”）
            self._log("\n[信息] 同步前的远程仓库配置 (git remote -v)：")
            _, remotes_before = self._run_git(["remote", "-v"], local_dir)
            self._log(remotes_before.strip() or "  (无远程仓库配置)")

            self._log("\n[信息] 本地分支列表 (git branch)：")
            _, branches_before = self._run_git(["branch"], local_dir)
            self._log(branches_before.strip() or "  (无本地分支)")

            # 3. 推送到目标 URL
            #    统一采用“直接推送到 URL”的方式（git push <url> ...），
            #    不会新增/修改本地 remote 配置，也不会改动本地分支。
            if not local_branch and not target_branch:
                # 两个分支都留空：推送所有本地分支（原逻辑）
                self._log("\n[步骤] 未指定分支，正在推送所有分支到目标地址 ...")
                push_cmd = ["push", url, "--all"]
                push_desc = "所有本地分支"
            else:
                # 指定分支：源分支留空则用当前分支 HEAD，目标分支留空则与源同名
                src = local_branch if local_branch else "HEAD"
                dst = target_branch if target_branch else local_branch
                src_desc = local_branch if local_branch else "当前分支(HEAD)"
                self._log(f"\n[步骤] 正在推送分支：{src_desc} -> 目标分支 {dst} ...")
                push_cmd = ["push", url, f"{src}:refs/heads/{dst}"]
                push_desc = f"{src_desc} → 目标分支 {dst}"
            if force:
                push_cmd.append("--force")
            ok, out = self._run_git(push_cmd, local_dir, stream=True)
            if not ok:
                self._log("\n[错误] 分支推送失败，请检查上方输出（常见原因：地址错误、无权限、需要认证、分支不存在或存在冲突）。")
                self._finish(False)
                return

            # 4. 可选：同步标签
            tag_result = "未同步"
            if sync_tags:
                self._log("\n[步骤] 正在推送标签 (--tags) ...")
                tag_cmd = ["push", url, "--tags"]
                if force:
                    tag_cmd.append("--force")
                ok, out = self._run_git(tag_cmd, local_dir, stream=True)
                if not ok:
                    tag_result = "推送失败（分支已成功）"
                    self._log("\n[警告] 标签推送失败，但分支已推送完成。")
                else:
                    tag_result = "已同步"

            # 5. 核对本地 remote 与分支是否保持原样
            self._log("\n[核对] 同步后的远程仓库配置 (git remote -v)：")
            _, remotes_after = self._run_git(["remote", "-v"], local_dir)
            self._log(remotes_after.strip() or "  (无远程仓库配置)")

            self._log("\n[核对] 同步后的本地分支列表 (git branch)：")
            _, branches_after = self._run_git(["branch"], local_dir)
            self._log(branches_after.strip() or "  (无本地分支)")

            if remotes_before == remotes_after and branches_before == branches_after:
                self._log("\n[成功] 同步完成，明细如下：")
                self._log(f"        推送内容 ： {push_desc}")
                self._log(f"        目标地址 ： {url}")
                self._log(f"        强制推送 ： {'是' if force else '否'}")
                self._log(f"        标签同步 ： {tag_result}")
                self._log("        本地仓库 ： 远程配置与分支保持原样未变")
                summary = (
                    "同步已完成！\n\n"
                    f"推送内容：{push_desc}\n"
                    f"目标地址：{url}\n"
                    f"强制推送：{'是' if force else '否'}\n"
                    f"标签同步：{tag_result}\n"
                    "本地仓库：远程配置与分支保持原样未变"
                )
                self._finish(True, summary)
            else:
                self._log("\n[完成] 同步已执行，但检测到本地 remote/分支与同步前存在差异，请人工核对上方输出。")
                self._log(f"        推送内容 ： {push_desc}")
                self._log(f"        目标地址 ： {url}")
                self._log(f"        标签同步 ： {tag_result}")
                summary = (
                    "同步已执行，但检测到本地仓库状态与同步前存在差异。\n\n"
                    f"推送内容：{push_desc}\n"
                    f"目标地址：{url}\n"
                    f"标签同步：{tag_result}\n\n"
                    "请核对日志中 remote / 分支的前后变化。"
                )
                self._finish(True, summary)

        except Exception as exc:  # 兜底异常处理
            self._log(f"\n[异常] 同步过程中发生未预期的错误：{exc}")
            self._finish(False)

    def _run_git(self, args, cwd, stream=False):
        """
        执行 git 命令。

        :param args: git 子命令及参数（不含开头的 'git'）
        :param cwd: 工作目录
        :param stream: 是否实时把输出写入日志
        :return: (是否成功, 输出文本)
        """
        cmd = ["git"] + args
        self._log(f"$ {' '.join(cmd)}")

        env = os.environ.copy()
        # 让 git 输出不带颜色，便于解析与显示
        env["GIT_PAGER"] = "cat"
        env["LC_ALL"] = "C.UTF-8" if os.name != "nt" else env.get("LC_ALL", "")

        try:
            proc = subprocess.Popen(
                cmd,
                cwd=cwd,
                stdin=subprocess.DEVNULL,  # 避免命令等待终端输入而卡死
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
                env=env,
            )
        except FileNotFoundError:
            return False, "未找到 git 可执行文件。"

        output_lines = []
        if proc.stdout is not None:
            for line in proc.stdout:
                if stream:
                    self._log(line.rstrip("\n"))
                output_lines.append(line)
        proc.wait()
        output = "".join(output_lines)
        return proc.returncode == 0, output

    # ------------------------------------------------------------------ #
    # 界面状态与日志（线程安全）
    # ------------------------------------------------------------------ #
    def _finish(self, success: bool, summary: str = ""):
        """工作线程结束时调用，通知主线程恢复界面状态并回传结果摘要"""
        self.log_queue.put(("finish", (success, summary)))

    def _log(self, message: str):
        """线程安全地写日志（放入队列由主线程刷新）"""
        self.log_queue.put(("log", message))

    def _process_log_queue(self):
        """主线程定时消费日志队列，更新界面"""
        try:
            while True:
                kind, payload = self.log_queue.get_nowait()
                if kind == "log":
                    self._append_log(payload)
                elif kind == "finish":
                    self._set_running(False)
                    success, summary = payload
                    if success:
                        self.status_var.set("同步完成")
                        self._append_log("\n===== 同步结束 =====")
                        messagebox.showinfo("同步完成", summary or "同步已完成，详情见日志输出。")
                    else:
                        self.status_var.set("同步失败")
                        self._append_log("\n===== 同步失败 =====")
                        messagebox.showerror("同步失败", summary or "同步未成功，请查看日志输出排查原因。")
        except queue.Empty:
            pass
        # 继续轮询
        self.root.after(100, self._process_log_queue)

    def _log_tag_for(self, message: str) -> str:
        """根据日志内容判断着色标签"""
        m = message.strip()
        if not m:
            return "plain"
        if m.startswith("$ "):
            return "cmd"
        if m.startswith("[错误]") or m.startswith("[异常]"):
            return "error"
        if m.startswith("[警告]"):
            return "warn"
        if m.startswith("[成功]") or m.startswith("[完成]"):
            return "success"
        if m.startswith("[信息]") or m.startswith("[步骤]") or m.startswith("[核对]"):
            return "info"
        if set(m) <= set("=") or m.startswith("====="):
            return "sep"
        return "plain"

    def _append_log(self, message: str):
        tag = self._log_tag_for(message)
        self.log_text.configure(state="normal")
        self.log_text.insert("end", message + "\n", tag)
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _clear_log(self):
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")

    def _set_running(self, running: bool):
        """切换运行状态：禁用/启用按钮，启停进度条"""
        self.is_running = running
        state = "disabled" if running else "normal"
        self.sync_btn.configure(state=state)
        self.browse_btn.configure(state=state)
        self.clear_btn.configure(state=state)
        self.url_entry.configure(state=state)
        self.dir_entry.configure(state=state)
        self.local_branch_entry.configure(state=state)
        self.target_branch_entry.configure(state=state)
        if running:
            self.status_var.set("正在同步...")
            self.progress.start(12)
        else:
            self.progress.stop()


def main():
    root = tk.Tk()
    GitSyncApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
