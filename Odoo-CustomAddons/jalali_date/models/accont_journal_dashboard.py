from odoo.addons.account.models.account_journal_dashboard import group_by_journal
import json
import logging
import random
from collections import defaultdict
from datetime import datetime, timedelta

from babel.dates import format_date, format_datetime

from odoo import _, fields, models
from odoo.release import version
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.tools import SQL
from odoo.tools.misc import format_date as odoo_format_date
from odoo.tools.misc import get_lang

from persiantools.jdatetime import JalaliDate

_logger = logging.getLogger(__name__)


class jaccount_journal(models.Model):
    _inherit = "account.journal"


    def _get_json_activity_data(self):
        today = fields.Date.context_today(self)
        activities = defaultdict(list)
        # search activity on move on the journal
        act_type_name = self.env["mail.activity.type"]._field_to_sql("act_type", "name")
        
        sql_query = SQL(
            """
        SELECT activity.id,
                activity.res_id,
                activity.res_model,
                activity.summary,
                CASE WHEN activity.date_deadline < %(today)s THEN 'late' ELSE 'future' END as status,
                %(act_type_name)s as act_type_name,
                act_type.category as activity_category,
                activity.date_deadline,
                move.journal_id
        FROM account_move move
        JOIN mail_activity activity ON activity.res_id = move.id AND activity.res_model = 'account.move'
        LEFT JOIN mail_activity_type act_type ON activity.activity_type_id = act_type.id
        WHERE move.journal_id = ANY(%(ids)s)
            AND move.company_id = ANY(%(company_ids)s)
    
    UNION ALL
    
        SELECT activity.id,
                activity.res_id,
                activity.res_model,
                activity.summary,
                CASE WHEN activity.date_deadline < %(today)s THEN 'late' ELSE 'future' END as status,
                %(act_type_name)s as act_type_name,
                act_type.category as activity_category,
                activity.date_deadline,
                journal.id as journal_id
        FROM account_journal journal
        JOIN mail_activity activity ON activity.res_id = journal.id AND activity.res_model = 'account.journal'
        LEFT JOIN mail_activity_type act_type ON activity.activity_type_id = act_type.id
        WHERE journal.id = ANY(%(ids)s)
            AND journal.company_id = ANY(%(company_ids)s)
            """,
            today=today,
            act_type_name=act_type_name,
            ids=self.ids,
            company_ids=self.env.companies.ids,
        )
        self.env.cr.execute(sql_query)
        for activity in self.env.cr.dictfetchall():
            act = {
                "id": activity["id"],
                "res_id": activity["res_id"],
                "res_model": activity["res_model"],
                "status": activity["status"],
                "name": activity["summary"] or activity["act_type_name"],
                "activity_category": activity["activity_category"],
                # "date": odoo_format_date(self.env, activity["date_deadline"]),
                "date": JalaliDate(activity["date_deadline"]).strftime("%Y/%m/%d"),
            }
    
            activities[activity["journal_id"]].append(act)
        for journal in self:
            journal.json_activity_data = json.dumps({"activities": activities[journal.id]})
    
    
    def _get_bank_cash_graph_data(self):
        """Computes the data used to display the graph for bank and cash journals in the accounting dashboard"""
    
        def build_graph_data(date, amount, currency):
            # display date in locale format
            name = format_date(date, "d LLLL Y", locale=locale)
            short_name = format_date(date, "d MMM", locale=locale)
            return {"x": short_name, "y": currency.round(amount), "name": name}
    
        today = datetime.today()
        last_month = today + timedelta(days=-30)
        locale = get_lang(self.env).code
    
        query = """
            SELECT move.journal_id,
                move.date,
                SUM(st_line.amount) AS amount
            FROM account_bank_statement_line st_line
            JOIN account_move move ON move.id = st_line.move_id
            WHERE move.journal_id = ANY(%s)
            AND move.date > %s
            AND move.date <= %s
            AND move.company_id = ANY(%s)
        GROUP BY move.date, move.journal_id
        ORDER BY move.date DESC
        """
        self.env.cr.execute(query, (self.ids, last_month, today, self.env.companies.ids))
        query_result = group_by_journal(self.env.cr.dictfetchall())
    
        result = {}
        for journal in self:
            graph_title, graph_key = journal._graph_title_and_key()
            # User may have read access on the journal but not on the company
            currency = journal.currency_id or self.env["res.currency"].browse(
                journal.company_id.sudo().currency_id.id
            )
            journal_result = query_result[journal.id]
    
            color = "#875A7B" if "e" in version else "#7c7bad"
            is_sample_data = not journal_result and not journal.has_statement_lines
    
            data = []
            if is_sample_data:
                for i in range(30, 0, -5):
                    current_date = today + timedelta(days=-i)
                    data.append(
                        build_graph_data(current_date, random.randint(-5, 15), currency)
                    )
                    graph_key = _("Sample data")
            else:
                last_balance = journal.current_statement_balance
                data.append(build_graph_data(today, last_balance, currency))
                date = today
                amount = last_balance
                # then we subtract the total amount of bank statement lines per day to get the previous points
                # (graph is drawn backward)
                for val in journal_result:
                    date = val["date"]
                    if date.strftime(DF) != today.strftime(
                        DF
                    ):  # make sure the last point in the graph is today
                        data[:0] = [build_graph_data(date, amount, currency)]
                    amount -= val["amount"]
    
                # make sure the graph starts 1 month ago
                if date.strftime(DF) != last_month.strftime(DF):
                    data[:0] = [build_graph_data(last_month, amount, currency)]
    
            result[journal.id] = [
                {
                    "values": data,
                    "title": graph_title,
                    "key": graph_key,
                    "area": True,
                    "color": color,
                    "is_sample_data": is_sample_data,
                }
            ]
        return result
    
    
    def _get_sale_purchase_graph_data(self):
        today = fields.Date.today()
        day_of_week = int(format_datetime(today, "e", locale=get_lang(self.env).code))
        first_day_of_week = today + timedelta(days=-day_of_week + 1)
        format_month = lambda d: JalaliDate(d).strftime("%B",locale="fa")
        
    
        self.env.cr.execute(
            """
            SELECT move.journal_id,
                COALESCE(SUM(move.amount_residual_signed) FILTER (WHERE invoice_date_due < %(start_week1)s), 0) AS total_before,
                COALESCE(SUM(move.amount_residual_signed) FILTER (WHERE invoice_date_due >= %(start_week1)s AND invoice_date_due < %(start_week2)s), 0) AS total_week1,
                COALESCE(SUM(move.amount_residual_signed) FILTER (WHERE invoice_date_due >= %(start_week2)s AND invoice_date_due < %(start_week3)s), 0) AS total_week2,
                COALESCE(SUM(move.amount_residual_signed) FILTER (WHERE invoice_date_due >= %(start_week3)s AND invoice_date_due < %(start_week4)s), 0) AS total_week3,
                COALESCE(SUM(move.amount_residual_signed) FILTER (WHERE invoice_date_due >= %(start_week4)s AND invoice_date_due < %(start_week5)s), 0) AS total_week4,
                COALESCE(SUM(move.amount_residual_signed) FILTER (WHERE invoice_date_due >= %(start_week5)s), 0) AS total_after
            FROM account_move move
            WHERE move.journal_id = ANY(%(journal_ids)s)
            AND move.state = 'posted'
            AND move.payment_state in ('not_paid', 'partial')
            AND move.move_type IN %(invoice_types)s
            AND move.company_id = ANY(%(company_ids)s)
        GROUP BY move.journal_id
        """,
            {
                "invoice_types": tuple(self.env["account.move"].get_invoice_types(True)),
                "journal_ids": self.ids,
                "company_ids": self.env.companies.ids,
                "start_week1": first_day_of_week + timedelta(days=-7),
                "start_week2": first_day_of_week + timedelta(days=0),
                "start_week3": first_day_of_week + timedelta(days=7),
                "start_week4": first_day_of_week + timedelta(days=14),
                "start_week5": first_day_of_week + timedelta(days=21),
            },
        )
        query_results = {r["journal_id"]: r for r in self.env.cr.dictfetchall()}
        result = {}
        for journal in self:
            # User may have read access on the journal but not on the company
            currency = journal.currency_id or self.env["res.currency"].browse(
                journal.company_id.sudo().currency_id.id
            )
            graph_title, graph_key = journal._graph_title_and_key()
            sign = 1 if journal.type == "sale" else -1
            journal_data = query_results.get(journal.id)
            data = []
            data.append({"label": _("Due"), "type": "past"})
            for i in range(-1, 3):
                if i == 0:
                    label = _("This Week")
                else:
                    start_week = JalaliDate(first_day_of_week) + timedelta(days=i * 7)
                    end_week = start_week + timedelta(days=6)
                    if start_week.month == end_week.month:
                        label = (
                            f"{start_week.day} - {end_week.day} {format_month(end_week)}"
                        )
                    else:
                        label = f"{start_week.day} {format_month(start_week)} - {end_week.day} {format_month(end_week)}"
                data.append({"label": label, "type": "past" if i < 0 else "future"})
            data.append({"label": _("Not Due"), "type": "future"})
    
            is_sample_data = not journal_data
            if not is_sample_data:
                data[0]["value"] = currency.round(sign * journal_data["total_before"])
                data[1]["value"] = currency.round(sign * journal_data["total_week1"])
                data[2]["value"] = currency.round(sign * journal_data["total_week2"])
                data[3]["value"] = currency.round(sign * journal_data["total_week3"])
                data[4]["value"] = currency.round(sign * journal_data["total_week4"])
                data[5]["value"] = currency.round(sign * journal_data["total_after"])
            else:
                for index in range(6):
                    data[index]["type"] = "o_sample_data"
                    # we use unrealistic values for the sample data
                    data[index]["value"] = random.randint(0, 20)
                    graph_key = _("Sample data")
    
            result[journal.id] = [
                {
                    "values": data,
                    "title": graph_title,
                    "key": graph_key,
                    "is_sample_data": is_sample_data,
                }
            ]
        return result
