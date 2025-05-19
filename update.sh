BACKUP_DIR="backup"

sleep 2

# Create backup directory
mkdir -p "$BACKUP_DIR"

rm -rf "$BACKUP_DIR/*"

# Detect OS
case "$(uname -s)" in
    MINGW*|CYGWIN*|MSYS*)
        # Windows
        if ! powershell -Command "Get-ChildItem -Path . -Exclude $BACKUP_DIR,.git | Copy-Item -Destination $BACKUP_DIR -Recurse -Force"; then
            echo "Backup failed. Exiting..."
            exit 1
        fi
        
        # Check if git is installed
        if ! where git > nul 2>&1; then
            echo "Downloading Git installer..."
            curl -o git-installer.exe https://github.com/git-for-windows/git/releases/download/v2.42.0.windows.2/Git-2.42.0.2-64-bit.exe
            ./git-installer.exe /VERYSILENT
            rm git-installer.exe
        fi
        ;;
    *)
        # Unix-like systems
        if ! find . -maxdepth 1 ! -name "$BACKUP_DIR" ! -name ".git" ! -name "." -exec cp -r {} "$BACKUP_DIR" \;; then
            echo "Backup failed. Exiting..."
            exit 1
        fi

        if ! command -v git &> /dev/null; then
            echo "Downloading Git..."
            if command -v apt-get &> /dev/null; then
                sudo apt-get update && sudo apt-get install -y git
            elif command -v yum &> /dev/null; then
                sudo yum install -y git
            elif command -v pacman &> /dev/null; then
                sudo pacman -S --noconfirm git
            else
                echo "Could not install git. Please install it manually."
                exit 1
            fi
        fi
        ;;
esac

rm -r *

git pull https://github.com/Orbinuity/MathAI.git

if [ -f "linux.py" ]; then
    python linux.py
else
    python windows.py
fi