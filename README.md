# Reddit Wallpaper Downloader

## How to use

Uses TKinter to render a small window. You can enter the URL of a subreddit and select which section to sort by (Hot, Top, or New).
The program will start from the top and preview only 5 images at once; you can go to the next 5 by clicking on next (and go back by clicking previous).

Clicking on an image will download it to the folder where the .py file is stored and immediately set it as your wallpaper. The naming convention is "wallpaper_x.jpg", where x is a number (based on how many you've downloaded.)

The directory where the wallpapers are stored can be changed, and clicking "Delete Wallpapers" will clean all the wallpaper files downloaded in that directory.

![app window](https://files.catbox.moe/mugxdj.png)

## Bonus

I thought it would be nice to make it so that non-image posts are skipped, because otherwise sometimes only 3 or 4 images get previewed. The links that are skipped are logged to the terminal so they can be visited if you want.

![terminal logs of skipped URLs](https://files.catbox.moe/twuwjv.png)