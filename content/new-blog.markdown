Title: New Blog
Date: 2014-05-04 12:10:35

I did something to my environment and my octopress setup exploded. So, I
decided it was time to move on. I've been wanting to toss octopress for
something less quirky for a while. So now I'm using
[Pelican](http://getpelican.com/) with the [Elegant
theme](http://oncrashreboot.com/elegant-best-pelican-theme-features). Pelican
is pretty simple, though I've had trouble with the makefiles and fabfiles it
generated. Rather than using them, I'm just invoking Pelican myself:

    pelican content -s pelicanconf.py -t themes/pelican-elegant-1.3

Easy enough! The Elegant theme is the best I've found so far (it seems to be a
pretty rarely used tool), but I'm not happy with its visual style. I'm still a
fan of the [Slash octopress
theme](https://github.com/tommy351/Octopress-Theme-Slash/), which I maintain.
I'll probably end up porting it to Pelican, possibly with some tweaks.

To my knowledge, no URIs should have changed in the migration. If you find a
broken URI, [please email me](mailto:corey@octayn.net). [Cool URIs don't
change](http://www.w3.org/Provider/Style/URI.html). One peculiar change is
that the 'Archives' link now goes to `/archives.html`. However, I have set it
up such that `/blog/archives` is still valid.

My configuration is [available on github](http://github.com/cmr/blog) if you
want to take a look.
