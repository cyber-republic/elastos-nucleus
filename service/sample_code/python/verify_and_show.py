import json

from elastos_adenine.hive import Hive

def main():
    api_key = "9A5Fy8jDxsJQSDdU4thLZs9fwDmtVzBU"
    message_hash = "516D5A554C6B43454C6D6D6B35584E664367546E437946674156784252425879444847474D566F4C464C6958454E"
    public_key = "022316EB57646B0444CB97BE166FBE66454EB00631422E03893EE49143B4718AB8"
    signature = "15FDD2752B686AF7CABE8DF72FCCC91AC25577C6AFB70A81A1D987DAACAE298621E227D585B7020100228AEF96D22AD0403612FFAEDCD7CA3A2070455418181C"
    file_hash = "QmZULkCELmmk5XNfCgTnCyFgAVxBRBXyDHGGMVoLFLiXEN"
    private_key = "1F54BCD5592709B695E85F83EBDA515971723AFF56B32E175F14A158D5AC0D99"

    try:
        hive = Hive()
        # Verify and Show
        print("\n--> Verify and Show")
        request_input = {
            "msg": message_hash,
            "pub": public_key,
            "sig": signature,
            "hash": file_hash,
            "private_key": private_key
        }
        response = hive.verify_and_show(api_key, request_input)
        if response.output:
            json_output = json.loads(response.output)
            print("Status Message :", response.status_message)
            for i in json_output['result']:
                print(i, ':', json_output['result'][i])
    except Exception as e:
        print(e)
    finally:
        hive.close()

if __name__ == '__main__':
    main()
