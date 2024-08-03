#!/usr/bin/python

import argparse
from colorama import Fore
from lrxy import mp3, flac, m4a
from lrxy.modules import get_filetype, fetch_lyric_data, get_lyric


def read_lrc() -> None:
    parser = argparse.ArgumentParser(
        prog="lrxy-embed",
        description="Utility of lrxy to embed lyric from lrc file",
    )

    parser.add_argument("input", type=str, help="path of lrc file")
    parser.add_argument("file", type=str, help="path of music file")

    args = parser.parse_args()

    audio_file: str = args.file
    lrc_file: str = args.input
    audio_extension = get_filetype(audio_file)

    if audio_extension["success"]:
        if audio_extension["format"] == "mp3":
            audio = mp3.load_audio(audio_file)
            embed_lyric = mp3.embed_lyric
        elif audio_extension["format"] == "flac":
            audio = flac.load_audio((audio_file))
            embed_lyric = flac.embed_lyric
        elif audio_extension["format"] == "m4a":
            audio = m4a.load_audio((audio_file))
            embed_lyric = m4a.embed_lyric

        with open(lrc_file, "r", encoding="utf-8") as f:
            lyric_text = f.read()

        embed_lyric(audio, lyric_text)
    else:
        print(audio_extension["message"])
        exit()


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="lrxy",
        description="A synced lyric fetcher and embedder for music files",
    )
    parser.add_argument(
        "-s", "--separate",
        action="store_true",
        help="write lyric to a lrc file",
    )
    parser.add_argument("file", nargs="+", help="path of music file")

    args = parser.parse_args()

    audio_files = args.file

    for audio_file in audio_files:
        audio_extension = get_filetype(audio_file)

        if audio_extension["success"]:
            if audio_extension["format"] == "mp3":
                audio = mp3.load_audio(audio_file)
                metadata_loader = mp3.load_metadata
                embed_lyric = mp3.embed_lyric
            elif audio_extension["format"] == "flac":
                audio = flac.load_audio(audio_file)
                metadata_loader = flac.load_metadata
                embed_lyric = flac.embed_lyric
            elif audio_extension["format"] == "m4a":
                audio = m4a.load_audio(audio_file)
                metadata_loader = m4a.load_metadata
                embed_lyric = m4a.embed_lyric
        else:
            print(Fore.RED + audio_extension["message"])
            continue

        print(f'Loading music info "{audio_file}"...')
        try:
            params: dict = metadata_loader(audio)
        except Exception as exp:
            print(
                f"{Fore.RED}Error: {Fore.RESET}There is something wrong with your music's tags!"
                f"{Fore.RED}{exp}{Fore.RESET}\n"
            )
            continue

        lyric_data = fetch_lyric_data(params, audio_file)
        if lyric_data["success"]:
            lyric_text = get_lyric(lyric_data["data"])
            if not lyric_text:
                print(f"This music {audio_file} has no lyrics")
        else:
            print(str(lyric_data["message"]))
            continue

        # Uncomment to remove space from beginning of the line
        # lyric_text = "]".join(lyric_text.split("] "))

        if args.separate:
            lrc_file: str = audio_file.removesuffix(audio_extension) + "lrc"
            with open(lrc_file, "w", encoding="utf-8") as f:
                f.write(lyric_text)
            print(
                f"{Fore.GREEN}Done: {Fore.RESET}Saved to: {Fore.CYAN}{lrc_file}{Fore.RESET}")
        else:
            embed_lyric(audio, lyric_text)
            print(
                f"{Fore.GREEN}Done: {Fore.RESET}Saved to: {Fore.CYAN}{audio_file}{Fore.RESET}")


if __name__ == "__main__":
    main()
