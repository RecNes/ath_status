import base64
from datetime import timedelta

import plotly.express as px
from django import template
from django.utils import timezone

register = template.Library()


@register.simple_tag
def get_graph(exchange_currency, day_range):
    end_datetime = timezone.now()
    start_datetime = end_datetime - timedelta(days=int(day_range))
    currency_data_qs = exchange_currency.exchangerate_set.filter(
        record_date__gte=start_datetime,
        record_date__lt=end_datetime
    ).order_by("record_date")
    date_list = list()
    rate_list = list()
    for item in currency_data_qs:
        date_list.append(item.record_date)
        rate_list.append(item.exchange_rate)
    if not date_list or not rate_list:
        return
    fig = px.line(None, x=date_list, y=rate_list)
    fig.update_xaxes(visible=False, fixedrange=True)
    fig.update_yaxes(visible=False, fixedrange=True)
    fig.update_layout(annotations=[], overwrite=True)
    fig.update_layout(
        showlegend=False,
        plot_bgcolor="white",
        margin=dict(t=5, l=0, b=5, r=0)
    )
    fig_image = fig.to_image(format="png", width=300, height=50)
    decoded = base64.b64encode(fig_image).decode('ascii')
    return decoded
