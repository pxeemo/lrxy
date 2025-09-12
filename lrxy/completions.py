import sys
import subprocess

import argparse
import argcomplete


def generate_completion(shell):
    command = ["register-python-argcomplete", "--shell", shell, "lrxy"]

    if sys.stdout.isatty():
        print("Pipe this command into the desired output path. e.g.:")
        print(f"lrxy --shell-completion {shell} > ", end="")
        match shell:
            case "bash":
                print("~/.local/share/bash-completion/completions/lrxy")
            case "zsh":
                print("~/.zsh/completion/_lrxy")
            case "fish":
                print("~/.config/fish/completions/lrxy.fish")

    else:
        subprocess.run(command)

    sys.exit()
