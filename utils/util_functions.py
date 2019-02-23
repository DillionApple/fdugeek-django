import hashlib

def get_md5(bytes):
    hash = hashlib.md5()
    hash.update(bytes)
    return hash.hexdigest()

def get_index_st_en(request, PG_SIZE=20):

    try:
        page = int(request.GET['page'])
    except:
        page = 0

    index_st = PG_SIZE * page
    index_en = PG_SIZE * (page + 1)

    return index_st, index_en


if __name__ == "__main__":
    print(check_fdu_auth("17210240047", "hello"))
