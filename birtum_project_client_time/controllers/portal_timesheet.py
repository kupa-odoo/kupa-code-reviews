# Part of Odoo. See LICENSE file for full copyright and licensing details.

from operator import itemgetter

from odoo import http
from odoo.fields import Domain
from odoo.tools import groupby as groupbyelem

from odoo.addons.hr_timesheet.controllers.portal import TimesheetCustomerPortal


class PortalTimesheetClientHours(TimesheetCustomerPortal):
    @http.route()
    def portal_my_timesheets(
        self, page=1, sortby=None, filterby=None, search=None, search_in="all", groupby="none", **kw
    ):
        response = super().portal_my_timesheets(
            page=page, sortby=sortby, filterby=filterby, search=search, search_in=search_in, groupby=groupby, **kw
        )

        if not hasattr(response, "qcontext"):
            return response

        values = response.qcontext
        searchbar_filters = values.get("searchbar_filters", {})
        pager = values.get("pager", {})
        Timesheet = http.request.env["account.analytic.line"]
        domain = Domain(Timesheet._timesheet_get_portal_domain())
        Timesheet_sudo = Timesheet.sudo()

        if not sortby:
            sortby = "date desc"
        if not filterby:
            filterby = "all"

        domain &= Domain(searchbar_filters[filterby]["domain"])
        if search and search_in:
            domain &= self._get_search_domain(search_in, search)
        if parent_task_id := kw.get("parent_task_id"):
            domain &= Domain("parent_task_id", "=", int(parent_task_id))

        field = None if groupby == "none" else groupby
        orderby = f"{field}, {sortby}" if field else sortby
        timesheets = Timesheet_sudo.search(domain, order=orderby, limit=100, offset=pager.get("offset", 0))
        if field:
            if groupby == "date":
                raw_timesheets_group = Timesheet_sudo._read_group(
                    domain, ["date:day"], ["client_time:sum", "id:recordset"], order="date:day desc"
                )
                grouped_timesheets = [(records, unit_amount) for __, unit_amount, records in raw_timesheets_group]
            else:
                time_data = Timesheet_sudo._read_group(domain, [field], ["client_time:sum"])
                mapped_time = {field.id: unit_amount for field, unit_amount in time_data}
                grouped_timesheets = [
                    (Timesheet_sudo.concat(*g), mapped_time[k.id])
                    for k, g in groupbyelem(timesheets, itemgetter(field))
                ]
        else:
            grouped_timesheets = (
                [(timesheets, Timesheet_sudo._read_group(domain, aggregates=["client_time:sum"])[0][0])]
                if timesheets
                else []
            )

        values.update({
            "timesheets": timesheets,
            "grouped_timesheets": grouped_timesheets,
        })
        return response
