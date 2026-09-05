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


class GitSyncApp:
    """Git 分支同步图形界面应用"""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Git 分支同步工具")
        self.root.geometry("760x560")
        self.root.minsize(640, 460)

        # 用于工作线程与主线程之间安全地传递日志/状态
        self.log_queue = queue.Queue()
        self.is_running = False

        self._build_widgets()
        # 定时从队列中取出日志刷新到界面
        self.root.after(100, self._process_log_queue)

    # ------------------------------------------------------------------ #
    # 界面构建
    # ------------------------------------------------------------------ #
    def _build_widgets(self):
        pad = {"padx": 10, "pady": 6}

        # 顶部输入区
        form = ttk.Frame(self.root)
        form.pack(fill="x", **pad)
        form.columnconfigure(1, weight=1)

        # 目标 Git 地址
        ttk.Label(form, text="目标 Git 地址：").grid(row=0, column=0, sticky="e", pady=6)
        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(form, textvariable=self.url_var)
        self.url_entry.grid(row=0, column=1, columnspan=2, sticky="we", pady=6, padx=(0, 6))

        # 本地 Git 仓库目录
        ttk.Label(form, text="本地仓库目录：").grid(row=1, column=0, sticky="e", pady=6)
        self.dir_var = tk.StringVar()
        self.dir_entry = ttk.Entry(form, textvariable=self.dir_var)
        self.dir_entry.grid(row=1, column=1, sticky="we", pady=6)
        self.browse_btn = ttk.Button(form, text="浏览...", command=self._choose_dir)
        self.browse_btn.grid(row=1, column=2, sticky="e", pady=6, padx=(6, 0))

        # 选项区
        opt = ttk.Frame(self.root)
        opt.pack(fill="x", padx=10)
        self.force_var = tk.BooleanVar(value=False)
        self.tags_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            opt, text="强制推送 (--force，覆盖目标端冲突分支)", variable=self.force_var
        ).pack(side="left", padx=(0, 20))
        ttk.Checkbutton(
            opt, text="同时同步标签 (--tags)", variable=self.tags_var
        ).pack(side="left")

        # 操作按钮区
        btns = ttk.Frame(self.root)
        btns.pack(fill="x", **pad)
        self.sync_btn = ttk.Button(btns, text="同步", command=self._on_sync_clicked)
        self.sync_btn.pack(side="left")
        self.clear_btn = ttk.Button(btns, text="清空日志", command=self._clear_log)
        self.clear_btn.pack(side="left", padx=8)

        # 进度条
        self.progress = ttk.Progressbar(self.root, mode="indeterminate")
        self.progress.pack(fill="x", padx=10)

        # 日志输出区
        log_frame = ttk.Frame(self.root)
        log_frame.pack(fill="both", expand=True, padx=10, pady=(6, 4))
        self.log_text = tk.Text(log_frame, wrap="word", state="disabled", height=15)
        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.log_text.pack(side="left", fill="both", expand=True)

        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, anchor="w")
        status_bar.pack(fill="x", side="bottom", padx=10, pady=(0, 6))

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

    def _append_log(self, message: str):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", message + "\n")
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
    # 使用系统原生主题（若可用）
    try:
        style = ttk.Style()
        if "vista" in style.theme_names():
            style.theme_use("vista")
        elif "clam" in style.theme_names():
            style.theme_use("clam")
    except tk.TclError:
        pass
    GitSyncApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
