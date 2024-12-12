# DDClient-GUI

DDClient-GUI is a graphical configuration editor for the `ddclient` tool, which is widely used for managing Dynamic DNS (DDNS) updates. This project provides an intuitive GUI for creating, editing, and exporting `ddclient.conf` files, making it easier to manage DDNS configurations.

---

## Features

- **Global Configuration Management**: Set global parameters like `daemon`, `ssl`, `use`, `protocol`, and more.
- **Domain Management**: Add, edit, and delete domain-specific configurations with a user-friendly dialog interface.
- **Real-Time Configuration Preview**: View and modify your configuration in an organized tree view.
- **Export Functionality**: Save your updated configurations to a new file easily.
- **Cross-Platform Compatibility**: Works on Windows, macOS, and Linux.

---

## Screenshots

### 1. Main Configuration Screen
![Main Configuration Screen](DNS-images/1.png)

### 2. Domain Editing Dialog
![Domain Editing Dialog](DNS-images/2.png)

---

## Installation

### Prerequisites

- Python 3.1+
- Tkinter (should be included with Python installations)
- `ddclient` tool installed (optional for configuration testing).

### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/arminkardovic/ddclient-gui.git
   cd ddclient-gui
