import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path

class Domain:
    def __init__(self, name="", login="", password="", hosts=None):
        self.name = name
        self.login = login
        self.password = password
        self.hosts = hosts if hosts is not None else []

    def __repr__(self):
        return f"Domain(name={self.name}, login={self.login}, password={self.password}, hosts={self.hosts})"


class Configurator:
    def __init__(self):
        self.daemon = None
        self.ssl = None
        self.use = None
        self.web = None
        self.protocol = None
        self.server = None
        self.domains = []

    def __repr__(self):
        return (f"Configurator(daemon={self.daemon}, ssl={self.ssl}, use={self.use}, "
                f"web={self.web}, protocol={self.protocol}, server={self.server}, "
                f"domains={self.domains})")


def find_config_file():
    possible_paths = [
        "/etc/ddclient.conf",
        str(Path.home() / "ddclient.conf"),
        str(Path.home() / ".ddclient.conf"),
    ]

    for p in possible_paths:
        if os.path.exists(p):
            return p

    raise FileNotFoundError("ddclient.conf not found in expected locations.")


def parse_ddclient_config(filepath):
    config = Configurator()
    current_domain = None
    domain_section_started = False

    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            # Check for domain block start
            if line.startswith('#') and 'Domain' in line:
                # If there was a previous domain block, push it to config
                if current_domain:
                    config.domains.append(current_domain)

                # Extract domain name from comment line, e.g. "# First Domain"
                domain_name = line.lstrip('#').strip()
                current_domain = Domain(name=domain_name)
                domain_section_started = True
                continue

            if domain_section_started:
                # We are inside a domain block
                if line.startswith('login='):
                    current_domain.login = line.split('=', 1)[1].strip()
                elif line.startswith('password='):
                    current_domain.password = line.split('=', 1)[1].strip()
                elif ',' in line:
                    # This should be the line with host entries
                    hosts = [h.strip() for h in line.split(',')]
                    current_domain.hosts.extend(hosts)
            else:
                # Global parameter line
                if '=' in line:
                    key, val = line.split('=', 1)
                    key = key.strip()
                    val = val.strip()
                    if key == 'daemon':
                        config.daemon = val
                    elif key == 'ssl':
                        config.ssl = val
                    elif key == 'use':
                        config.use = val
                    elif key == 'web':
                        config.web = val
                    elif key == 'protocol':
                        config.protocol = val
                    elif key == 'server':
                        config.server = val

    # After loop ends, if there's a domain in progress, add it
    if current_domain:
        config.domains.append(current_domain)

    return config


def write_ddclient_config(config, filepath):
    lines = []

    # Global config
    if config.daemon is not None:
        lines.append(f"daemon={config.daemon}")
    if config.ssl is not None:
        lines.append(f"ssl={config.ssl}")
    if config.use is not None:
        lines.append(f"use={config.use}")
    if config.web is not None:
        lines.append(f"web={config.web}")
    if config.protocol is not None:
        lines.append(f"protocol={config.protocol}")
    if config.server is not None:
        lines.append(f"server={config.server}")

    lines.append("")  # blank line before domains

    # Domains
    for domain in config.domains:
        lines.append(f"# {domain.name}")
        lines.append(f"login={domain.login}")
        lines.append(f"password={domain.password}")
        lines.append(", ".join(domain.hosts))
        lines.append("")  # blank line after each domain block

    with open(filepath, 'w') as f:
        for line in lines:
            f.write(line.rstrip() + "\n")


