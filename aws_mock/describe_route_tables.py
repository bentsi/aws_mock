from flask import render_template


def describe_route_tables() -> str:
    return render_template(
        "responses/describe_route_tables.xml",
        route_table_id='rtb-0177edc4ef11712e8',
        vpc_id='vpc-0b04728271b54803d',
    )
