#!/usr/bin/python

import requests
import json
import argparse
from colorama import Fore
from lrxy import mp3
from lrxy import flac


def get_filetype(filename: str) -> str:
    if filename.lower().endswith('.mp3'):
        return "mp3"
    elif filename.lower().endswith('.flac'):
        return "flac"
    else:
        print(f"{Fore.RED}Error: {Fore.RESET}Unsupported file format.")
        exit(1)


def fetch_lyric(params: dict) -> str:
    print("Fetching...")
    url: str = "https://lrclib.net/api/get"
    response = requests.get(url, params=params)
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


def main() -> None:
    parser = argparse.ArgumentParser(
        description='A synced lyric fetcher and embedder for music files')
    parser.add_argument('file', type=str, help='path of music file')
    parser.add_argument('-s', '--separate',
                        action='store_true', help='write lyric to a lrc file')
    parser.add_argument('-i', '--input', dest='lrc', type=str,
                        help='embed from a lrc file')

    args = parser.parse_args()

    filename: str = args.file
    filetype: str = get_filetype(filename)

    if filetype == "mp3":
        audio = mp3.load_audio(filename)
        metadata_loader = mp3.load_metadata
        embed_lyric = mp3.embed_lyric
    else:
        audio = flac.load_audio(filename)
        metadata_loader = flac.load_metadata
        embed_lyric = flac.embed_lyric

    if args.lrc:
        with open(args.lrc, "r", encoding="utf-8") as f:
            lyric_text = f.read()
    else:
        print("Loading music info...")
        try:
            params: dict = metadata_loader(audio)
        except:
            print(
                f"{Fore.RED}Error: {Fore.RESET}There is something wrong with your music's tags!")
            exit(1)

        try:
            lyric_text: str = fetch_lyric(params)
        except:
            print(
                f"{Fore.RED}Error: {Fore.RESET}You might need to check your network connection!")
            exit(1)

        # Uncomment to remove space from beginning of the line
        # lyric_text = "]".join(lyric_text.split("] "))

    if args.separate:
        lrcfilename: str = filename.removesuffix(filetype) + "lrc"
        with open(lrcfilename, "w", encoding="utf-8") as f:
            f.write(lyric_text)
        print(
            f"{Fore.GREEN}Done: {Fore.RESET}Saved to: {Fore.CYAN}{lrcfilename}{Fore.RESET}")
    else:
        embed_lyric(audio, lyric_text)
        print(
            f"{Fore.GREEN}Done: {Fore.RESET}Saved to: {Fore.CYAN}{filename}{Fore.RESET}")


if __name__ == "__main__":
    main()

