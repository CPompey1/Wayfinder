


from BFS import BFS


def func(bfs,start,goal):
    startingFloor = start[0][2]
    twoFloors = False
    before_stairs = []
    after_stairs =  []
    for nodeId in start:
        #if floors are different
        if startingFloor != nodeId[2] and not twoFloors:
            before_stairs = after_stairs
            after_stairs = []
            after_stairs.append(nodeId)
            twoFloors = True
        else:
            after_stairs.append(nodeId)
    
    return before_stairs,after_stairs

bfs = BFS() 
in1 = [[0,0,0],[0,1,0],[1,0,1]]
in2 = [[0,1,0],[1,0,1],[2,0,1]]
before_stairs,after_stairs = func(bfs,in1,in2)
print(before_stairs)
print(after_stairs)