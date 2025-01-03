import os
import sys

def add_pythonpath_to_shell():
    # Detect the current shell
    shell = os.environ.get('SHELL', '')
    shell_config = None
    
    if 'bash' in shell:
        shell_config = os.path.expanduser('~/.bashrc')
    elif 'zsh' in shell:
        shell_config = os.path.expanduser('~/.zshrc')
    elif 'fish' in shell:
        shell_config = os.path.expanduser('~/.config/fish/config.fish')
    else:
        print("Unsupported shell or shell not detected. Please add the PYTHONPATH manually.")
        return

    # Determine project root
    project_root = os.path.abspath(os.path.dirname(__file__))

    # Prepare the export command
    export_command = f'export PYTHONPATH=$PYTHONPATH:{project_root}'

    # Check if PYTHONPATH is already added
    if shell_config and os.path.exists(shell_config):
        with open(shell_config, 'r') as f:
            if export_command in f.read():
                print(f"PYTHONPATH is already set in {shell_config}.")
                return

    # Add PYTHONPATH to the shell configuration
    with open(shell_config, 'a') as f:
        f.write(f'\n# Added by setup_project.py\n{export_command}\n')

    print(f"PYTHONPATH has been added to {shell_config}.")
    print("Please restart your terminal or run `source {shell_config}` to apply the changes.")

if __name__ == "__main__":
    add_pythonpath_to_shell()
