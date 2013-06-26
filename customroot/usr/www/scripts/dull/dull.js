top.document.title = "(" + location.hostname + ") Alt-F " + document.title

/* menus */

function side_shortcuts(obj) {
	var sc = '<ul class="menu vmenu">'
	sc += '<li><label for="vmenu_' + obj.label + '"<a href="#">' + obj.label +
		'...</a></label><input type="checkbox" name="vmenu_radio" id="vmenu_' +
		obj.label + '"><ul>'

	while (sm = obj.smenu.shift()) {
		if (sm.item == "<hr>") {
			sc += '</ul></li></ul><ul class="short">'
			continue;
		}
		sc += '<li><a href="' + sm.url + '" target="content">' + sm.item + '</a></li>'
	}
	return sc += '</ul>'
}

function top_shortcuts(obj) {
	var sc = '<li><a href="#">' + obj.label + '</a><ul>'
	while (sm = obj.smenu.shift()) {
		if (sm.item == "<hr>") {
			sc += '<li><div><ul style="border:1px solid black" class="short">'
			continue;
		}
		sc += '<li><a href="' + sm.url + '" target="content">' + sm.item + '</a></li>'
	}
	return sc += '</ul></div></li></ul></li>'
}

function menuSetup(where, display) {
	var cl, frm, sc
	if (where == "side") {
		if (display == "no") {
			top.altf.cols="0,*" // hide nav frame
			return
		} else
			top.altf.cols="15%,*"
		frm = parent.nav.document
		cl = "vmenu"
	} else {
		if (display == "no")
			return
		frm = document
		cl = "hmenu"
	}

	frm.writeln('<div class="menu ', cl, '" id="sc_id"></div>')
	frm.writeln('<div class="menu ', cl, '"><ul>')
	while (obj = menu.shift()) {
		if (typeof(obj.url) != "undefined") { // no submenu, i.e., Logout, Status
			frm.writeln('<li><a href="', obj.url, '" target="content">', obj.label, '</a></li>')
		} else {
			if (obj.label == "Shortcuts") {
				if (where == "side")
					sc = side_shortcuts(obj)
				else
					sc = top_shortcuts(obj)
				document.getElementById("sc_id").innerHTML = sc
			} else {
				/* use 'radio' instead of 'checkbox' bellow to auto-close menus */
				frm.writeln('<li><label for="vmenu_', obj.label, '"<a href="#">', obj.label,
					'...</a></label><input type="checkbox" name="vmenu_radio" id="vmenu_',
					obj.label, '"><ul>')

				while (sm = obj.smenu.shift())
					frm.writeln('<li><a href="', sm.url, '" target="content">', sm.item, '</a></li>')
				frm.writeln('</ul></li>')
			}
		}
	}
	frm.writeln('</ul></div><br>')
}

/* tooltips */

var stat_id, stat_ev

function popDown(id) {
	if (stat_id)
		clearTimeout(stat_id)
	stat_id = null
	document.getElementById(id).style.visibility = "hidden"
}

function popUp(ev, id) {
	if (stat_id)
		clearTimeout(stat_id)
	stat_ev = ev
	stat_id = id
	setTimeout("iPopUp()", 1000)
}

function iPopUp() {
	if (! stat_id)
		return

	obj = document.getElementById(stat_id)
	stat_id = null

	objWidth = obj.offsetWidth
	objHeight = obj.offsetHeight

	y = stat_ev.pageY + 20
	x = stat_ev.pageX - objWidth/4

	if (x + objWidth > window.innerWidth)
		x -= objWidth/2
	else if (x < 2)
		x = 2

	if (y + objHeight > window.innerHeight)
		y -= 2*objHeight

	obj.style.left = x + 'px'
	obj.style.top = y + 'px'
	obj.style.visibility = "visible"
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
	return title + "&url=" + encodeURIComponent(url)
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