class DomainDialog(tk.Toplevel):
    def __init__(self, parent, title="Edit Domain", domain=None):
        super().__init__(parent)
        self.title(title)
        self.parent = parent
        self.domain = domain if domain else Domain()
        self.result = None

        # Make the second column expandable
        self.grid_columnconfigure(1, weight=1)

        # Wider entries
        entry_width = 60

        tk.Label(self, text="Domain Name:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.name_entry = tk.Entry(self, width=entry_width)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        tk.Label(self, text="Login:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.login_entry = tk.Entry(self, width=entry_width)
        self.login_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')

        tk.Label(self, text="Password:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.password_entry = tk.Entry(self, width=entry_width)
        self.password_entry.grid(row=2, column=1, padx=5, pady=5, sticky='ew')

        tk.Label(self, text="Hosts (comma-separated):").grid(row=3, column=0, padx=5, pady=5, sticky='e')
        self.hosts_entry = tk.Entry(self, width=entry_width)
        self.hosts_entry.grid(row=3, column=1, padx=5, pady=5, sticky='ew')

        # Pre-fill data if editing
        self.name_entry.insert(0, self.domain.name)
        self.login_entry.insert(0, self.domain.login)
        self.password_entry.insert(0, self.domain.password)
        self.hosts_entry.insert(0, ", ".join(self.domain.hosts))

        btn_frame = tk.Frame(self)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=10)

        ok_btn = tk.Button(btn_frame, text="OK", command=self.on_ok)
        ok_btn.pack(side='left', padx=5)

        cancel_btn = tk.Button(btn_frame, text="Cancel", command=self.on_cancel)
        cancel_btn.pack(side='left', padx=5)

        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)
        self.transient(parent)
        self.wait_window(self)

    def on_ok(self):
        name = self.name_entry.get().strip()
        login = self.login_entry.get().strip()
        password = self.password_entry.get().strip()
        hosts_str = self.hosts_entry.get().strip()
        hosts = [h.strip() for h in hosts_str.split(',') if h.strip()]

        if not name:
            messagebox.showerror("Error", "Domain Name is required.")
            return

        self.domain = Domain(name=name, login=login, password=password, hosts=hosts)
        self.result = self.domain
        self.destroy()

    def on_cancel(self):
        self.result = None
        self.destroy()


