import random



def get_tls() -> str:
    """
    Modify encryption logic of tls fingerprint
    """
    tls = 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:ECDHE-RSA-AES128-SHA:ECDHE-RSA-AES256-SHA:AES128-GCM-SHA256:AES256-GCM-SHA384:AES256-SHA:AES128-SHA:DES-CBC3-SHA:ECDHE-RSA-AES256-SHA384:ECDHE-RSA-AES128-SHA256'
    ciphers = tls.split(":")
    new_ciphers = []
    while ciphers:
        random_cipher = random.choice(ciphers)
        new_ciphers.append(random_cipher)
        ciphers.remove(random_cipher)
    return ":".join(new_ciphers)
