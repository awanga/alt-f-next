#!/bin/sh

# script to execute once a week,
# updates news.log with new files since NEWS_CHK
# update NEWS_CHK in misc.conf
#
# Status checks for news.log, and if its date is more recent than NEWS_ACK show the warning.
# If the user ack the news, update NEWS_ACK

MISCC=/etc/misc.conf
LOGF=/var/log/news.log
NEWS_URL="http://sourceforge.net/api/file/index/project-id/796573/crtime/asc/rss"

if test -s $MISCC; then
	. $MISCC
fi

if test -z "$NEWS_CHK"; then
	first=yes
	NEWS_CHK=$(date +%s)
fi

# RSS file format:
# <item>
#   <title><![CDATA[/Releases/0.1RC3/README-0.1RC3.txt]]></title>
#   <link>http://sourceforge.net/projects/alt-f/files/Releases/0.1RC3/README-0.1RC3.txt/download</link>
#   <guid>http://sourceforge.net/projects/alt-f/files/Releases/0.1RC3/README-0.1RC3.txt/download</guid>
#   <description><![CDATA[/Releases/0.1RC3/README-0.1RC3.txt]]></description>
#   <pubDate>Fri, 29 Mar 2013 18:38:25 +0000</pubDate>
#   <files:sf-file-id xmlns:files="http://sourceforge.net/api/files.rdf#">7845912</files:sf-file-id>
#   <files:extra-info xmlns:files="http://sourceforge.net/api/files.rdf#">English text</files:extra-info>
#   <media:content xmlns:media="http://video.search.yahoo.com/mrss/" type="text/plain; charset=us-ascii" url="http://sourceforge.net/projects/alt-f/files/Releases/0.1RC3/README-0.1RC3.txt/download" filesize="3170">
#     <media:title></media:title>
#     <media:hash algo="md5">c43e012fa51fab06616b04abc0ae8e60</media:hash>
#   </media:content>
# </item>

last_rel=$(wget -q -O - $NEWS_URL | tee /root/rss | awk -v last_chk="$NEWS_CHK" -v logf="$LOGF" '
	BEGIN {
		w["Jan"]="01"; w["Feb"]="02"; w["Mar"]="03"; w["Apr"]="04"; w["May"]="05"; w["Jun"]="06";
		w["Jul"]="07"; w["Aug"]="08"; w["Sep"]="09"; w["Oct"]=10; w["Nov"]=11; w["Dec"]=12;
		#printf("current:%s\n", strftime("%Y-%b-%e %H:%M:%S", systime()))
	}
	/<item>/,/<\/item>/{
		if (match($0,"<title>"))
			item = gensub("<title><!\\[CDATA\\[(.*)\\]\\]></title>","\\1","g");
		if (match($0,"filesize=\"\"")) { # skip itens with no size (directories)
			while (! match($0,"</item>"))
				getline
			next
		}
		if (match($0,"<pubDate>")) {
			split($0, a);
			dt = sprintf("%s-%s-%s %s", a[4], a[3], a[2], a[5]);

			split(a[5], h, ":");
			ts = mktime(sprintf("%s %s %s %s %s %s", a[4], w[a[3]], a[2], h[1], h[2], h[3]));
		}
		if (match($0,"</item>")) {
			if (ts > last_chk)
				printf("%s %s\n",dt, item) >> logf
			if (ts > last_rel)
				last_rel = ts;
		}
	}
	END {
		print last_rel
	}
')

if test -n "$first" -o "$last_rel" -gt "$NEWS_CHK"; then
	sed -i '/^NEWS_CHK=/d' $MISCC
	echo NEWS_CHK=$last_rel >> $MISCC
fi
