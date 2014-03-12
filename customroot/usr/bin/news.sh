#!/bin/sh

# script to execute once/twice a week,
# updates news.log with new files/announcements since NEWS_CHK
# update NEWS_CHK in misc.conf
#
# Status checks for news.log, and if its date is more recent than NEWS_ACK show the warning.
# If the user ack the news, update NEWS_ACK

MISCC=/etc/misc.conf
LOGF=/var/log/news.log

FILES_URL=http://sourceforge.net/api/file/index/project-id/796573/crtime/asc/rss
NEWS_URL=http://sourceforge.net/p/alt-f/news/feed

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

# $1-rss url, $2-most recent item date
parse_rss() {
	wget -q -O - "$1" | \
	sed -e 's/<item>/\n<item>/' -e 's/<title>/\n<title>/' -e 's/<pubDate>/\n<pubDate>/' | \
	awk -v last_chk="$2" -v logf="$LOGF" '
	BEGIN {
		w["Jan"]="01"; w["Feb"]="02"; w["Mar"]="03"; w["Apr"]="04"; w["May"]="05"; w["Jun"]="06";
		w["Jul"]="07"; w["Aug"]="08"; w["Sep"]="09"; w["Oct"]=10; w["Nov"]=11; w["Dec"]=12;
#printf("current:%s %s\n", strftime("%Y-%b-%d %H:%M:%S", systime()), systime())  > "/dev/stderr"
	}
	/<item>/,/<\/item>/{
		if (match($0,"<title>")) {
			item = gensub(".*<title>(.*)</title>.*","\\1","g");
			if (match(item,"CDATA"))
				item = gensub("<!\\[CDATA\\[(.*)\\]\\]>","\\1","g",item);
		}
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
#printf("%s %s %s\n", dt, ts, item) > "/dev/stderr"
			if (ts > last_chk) { # log everything published since the last check
#printf("NEW: %s %s\n", dt, item)
				printf("%s %s\n", dt, item) >> logf
			}
			if (ts > last_rel) # items can be out of order, so record the latest date
				last_rel = ts;
		}
	}
	END {
		print last_rel
	}'
}

if test -s $MISCC; then
	. $MISCC
fi

if test -z "$NEWS_CHK" -o -z "$FILES_CHK"; then # FIXME: to remove after RC4
	#echo NEWS_CHK=$(date +%s) >> $MISCC
	#echo FILES_CHK=$(date +%s) >> $MISCC
	eval $(grep NEWS_CHK /rootmnt/ro/etc/misc.conf)
	echo NEWS_CHK=$NEWS_CHK >> $MISCC
	eval $(grep FILES_CHK /rootmnt/ro/etc/misc.conf)
	echo FILES_CHK=$FILES_CHK >> $MISCC
fi

last_files=$(parse_rss $FILES_URL $FILES_CHK)
#last_files=$(parse_rss /root/rss $FILES_CHK)
#echo last_files=$last_files

# update last check date with date of most recent item
if test "$last_files" -gt "$FILES_CHK"; then
	sed -i '/^FILES_CHK=/d' $MISCC
	echo FILES_CHK=$last_files >> $MISCC
fi

last_news=$(parse_rss $NEWS_URL $NEWS_CHK)
#last_news=$(parse_rss /root/feed $NEWS_CHK)
#echo last_news=$last_news

if test "$last_news" -gt "$NEWS_CHK"; then
	sed -i '/^NEWS_CHK=/d' $MISCC
	echo NEWS_CHK=$last_news >> $MISCC
fi
