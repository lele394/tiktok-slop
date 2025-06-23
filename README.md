# TikTok Slop Maker

This script is not productive and automates the creation and publishing of tiktok ball circle slop.

I made it to see if I can automate a content farm that actually brings back revenue. I hope it does not. My faith in Humanity is already at its lowest.


### Tricks

##### Flatpak install of firefox

since firefox is installed on flatpak, use a vm with distrobox. Setup the vm to run your favorit flavor of drivers.
In case tiktok-uploader eats the dirt and can't boot a driver, go at the end of browser.py in its library and modify the browser dictionnary to have your correct paths.

```python

services = {
    "chrome": lambda: ChromeService(ChromeDriverManager().install()),
    "firefox": lambda: FirefoxService("/home/name/Desktop/tiktok-slop/geckodriver"),
    "edge": lambda: EdgeService(EdgeChromiumDriverManager().install()),
}
```

Short format content will kill humanity.