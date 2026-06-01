# analytics/trend_html.py

def generate_html(trend):
    html = f"""
    <html>
    <head><title>Performance Trend</title></head>
    <body>
        <h1>Last 5 Runs Trend</h1>

        <h3>Response Time</h3>
        <p>{trend['avg_response_time']}</p>

        <h3>Error Rate</h3>
        <p>{trend['error_rate']}</p>

    </body>
    </html>
    """

    with open("results/trend/trend.html", "w") as f:
        f.write(html)