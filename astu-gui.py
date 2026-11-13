#!/usr/bin/env python3
"""
ASTU GUI — Advanced Security Tool Utility, graphical version.
Python 3 + Tkinter only (no extra dependencies).

Run:
    python3 astu-gui.py
    # or, after install:
    astu-gui

The GUI is a front-end for the `astu` CLI script. It finds `astu`
in PATH, /usr/local/bin/astu, or ./astu next to this file, and runs
the same commands, showing output in the pane below.

EDUCATIONAL / AUTHORIZED USE ONLY.
Only run this on networks and systems you own or have explicit
permission to test. Privileged actions need sudo / root — run the
GUI with `sudo python3 astu-gui.py` for those, or they will fail
with a root error, just like the CLI.
"""

import os
import shutil
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk

VERSION = "2.0.0"
APP_TITLE = f"ASTU — Advanced Security Tool Utility v{VERSION}"


def find_astu() -> str | None:
    """Return the path to the astu CLI, if found."""
    for candidate in (
        shutil.which("astu"),
        "/usr/local/bin/astu",
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "astu"),
        "./astu",
    ):
        if candidate and os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate
    return shutil.which("astu")


class ASTUGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("980x720")
        self.root.minsize(760, 540)

        self.astu = find_astu()
        self.proc: subprocess.Popen | None = None
        self.is_root = os.geteuid() == 0 if hasattr(os, "geteuid") else False

        self._build_ui()
        self._show_welcome()
        if not self.is_root:
            self.append_output(
                "Note: you are not running as root. Privileged actions "
                "(on/off, monitor, scans, arpspoof, etc.) will ask you "
                "to use sudo. Run with `sudo python3 astu-gui.py` for those.\n"
            )
        # Disclaimer on first start — informational, not blocking.
        self.root.after(
            300,
            lambda: messagebox.showinfo(
                "Authorized use only",
                "ASTU is for educational and security research on networks "
                "and systems you own or have explicit permission to test.\n\n"
                "Do not use the attack / sniffing tools on other people's networks.",
            ),
        )

    # ---------- UI ----------
    def _build_ui(self):
        top = ttk.Frame(self.root, padding=10)
        top.pack(fill=tk.X)

        ttk.Label(
            top,
            text="ASTU",
            font=("TkDefaultFont", 20, "bold"),
        ).pack(side=tk.LEFT)
        ttk.Label(
            top,
            text="  Advanced Security Tool Utility  •  Educational / authorized use only",
        ).pack(side=tk.LEFT, pady=(8, 0))

        status = "Running as root" if self.is_root else "Not root — some actions need sudo"
        astu_path = self.astu or "astu CLI not found in PATH"
        ttk.Label(top, text=f"{status}  •  {astu_path}", foreground="gray").pack(
            side=tk.RIGHT, pady=(8, 0)
        )

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self.tabs = {}
        for name in ("Networking", "Recon", "System", "Scans", "Advanced"):
            frame = ttk.Frame(notebook, padding=10)
            notebook.add(frame, text=name)
            self.tabs[name] = frame

        self._build_networking(self.tabs["Networking"])
        self._build_recon(self.tabs["Recon"])
        self._build_system(self.tabs["System"])
        self._build_scans(self.tabs["Scans"])
        self._build_advanced(self.tabs["Advanced"])

        # Output pane
        out_frame = ttk.LabelFrame(self.root, text="Output", padding=8)
        out_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self.output = scrolledtext.ScrolledText(
            out_frame, height=14, font=("TkFixedFont", 10), wrap=tk.WORD
        )
        self.output.pack(fill=tk.BOTH, expand=True)

        btn_row = ttk.Frame(out_frame)
        btn_row.pack(fill=tk.X, pady=(8, 0))
        ttk.Button(btn_row, text="Stop current command", command=self.stop_command).pack(side=tk.LEFT)
        ttk.Button(btn_row, text="Clear output", command=lambda: self.output.delete("1.0", tk.END)).pack(side=tk.LEFT, padx=6)
        ttk.Button(btn_row, text="Check dependencies", command=lambda: self.run_astu(["check"])).pack(side=tk.LEFT)
        ttk.Button(btn_row, text="Help", command=lambda: self.run_astu(["help"])).pack(side=tk.LEFT, padx=6)

        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(self.root, textvariable=self.status_var, padding=(10, 0, 10, 8)).pack(fill=tk.X)

    def _section(self, parent, title):
        frame = ttk.LabelFrame(parent, text=title, padding=8)
        frame.pack(fill=tk.X, pady=5)
        return frame

    def _btn(self, parent, label, args, row=0, col=0, **kw):
        b = ttk.Button(parent, text=label, command=lambda a=args: self.run_astu(a))
        b.grid(row=row, column=col, padx=4, pady=4, sticky="ew", **kw)
        return b

    def _entry_row(self, parent, label, default="", show=None, width=24):
        row = ttk.Frame(parent)
        row.pack(fill=tk.X, pady=3)
        ttk.Label(row, text=label, width=16).pack(side=tk.LEFT)
        var = tk.StringVar(value=default)
        entry = ttk.Entry(row, textvariable=var, width=width, show=show or "")
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        return var

    # ---------- Tabs ----------
    def _build_networking(self, parent):
        f = self._section(parent, "Wi-Fi")
        for i, (label, cmd) in enumerate(
            [("Wi-Fi On", ["on"]), ("Wi-Fi Off", ["off"]), ("Status", ["status"]),
             ("Interfaces", ["interfaces"]), ("Devices", ["devices"]), ("Scan networks", ["scan"])]
        ):
            self._btn(f, label, cmd, row=i // 3, col=i % 3)
        for c in range(3):
            f.columnconfigure(c, weight=1)

        f2 = self._section(parent, "Connect")
        self.ssid_var = self._entry_row(f2, "SSID:")
        self.pw_var = self._entry_row(f2, "Password:", show="*")
        ttk.Button(
            f2, text="Connect",
            command=lambda: self.run_astu(["connect", self.ssid_var.get(), self.pw_var.get()]),
        ).pack(pady=4)

        f3 = self._section(parent, "Network info")
        for i, (label, cmd) in enumerate(
            [("Local IP", ["ip"]), ("Public IP", ["publicip"]), ("Ping 8.8.8.8", ["ping"]),
             ("Restart NetworkManager", ["restart"]), ("Monitor On", ["monitor-on"]),
             ("Monitor Off", ["monitor-off"])]
        ):
            self._btn(f3, label, cmd, row=i // 3, col=i % 3)
        for c in range(3):
            f3.columnconfigure(c, weight=1)

        f4 = self._section(parent, "Capture")
        self.capture_var = self._entry_row(f4, "Seconds:", default="10")
        ttk.Button(
            f4, text="Capture to capture.pcap",
            command=lambda: self.run_astu(["capture", self.capture_var.get()]),
        ).pack(pady=4)

    def _build_recon(self, parent):
        f = self._section(parent, "Target")
        self.target_var = self._entry_row(f, "IP / domain:")
        self.target_var.set("8.8.8.8")

        f2 = self._section(parent, "Lookups")
        for i, (label, cmd_fn) in enumerate(
            [
                ("DNS Lookup", lambda: ["dnslookup", self.target_var.get()]),
                ("Traceroute", lambda: ["traceroute", self.target_var.get()]),
                ("Port Scan", lambda: ["portscan", self.target_var.get()]),
                ("IP Info", lambda: ["ipinfo", self.target_var.get()]),
                ("Whois", lambda: ["whois", self.target_var.get()]),
                ("Deep Scan", lambda: ["deep-scan", self.target_var.get()]),
            ]
        ):
            b = ttk.Button(f2, text=label, command=lambda fn=cmd_fn: self.run_astu(fn()))
            b.grid(row=i // 3, column=i % 3, padx=4, pady=4, sticky="ew")
        for c in range(3):
            f2.columnconfigure(c, weight=1)

        f3 = self._section(parent, "Discovery")
        ttk.Button(f3, text="Discover LAN devices", command=lambda: self.run_astu(["discover"])).pack(pady=4)

    def _build_system(self, parent):
        f = self._section(parent, "System")
        for i, (label, cmd) in enumerate(
            [("Hidden files", ["hidden"]), ("Suspicious processes", ["suspicious"]),
             ("SSH connections", ["sshcon"]), ("MAC Spoof", ["macspoof"]),
             ("Traffic", ["traffic"]), ("Cron jobs", ["cron"]), ("Tor check", ["tor"])]
        ):
            self._btn(f, label, cmd, row=i // 3, col=i % 3)
        for c in range(3):
            f.columnconfigure(c, weight=1)

        f2 = self._section(parent, "VirusTotal URL scan")
        self.vt_url_var = self._entry_row(f2, "URL:")
        self.vt_key_var = self._entry_row(f2, "API key:", show="*")
        ttk.Label(
            f2,
            text="Note: the CLI version asks for the key interactively. "
            "In the GUI, enter it here — it is not saved.",
            foreground="gray",
        ).pack(pady=2)
        ttk.Button(f2, text="Scan URL (via CLI vturl prompt — use CLI for now)",
                   command=lambda: self.run_astu(["vturl"])).pack(pady=4)

    def _build_scans(self, parent):
        f = self._section(parent, "Target")
        self.scan_target_var = self._entry_row(f, "IP / host:")
        self.scan_target_var.set("127.0.0.1")

        f2 = self._section(parent, "Scans (need root)")
        for label, cmd in [
            ("Fast Scan", "fast-scan"),
            ("Stealth Scan", "stealth-scan"),
            ("Vuln Scan", "vuln-scan"),
        ]:
            ttk.Button(
                f2, text=label,
                command=lambda c=cmd: self.run_astu([c, self.scan_target_var.get()]),
            ).pack(fill=tk.X, pady=4)

    def _build_advanced(self, parent):
        ttk.Label(
            parent,
            text="⚠️  Advanced tools — only on networks you own or are authorized to test.",
            foreground="red",
        ).pack(pady=6)

        f = self._section(parent, "ARP Spoof")
        self.arp_target_var = self._entry_row(f, "Target IP:")
        self.arp_gw_var = self._entry_row(f, "Gateway IP:")
        ttk.Button(
            f, text="Start ARP Spoof (Ctrl+C / Stop to end)",
            command=lambda: self.run_astu(["arpspoof", self.arp_target_var.get(), self.arp_gw_var.get()]),
        ).pack(pady=4)

        f2 = self._section(parent, "Other")
        self.bssid_var = self._entry_row(f2, "BSSID (WPS):")
        ttk.Button(f2, text="WPS Crack", command=lambda: self.run_astu(["wpscrack", self.bssid_var.get()])).pack(pady=4)
        ttk.Button(f2, text="Sniff Traffic (Stop to end)", command=lambda: self.run_astu(["sniff-traffic"])).pack(pady=4)

    # ---------- Running commands ----------
    def _show_welcome(self):
        self.append_output(
            f"{APP_TITLE}\n"
            f"ASTU CLI: {self.astu or 'NOT FOUND — install astu first, or run from the repo folder'}\n"
            "Pick a tab above and click a button. Output appears here.\n"
            "Use 'Stop current command' for long-running captures / spoofing / sniffing.\n\n"
        )

    def append_output(self, text: str):
        self.output.insert(tk.END, text)
        self.output.see(tk.END)

    def run_astu(self, args):
        if not self.astu:
            messagebox.showerror("ASTU not found", "Could not find the `astu` script. Install it first (see install.sh) or run this GUI from the repo folder.")
            return
        if self.proc and self.proc.poll() is None:
            messagebox.showinfo("Busy", "A command is already running. Stop it first.")
            return
        # Basic validation: don't run with empty required args.
        if any(a == "" for a in args):
            messagebox.showwarning("Missing input", "Fill in the required field first.")
            return

        cmd = [self.astu] + [str(a) for a in args]
        self.status_var.set(f"Running: astu {' '.join(args)} …")
        self.append_output(f"\n$ astu {' '.join(args)}\n")
        threading.Thread(target=self._run_thread, args=(cmd,), daemon=True).start()

    def _run_thread(self, cmd):
        try:
            self.proc = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, bufsize=1,
            )
            assert self.proc.stdout is not None
            for line in self.proc.stdout:
                self.root.after(0, self.append_output, line)
            self.proc.wait()
            rc = self.proc.returncode
            self.root.after(0, self.status_var.set, f"Finished (exit {rc})" if rc == 0 else f"Finished with exit code {rc}")
        except FileNotFoundError:
            self.root.after(0, self.append_output, "Error: astu executable not found.\n")
        except Exception as exc:  # noqa: BLE001 — show it in the GUI
            self.root.after(0, self.append_output, f"Error: {exc}\n")
        finally:
            self.proc = None

    def stop_command(self):
        if self.proc and self.proc.poll() is None:
            self.proc.terminate()
            self.append_output("\n[!] Stopped.\n")
            self.status_var.set("Stopped")
        else:
            self.status_var.set("Nothing running")


def main():
    root = tk.Tk()
    try:
        from tkinter import ttk as _ttk  # noqa: F401 — ensure themed widgets load
    except Exception:
        pass
    app = ASTUGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
