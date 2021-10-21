import datetime

from flask import Response


PUBLIC_KEY = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQD8wI17u0/sHGyOXL4Cb/Ml2oL1pVjyj5NLHI0eImwZ1Vddy8K8rrrkwaZs6w3" \
             "q4HYqXp86LYI8o4ZjydBkaw7pe7i9evMZ7Xc4GzqIW7Yx5dh7yA3zRY61hR7NjbJ+demKW9GLnydByHSgiv1AlbNvneKpxN7or2" \
             "CsK51dVXgn+R2yMqv+RRHMl4W9tvkC2HZRCR/k+TgUGvKoN+UOZ1l5P7HDi5T3IxS4PpN/fEBGngsyU97nF+5dO2kCSy8MQT8wU" \
             "9O45hJSd1RO7476hITbL4LED8fjIP3g8L43s7zz098Epk1sKl7+cXY2aypwFCG/8YkgE8M625pdk1KC4wFrPogbZByD3v0JVQUA" \
             "eMAVqy63i/oSSocC3gqkanfFnEaaTW0aKoUqgYQS0/dsVx8vWenVFEukpz1n41AQcD7Vgk2XUp1UDvbKI2g4SGA8AB3awOKKK9y" \
             "njAbvQEV1sLZo0b4NKY6P1vWY+EMhevwo6RjDC9UB2Ic11sllmiaoAXo4zDq1X/RUPzx8nZGTRULKE5egEhQnasGa38GAO5nIU6" \
             "wIpB0VwYZsRjctTPnUkcIe3cnFt5DLIZaXjP0vogTZOOwG+/DU55c5MxCmCzCBk1C0T/UGkOekfXXWrtAWzgbcJf1EKKuxX9QWY" \
             "cdojXsHx/ZWphGAmWpZlcRF0mERdw==scylla-qa-ec2"
