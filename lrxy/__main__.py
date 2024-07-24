#!/usr/bin/python

import requests
import json
import argparse
from colorama import Fore
from lrxy import mp3
from lrxy import flac


def get_filetype(audio_file: str) -> str:
    if audio_file.lower().endswith('.mp3'):
        return "mp3"
    elif audio_file.lower().endswith('.flac'):
        return "flac"
    else:
        print(f"{Fore.RED}Error: {Fore.RESET}Unsupported file format.")
        exit(1)


def fetch_lyric(params: dict) -> str:
    print("Fetching...")
    url: str = "https://lrclib.net/api/get"
    try:
        response = requests.get(url, params=params)
    except:
        print(
            f"{Fore.RED}Error: {Fore.RESET}You might need to check your network connection!")
        exit(1)
    data = json.loads(response.text)

    match response.status_code:
        case 200:
            print(f"Fetched Successfully.")
        case 404:
            print(
                f"{Fore.RED}Error: {Fore.RESET}Couldn't find this music. Try to change music tags.")
            exit(1)
        case _:
            print(f"{Fore.RED}Error: {Fore.RESET}{data.message}")
            exit(1)

    plain_lyric: str = data.get("plainLyrics")
    synced_lyric: str = data.get("syncedLyrics")
    if synced_lyric:
        return synced_lyric
    elif plain_lyric:
        choice: str = input(
            "This music doesn't have synced lyric. Use plain lyric (Y/n)? ")
        match choice:
            case "Y" | "y" | "":
                return plain_lyric
            case "N" | "n":
                exit(0)
            case _:
                print('Please enter "y" or "n"!')
                exit(1)
    else:
        print(f"{Fore.RED}Error: {Fore.RESET}This song has no lyric.")
        exit(1)


def read_lrc() -> None:
    parser = argparse.ArgumentParser(
        prog="lrxy-embed", description='Utility of lrxy to embed lyric from lrc file')

    parser.add_argument('input', type=str, help='path of lrc file')
    parser.add_argument('file', type=str, help='path of music file')

    args = parser.parse_args()

    audio_file: str = args.file
    lrc_file: str = args.input
    audio_type: str = get_filetype(audio_file)

    if audio_type == "mp3":
        audio = mp3.load_audio(audio_file)
        embed_lyric = mp3.embed_lyric
    else:
        audio = flac.load_audio(audio_file)
        embed_lyric = flac.embed_lyric

    with open(lrcfile, "r", encoding="utf-8") as f:
        lyric_text = f.read()

    embed_lyric(audio, lyric_text)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="lrxy", description='A synced lyric fetcher and embedder for music files')
    parser.add_argument(
        '-s', '--separate', action='store_true',
        help='write lyric to a lrc file')
    parser.add_argument('file', type=str, help='path of music file')

    args = parser.parse_args()

    audio_file: str = args.file
    audio_type: str = get_filetype(audio_file)

    if audio_type == "mp3":
        audio = mp3.load_audio(audio_file)
        metadata_loader = mp3.load_metadata
        embed_lyric = mp3.embed_lyric
    else:
        audio = flac.load_audio(audio_file)
        metadata_loader = flac.load_metadata
        embed_lyric = flac.embed_lyric

    print("Loading music info...")
    try:
        params: dict = metadata_loader(audio)
    except:
        print(
            f"{Fore.RED}Error: {Fore.RESET}There is something wrong with your music's tags!")
        exit(1)

    lyric_text: str = fetch_lyric(params)

    # Uncomment to remove space from beginning of the line
    # lyric_text = "]".join(lyric_text.split("] "))

    if args.separate:
        lrc_file: str = audio_file.removesuffix(audio_type) + "lrc"
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
