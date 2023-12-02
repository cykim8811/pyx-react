
def base62(num):
    alphabet = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    base = len(alphabet)
    result = ""
    while num:
        num, rem = divmod(num, base)
        result = alphabet[rem] + result
    return result

def hashObj(obj):
    hash = hashlib.md5(str(id(obj)).encode()).hexdigest()
    hash = int(hash, 16)
    hash = base62(hash)
    return hash