# Django Template Variable Formatting

## The Problem

Template variables were written with `{{` on one line and the variable + `}}` on the next:

```django
<p class="...">{{
    next_tour.location }}</p>
```

**Result:** Django treats everything between `{{` and `}}` as the expression, but the **whitespace (newline + indentation) before the variable is included in the rendered output**. So instead of clean `NAIROBI, KE`, the HTML received extra spaces and a newline, affecting layout and display.

The same issue occurred with date filters: split across lines, the output included unwanted whitespace between the day, month, and weekday.

## The Fix

1. **Single line** – Put the full `{{ variable }}` or `{{ variable|filter }}` on one line so no extra whitespace is rendered.

2. **Timezone for dates** – With `USE_TZ=True`, datetimes are stored in UTC. Add `|localtime` before `|date` so they display in the active timezone; otherwise you may see the wrong day (e.g. midnight UTC showing as the previous day in other zones).

3. **Load tz** – Add `{% load tz %}` at the top of the template when using the `localtime` filter.

---

## Rule

Keep Django template variables on a **single line** to avoid unwanted whitespace in rendered output.

### Do

```django
{{ next_tour.location }}
{{ next_tour.date|localtime|date:'d' }}
{{ next_tour.date|localtime|date:'M' }}
{{ next_tour.date|localtime|date:'l' }}
{{ next_tour.venue }}
```

### Don't

```django
{{
    next_tour.location }}
{{
    next_tour.date|localtime|date:'d' }}
```

Splitting `{{` and `variable }}` across lines injects newlines and spaces into the output.

## DateTimeField with Timezones

When displaying dates from `DateTimeField` with `USE_TZ=True`, use the `localtime` filter before `date` so values render in the active timezone:

```django
{% load tz %}
{{ next_tour.date|localtime|date:'d' }}
{{ next_tour.date|localtime|date:'M' }}
{{ next_tour.date|localtime|date:'l' }}
```
