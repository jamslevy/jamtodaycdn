# Copyright 2008 Thomas Quemard
#
# Paste-It is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published
# by the Free Software Foundation; either version 3.0, or (at your option)
# any later version.
#
# Paste-It is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public
# License for more details.

import cgi
import paste_app.paste
import paste_app.paste.model
import paste_app.paste.web
import paste_app.paste.web.ui

class Index(paste_app.paste.web.RequestHandler):
    def __init__(self):
        paste_app.paste.web.RequestHandler.__init__(self)
        self.set_module("page.pasties.index")
        self.page = 1
        self.pastes_per_page = 10

    def get(self):
        if self.request.get("page").isdigit() and int(self.request.get("page")) > 1:
            self.page = int(self.request.get("page"))

        db = paste_app.paste.model.Pasty.all()
        db.order("-posted_at")
        dbpastes = db.fetch(self.pastes_per_page, (self.page - 1) * self.pastes_per_page)
        pastes = []

        if dbpastes != None:
            for opaste in dbpastes:
                dpaste = {}
                if opaste.title != None:
                    dpaste["title"] = cgi.escape(opaste.title)
                else:
                    dpaste["title"] = cgi.escape(opaste.slug)
                dpaste["u"] = paste_app.paste.url("%s", opaste.slug)

                if opaste.posted_by_user_name != None:
                    dpaste["user_name"] = cgi.escape(opaste.posted_by_user_name)
                else:
                    dpaste["user_name"] = "Anonymous"

                if opaste.posted_at != None:
                    dpaste["posted_at"] = opaste.posted_at.strftime("%b, %d %Y")
                else:
                    dpaste["posted_at"] = ""
                pastes.append(dpaste)

        paste_count = self.get_paste_count()

        paging = paste_app.paste.web.ui.CursorPaging()
        paging.page = self.page
        paging.items = paste_count
        paging.page_length = 10
        paging.left_margin = 2
        paging.right_margin = 2
        paging.cursor_margin = 1
        paging.page_url = paste_app.paste.url("pastes/?page={page}")
        paging.prepare()

        if paging.page_count > 1:
            self.content["pages"] = paging.pages
        self.content["paste_count"] = paste_count
        self.content["pastes"] = pastes
        self.use_template("page/pasties/index/200.html")
        self.write_out()

    def get_paste_count(self):
        count = 0
        stats = paste_app.paste.model.PasteStats.all()
        stats.id = 1
        stat = stats.get()
        if stat != None:
            count = stat.paste_count
        return count