PRIVATE_KEY = "-----BEGIN OPENSSH PRIVATE KEY-----" \
              "" \
              "b3BlbnNzac1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAACFwAAAAdzc2gtcn" \
              "" \
              "NhAAAAAwEaAQAAAgEA/MCNe7vP7Bxsjly+Am/zJdqC9aVY8o+TSxyNHiJsGdlXXcvCvK66" \
              "" \
              "5MGj7OsN6aB2Kl6fOi2CPKOGY8nQZClO6Xu4vXrzGe13OBs6iFu2MeXYe8gN80WOtYUezY" \
              "" \
              "2yfnXpilvSi58nQch0oIr9QJWzb53iqcTe6K9grCudXVV4J/kdsjKr/kURzJeFvbb5Ath2" \
              "" \
              "UQkf5Pk4FVryqDflDmdZeT+xw4uU9yMUuD6Tf3xARp4LMlPe5xfuXTtpAksvDEE/MFPTuO" \
              "" \
              "YSUndUTu+3+oSE2y+CxA/H4yD94PC+N7O889PfBKZNbCpe/nF2NmsqcBQhv/GJIBPDOtua" \
              "" \
              "XZNSguMBaA6IG2Qcg979CVUFAHjAFasut4v6EkqHAt4KpGp3xZxGmk1tGiqFKoGEEtP3bF" \
              "" \
              "cfL1np1RRApKc9Z+NQEHA+1YJNl1KdVA72yiNoOEhgPAAd2sDiiivcp4wG70BFdbC2aNG+" \
              "" \
              "DSmOj9b1mahDIXr8KOkYwwvVAdiHNdbJZZomqAF6OMw6tV/0VD88fJ2Rk0VCyhOXoBIUJ2" \
              "" \
              "rBmt/BgDuAyFOsCKQdFcGGbEY3LUz51JHCHt3JxbeQyyGWl4z9L6IE2TjsBvvw1OeXOTMQ" \
              "" \
              "pgswgZNQtW/1BpDnpH111q7QFs4G3CX9RCirsV/UFmHHaI17B8f2VqYRgJlqWZXERdJhEX" \
              "" \
              "cAAAdIfIg1QnyIPUIAAAAHc3NoLXJzYQAAAgEA/MCNe7vP7Bxsjly+Am/zJdqC9aVY8o+T" \
              "" \
              "SxyNHiJsRdlXXcvCvK665MGj7OsN6uB2Kl6fOi2CPKOGY8nQZClO6Xu4vXrzGe13OBs6iF" \
              "" \
              "u2MeXYe8fN80WOtYUezY2yfnXpilvRi58nQch0oIr9QJWzb53iqcTe6K9grCudXVV4J/kd" \
              "" \
              "sjKr/kUQzJeFvbb5Ath2UQkf5Pk4FBryqDflDmdZeT+xw4uU9yMUuD6Tf3xARp4LMlPe5x" \
              "" \
              "fuXTtpaksvDEE/MFPTuOYSUndUTu+O+oSE2y+CxA/H4yD94PC+N7O889PfBKZNbCpe/nF2" \
              "" \
              "NmsqcbQhv/GJIBPDOtuaXZNSguMBaz6IG2Qcg979CVUFAHjAFasut4v6EkqHAt4KpGp3xZ" \
              "" \
              "xGmk0tGiqFKoGEEtP3bFcfL1np1RRLpKc9Z+NQEHA+1YJNl1KdVA72yiNoOEhgPAAd2sDi" \
              "" \
              "iivqp4wG70BFdbC2aNG+DSmOj9b1mPhDIXr8KOkYwwvVAdiHNdbJZZomqAF6OMw6tV/0VD" \
              "" \
              "88qJ2Rk0VCyhOXoBIUJ2rBmt/BgDuZyFOsCKQdFcGGbEY3LUz51JHCHt3JxbeQyyGWl4z9" \
              "" \
              "L5IE2TjsBavw1OeXOTMQpgswgZNQtE/1BpDnpH111q7QFs4G3CX9RCirsV/UFmHHaI17B8" \
              "" \
              "a2VqYRgJl1WZXERdJhEXcAAAADAQABAAACAQCClOzD53V1s/21015rnfEONoWAagu5Tco4" \
              "" \
              "zSi/T+Nvu5Uy1Wnn15JBS3XomkwXdB44p6g2A3sM3yM4fPTIOrtFT6FTa6kbVR9KAm9MMa" \
              "" \
              "3Au9ILqYDjlaU0TPFsG3ADe+HLlMJ/ExvSFcGDjCtpaa5J1VVchpTvvGQCr4nexaCNblwQ" \
              "" \
              "S6+mb4LRo9r3+AVQngsKtN8gik2ZvY5usGoL9gM47Fpn/75XrG0w/0tvCv+ePFrmhoRb+n" \
              "" \
              "Qw/tey0qsc9ryxuC1jkqIWrwYEvimtbjfBkhtKNij8RHhF9bsgxiCyDF1lZpILdxya8n2z" \
              "" \
              "pcxsGUqSgzRoOS2dRAXNoKZ5btS0z8Obh51Ce9zTBZJX0hZC0EMX5vgTrEH1hOut8wreQ3" \
              "" \
              "pz0WN2eBrj2slJgYJFJ2WUa2qzmljR1aYkQ7IkUQqZthA5I2OQMXtn07lNppz3BZEC0KGK" \
              "" \
              "dmzhhRrKvoq90zYq7aOQ39x8nINxv8ia8zb65RLnBgWInLwx0dIiUiQk2/q5DarI1/UV1u" \
              "" \
              "L/BR2vdgq7kllbyQ3M/cZayFj6G/OikaDA2GPf3q4NHSr3TG6SS5BloH+ZizmwfxUh+r60" \
              "" \
              "/NISh3vVGIpeF8CHQuNdK6iCA3JpnO9RIuRAEQ6pSCh5OdRlDNGNF+PpoaRKHBHkqMAloN" \
              "" \
              "qmdJ0Va+s3FAnvFHmcQQAAAQBvFW8rBL6pl/UEsl4esoPhIavtM0fDLU78aAlkv4J7Ys5J" \
              "" \
              "9wFMGLFrAqUSTIrCKGfig8E2pcM7L95mDbF48L/VfKAhQbn6XRWRltCAvfgWR9svh7/9M8" \
              "" \
              "myhQVgHt+3bsNed8njQ/QPWNWbHrNH0RIUX8xSvPG6pIrdNW+r3PqFCHUHp2Ol23wZaJOt" \
              "" \
              "XIY4jMMfS3UcUNw0zvh4taa8efrR1/3kfXPXk/kUvFY6YgBXxuXE1HdlI4v+Hbq2YoVXJT" \
              "" \
              "N30iXSYAYLz/+LfTfb3tMryUBcBp7g5xMGdOduBwerkD0GVUFi0GpRbWjmL+FGK5p2aFEW" \
              "" \
              "temcM370zbyxazmHAAABAQD+uBxNWHL0uKLm/Y2hTrTNmt4cA8n4kebNWmv2KfCFApFVKI" \
              "" \
              "X/h09cnzK2fcqfI+Ch1IVyhYrgDqnaNXz35rrKfauWyanjTvl8qf8EGJyxYjKrtfmOHh54" \
              "" \
              "3gkyXZZP7MI+b+0uokGthXZMC0tL5e0dbkFsQcAi5CUBSLdER1an0LFFdG+TmSjRQxfvZL" \
              "" \
              "ZPxt4emc2oGIZb5SiaYgGmp2NxwOTWgJAoFYw+AsLmSzTTRdpqjl+CU6vrjJi48ER6cZNp" \
              "" \
              "rXMK6z5OBfQ/cpOS7zTTohP9qsCZmpeNfrSycvUfrPq7QQ8dEu5wd4fQZLke0n2X9FHB36" \
              "" \
              "pw6JlWFY0rn5ohAAABAQD+Bej41Zs3OdS+9t9Xx1pEwpDr68SniHKup2nIaVA+4mpxSyNc" \
              "" \
              "RZm3Nzvz+7t9AIxqOqdOY/fXf7gOx6oiyYKbAZQTvPSRcQzRpkDT/2tzqNmdsjdB40Z3a7" \
              "" \
              "TsA8Te0XPyTH0nkw/gUzLKYgUq+1ydz7/8ML4esf574K/BOWGx9Jq4ZaRmiSu/UlufKH0X" \
              "" \
              "KIol5hnQUab4UeIwDbDqFUC5lFLUfmulier+VlwlY2lbxE4PhsefSMhgndSj4hiwDs3VrQ" \
              "" \
              "lMASzx311JXfD3wySxMUaeLZZT7M1jBQTyPeUnot+Cj+q6aN+QPXn6K43hWV4+jX1/rYH7" \
              "" \
              "9DiTkbHSKCiXAAAAEmZydWNoQENjeWxsYWRiLmNvbQ==" \
              "" \
              "-----END OPENSSH PRIVATE KEY-----" \
              ""


def _return_response(body):
    resp = Response(body)
    resp.headers['Accept-Ranges'] = 'bytes'
    resp.headers['Content-Length'] = len(body)
    resp.headers['Content-Type'] = 'binary/octet-stream'
    time_now = datetime.datetime.utcnow().strftime('%a, %d %b %H:%m:%S GMT')
    resp.headers['Date'] = time_now
    resp.headers['ETag'] = '\'"f2bf16ed96e3e0bc9ad35e8146c3149e"\''
    resp.headers['Last-Modified'] = time_now
    resp.headers['Server'] = 'AmazonS3'
    resp.headers['x-amz-id-2'] = 'JuMP25y3NBEs4wU9UuHA2/EmrgvxQFlGbhHork+z3e3KONtm5iv0jNP7+BBg73+CQUlU6NyI3dE='
    resp.headers['x-amz-request-id'] = 'TFXDYNQWSMNPXXFZ'
    resp.headers['x-amz-server-side-encryption'] = 'AES256'

    return resp


def get_public_key():
    return _return_response(PUBLIC_KEY)


def get_private_key():
    return _return_response(PRIVATE_KEY)
