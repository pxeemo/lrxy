import sys
import subprocess
from pathlib import Path


_lrxy_fish_completion = """# generated with `lrxy --shell-completion fish`
complete -c lrxy -s h -l help -d "show help"
complete -c lrxy -s v -l version -d "show version"
complete -c lrxy -l no-overwrite -d "do not overwrite existing lyrics"
complete -c lrxy -s n -l no-embed -d "write lyrics to separate text files"
complete -c lrxy -s p -l provider -xa "lrclib musixmatch applemusic qq" -d "provider to fetch lyrics"
complete -c lrxy -s f -l format -xa "ttml lrc srt json" -d "output lyrics format"
complete -c lrxy -l embed -a "(__fish_complete_path)" -d "embed existing lyric file into music"
complete -c lrxy -l log-level -xa "error warning info debug" -d "command line verbosity"
"""

_lrxy_convert_fish_completion = """# generated with `lrxy-convert --shell-completion fish`
complete -c lrxy-convert -s h -l help -d "show help"
complete -c lrxy-convert -s i -l input-format -xa "ttml lrc srt json" -d "input lyric file format"
complete -c lrxy-convert -s o -l output-format -xa "ttml lrc srt json" -d "output lyric file format"
complete -c lrxy-convert -l log-level -xa "error warning info debug" -d "provide shell completion"
"""


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
        if shell == "fish":
            if command_name == "lrxy":
                sys.stdout.write(_lrxy_fish_completion)
            elif command_name == "lrxy-convert":
                sys.stdout.write(_lrxy_convert_fish_completion)
        else:
            subprocess.run(command)

    sys.exit()
