---
layout: default
title: Windows
parent: Downloads
nav_order: 4
---

---
  
[Videomass 3.4.6 Installer](https://github.com/jeanslack/Videomass/releases/latest/download/Videomass-v3.4.6-x86_64-Setup.exe){: .btn .btn-green .fs-5 .mb-4 .mb-md-0 .mr-2} 
[Videomass 3.4.6 Portable](https://github.com/jeanslack/Videomass/releases/latest/download/Videomass-v3.4.6-x86_64-portable.7z){: .btn .btn-green .fs-5 .mb-4 .mb-md-0 .mr-2} 
[Pyembed package](#pyembed-package){: .btn .fs-5 .mb-4 .mb-md-0 }   

Minimum requirements:
- [Microsoft Windows 8 / 10](https://en.wikipedia.org/wiki/Windows_10)
- [x86_64](https://en.wikipedia.org/wiki/X86-64) architecture. 
- [Microsoft Visual C++ 2010 Service Pack 1 Redistributable Package (x86)](https://download.microsoft.com/download/1/6/5/165255E7-1014-4D0A-B094-B6A430A6BFFC/vcredist_x86.exe).   

### Important note
{: .bg-red-300}

A lot of antivirus vendors detect Videomass **installer** and **portable** as 
malicious. Since these are false positives, to resolve this problem the only thing 
to do is to submit the Videomass.exe file to your antivirus vendor for advanced 
analysis and making a False Positive claim. 
So, if you are still worried (or worse, scared) by the alarm cry of an overly 
susceptible array of antivirus, you can always try the new 
[Pyembed package](#pyembed-package) or install Videomass from 
[PyPi](https://pypi.org/project/videomass/). You will have the exact same program 
but installed in a more Pythonic way and certainly free from false positives.   
Visit the 
[Installing-dependencies](https://github.com/jeanslack/Videomass/wiki/Installing-dependencies#ms-windows) 
and then 
[installation using pip](https://github.com/jeanslack/Videomass/wiki/Installation-using-pip) 
wiki pages for more installation details.

## Pyembed package
{: .d-inline-block } 

Experimental
{: .label .label-purple }  

[Videomass 3.4.6 pyembed](https://github.com/jeanslack/Videomass/releases/latest/download/Videomass-v3.4.6-WIN-x86_64-pyembed.7z){: .btn .btn-green .fs-5 .mb-4 .mb-md-0 }

Minimum requirements:   
- [Microsoft Windows 8 / 10](https://en.wikipedia.org/wiki/Windows_10)
- [x86_64](https://en.wikipedia.org/wiki/X86-64) architecture. 
- [Microsoft Visual C++ 2010 Service Pack 1 Redistributable Package (x86)](https://download.microsoft.com/download/1/6/5/165255E7-1014-4D0A-B094-B6A430A6BFFC/vcredist_x86.exe).
- [Microsoft C Runtime](https://www.microsoft.com/en-us/download/details.aspx?id=48145)

This is a fully portable and ready-to-use experimental implementation of the 
[Python embeddable package](https://docs.python.org/3/using/windows.html#the-embeddable-package), 
which has been optimized to include Videomass and its dependencies. 
An embeddable-package is a portable Python distribution completely isolated from 
the user’s system, including environment variables, system registry settings, and 
installed packages.   

For any other application-related issues, please read 
[Known Problems](../../known_problems) and [Bug Reports](../Bugs) pages.
{: .fs-3 .text-grey-dk-100} 
