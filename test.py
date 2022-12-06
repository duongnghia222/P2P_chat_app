# user = "nghia"
# from_user = 'nhan'
# mess = ('-friend_request_from_{}-'.format(from_user))
# print(mess[:21])
# print(mess[21:-1])

import threading



def whilee():
    x = 0
    while True:
        x= x + 1
        if x == 9999999:
            break

if __name__ == "__main__":
    # creating thread
    t = threading.Thread(target=whilee)
    print("hello")
    # starting thread 1
    t.start()
    # starting thread 2


    # wait until thread 1 is completely executed
    t.join()
    # wait until thread 2 is completely executed


    # both threads completely executed
    print("Done!")