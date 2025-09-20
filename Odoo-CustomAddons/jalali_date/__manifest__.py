
{
    "name": "Jalali Date",
    "summary": """Jalali Date""",
    "description": """Jalali Date""",
    "author": "Wahab Safi",
    "category": "Localization/Iran",
    "version": "1.0.1",
    "depends": [
        "base",
        "web",
        "appointment"
    ],
    "assets": {
        "web.assets_backend": [
            "jalali_date/static/src/luxon.js",
            "jalali_date/static/src/style.scss",
            "jalali_date/static/src/lib/*.js",
            (
                "before",
                "web/static/src/core/l10n/dates.js",
                "jalali_date/static/src/jutils.js",
            ),
            (
                "after",
                "web/static/src/core/l10n/dates.js",
                "jalali_date/static/src/l10n/dates.js",
            ),
            (
                "after",
                "web/static/src/search/utils/dates.js",
                "jalali_date/static/src/search/dates.js",
            ),
            "jalali_date/static/src/datetime_picker/*.js",
            "jalali_date/static/src/calendar/*.js",
        ],
        "web.assets_frontend": [
            "jalali_date/static/src/luxon.js",
            "jalali_date/static/src/jutils.js",
            "jalali_date/static/src/lib/persian-date.js",
            "jalali_date/static/src/appointment/select_appointment_slot.js",
        ],
        
        "web.fullcalendar_lib": [
            (
                "replace",
                "web/static/lib/fullcalendar/core/index.global.js",
                "jalali_date/static/src/fullcalendar/index.global.js"
            ),
        ],
        
        "point_of_sale._assets_pos": [
            "jalali_date/static/src/luxon.js",
            (
                "after",
                "web/static/src/core/l10n/dates.js",
                "jalali_date/static/src/l10n/dates.js",
            ),
            "jalali_date/static/src/jutils.js",
        ],
       
        
    },
}
