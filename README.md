# Git GUI Manager 🚀

> A modern, feature-rich Git graphical interface built with Python and PyQt5

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Python Version](https://img.shields.io/badge/python-3.6+-blue.svg)
![PyQt Version](https://img.shields.io/badge/PyQt-5-green.svg)

Git GUI Manager is a user-friendly graphical interface that simplifies Git operations through an intuitive visual interface. Built with Python and PyQt5, it offers both basic and advanced Git functionality in a modern, Material Design-inspired environment.

## ✨ Features

### 🔧 Basic Git Operations
- Initialize repositories (`git init`)
- Stage files (`git add`)
- Create commits with messages
- Push and pull changes
- View repository status

### 🎯 Advanced Git Features
- Complete branch management (create, delete, rename)
- Branch merging with conflict resolution
- Remote repository handling
- Branch history visualization
- Force push capability with safety checks

### 💻 Terminal Integration
- Live Git command line interface
- Command history tracking
- Real-time output display

### 🎨 User Interface
- Dark/Light theme support
- Drag-and-drop repository selection
- Material Design-inspired modern interface
- Tab-based layout for easy navigation
- Status bar notifications
- Intuitive workflow management

## 🚀 Getting Started

### Prerequisites
```
- Python 3.6 or higher
- PyQt5
- Git (installed on system)
```

### 📥 Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd git-gui-manager
```

2. Install required packages:
```bash
pip install PyQt5
```

3. Launch the application:
```bash
python gitprojectmanager.pyw
```

## 📖 Usage Guide

### 📁 Repository Selection
1. Click the "Browse" button
2. Select your Git repository folder
3. Path will be automatically saved

### 🔰 Basic Operations
1. Navigate to "Basic Git Operations" tab
2. Select repository path
3. Execute Git commands using the provided buttons

### 🛠️ Advanced Operations
1. Switch to "Advanced Git" tab
2. Use top section tools for branch operations
3. Use bottom section for remote operations

### ⌨️ Terminal Usage
1. Go to "Live Terminal" tab
2. Type Git commands directly
3. View output in the terminal screen

## 🔒 Security Features

- Restricted to Git commands only
- System command execution prevention
- Repository path validation
- User notification for all error states

## ⚠️ Troubleshooting

### Common Issues and Solutions

1. **"Git command not found"**
   - Ensure Git is installed
   - Verify Git is in system PATH

2. **"Repository not found"**
   - Verify selected folder is a valid Git repository
   - Initialize repository with `git init`

3. **"Permission denied"**
   - Check file/folder permissions
   - Verify Git credential helper configuration

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🌟 Support

If you find this project helpful, please consider giving it a star ⭐

## 📞 Contact

For questions or suggestions, please open an issue in the repository.

## 🙏 Acknowledgments

- PyQt5 team for the amazing framework
- Material Design team for interface inspiration
- All contributors who helped shape this project

---
Made with ❤️ by Melih Can Demir for developers