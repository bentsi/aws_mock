from pathlib import Path

from flask import Flask, render_template

from aws_mock.lib import set_debug
from aws_mock.certificates import AWS_MOCK_DEFAULT_DIRNAME, AWS_MOCK_CA_CERTIFICATE_FILENAME


app = set_debug(Flask(__name__))


@app.route("/install-ca.sh")
def install_ca_sh() -> str:
    ca_cert_file = Path(AWS_MOCK_DEFAULT_DIRNAME) / AWS_MOCK_CA_CERTIFICATE_FILENAME
    return render_template(
        "admin/install-ca.sh",
        certificate=ca_cert_file.read_text(encoding="ascii"),
    )


if __name__ == "__main__":
    app.run(debug=True)
