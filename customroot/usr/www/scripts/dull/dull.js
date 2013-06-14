top.document.title = "(" + location.hostname + ") Alt-F " + document.title;

/* menus */

function MenuSetup() {
	document.writeln('<table cellspacing="0" cellpadding="0"><tr>')
	while (obj = menu.shift()) {
		if (typeof(obj.url) != "undefined") {
			document.writeln('<td><a class="Menu" href="', obj.url, '" target="content">',
				 obj.label, '</a></td>')
		} else {
			document.writeln('<td><div id="', obj.label, '" class="Menu">', obj.label,
				'</div><div id="', obj.label, '_sub">')
			while (sm = obj.smenu.shift()) {
				document.writeln('<a class="Menu" href="', sm.url,
					'" target="content">', sm.item, '</a>')
			}
			document.writeln('</div></td>')
			MenuEntry(obj.label)
		}
	}
	document.write('</tr></table>')
}

function MenuShow() {
	var menu = document.getElementById(this["m_id"])
	var smenu = document.getElementById(this["sm_id"])

	var top  = menu.offsetHeight - 1
	var left = 0

	while(menu) {
		top += menu.offsetTop
		left += menu.offsetLeft
		menu = menu.offsetParent
	}
	smenu.style.position = "absolute"
	smenu.style.top = top + 'px'
	smenu.style.left = left + 'px'
	smenu.style.visibility = "visible"
	smenu.style.display = "block"
}

function MenuHide() {
	var smenu = document.getElementById(this["sm_id"])
	smenu.style.visibility = "hidden"
	smenu.style.display = "none"
}

function MenuEntry(menu_id) {
	var menu = document.getElementById(menu_id)
	var smenu = document.getElementById(menu_id + "_sub")

	menu["m_id"] = menu.id
	menu["sm_id"] = smenu.id
	menu.onmouseover = MenuShow
	menu.onmouseout = MenuHide

	smenu["m_id"] = menu.id 
	smenu["sm_id"] = smenu.id
	smenu.style.position = "absolute"
	smenu.style.visibility = "hidden"
	smenu.style.display = "none"
	smenu.onmouseover = MenuShow
	smenu.onmouseout = MenuHide
}

/* tooltips */

var stat_id, stat_ev

function popDown(id) {
	if (stat_id)
		clearTimeout(stat_id);
	stat_id = null;
	document.getElementById(id).style.visibility = "hidden";
}

function popUp(ev, id) {
	if (stat_id)
		clearTimeout(stat_id);
	stat_ev = ev;
	stat_id = id;
	setTimeout("iPopUp()", 1000)
}

function iPopUp() {
	if (! stat_id)
		return;

	obj = document.getElementById(stat_id);
	stat_id = null

	objWidth = obj.offsetWidth;
	objHeight = obj.offsetHeight;

	y = stat_ev.pageY + 20;
	x = stat_ev.pageX - objWidth/4;

	if (x + objWidth > window.innerWidth)
		x -= objWidth/2;
	else if (x < 2)
		x = 2;

	if (y + objHeight > window.innerHeight)
		y -= 2*objHeight;

	obj.style.left = x + 'px';
	obj.style.top = y + 'px';
	obj.style.visibility = "visible";
}

/* bookmarks */

function commonbookmark() {
	try {
		x = parent.content.document.embedf
		title = x.ifname.value
		url = x.ifsrc.value
	} catch(err) {
		title = parent.content.document.title
		url = parent.content.document.location.pathname
	}
	return title + "&url=" + url
}

function addbookmark() {			
	parent.content.document.location.assign("/cgi-bin/bookmark.cgi?add=" + commonbookmark())
	return false
}

function rmbookmark() {
	parent.content.document.location.assign("/cgi-bin/bookmark.cgi?rm=" + commonbookmark())
	return false
}

function rmall() {
	try {
		url = parent.content.document.embedf.ifsrc.value
	} catch(err) {
		url = parent.content.document.location.pathname
	}
	parent.content.document.location.assign("/cgi-bin/bookmark.cgi?rm=all&url=" + url)
	return false
}
