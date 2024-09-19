# unused right now

from cache import Cache
import parsing
import pytubefix as pt

def run_cli():
    cache = Cache("video_cache.pkl")
    message_links = parsing.find_links_file("message.txt")
    new_links = cache.find_new_strings(message_links)

    for link in new_links:
        try:
            pt.YouTube(link).streams.get_highest_resolution(progressive=True).download("./videos")
            print(f"downloading: {link}...")
            cache.update_cache([link])
        except Exception as e:
            print(f"Couldn't download a video with url: {link}\nGot error{e}\nSkipping it!s")

    print("Finished download!")

if __name__ == "__main__":
    run_cli()
