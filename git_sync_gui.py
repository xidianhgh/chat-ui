# -*- coding: utf-8 -*-
"""
Git 分支同步工具

功能：
    - 界面提供两个输入框：目标 Git 地址、本地 Git 仓库目录
    - 点击“同步”按钮后，把本地仓库的所有分支推送到目标 Git 地址（分支名保持一致）
    - 同步过程采用 `git push <url> --all` 的“直接推送到 URL”方式，
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
        self.root.geometry("820x620")
        self.root.minsize(720, 540)
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
        style.map("TCheckbutton", background=[("active", COLOR_CARD)],
                  indicatorcolor=[("selected", COLOR_ACCENT), ("!selected", "#ffffff")])

        # 进度条
        style.configure("Horizontal.TProgressbar", troughcolor="#dcedc8", background=COLOR_ACCENT,
                        bordercolor=COLOR_BORDER, lightcolor=COLOR_ACCENT, darkcolor=COLOR_ACCENT,
                        thickness=12)

        # 滚动条
        style.configure("Vertical.TScrollbar", troughcolor="#e8f5e9", background="#a5d6a7",
                        bordercolor=COLOR_BG, arrowcolor=COLOR_ACCENT_DK, relief="flat")
        style.map("Vertical.TScrollbar", background=[("active", COLOR_ACCENT)])

    # ------------------------------------------------------------------ #
    # 界面构建
    # ------------------------------------------------------------------ #
    def _build_widgets(self):
        # ---------- 顶部标题横幅 ----------
        header = ttk.Frame(self.root, style="Header.TFrame")
        header.pack(fill="x")
        ttk.Label(header, text="Git 分支同步工具", style="HeaderTitle.TLabel").pack(
            anchor="w", padx=22, pady=(16, 2))
        ttk.Label(header, text="把本地仓库的所有分支同步到目标 Git 地址，且不改动本地远程配置与分支",
                  style="HeaderSub.TLabel").pack(anchor="w", padx=22, pady=(0, 16))

        # ---------- 主体区域 ----------
        body = ttk.Frame(self.root)
        body.pack(fill="both", expand=True, padx=18, pady=16)

        # 卡片一：仓库配置
        card1 = ttk.Frame(body, style="Card.TFrame", padding=18)
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

        # 卡片二：同步选项
        card2 = ttk.Frame(body, style="Card.TFrame", padding=18)
        card2.pack(fill="x", pady=(14, 0))
        ttk.Label(card2, text="同步选项", style="CardTitle.TLabel").pack(anchor="w", pady=(0, 8))
        self.force_var = tk.BooleanVar(value=False)
        self.tags_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            card2, text="强制推送 (--force)：覆盖目标端冲突分支，可能导致目标端数据丢失",
            variable=self.force_var).pack(anchor="w", pady=2)
        ttk.Checkbutton(
            card2, text="同时同步标签 (--tags)", variable=self.tags_var).pack(anchor="w", pady=2)

        # 操作区：按钮 + 状态
        action = ttk.Frame(body)
        action.pack(fill="x", pady=(16, 10))
        self.sync_btn = ttk.Button(action, text="同 步", style="Accent.TButton",
                                   command=self._on_sync_clicked)
        self.sync_btn.pack(side="left")
        self.clear_btn = ttk.Button(action, text="清空日志", command=self._clear_log)
        self.clear_btn.pack(side="left", padx=(10, 0))
        self.status_var = tk.StringVar(value="就绪")
        ttk.Label(action, textvariable=self.status_var, style="Status.TLabel").pack(side="right")

        # 进度条
        self.progress = ttk.Progressbar(body, mode="indeterminate",
                                        style="Horizontal.TProgressbar")
        self.progress.pack(fill="x", pady=(0, 12))

        # 日志卡片（终端风格）
        log_card = ttk.Frame(body, style="Card.TFrame")
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
            args=(url, local_dir, self.force_var.get(), self.tags_var.get()),
            daemon=True,
        )
        worker.start()

    # ------------------------------------------------------------------ #
    # 后台同步逻辑
    # ------------------------------------------------------------------ #
    def _sync_worker(self, url: str, local_dir: str, force: bool, sync_tags: bool):
        try:
            self._log("=" * 60)
            self._log("开始同步...")
            self._log(f"目标 Git 地址 : {url}")
            self._log(f"本地仓库目录 : {local_dir}")
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

            # 3. 推送所有本地分支到目标 URL
            #    使用 `git push <url> --all` 直接推送到 URL，
            #    不会新增/修改 remote，也不会改动本地分支。
            self._log("\n[步骤] 正在推送所有分支到目标地址 ...")
            push_cmd = ["push", url, "--all"]
            if force:
                push_cmd.append("--force")
            ok, out = self._run_git(push_cmd, local_dir, stream=True)
            if not ok:
                self._log("\n[错误] 分支推送失败，请检查上方输出（常见原因：地址错误、无权限、需要认证或存在冲突）。")
                self._finish(False)
                return

            # 4. 可选：同步标签
            if sync_tags:
                self._log("\n[步骤] 正在推送标签 (--tags) ...")
                tag_cmd = ["push", url, "--tags"]
                if force:
                    tag_cmd.append("--force")
                ok, out = self._run_git(tag_cmd, local_dir, stream=True)
                if not ok:
                    self._log("\n[警告] 标签推送失败，但分支已推送完成。")

            # 5. 核对本地 remote 与分支是否保持原样
            self._log("\n[核对] 同步后的远程仓库配置 (git remote -v)：")
            _, remotes_after = self._run_git(["remote", "-v"], local_dir)
            self._log(remotes_after.strip() or "  (无远程仓库配置)")

            self._log("\n[核对] 同步后的本地分支列表 (git branch)：")
            _, branches_after = self._run_git(["branch"], local_dir)
            self._log(branches_after.strip() or "  (无本地分支)")

            if remotes_before == remotes_after and branches_before == branches_after:
                self._log("\n[成功] 所有分支已同步到目标地址，且本地远程配置与分支保持原样未变。")
                self._finish(True)
            else:
                self._log("\n[完成] 同步已执行，但检测到本地 remote/分支与同步前存在差异，请人工核对上方输出。")
                self._finish(True)

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
    def _finish(self, success: bool):
        """工作线程结束时调用，通知主线程恢复界面状态"""
        self.log_queue.put(("finish", success))

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
                    if payload:
                        self.status_var.set("同步完成")
                        self._append_log("\n===== 同步结束 =====")
                        messagebox.showinfo("完成", "同步已完成，详情见日志输出。")
                    else:
                        self.status_var.set("同步失败")
                        self._append_log("\n===== 同步失败 =====")
                        messagebox.showerror("失败", "同步未成功，请查看日志输出排查原因。")
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
