Retro Programming Works 怀旧编程作品
====================================

一些古董平台上的编程作品。仅供娱乐。  
Some retro programming works for some old platforms. Just for fun.

GW-BASIC
--------

一个类似1980年代家用电脑上的BASIC编程环境。  
A BASIC environment similar to those on home computers in 1980's.

因为该语言的[诸多缺陷](http://www.cnbeta.com/articles/deep/232400.htm)，导致代码难以维护，故该语言仅用于简单计算，或编写猜数字、2048之类的小游戏。  
However, due to the [limitations](http://programmingisterrible.com/post/40132515169/dijkstra-basic) of this programming language, the code for this language is very hard to maintain, so it's only used for simple calculations, small games like *Bulls and Cows* and *2048*.

### 截图欣赏 Screenshots

![Startup](http://frank-deng.github.io/retro-works/Startup.png)

![Prime Numbers](http://frank-deng.github.io/retro-works/Prime%20Numbers.png)

![Bulls and Cows](http://frank-deng.github.io/retro-works/Guessnum.png)

![2048](http://frank-deng.github.io/retro-works/2048-1.png)

![2048](http://frank-deng.github.io/retro-works/2048-2.png)


telnet-site
-----------

一个简单的telnet站点，使用[w3m](http://w3m.sourceforge.net)浏览器在字符界面下显示HTML页面。  
A simple site designed for console-based browser [w3m](http://w3m.sourceforge.net), which makes it works like an old-school telnet BBS site.

DOSBox模拟的客户端硬件  
Client side hardware emulated by DOSBox

* Old 386 platform
* VGA display
* Floppy drive only
* Virtual serial modem with Hayes command set

客户端使用的软件  
Client side software

* MS-DOS 5.0
* ANSI.SYS
* UCDOS 7.0
* COMTOOL.COM

### 截图欣赏 Screenshots

![](http://frank-deng.github.io/retro-works/Telnet%201.png)

![](http://frank-deng.github.io/retro-works/Telnet%202.png)

### Linux服务器端配置 Linux Server Configuration

在`/etc/locale.gen`中加上`zh_CN.GB2312`，然后运行`sudo locale-gen`。  
Add `zh_CN.GB2312` into `/etc/locale.gen`, then run `sudo locale-gen`.

安装需要的软件包  
Install package needed

	sudo apt-get install ncurses-term tcpser
	
创建`user`用户
Add user with username `user`
	
	sudo adduser user

在`/home/user/.bashrc`中加上以下内容：  
Add the following lines into `/home/user/.bashrc`:

	export TERM='ansi43m';
	export LINES=25;
	export COLUMNS=80;
	export LC_ALL=zh_CN.GB2312
	export LANG=zh_CN.GB2312
	export WWW_HOME='http://127.0.0.1'
	w3m -no-mouse
	exit

登录`user`用户，然后对`w3m`浏览器作如下设置：  
Login as user `user`, then setup `w3m` with the settings below:

* Run external viewer in the background: No
* Use combining characters: No
* Use double width for some Unicode characters: Yes
* Charset conversion when loading: Yes

将`keymap`文件复制到`/home/user/.w3m`目录中，以禁止从`w3m`浏览器中运行外部命令，增强站点的安全性。  
Copy file `keymap` to folder `/home/user/.w3m` to disable executing external commands from `w3m` browser, so as to enhance the safety of the site.

在`/etc/crontab`中加入以下命令，实现开机时自动启动`telnetd.py`和[`tcpser`](http://www.jbrain.com/pub/linux/serial/)：  
Add the following command to `/etc/crontab`, so as to start `telnetd.py` on boot:

	@reboot root    /usr/local/bin/telnetd.py -E TERM=ansi43m -E LANG=zh_CN.GB2312 -E LC_ALL=zh_CN.GB2312 -E LINES=25 -E COLUMNS=80 -E ERASECHAR=010
	@reboot frank   /usr/bin/tcpser -v 6401 -s 2400 -n"92163=127.0.0.1:23"

### DOSBox客户端使用方法

输入以下命令打开串口终端程序  
Run serial terminal program with the following command

	COMTOOL.COM 1 ^b6

在串口终端中输入`ATDT92163`连接telnet站点，然后按`Enter`进入登录界面。  
Input `ATDT92163` in the serial terminal, then press `Enter` to open login panel.


TX-console
----------

使用UCDOS自带的特显程序`TX.COM`，以显示不同字体和字号的中文，并绘制一些简单的图表。  
An environment use `TX.COM` (Special Display) shipped along with UCDOS to display Chinese characters in different sizes and fonts, as well as drawing some simple graphs.

可用的程序  
Applications available

* 飞控中心 (Flight Information Center)
* 猜数字控制台 (Control center for Bulls and Cows AI)
* 2048控制台 (Control center for 2048 AI)

DOSBox模拟的客户端硬件  
Client side hardware emulated by DOSBox

* Old 286 platform
* Hercules Monochrome display
* Floppy drive only
* Virtual serial line connection

客户端使用的软件  
Client side software

* MS-DOS 5.0
* UCDOS 7.0
* COMTOOL.COM

### 截图欣赏 Screenshots

![Startup](http://frank-deng.github.io/retro-works/startup-tx.png)

![Main Menu](http://frank-deng.github.io/retro-works/menu.png)

![Flight Control Center](http://frank-deng.github.io/retro-works/fgfs.png)

![Bulls and Cows AI](http://frank-deng.github.io/retro-works/guessnum-console.png)

![2048](http://frank-deng.github.io/retro-works/2048-console.png)


Notes 
-----

将原始硬盘镜像转换成VDI格式硬盘镜像  
Convert raw disk image into VDI format image

	VBoxManage convertdd source.img destination.vdi --format VDI

将VDI格式硬盘镜像转换成原始硬盘镜像  
Convert VDI format HDD image into raw one

	VBoxManage clonehd source.vdi destination.img --format RAW

Linux下挂载虚拟软盘（使用GB2312编码的文件名）  
Mount floppy image under Linux (Use GB2312 for filename encoding)

	sudo mount -o loop,codepage=936,iocharset=utf8 floppy.img /mnt

