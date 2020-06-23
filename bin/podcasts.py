#! /usr/bin/env python3

""" Copy of getpodcast module with fix """


import argparse
import collections
import datetime
import email.utils
import mimetypes
import os
import re
import shutil
import socket
import sys
import urllib.error
import urllib.request

from pyPodcastParser.Podcast import Podcast

mimetypes.init()

# options tuple
Options = collections.namedtuple(
    "Options",
    [
        "run",
        "dryrun",
        "onlynew",
        "quiet",
        "list",
        "keywords",
        "podcast",
        "date_from",
        "root_dir",
        "template",
        "user_agent",
        "hooks",
    ],
)

# Global for the message function
quiet = False


def options(**kwargs) -> Options:
    parser = argparse.ArgumentParser(
        description="Download podcasts.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    default_template = "{rootdir}/{podcast}/{year}/{date} {title}{ext}"

    parser.add_argument("--run", action="store_true", help="Download podcasts.", default=kwargs.get("run",True))
    parser.add_argument(
        "--dryrun", action="store_true", help="Test. Does not download podcasts."
    )
    parser.add_argument(
        "--onlynew", action="store_true", help="Only process new entries.",default=kwargs.get("onlynew",True)
    )
    parser.add_argument(
        "--quiet", action="store_true", help="Quiet mode (for cron jobs)"
    )
    parser.add_argument("--list", action="store_true", help="List all podcasts")
    parser.add_argument(
        "--keywords",
        action="store_true",
        help="List available keywords for filename template",
    )
    parser.add_argument(
        "--template",
        default=kwargs.get("template", default_template),
        help="Filename template",
    )
    parser.add_argument(
        "--podcast",
        default=kwargs.get("podcast", ""),
        help="Only process this podcast. default: all",
    )
    parser.add_argument(
        "--date-from",
        default=kwargs.get("date_from", "1970-01-01"),
        help="Only download podcast newer then date",
    )
    parser.add_argument(
        "--root-dir",
        default=kwargs.get("root_dir", "./podcast"),
        help="Podcast download directory",
    )
    parser.add_argument(
        "--user-agent",
        default=kwargs.get("user_agent", ""),
        help="web request identification",
    )
    parser.add_argument(
        "--hooks",
        default=kwargs.get("hooks", ""),
        help="comma seperated key=value list of hooks",
    )

    args = parser.parse_args()

    # verify hooks
    try:
        list(parse_hooks_string(args.hooks))
    except ValueError:
        print("Error parsing hooks string. Expected format:")
        print("validated=funcname,preprocess=anotherfunc")
        raise SystemExit()

    print(args)
    opt = Options(**args.__dict__)

    global quiet
    quiet = opt.quiet

    # if missing argument print help
    if not any((opt.run, opt.dryrun, opt.list, opt.keywords)):
        print("wtf")
        print(opt.run)
        print(opt.dryrun)
        print(opt.list)
        print(opt.keywords)
        parser.print_help()
    return opt


def getpodcast(podcasts: dict, args: Options) -> None:

    # print list of podcasts
    if args.list:
        for p in podcasts.keys():
            print(p)
        return

    # print list of keywords
    if args.keywords:
        for item in (
            ("rootdir", "base directory for downloads"),
            ("podcast", "key part of podcast dict"),
            ("date", "item publish date (format: YYYY-MM-DD)"),
            ("title", "item title"),
            ("year", "item publish year"),
            ("ext", "enclosure file extension"),
        ):
            print("{%s} = %s" % item)
        return

    if not (args.run or args.dryrun):
        return

    headers = {}
    if args.user_agent:
        headers["User-Agent"] = args.user_agent

    fromdate = datetime.datetime.strptime(args.date_from, "%Y-%m-%d")

    for pod, url in podcasts.items():
        process_podcast(pod, url, headers, fromdate, args)


def process_podcast(pod: str, url: str, headers: dict, fromdate, args: Options):
    # if --podcast is used we will only process a matching name
    if args.podcast:
        if not args.podcast == pod:
            return  # continue

    try:
        request = urllib.request.Request(url, headers=headers)
        content = urllib.request.urlopen(request)
        podcast = Podcast(content.read())
    except (urllib.error.HTTPError, urllib.error.URLError) as err:
        message("Podcast: {}".format(pod), wait=True)
        message("Connection error: {}".format(err))
        return  # continue

    for item in podcast.items:
        try:
            process_podcast_item(pod, item, headers, fromdate, args)
        except SkipPodcast:
            break


class SkipPodcast(Exception):
    pass


def process_podcast_item(pod: str, item, headers: dict, fromdate, args: Options):
    # skip if date is older then --date-from
    if fromdate:
        if item.date_time < fromdate:
            return  # continue

    # create a dict with info to be used in filename
    data = {
        "rootdir": args.root_dir.rstrip("/"),
        "podcast": pod,
        "date": item.date_time.strftime("%Y.%m.%d"),
        "title": getSafeFilenameFromText(item.title.strip(" .")),  # scrub title
        "year": str(item.date_time.year),
        "ext": parseFileExtensionFromUrl(item.enclosure_url)
        or mimetypes.guess_extension(item.enclosure_type),
    }

    filename_template = args.template
    newfilename = filename_template.format(**data)
    newfilelength = 0
    newfilemtime = item.time_published

    message(
        "\n".join(
            (
                "",
                "Podcast: {}",
                "  Date:  {}",
                "  Title: {}",
                "  File:  {}:",
                "  Status:",
            )
        ).format(pod, data["date"], data["title"], newfilename),
        wait=True,
    )

    # if file exist we check if filesize match with content length...
    if os.path.isfile(newfilename):
        newfilelength = os.path.getsize(newfilename)
        try:
            if validateFile(
                newfilename,
                item.time_published,
                item.enclosure_length,
                item.enclosure_url,
                headers,
            ):
                if (
                    args.onlynew
                ):  # if file is valid and --onlynew is set then we jump to next podcast
                    raise SkipPodcast
                else:
                    return  # continue
        except (urllib.error.HTTPError, urllib.error.URLError):
            message("Connection when verifying existing file")
            return  # continue
        except socket.timeout:
            message("Connection timeout when downloading file")
            return  # continue

    # use --dryrun to test parameter changes.
    if args.dryrun:
        if newfilelength:
            message("Pretending to resume from byte {}".format(newfilelength))
            return  # continue
        else:
            message("Pretending to download")
            return  # continue

    # download or resume podcast. retry if timeout. cancel if error
    cancel_validate, newfilelength = try_download_item(
        newfilelength, newfilename, item, headers
    )

    if cancel_validate:
        return  # continue

    # validate downloaded file
    try:
        if validateFile(
            newfilename, 0, item.enclosure_length, item.enclosure_url, headers
        ):
            # set mtime if validated
            os.utime(newfilename, (newfilemtime, newfilemtime))
            message("File validated")
            hooks(args.hooks, "validated", locals())

        elif newfilelength:
            # did not validate. see if we got same size as last time we
            # downloaded this file
            if newfilelength == os.path.getsize(newfilename):
                # ok, size is same. maybe data from response and rss is wrong.
                os.utime(newfilename, (newfilemtime, newfilemtime))
                message("File is assumed to be ok.")
    except urllib.error.HTTPError:
        message("Connection error when verifying download")
        return  # continue
    except socket.timeout:
        message("Connection timeout when downloading file")
        return  # continue


def try_download_item(newfilelength, newfilename, item, headers):
    # download or resume podcast. retry if timeout. cancel if error
    retry_downloading = True
    while retry_downloading:
        retry_downloading = False
        cancel_validate = False
        try:
            if newfilelength:
                resumeDownloadFile(newfilename, item.enclosure_url, headers)
            else:
                downloadFile(newfilename, item.enclosure_url, headers)
        except (urllib.error.HTTPError, urllib.error.URLError):
            message("Connection error when downloading file")
            cancel_validate = True
        except socket.timeout:
            if newfilelength:
                if os.path.getsize(newfilename) > newfilelength:
                    message("Connection timeout. File partly resumed. Retrying")
                    retry_downloading = True
                    newfilelength = os.path.getsize(newfilename)
                else:
                    message("Connection timeout when resuming file")
                    cancel_validate = True
            else:
                if os.path.isfile(newfilename):
                    newfilelength = os.path.getsize(newfilename)
                    if newfilelength > 0:
                        message("Connection timeout. File partly downloaded. Retrying")
                        retry_downloading = True
                    else:
                        message("Connection timeout when downloading file")
                        cancel_validate = True
                else:
                    message("Connection timeout when downloading file")
                    cancel_validate = True

    return cancel_validate, newfilelength


def downloadFile(newfilename: str, enclosure_url: str, headers: dict) -> None:
    # create download dir path if it does not exist
    if not os.path.isdir(os.path.dirname(newfilename)):
        os.makedirs(os.path.dirname(newfilename))

    # download podcast
    message("Downloading ...")

    request = urllib.request.Request(enclosure_url, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        with open(newfilename, "wb") as out_file:
            shutil.copyfileobj(response, out_file, 100 * 1024)

    message("Download complete")


def resumeDownloadFile(newfilename: str, enclosure_url: str, headers: dict) -> None:
    # find start-bye and total byte-length
    message("Prepare resume")
    request = urllib.request.Request(enclosure_url, headers=headers)
    with urllib.request.urlopen(request) as response:
        info = response.info()
        if "Content-Length" in info:
            contentlength = int(info["Content-Length"])
        else:
            contentlength = -1

    if os.path.isfile(newfilename):
        start_byte = os.path.getsize(newfilename)
    else:
        start_byte = 0

    request = urllib.request.Request(enclosure_url, headers=headers)
    if start_byte > 0:
        if start_byte >= contentlength:
            message("Resume not possible. (startbyte greater then contentlength)")
            return
        request.add_header("Range", "bytes={}-".format(start_byte))

    with urllib.request.urlopen(request, timeout=30) as response:
        with open(newfilename, "ab+") as out_file:

            info = response.info()
            out_file.seek(start_byte)

            if "Content-Range" in info:
                contentrange = info["Content-Range"].split(" ")[1].split("-")[0]
                if not int(contentrange) == start_byte:
                    message(
                        "Resume not possible. Cannot start download from byte {}".format(
                            start_byte
                        )
                    )
                    return

            if not out_file.tell() == start_byte:
                message(
                    "Resume not possible. Cannot append data from byte {}".format(
                        start_byte
                    )
                )
                return

            message("Start resume from byte {}".format(start_byte))
            message("Downloading ...")
            shutil.copyfileobj(response, out_file, 100 * 1024)

    message("Resume complete")


def validateFile(
    newfilename: str,
    time_published: int,
    enclosure_length: int,
    enclosure_url: str,
    headers: dict,
) -> bool:
    if os.path.isfile(newfilename + ".err"):
        return True  # skip file

    # try to validate size

    filelength = os.path.getsize(newfilename)
    if enclosure_length:
        if abs(filelength - enclosure_length) <= 1:
            return True
    else:
        enclosure_length = 0

    request = urllib.request.Request(enclosure_url, headers=headers)
    with urllib.request.urlopen(request) as response:
        info = response.info()
        if "Content-MD5" in info:
            message("Content-MD5:{}".format(info["Content-MD5"]))

        if "Content-Length" in info:
            contentlength = int(info["Content-Length"])
            if abs(filelength - contentlength) <= 1:
                return True
            elif filelength > contentlength:
                return True

        message(
            "Filelength and content-length mismatch. filelength:{:,} enclosurelength:{:,} contentlength:{:,}".format(
                filelength, enclosure_length, int(info.get("Content-Length", "0"))
            )
        )

        # if size validation fail, try to validate mtime.

        if time_published:
            filemtime = parseUnixTimeToDatetime(os.path.getmtime(newfilename))
            time_published = parseUnixTimeToDatetime(time_published)
            if time_published == filemtime:
                return True

            if "Last-Modified" in info:
                last_modified = parseRftTimeToDatetime(info["Last-Modified"])
                if last_modified == filemtime:
                    return True
            else:
                last_modified = ""

            message(
                "Last-Modified mismatch. file-mtime:{} Last-Modified:{} pubdate:{}".format(
                    filemtime, last_modified, time_published
                )
            )
    return False


def getSafeFilenameFromText(text):
    # remove reserved windows keywords
    reserved_win_keywords = r"(PRN|AUX|CLOCK\$|NUL|CON|COM[1-9]|LPT[1-9])"

    # remove reserved windows characters
    reserved_win_chars = '[\x00-\x1f\\\\?*:";|/<>]'
    # reserved posix is included in reserved_win_chars. reserved_posix_characters = '/\0'

    extra_chars = "[$@{}]"

    tmp = re.sub(
        "|".join((reserved_win_keywords, reserved_win_chars, extra_chars)), "", text
    )
    return tmp


def parseFileExtensionFromUrl(enclosure_url):
    return os.path.splitext(enclosure_url)[1].split("?")[0].lower()


def parseRftTimeToDatetime(datetimestr: str) -> datetime.datetime:
    return email.utils.parsedate_to_datetime(datetimestr)


def parseUnixTimeToDatetime(datetimestamp: int) -> datetime.datetime:
    return datetime.datetime.fromtimestamp(datetimestamp)


messagebuffer = ""


def message(msg: str, wait=False) -> None:
    if quiet:
        return

    global messagebuffer
    if wait:
        messagebuffer = msg
        return

    if messagebuffer:
        print(messagebuffer)
        messagebuffer = ""

    print("        ", msg)


def parse_hooks_string(hooks: str):
    if hooks:
        for hook in hooks.split(","):
            key, val = hook.split("=")
            yield key, val


def hooks(hook_string: str, hook_name: str, kwargs: dict):
    for key, val in parse_hooks_string(hook_string):
        if key == hook_name:
            mod = sys.modules.get("__main__", __name__)
            if hasattr(mod, val):
                hook = getattr(mod, val)
                if callable(hook):
                    hook(**kwargs)