class ConfigGUI:
    def __init__(self, root, initial_config, initial_path):
        self.root = root
        self.config = initial_config
        self.filepath = initial_path if initial_path else ""
        self.root.title("DDClient Configuration Editor")

        self._create_menu()

        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill='both', expand=True)

        # Build UI
        self._build_ui()

    def _create_menu(self):
        menubar = tk.Menu(self.root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open...", command=self._open_config_file)
        filemenu.add_command(label="Export...", command=self._export_config_file)
        menubar.add_cascade(label="File", menu=filemenu)
        self.root.config(menu=menubar)

    def _build_ui(self):
        # Clear anything if rebuild
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Global config
        global_frame = tk.LabelFrame(self.main_frame, text="Global Configuration")
        global_frame.pack(fill='x', padx=5, pady=5)
        self.global_entries = self._add_global_config(global_frame)

        # Domain table
        domain_frame = tk.LabelFrame(self.main_frame, text="Domains")
        domain_frame.pack(fill='both', expand=True, padx=5, pady=5)

        self.tree = ttk.Treeview(domain_frame, columns=("Name", "Login", "Password", "Hosts"), show='headings')
        self.tree.heading("Name", text="Name")
        self.tree.heading("Login", text="Login")
        self.tree.heading("Password", text="Password")
        self.tree.heading("Hosts", text="Hosts")

        self.tree.pack(fill='both', expand=True, side='left')

        # Insert initial domains
        for d in self.config.domains:
            self.tree.insert("", "end", values=(d.name, d.login, d.password, ", ".join(d.hosts)))

        # Scrollbar
        sb = ttk.Scrollbar(domain_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=sb.set)
        sb.pack(side='right', fill='y')

        # Buttons for domain operations
        btn_frame = tk.Frame(self.main_frame)
        btn_frame.pack(fill='x', pady=5)

        add_btn = tk.Button(btn_frame, text="Add Domain", command=self.add_domain)
        add_btn.pack(side='left', padx=5)

        edit_btn = tk.Button(btn_frame, text="Edit Selected", command=self.edit_domain)
        edit_btn.pack(side='left', padx=5)

        del_btn = tk.Button(btn_frame, text="Delete Selected", command=self.delete_domain)
        del_btn.pack(side='left', padx=5)

        # Save button at the bottom
        save_btn = tk.Button(self.main_frame, text="Save", command=self.save_config)
        save_btn.pack(side='bottom', pady=10)

    def _add_global_config(self, frame):
        # Wider entries
        entry_width = 40
        fields = [
            ("daemon", self.config.daemon),
            ("ssl", self.config.ssl),
            ("use", self.config.use),
            ("web", self.config.web),
            ("protocol", self.config.protocol),
            ("server", self.config.server),
        ]

        entries = {}
        for i, (key, val) in enumerate(fields):
            tk.Label(frame, text=key, font=('Arial', 10, 'bold')).grid(row=i, column=0, sticky='e', padx=5, pady=2)
            e = tk.Entry(frame, width=entry_width)
            e.insert(0, val if val is not None else "")
            e.grid(row=i, column=1, sticky='w', padx=5, pady=2)
            entries[key] = e

        return entries

    def add_domain(self):
        dlg = DomainDialog(self.root, title="Add Domain")
        if dlg.result:
            d = dlg.result
            self.tree.insert("", "end", values=(d.name, d.login, d.password, ", ".join(d.hosts)))

    def get_selected_domain(self):
        selection = self.tree.selection()
        if not selection:
            return None
        item = self.tree.item(selection[0], 'values')
        # item is tuple: (Name, Login, Password, Hosts)
        name, login, password, hosts_str = item
        hosts = [h.strip() for h in hosts_str.split(',') if h.strip()]
        return (selection[0], Domain(name=name, login=login, password=password, hosts=hosts))

    def edit_domain(self):
        selected = self.get_selected_domain()
        if not selected:
            messagebox.showwarning("Edit Domain", "No domain selected.")
            return
        item_id, domain = selected
        dlg = DomainDialog(self.root, title="Edit Domain", domain=domain)
        if dlg.result:
            d = dlg.result
            self.tree.item(item_id, values=(d.name, d.login, d.password, ", ".join(d.hosts)))

    def delete_domain(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Delete Domain", "No domain selected.")
            return
        for sel in selection:
            self.tree.delete(sel)

    def save_config(self):
        # Update global config
        self._update_config_from_fields()

        try:
            write_ddclient_config(self.config, self.filepath)
            messagebox.showinfo("Success", f"Configuration saved to {self.filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration:\n{e}")

    def _open_config_file(self):
        # Prompt user for a file path
        new_path = filedialog.askopenfilename(
            title="Open ddclient.conf",
            filetypes=[("ddclient config", "ddclient.conf"), ("All files", "*.*")]
        )
        if new_path:
            self._load_config(new_path)

    def _load_config(self, path):
        try:
            new_config = parse_ddclient_config(path)
            self.config = new_config
            self.filepath = path
            # Rebuild UI with new config
            self._build_ui()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load configuration:\n{e}")

    def _update_config_from_fields(self):
        self.config.daemon = self.global_entries['daemon'].get().strip() or None
        self.config.ssl = self.global_entries['ssl'].get().strip() or None
        self.config.use = self.global_entries['use'].get().strip() or None
        self.config.web = self.global_entries['web'].get().strip() or None
        self.config.protocol = self.global_entries['protocol'].get().strip() or None
        self.config.server = self.global_entries['server'].get().strip() or None

        domains = []
        for line in self.tree.get_children():
            vals = self.tree.item(line, 'values')
            name, login, password, hosts_str = vals
            hosts = [h.strip() for h in hosts_str.split(',') if h.strip()]
            domains.append(Domain(name=name, login=login, password=password, hosts=hosts))

        self.config.domains = domains

    def _export_config_file(self):
        # Prompt user for a file path to save the current config
        save_path = filedialog.asksaveasfilename(
            title="Export ddclient.conf",
            defaultextension=".conf",
            filetypes=[("ddclient config", "*.conf"), ("All files", "*.*")]
        )
        if save_path:
            # Update config from current UI values
            self._update_config_from_fields()
            try:
                write_ddclient_config(self.config, save_path)
                messagebox.showinfo("Success", f"Configuration exported to {save_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export configuration:\n{e}")

def main():
    # Find and parse config
    try:
        config_path = find_config_file()
    except FileNotFoundError as e:
        # If not found, we won't exit here, just start with a blank config
        print(e)
        config_path = None

    config = None
    if config_path and os.path.exists(config_path):
        config = parse_ddclient_config(config_path)
    else:
        # Start with empty config if not found
        config = Configurator()

    # Start GUI
    root = tk.Tk()
    app = ConfigGUI(root, config, config_path if config_path else "")
    root.mainloop()


if __name__ == "__main__":
    main()