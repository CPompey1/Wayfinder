from collections import deque
from math import sqrt, floor
import json



class BFS:
    def __init__(self):
        filename = 'node.json'

        with open(filename, 'r') as file:
            data = json.load(file)

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

    def calculate_distance(self,point1, point2):
        x1, y1 = point1[:2]
        x2, y2 = point2[:2]
        distance = sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
        return distance


    def feet_to_node_units(self, x, y):
        x_converted = floor(x / 6) if x > 0 else round(x / 6)
        y_converted = floor(y / 6) if y > 0 else round(y / 6)
        return x_converted, y_converted


    def find_destination_by_id(self, dest_id, destinations):
        for destination in destinations:
            if destination["dest_id"] == dest_id:
                return destination["location_x"], destination["location_y"], destination["location_z"]
        return None


    def find_nearest_node_feet(self, user_location, input_nodes):
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
        user_x, user_y, user_z = user_location[0], user_location[1], user_location[2]
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


    def get_direction(self, current_node, next_node):
        dx = next_node[0] - current_node[0]
        dy = next_node[1] - current_node[1]

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


    def bfs(self, input_graph, start_node, target_node, input_nodes, preference):
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

                        if not preference or neighbor_type == preference or neighbor_type is None:
                            if (neighbor_type == "elevator" or current_node_data.get("node_type") == "elevator") and \
                                    current_node_data['location'][2] != neighbor_data['location'][2]:
                                queue.append((neighbor, path + [neighbor]))
                            elif neighbor_type != "elevator" or current_node_data.get("node_type") != "elevator":
                                queue.append((neighbor, path + [neighbor]))

        return None



    def find_nearest_elevator(self, start_node, input_nodes, input_graph, current_floor):
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


    def find_nearest_elevator_for_floor(self, input_nodes, floor):
        for node_id, node_info in input_nodes.items():
            if node_info.get("node_type") == "elevator" and node_info["location"][2] == floor:
                return node_id

        return None


    def bfs_same_floor(self, input_graph, start_node, target_node, input_nodes, floor):
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
        start_node = self.find_nearest_node_feet(user_location, input_nodes)
        start_floor = input_nodes[start_node]['location'][2]
        target_location = self.find_destination_by_id(input_dest_id, input_destinations)
        target_node = self.find_nearest_node_destination(target_location, input_nodes)
        target_floor = input_nodes[target_node]['location'][2]

        if target_floor == 1 and start_floor != 1 and preference == "elevator":
            nearest_elevator_on_current_floor = self.find_nearest_elevator(self, start_node, input_nodes, input_graph, start_floor)
            path_to_elevator = self.bfs(input_graph, start_node, nearest_elevator_on_current_floor, input_nodes, preference)
            fixed_path = [17, 101, 102, 104, 105, 106]

            path_to_destination = self.bfs(input_graph, 97, target_node, input_nodes, preference)
            complete_path = path_to_elevator + fixed_path + path_to_destination
            return complete_path

        # if target_floor != 1 and start_floor == 1 and preference == "elevator":
        #     nearest_elevator_on_current_floor = find_nearest_elevator(start_node, input_nodes, input_graph, start_floor)
        #     path_to_elevator = bfs(input_graph, start_node, nearest_elevator_on_current_floor, input_nodes, preference)
        #     target_floor_elevator = find_nearest_elevator_for_floor(input_nodes, target_floor)
        #     fixed_path = [106, 105, 104, 102, 101, 17, target_floor_elevator]
        #     path_to_destination = bfs_same_floor(input_graph, target_floor_elevator, target_node, input_nodes, target_floor)
        #     complete_path = path_to_elevator + fixed_path + path_to_destination
        #     return complete_path

        if target_floor != 1 and preference == "elevator":
            nearest_elevator_on_current_floor = self.find_nearest_elevator(start_node, input_nodes, input_graph, start_floor)
            path_to_elevator = self.bfs(input_graph, start_node, nearest_elevator_on_current_floor, input_nodes, preference)
            target_floor_elevator = self.find_nearest_elevator_for_floor(input_nodes, target_floor)
            path_to_destination = self.bfs_same_floor(input_graph, target_floor_elevator, target_node, input_nodes, target_floor)
            if start_floor == 1:
                fixed_path = [106, 105, 104, 102, 101, 17, target_floor_elevator]
                complete_path = path_to_elevator + fixed_path + path_to_destination
            else:
                complete_path = path_to_elevator + path_to_destination
            return complete_path

        if target_floor == 1 and start_floor != 1 and preference == "stairs":
            return self.bfs(input_graph, start_node, target_node, input_nodes, preference)
        
        if target_floor == start_floor:
            return self.bfs_same_floor(input_graph, start_node, target_node, input_nodes, target_floor)

        if target_floor != 1 and start_floor != 1 and preference == "stairs":
            return self.bfs(input_graph, start_node, target_node, input_nodes, preference)

        if start_floor == 1 and target_floor != 1 and preference == "stairs":
            return self.bfs(input_graph, start_node, target_node, input_nodes, preference)

        return None


    def get_floor_name(self, z):
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
            start_direction = self.get_direction(start_location, nodes[start_node_id]['location'])
            start_distance = self.calculate_distance(start_location[:2], nodes[start_node_id]['location'][:2])
            directions.append(f"Start at your location and go {start_direction} for {round(start_distance)} feet to reach node {start_node_id}")

        for i in range(len(path) - 1):
            current_node_id = path[i]
            next_node_id = path[i + 1]
            current_node = nodes[current_node_id]
            next_node = nodes[next_node_id]

            node_type = current_node.get("node_type")
            current_location = current_node['location']
            next_location = next_node['location']
            direction = self.get_direction(current_location, next_location)
            distance = self.calculate_distance(current_location[:2], next_location[:2])

            if direction:
                if node_type in ["stairs", "elevator"]:
                    if current_location[2] != next_location[2]:
                        action = "take the elevator" if node_type == "elevator" else "use the stairs"
                        floor_name = self.get_floor_name(next_location[2])
                        directions.append(f"Go {direction} for {round(distance)} feet and {action} to reach the {floor_name}")
                    else:
                        directions.append(f"Go {direction} for {round(distance)} feet and pass by the {node_type}")
                else:
                    directions.append(f"Go {direction} for {round(distance)} feet to reach node {next_node_id}")

        if end_location and end_location != nodes[end_node_id]['location']:
            end_direction = self.get_direction(nodes[end_node_id]['location'], end_location)
            end_distance = self.calculate_distance(nodes[end_node_id]['location'][:2], end_location[:2])
            directions.append(f"From node {end_node_id}, go {end_direction} for {round(end_distance)} feet to reach your destination")

        return directions



def testScript():
    bfs = BFS()
    # below is how you would call different functions
    # things I need before BFS can run
    user_location_feet = (45, 65, 1)
    dest_id = "Third Floor Bathroom_a"
    preference = "stairs"

    end_location = bfs.find_destination_by_id(dest_id, bfs.endpoints)
    nearest_node_id = bfs.find_nearest_node_feet(user_location_feet, bfs.nodes)
    print(f"Your Nearest Node is:{nearest_node_id}")
    shortest_path = bfs.find_path(user_location_feet, dest_id, bfs.nodes, bfs.graph, bfs.endpoints, preference)
    print(f"The shortest path from your current location to your destination is: {shortest_path}")

    directions = bfs.generate_directions(shortest_path, bfs.nodes, user_location_feet, end_location)
    for direction in directions:
        print(direction)
