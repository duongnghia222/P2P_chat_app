# user = "nghia"
# from_user = 'nhan'
# mess = ('-friend_request_from_{}-'.format(from_user))
# print(mess[:21])
# print(mess[21:-1])

# to_user = "nghsdia"
# from_user = 'nhasn'
# mess = ('-accept_request_from_{}_to_{}-'.format(from_user, to_user))
# print(mess[:21])
# print(mess[21:mess.index('_to_')])
# print(mess[mess.index('_to_')+4:-1])


# from_user = 'nhaan'
# from_user_address = '18101996'
# from_user_port = '1802'
# response = ('-friend_request_from_{}_ip={}_port={}-'.format(from_user,
#                                                 from_user_address, from_user_port))
# print(response[:21])
# print(response[21:response.index('_ip=')])
# print(response[response.index('_ip=')+4:response.index('_port=')])
# print(response[response.index('_port=')+6:-1])

# import threading
# str = None
# lock = threading.Lock()
# str = input("text")
#
# # while str:
# l = []
# if not l:
#     print("eu")
# l .append({'username': 'nghia', 'conn': 2002})
# print(l)
#
# n = 'nhan'
# l.append({'username': n, 'conn': None})
# print(l)
#
# l[-1]['conn'] = 1996
#
# print(l)

# list = []
# msg = '1'
# from_whom = 'nghia'
# list.append({'username':from_whom, 'msg':[msg]})
# print(list)
# for user in list:
#     if from_whom == user['username']:
#         user['msg'].append('2')
#
# print(list)
# open = '123'
# rest = '345'
# msg = open + ': '+ rest
# print(msg)
# print(msg[:msg.index(':')])
# print(msg[msg.index(':')+2:])
# import threading
#
#
#
# def whilee():
#     x = 0
#     while True:
#         x= x + 1
#         if x == 9999999:
#             break
#
# if __name__ == "__main__":
#     # creating thread
#     t = threading.Thread(target=whilee)
#     print("hello")
#     # starting thread 1
#     t.start()
#     # starting thread 2
#
#
#     # wait until thread 1 is completely executed
#     t.join()
#     # wait until thread 2 is completely executed
#
#
#     # both threads completely executed
#     print("Done!")
filename = 'hello.txt'
SEPARATOR = "<SEPARATOR>"
file_size = 4
response = '-send_file-{}{}{}'.format(filename, SEPARATOR, file_size)
print(response[11:])
print(response[:11])