from collections import deque
from math import sqrt, floor
import json


class BFS:
    def __init__(self):
        # nodes and destinations of the library, to add more nodes / destination, edit this file
        filename = 'node.json'

        with open(filename, 'r') as file:
            data = json.load(file)
        # initialization
        self.nodes_data = data["nodes"]

        self.graph = {node["node_id"]: node["connections"] for node in self.nodes_data}
        self.locations = {node["node_id"]: (node["location_x"], node["location_y"], node["location_z"]) for node in self.nodes_data}

        self.nodes = {
            node["node_id"]: {
                "location": (node["location_x"], node["location_y"], node["location_z"]),
                "connections": node["connections"],
                "node_type": node.get("node_type")
            } for node in self.nodes_data
        }

        self.endpoints = data["destinations"]

    def calculate_distance(self, point1, point2):
        # calculate distance between two point, return unit in feet
        x1, y1 = point1[:2]
        x2, y2 = point2[:2]
        distance = sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)*6
        return distance

    def feet_to_node_units(self, x, y):
        # convert feet to node unit, 6ft = 1 node unit
        x_converted = floor(x / 6) if x > 0 else round(x / 6)
        y_converted = floor(y / 6) if y > 0 else round(y / 6)
        return x_converted, y_converted

    def find_destination_by_id(self, user_location_feet, dest_id, destinations):
        # find the dest_id that matches the user selection
        # user location [x value, y value, floor number]
        # basement floor 0, 1st floor 1 .... fifth floor 5
        current_floor = user_location_feet[2]
        if dest_id.find("Bathroom") == -1:
            for destination in destinations:
                # if they match exactly, for locations other than stairs and bathrooms
                if destination["dest_id"] == dest_id:
                    return destination["location_x"], destination["location_y"], destination["location_z"]
        else:
            # if it's located in second first floor or the basement
            if dest_id.find("Second") != -1 or dest_id.find("First") != -1 or dest_id.find("Basement") != -1:
                for destination in destinations:
                    # look for dest_id that matches in the json file
                    if destination["dest_id"] == dest_id:
                        return destination["location_x"], destination["location_y"], destination["location_z"]
            # Third Floor Bathroom
            elif dest_id.find("Third") != -1:
                if current_floor == 3:
                    # guide them to the nearest bathroom
                    bathroom_a = self.calculate_distance(user_location_feet[:2], [6, 23])
                    bathroom_b = self.calculate_distance(user_location_feet[:2], [13, -5])
                    if bathroom_a < bathroom_b:
                        return 6, 23, 3
                    else:
                        return 13, -5, 3
                else:
                    return 13, -5, 3
            # Forth Floor Bathroom
            elif dest_id.find("Fourth") != -1:
                if current_floor == 4:
                    # guide them to the nearest bathroom
                    bathroom_a = self.calculate_distance(user_location_feet[:2], [6, 28])
                    bathroom_b = self.calculate_distance(user_location_feet[:2], [15, -3])
                    if bathroom_a < bathroom_b:
                        return 6, 28, 4
                    else:
                        return 15, -3, 4
                else:
                    return 15, -3, 4
            # Fifth Floor Bathroom
            elif dest_id.find("Fifth") != -1:
                if current_floor == 5:
                    # guide them to the nearest bathroom
                    bathroom_a = self.calculate_distance(user_location_feet[:2], [6, 28])
                    bathroom_b = self.calculate_distance(user_location_feet[:2], [15, -3])
                    if bathroom_a < bathroom_b:
                        return 6, 28, 5
                    else:
                        return 15, -3, 5
                else:
                    return 15, -3, 5
        return None


    def find_nearest_node_feet(self, user_location, input_nodes):
        # used to determine where the user is currently at, as the starting node of the BFS
        user_x, user_y = self.feet_to_node_units(user_location[0], user_location[1])
        user_z = user_location[2]
        nearest_node = None
        min_distance = float('inf')

        for node_id, node_info in input_nodes.items():
            node_x, node_y, node_z = node_info["location"]
            if user_z == node_z:
                distance = self.calculate_distance((user_x, user_y), (node_x, node_y))
                if distance < min_distance:
                    min_distance = distance
                    nearest_node = node_id

        return nearest_node

    def find_nearest_node_destination(self, user_location, input_nodes):
        # most of the time the end points are not a node, BFS only output path with nodes
        # this output the nearest node to the endpoints, so this will be the destination for BFS
        user_x, user_y, user_z = user_location[0], user_location[1], user_location[2]
        nearest_node = None
        min_distance = float('inf')

        for node_id, node_info in input_nodes.items():
            node_x, node_y, node_z = node_info["location"]
            if user_z == node_z:
                # calculate distance between node and the
                distance = self.calculate_distance((user_x, user_y), (node_x, node_y))
                if distance < min_distance:
                    min_distance = distance
                    nearest_node = node_id

        return nearest_node

    def remove_duplicate_sequence(self, path, target):
        indices = [index for index, value in enumerate(path) if value == target]

        if len(indices) > 1:
            first_index, second_index = indices[0], indices[1]
            return path[:first_index + 1] + path[second_index:]
        else:
            return path
    def get_direction(self, current_node, next_node):
        # generate directions for user to decide which direction they should go
        dx = next_node[0] - current_node[0]
        dy = next_node[1] - current_node[1]
        # floor number
        dz = next_node[2] - current_node[2]

        if dx == 0 and dy > 0:
            return "North"
        elif dx == 0 and dy < 0:
            return "South"
        elif dx > 0 and dy == 0:
            return "East"
        elif dx < 0 and dy == 0:
            return "West"
        elif dx > 0 and dy > 0:
            return "North-East"
        elif dx > 0 > dy:
            return "South-East"
        elif dx < 0 < dy:
            return "North-West"
        elif dx < 0 and dy < 0:
            return "South-West"
        # dx and dy will be zero if they're taking the elevator or using the stairs
        elif dx == 0 and dy == 0 and dz > 0:
            return "Up"
        # so no directions only up and down
        elif dx == 0 and dy == 0 and dz < 0:
            return "Down"

    def bfs(self, input_graph, start_node, target_node, input_nodes, preference):
        # just a normal bfs for path finding
        visited = set()
        queue = deque([(start_node, [start_node])])

        while queue:
            current_node, path = queue.popleft()
            current_node_data = input_nodes[current_node]

            if current_node == target_node:
                return path

            if current_node not in visited:
                visited.add(current_node)

                for neighbor in input_graph[current_node]:
                    if neighbor not in visited:
                        neighbor_data = input_nodes[neighbor]
                        neighbor_type = neighbor_data.get("node_type")

                        if preference == "stairs" and neighbor_type == "elevator":
                            if current_node_data['location'][2] == neighbor_data['location'][2]:
                                queue.append((neighbor, path + [neighbor]))
                        elif not preference or neighbor_type == preference or neighbor_type is None:
                            queue.append((neighbor, path + [neighbor]))

        return None


    def find_nearest_elevator(self, start_node, input_nodes, input_graph, current_floor):
        # a twisted version of bfs to find the nearest elevator, because lockwood library 1st floor's elevator is detached from other floors
        visited = set()
        queue = deque([start_node])

        while queue:
            current_node = queue.popleft()
            if current_node in visited:
                continue

            visited.add(current_node)

            if input_nodes[current_node].get("node_type") == "elevator":
                if input_nodes[current_node]['location'][2] == current_floor:
                    return current_node

            for neighbor in input_graph[current_node]:
                if neighbor not in visited:
                    queue.append(neighbor)

        return None

    def find_nearest_stairs(self, start_node, input_nodes, input_graph, current_floor):
        # a twisted version of bfs to find the nearest elevator, because lockwood library 1st floor's elevator is detached from other floors
        visited = set()
        queue = deque([start_node])

        while queue:
            current_node = queue.popleft()
            if current_node in visited:
                continue

            visited.add(current_node)

            if input_nodes[current_node].get("node_type") == "stairs":
                if input_nodes[current_node]['location'][2] == current_floor:
                    return current_node

            for neighbor in input_graph[current_node]:
                if neighbor not in visited:
                    queue.append(neighbor)

        return None

    def find_nearest_elevator_for_floor(self, input_nodes, floor):
        # another helper function, get the node id for the elevator of that floor
        for node_id, node_info in input_nodes.items():
            if node_info.get("node_type") == "elevator" and node_info["location"][2] == floor:
                return node_id
        return None

    def bfs_same_floor(self, input_graph, start_node, target_node, input_nodes, floor):
        # another version of bfs if only looking for a destination that's on the same floor
        visited = set()
        queue = deque([(start_node, [start_node])])

        while queue:
            current_node, path = queue.popleft()

            if current_node == target_node:
                return path

            if current_node not in visited:
                visited.add(current_node)
                for neighbor in input_graph[current_node]:
                    if neighbor not in visited and input_nodes[neighbor]['location'][2] == floor:
                        queue.append((neighbor, path + [neighbor]))

        return None

    def find_path(self, user_location, input_dest_id, input_nodes, input_graph, input_destinations, preference):
        # combine bfs and other helper function and hard coding to return a valid path
        start_node = self.find_nearest_node_feet(user_location, input_nodes)
        start_floor = input_nodes[start_node]['location'][2]
        target_location = self.find_destination_by_id(user_location, input_dest_id, input_destinations)
        # target_location is the endpoint, target node is the last node in BFS
        target_node = self.find_nearest_node_destination(target_location, input_nodes)
        target_floor = input_nodes[target_node]['location'][2]
        # user will choose if they wanted to use stairs or elevators during the navigation, they can't use both, only one
        if target_floor == start_floor == 2 and preference == "stairs":
            return self.bfs_same_floor(input_graph, start_node, target_node, input_nodes, target_floor)
        # essentially for user to get to any other floor but floor 1 starting from floor 2
        if target_floor != 1 and start_floor == 2 and preference == "elevator":
            target_floor_elevator = self.find_nearest_elevator_for_floor(input_nodes, target_floor)
            # because there's two elevator on floor 2, determine what should the path be
            nearest_elevator_on_current_floor = self.find_nearest_elevator(start_node, input_nodes, input_graph, start_floor)
            path_to_elevator = self.bfs(input_graph, start_node, nearest_elevator_on_current_floor, input_nodes, preference)
            # bfs essentially after reach the destination floor
            path_to_destination = self.bfs_same_floor(input_graph, target_floor_elevator, target_node,
                                                      input_nodes,
                                                      target_floor)
            # if they start at node 103
            if start_node == 103:
                fixed_path = [103, 102, 101, 17]
                return fixed_path+path_to_destination
            # if they start at node 102
            if start_node == 102:
                fixed_path = [102, 101, 17]
                return fixed_path + path_to_destination
            # if they start outside the library
            if path_to_elevator[0]>=104:
                fixed_path = [108, 107, 106, 105, 104, 102, 101, 17]
                # generate fixed path based on their starting point
                if path_to_elevator[0] in fixed_path:
                    start_index = fixed_path.index(path_to_elevator[0])
                    # path from starting point to second floor elevator
                    new_fix = fixed_path[start_index:]
                    # path from starting point to the destination
                    return new_fix + path_to_destination
            else:
                # if they start inside the library just normal bfs
                path_to_destination = self.bfs_same_floor(input_graph, target_floor_elevator, target_node, input_nodes,
                                                     target_floor)
                complete_path = path_to_elevator + path_to_destination
                return complete_path

        if target_floor == 1 and start_floor == 0 and preference == "stairs":
            # another special case when going from basement to first floor with stairs
            # user will use the stiarcase that only connect basement, 1, and 2
            nearest_elevator_on_current_floor = self.find_nearest_elevator(start_node, input_nodes, input_graph, start_floor)
            path_to_elevator = self.bfs(input_graph, start_node, nearest_elevator_on_current_floor, input_nodes, preference)
            path_to_destination = self.bfs(input_graph, 10, target_node, input_nodes, preference)
            complete_path = path_to_elevator + [96] + path_to_destination
            return complete_path

        if target_floor == 1 and start_floor == 2 and preference == "elevator":
            # user needs to navigate outside the library to find the elevator to the first floor
            nearest_elevator_on_current_floor = self.find_nearest_elevator(start_node, input_nodes, input_graph, start_floor)
            path_to_elevator = self.bfs(input_graph, start_node, nearest_elevator_on_current_floor, input_nodes, preference)
            fixed_path = [101, 102, 104, 105, 106]
            path_to_destination = self.bfs(input_graph, 97, target_node, input_nodes, preference)
            complete_path = path_to_elevator + fixed_path + path_to_destination
            # remove duplicates in generated path to avoid confusion
            removed = self.remove_duplicate_sequence(complete_path, 106)
            return removed

        if target_floor == 1 and start_floor != 1 and preference == "elevator":
            # if user started with a floor that's not floor one and chose to take the elevator
            # they need to go to second floor and walk out side the library to go to the first floor using elevator
            nearest_elevator_on_current_floor = self.find_nearest_elevator(start_node, input_nodes, input_graph, start_floor)
            path_to_elevator = self.bfs(input_graph, start_node, nearest_elevator_on_current_floor, input_nodes, preference)
            fixed_path = [17, 101, 102, 104, 105, 106]

            path_to_destination = self.bfs(input_graph, 97, target_node, input_nodes, preference)
            complete_path = path_to_elevator + fixed_path + path_to_destination
            removed = self.remove_duplicate_sequence(complete_path, 106)
            return removed

        if target_floor != 1 and preference == "elevator":
            # if going somewhere else other than first floor and use elevator
            nearest_elevator_on_current_floor = self.find_nearest_elevator(start_node, input_nodes, input_graph, start_floor)
            path_to_elevator = self.bfs(input_graph, start_node, nearest_elevator_on_current_floor, input_nodes, preference)
            target_floor_elevator = self.find_nearest_elevator_for_floor(input_nodes, target_floor)
            path_to_destination = self.bfs_same_floor(input_graph, target_floor_elevator, target_node, input_nodes,
                                                 target_floor)
            # pretty sure I don't need this block anymore
            # if target_floor == 2 and start_floor == 2:
            #     between_two_elevators = self.bfs_same_floor(input_graph, nearest_elevator_on_current_floor,
            #                                            target_floor_elevator, input_nodes, 2)
            #     del between_two_elevators[0]
            #     del between_two_elevators[-1]
            #     complete_path = path_to_elevator + between_two_elevators + path_to_destination
            # the other way around from the previous case, start from floor 1 elevator and enter from the main entrance
            # the do some navigation there
            if start_floor == 1 and target_floor == 2:
                fixed_path = [106, 105, 104, 102, 101]
                complete_path = path_to_elevator + fixed_path + path_to_destination
            # if want to take one step further and go to some other floor
            elif start_floor == 1:
                fixed_path = [106, 105, 104, 102, 101, 17, target_floor_elevator]
                complete_path = path_to_elevator + fixed_path + path_to_destination
            else:
                complete_path = path_to_elevator + path_to_destination
            return complete_path
        # some normal cases below
        if target_floor == start_floor:
            return self.bfs_same_floor(input_graph, start_node, target_node, input_nodes, target_floor)

        if target_floor == 1 and start_floor != 1 and preference == "stairs":
            return self.bfs(input_graph, start_node, target_node, input_nodes, preference)

        if target_floor != 1 and start_floor != 1 and preference == "stairs":
            return self.bfs(input_graph, start_node, target_node, input_nodes, preference)

        if start_floor == 1 and target_floor != 1 and preference == "stairs":
            return self.bfs(input_graph, start_node, target_node, input_nodes, preference)

        return None

    @staticmethod
    def get_floor_name(z):
        # auto generate names for output directions to the user
        if z == 0:
            return "Basement"
        elif 1 <= z <= 5:
            return f"{z}{'st' if z == 1 else 'nd' if z == 2 else 'rd' if z == 3 else 'th'} Floor"

    def generate_directions(self, path, nodes, start_location, end_location):
        if not path:
            return []

        directions = []

        start_node_id = path[0]
        end_node_id = path[-1]

        if start_location and start_location != nodes[start_node_id]['location']:
            # if the user didn't start on a node, first direct them to the nearest node
            start_direction = self.get_direction(start_location, nodes[start_node_id]['location'])
            start_distance = self.calculate_distance(self.feet_to_node_units(start_location[0], start_location[1]), nodes[start_node_id]['location'][:2])
            directions.append(f"Start at your location and go {start_direction} for {round(start_distance)} feet")

        for i in range(len(path) - 1):
            # keep track of the current node and next node to output direction
            current_node_id = path[i]
            next_node_id = path[i + 1]
            current_node = nodes[current_node_id]
            next_node = nodes[next_node_id]
            # get the node type, for elevator and staris only
            node_type = current_node.get("node_type")
            # get the specific location in number
            current_location = current_node['location']
            next_location = next_node['location']
            # get direction from previous helper function
            direction = self.get_direction(current_location, next_location)
            distance = self.calculate_distance(current_location[:2], next_location[:2])

            if direction:
                # if returns none, there's not a valid direction formed from previous code
                if node_type in ["stairs", "elevator"]:
                    # output take the elevator or use the stairs when user are moving up and down in floor but not in s, y position
                    if next_location[2] != current_location[2]:
                        action = "take the elevator" if node_type == "elevator" else "use the stairs"
                        floor_name = self.get_floor_name(next_location[2])
                        # I don't think the distance will be >0 but just in case
                        if distance > 0:
                            directions.append(
                                f"Go {direction} for {round(distance)} feet and {action} to reach the {floor_name}")
                        else:
                            # usually this case, they only move up and down to a new floor
                            directions.append(f"{action.capitalize()} to reach the {floor_name}")
                    else:
                        # if only moving x and y, calculate the distance user need to move and in which direction
                        # also although node is elevator or stairs, since they're not moving up and down, will indicate
                        # in direction they're passing not taking the elavator and stairs
                        directions.append(f"Go {direction} for {round(distance)} feet and you will pass by the {node_type}")

                else:
                    # if they're just moving in x, y and not changing floors, and they're not a special node which is elevator and stairs
                    directions.append(f"Go {direction} for {round(distance)} feet")

        if end_location and end_location != nodes[end_node_id]['location']:
            # if the endpoint is not a node, output an additional instruction to guide user from the last node to the destination
            end_direction = self.get_direction(nodes[end_node_id]['location'], end_location)
            end_distance = self.calculate_distance(nodes[end_node_id]['location'][:2], end_location[:2])
            directions.append(f"Go {end_direction} for {round(end_distance)} feet to reach your destination")
        directions.append("Thank you for using Wayfiner!")
        return directions


def testScript():
    bfs = BFS()
    # change here if you want to test it
    user_location_feet = (20, 50, 0)
    # make sure this matches the destinations in the node.json file
    dest_id = "First Floor Bathroom"
    preference = "stairs"

    # only thing visible to the user should just be directions, the print statement is to help us identify the generated path legitimacy
    end_location = bfs.find_destination_by_id(dest_id, dest_id, bfs.endpoints)
    nearest_node_id = bfs.find_nearest_node_feet(user_location_feet, bfs.nodes)
    print(f"Your Nearest Node is:{nearest_node_id}")
    shortest_path = bfs.find_path(user_location_feet, dest_id, bfs.nodes, bfs.graph, bfs.endpoints, preference)
    print(f"The shortest path from your current location to your destination is: {shortest_path}")

    directions = bfs.generate_directions(shortest_path, bfs.nodes, user_location_feet, end_location)
    for direction in directions:
        print(direction)


testScript()
