# ------------------- Switch List -------------------------
# s1,s2,s3,s4,s5
# link -> cost
# s1 - s2 = 1
# s1 - s3 = 2
# s2 - s4 = 3
# s3 - s5 = 4
# s4 - s5 = 5


def data_link_cost(src, dst):

    # menggunakan dpid sebagai identitas dari switch s1 = 1, s2= 2, dst...
    # link hanya antar satu switch dengan switch lainnya
    # link_array = {([src],[dst]) = [cost]), .. }
    link_dict = {
        
        (1, 2): 1,
        (1, 3): 1,
        (2, 3): 100,
        (2, 5): 10,
        (3, 5): 10,
        (3, 4): 10,
        (4, 5): 10,
        (4, 6): 100,
        (5, 6): 100,
        (6, 7): 1,
        (6, 8): 1,
        (6, 9): 1,
        
        # reverse
        (2, 1): 1,
        (3, 1): 1,
        (3, 2): 100,
        (5, 2): 10,
        (5, 3): 10,
        (4, 3): 10,
        (5, 4): 10,
        (6, 4): 100,
        (6, 5): 100,
        (7, 6): 1,
        (8, 6): 1,
        (9, 6): 1,
    }

    return link_dict[src, dst]
