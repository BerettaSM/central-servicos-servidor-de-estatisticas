import datetime as dt
import pandas as pd
import plotly.express as px
import bs4


class DataAnalyser:

    def get_basic_analysis(self, ticket_data, last_x_days: int):
        return self._perform_basic_analysis(ticket_data, last_x_days)

    def _perform_basic_analysis(self, ticket_data, last_x_days):
        today = dt.datetime.today()
        df = pd.read_json(ticket_data)
        # Cast columns to datetime, for proper handling.
        df['dateEnd'] = pd.to_datetime(df['dateEnd'])
        df['dateStart'] = pd.to_datetime(df['dateStart'])
        df['dateUpdated'] = pd.to_datetime(df['dateUpdated'])

        total_tickets = df.ticketId.count()

        # Total open tickets with high/highest priority.
        total_urgent_tickets = df.query(
            '(priority == "Alta" or priority == "Altíssima") and (statusId != 4 and statusId != 5)'
        )['ticketId'].count()

        # Total solved tickets(closed) on last X days.
        range_min = today - dt.timedelta(days=last_x_days)
        total_solved_tickets = df[(df.statusId == 4) & (df.dateStart >= range_min)]['ticketId'].count()

        # Percentage of tickets that are late. (open ticket and not on time)
        late_tickets = df.query('statusId == 1 and onTime == False')['ticketId'].count()
        percentage_late = (late_tickets / total_tickets) * 100
        late_tickets_data = {
            'late_tickets': int(late_tickets),
            'percentage_late': float(percentage_late)
        }

        # Percentage of tickets solved on time. (closed ticket and on time)
        solved_tickets_on_time = df.query('statusId == 4 and onTime == True')['ticketId'].count()
        percentage_solved_on_time = (solved_tickets_on_time / total_tickets) * 100
        on_time_tickets_data = {
            'solved_tickets_on_time': int(solved_tickets_on_time),
            'percentage_solved_on_time': float(percentage_solved_on_time)
        }

        # Average speed of ticket resolution. (Closed tickets/diff in between start date and end)
        closed_tickets = df.query('statusId == 4')
        diff = closed_tickets.dateUpdated - closed_tickets.dateStart
        diff_delta = diff.mean().to_pytimedelta()
        days = diff_delta.days
        hours = diff_delta.seconds // 3600
        minutes = (diff_delta.seconds % 3600) // 60
        ticket_resolution_average_speed = {
            'days': int(days),
            'hours': int(hours),
            'minutes': int(minutes)
        }

        chart_html = self._get_basic_chart_html(df, last_x_days)

        return {
            'total_urgent_tickets': int(total_urgent_tickets),
            'total_solved_tickets': int(total_solved_tickets),
            'late_tickets_data': late_tickets_data,
            'on_time_tickets_data': on_time_tickets_data,
            'ticket_resolution_average_speed': ticket_resolution_average_speed,
            'chart_html': chart_html
        }

    def _get_basic_chart_html(self, pd_dataframe, last_x_days: int):
        # Main chart: Quantity of tickets from last X days, by priority.
        today = dt.datetime.today()
        range_min = today - dt.timedelta(days=last_x_days)

        chart_df = pd_dataframe.copy()
        chart_df = chart_df[chart_df.dateStart >= range_min]
        chart_df.dateStart = chart_df.dateStart.dt.date
        chart_df = chart_df[['dateStart', 'priority', 'statusId']]
        priority_chart = chart_df.groupby(['dateStart', 'priority']).statusId.count().unstack('priority')

        fig = px.line(
            priority_chart,
            x=priority_chart.index,
            y=priority_chart.columns
        )

        fig.update_layout(
            title_text='Histórico de tickets criados, por prioridade',
            xaxis_title=f'Últimos {last_x_days} dias',
            yaxis_title='Tickets abertos',
            legend_title='Prioridade',
            font={
                'family': 'Roboto',
                'size': 20
            },
            legend={
                'font': {
                    'family': 'Roboto',
                    'size': 18
                }
            },

        )

        fig['data'] = (fig['data'][2], fig['data'][3], fig['data'][0], fig['data'][1])
        colors = ['#25BE75', '#FED402', '#FF8C00', '#FF0000']

        for i, c in enumerate(colors):
            fig['data'][i]['line']['color'] = c

        html = fig.to_html(full_html=False, include_plotlyjs=True)
        html = self._scrape_html_for_content(html)
        return html

    @staticmethod
    def _scrape_html_for_content(html):
        soup = bs4.BeautifulSoup(html, 'html.parser')
        chart_html = soup.select_one('div.plotly-graph-div')
        scripts = soup.select('script')
        scripts = [str(s.contents[0]) for s in scripts]
        return {'html': str(chart_html), 'scripts': scripts}

