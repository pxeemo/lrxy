import sys
import subprocess
from pathlib import Path


def generate_completion(shell):
    command_name = Path(sys.argv[0]).name
    command = ["register-python-argcomplete", "--shell", shell, command_name]

    if sys.stdout.isatty():
        print("Pipe this command into the desired output path. e.g.:")
        print(f"{command_name} --shell-completion {shell} > ", end="")
        match shell:
            case "bash":
                print(f"~/.local/share/bash-completion/completions/{command_name}")
            case "zsh":
                print(f"~/.zsh/completion/_{command_name}")
            case "fish":
                print(f"~/.config/fish/completions/{command_name}.fish")

    else:
        subprocess.run(command)

    sys.exit()
