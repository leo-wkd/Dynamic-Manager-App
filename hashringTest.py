from uhashring import HashRing

if __name__ == '__main__':
    uhash = HashRing()
    # uhash.add_node("instance_1")
    # uhash.add_node("instance_2")
    target = uhash.get_node("12.jpg")
    print(target)
    # uhash.remove_node("instance_1")
    # target = uhash.get_node("12.jpg")
    # print(target)
