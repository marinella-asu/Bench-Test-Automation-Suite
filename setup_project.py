import os
import sys

def add_pythonpath_to_shell():
    # Detect the current shell using 'COMSPEC' or 'SHELL' environment variable
    shell = os.environ.get('SHELL', os.environ.get('COMSPEC', ''))
    shell_config = None
    shell_type = None

    if 'bash' in shell:
        shell_config = os.path.expanduser('~/.bashrc')
        shell_type = 'bash'
    elif 'zsh' in shell:
        shell_config = os.path.expanduser('~/.zshrc')
        shell_type = 'zsh'
    elif 'fish' in shell:
        shell_config = os.path.expanduser('~/.config/fish/config.fish')
        shell_type = 'fish'
    elif 'powershell' in shell.lower() or 'pwsh' in shell.lower():
        shell_type = 'powershell'
    elif 'cmd' in shell.lower():
        shell_type = 'cmd'
    else:
        print("Unsupported shell or shell not detected. Please add the PYTHONPATH manually.")
        return

    # Determine project root
    project_root = os.path.abspath(os.path.dirname(__file__))
    sys.path.append(project_root)
    
    # Prepare the export command for Unix-like shells
    export_command = f'export PYTHONPATH=$PYTHONPATH:{project_root}'

    if shell_type == 'powershell':
        # PowerShell command to set PYTHONPATH
        export_command = f'$env:PYTHONPATH="$env:PYTHONPATH;{project_root}"'
        # Check if PYTHONPATH is already set in PowerShell profile
        shell_config = os.path.expanduser('~\\Documents\\PowerShell\\Microsoft.PowerShell_profile.ps1')
    elif shell_type == 'cmd':
        # CMD command to set PYTHONPATH
        export_command = f'set PYTHONPATH={project_root};%PYTHONPATH%'
        # Check if PYTHONPATH is already set in CMD autoexec.bat or a similar file
        shell_config = os.path.expanduser('~\\autoexec.bat')
    
    # Check if the shell configuration file exists and the export command is already present
    if shell_config and os.path.exists(shell_config):
        with open(shell_config, 'r') as f:
            if export_command in f.read():
                print(f"PYTHONPATH is already set in {shell_config}.")
                print(shell_config)
                return

    # Add PYTHONPATH to the shell configuration
    with open(shell_config, 'a') as f:
        f.write(f'\n# Added by setup_project.py\n{export_command}\n')

    print(f"PYTHONPATH has been added to {shell_config}.")
    print("Please restart your terminal or run `source {shell_config}` (for Unix-like shells) or restart PowerShell (for PowerShell) to apply the changes.")

if __name__ == "__main__":
    add_pythonpath_to_shell()
