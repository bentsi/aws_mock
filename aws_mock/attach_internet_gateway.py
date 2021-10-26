from flask import render_template


def attach_internet_gateway() -> str:
    return render_template("responses/attach_internet_gateway.xml")
