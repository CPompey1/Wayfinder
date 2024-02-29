from collections import deque


def bfs(graph, start):
    # Set to keep track of visited nodes.
    visited = set()
    # Initialize a queue and enqueue the start node.
    queue = deque([start])

    while queue:
        # Dequeue a node from the queue.
        vertex = queue.popleft()

        # If not visited, mark as visited and enqueue its neighbors.
        if vertex not in visited:
            print(vertex, end=" ")  # Process the node (e.g., print or store it).
            visited.add(vertex)

            # Enqueue all unvisited neighbors.
            for neighbor in graph[vertex]:
                if neighbor not in visited:
                    queue.append(neighbor)

# Example usage
graph= {
    'A': ['E', 'C'],
    'B': ['A', 'D', 'E'],
    'C': ['A', 'F'],
    'D': ['B'],
    'E': ['B', 'F'],
    'F': ['C', 'E']
}
bfs(graph, 'A')