# MIRCI AI PP TOOLS - Installation & Launch Guide

Welcome to **MIRCI AI PP TOOLS**! This repository provides AI-powered post-production tools to enhance your workflow. Follow the steps below to set up and launch the application.

## 🚀 Quick Start Guide

### Prerequisites
Ensure you have the following installed on your system:
- **Git**: [Download Git](https://git-scm.com/downloads)
- **Windows OS** (for `.bat` execution)

### 📥 Installation & Setup
1. **Clone the Repository**  
   Download the repository by running the following command in **Command Prompt** (CMD):
   ```sh
   git clone https://github.com/sam4muzix/MIRCI_AI_PP_TOOLS.git
   ```
   
2. **Run the Setup Script**  
   Navigate to the cloned folder and execute:
   ```sh
   cd MIRCI_AI_PP_TOOLS
   setup_env.bat
   ```

3. **Launch the Web UI**  
   After setup completes, start the application:
   ```sh
   launch_webui.bat
   ```

### 🔄 Automate the Process (Optional)
For a **one-click** installation and launch, use `run_mirci.bat`:
1. Download and place the following script in the same directory:
   ```bat
   @echo off
   cd /d %~dp0
   echo Cloning the repository...
   git clone https://github.com/sam4muzix/MIRCI_AI_PP_TOOLS.git

   cd MIRCI_AI_PP_TOOLS
   echo Running setup_env.bat...
   call setup_env.bat

   echo Running launch_webui.bat...
   call launch_webui.bat

   echo All processes completed.
   pause
   ```
2. Double-click `run_mirci.bat` to install and launch automatically.

## 🛠 Troubleshooting
- **Git is not recognized as an internal command?**  
  Install [Git](https://git-scm.com/downloads) and restart your PC.
- **Scripts not running?**  
  Right-click `.bat` files → **Run as Administrator**.

## 📜 License
This project is open-source. Feel free to modify and contribute!

## 🙌 Credits
Developed by Shyam L Raj https://github.com/sam4muzix.

---
📩 Need help? Reach out to the repository owner.

