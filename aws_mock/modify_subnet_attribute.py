from flask import render_template


def modify_subnet_attribute() -> str:
    return render_template("responses/modify_subnet_attributes.xml")
