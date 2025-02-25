import get from 'lodash/get';
import set from 'lodash/set';
import isEmpty from 'lodash/isEmpty';
import isObject from 'lodash/isObject';
import forEach from 'lodash/forEach';
import { EvaluateResult } from './types';




export const EVALUATION_RESULT = {
    "result": {
        "Database Operations": {
            "average_score": 3.8,
            "min_score": 3,
            "max_score": 5.0,
            "evaluated_pairs": [
                {
                    "question": "How do you perform an UPDATE operation in PostgreSQL using psycopg2?",
                    "solution": "Here's an example of updating records in a PostgreSQL database:\n\n```python\nimport psycopg2\n\n# Establish connection\nconn = psycopg2.connect(\n    dbname='mydatabase',\n    user='myuser',\n    password='mypassword',\n    host='localhost'\n)\n\n# Create cursor\ncursor = conn.cursor()\n\n# Update single record\ncursor.execute('''\n    UPDATE employees\n    SET salary = %s\n    WHERE department = %s\n''', (55000, 'Sales'))\n\n# Update multiple records\ncursor.execute('''\n    UPDATE employees\n    SET status = 'Active'\n    WHERE last_login > %s\n''', ('2023-01-01',))\n\n# Commit changes\nconn.commit()\n\n# Close connections\ncursor.close()\nconn.close()\n```\n\nThis code shows how to connect to PostgreSQL and perform UPDATE operations with parameterized queries.",
                    "evaluation": {
                        "score": 3,
                        "justification": "The code demonstrates a solid implementation of PostgreSQL UPDATE operations using psycopg2 with key strengths:         - Correctly establishes database connection         - Shows parameterized query usage for safe SQL execution         - Demonstrates both single and multiple record update scenarios         - Includes proper connection and cursor management                  Areas for improvement:         - Lacks error handling (no try/except blocks)         - No connection pool or context manager for connection management         - Missing input validation         - No logging or detailed error reporting                  The solution provides a basic, functional approach to database updates that would work in simple scenarios but requires additional robustness for production use."
                    }
                },
                {
                    "question": "How do you perform a SELECT query in SQLAlchemy?",
                    "solution": "Here's an example of executing a SELECT query using SQLAlchemy:\n\n```python\nfrom sqlalchemy import create_engine, select\nfrom sqlalchemy.orm import Session\n\n# Create engine\nengine = create_engine('sqlite:///example.db')\n\n# Create session\nwith Session(engine) as session:\n    # Assuming 'User' is an ORM model\n    query = select(User).where(User.age > 25)\n    results = session.execute(query).scalars().all()\n\n    # Process results\n    for user in results:\n        print(user.name)\n```\n\nThis example shows how to create a database engine, start a session, and execute a SELECT query with a filter condition.",
                    "evaluation": {
                        "score": 4,
                        "justification": "The code demonstrates a high-quality implementation of a SELECT query in SQLAlchemy with several strong points:\n\n1. Correct Core Functionality: Properly uses SQLAlchemy's select() method with a filter condition\n2. Proper Session Management: Uses context manager (with statement) for session handling\n3. Clear Query Structure: Shows filtering with .where() clause and retrieving results with .scalars().all()\n4. Professional Coding Practices: Uses create_engine() correctly, shows result iteration\n\nPoints for potential improvement:\n- Could add type hints\n- Lacks explicit error handling\n- No connection/query timeout configurations\n\nOverall, it's a solid, professional-grade example of performing a SELECT query in SQLAlchemy that would be suitable for most production scenarios."
                    }
                },
                {
                    "question": "How do you insert data into a SQLite database using Python?",
                    "solution": "Here's a method to insert data into a SQLite database:\n\n```python\nimport sqlite3\n\n# Connect to database\nconn = sqlite3.connect('example.db')\ncursor = conn.cursor()\n\n# Create table\ncursor.execute('''\n    CREATE TABLE IF NOT EXISTS users (\n        id INTEGER PRIMARY KEY,\n        name TEXT,\n        age INTEGER\n    )\n''')\n\n# Insert single record\ncursor.execute('INSERT INTO users (name, age) VALUES (?, ?)', ('John Doe', 30))\n\n# Insert multiple records\nusers_data = [\n    ('Alice', 25),\n    ('Bob', 35),\n    ('Charlie', 40)\n]\ncursor.executemany('INSERT INTO users (name, age) VALUES (?, ?)', users_data)\n\n# Commit changes and close connection\nconn.commit()\nconn.close()\n```\n\nThis code demonstrates creating a table, inserting single and multiple records using SQLite.",
                    "evaluation": {
                        "score": 3,
                        "justification": "The code demonstrates solid SQLite database interaction in Python with several key strengths:         - Correctly shows database connection and cursor creation         - Illustrates table creation with IF NOT EXISTS clause         - Demonstrates both single and multiple record insertion         - Uses parameterized queries for safe data insertion         - Properly commits changes and closes connection          Areas for improvement:         - Lacks error handling (no try/except blocks)         - No type hints or docstrings         - No logging or advanced error tracking         - Could benefit from context manager (with statement) for connection         - Minimal input validation          The solution provides a clear, functional approach to SQLite database insertion that would be suitable for basic applications, but lacks some advanced programming best practices."
                    }
                },
                {
                    "question": "How do you establish a connection to a MySQL database using Python?",
                    "solution": "You can use the mysql-connector-python library to connect to a MySQL database:\n\n```python\nimport mysql.connector\n\n# Establish connection\ndb_connection = mysql.connector.connect(\n    host='localhost',\n    user='your_username',\n    password='your_password',\n    database='your_database'\n)\n\n# Create a cursor object\ncursor = db_connection.cursor()\n\n# Close connection when done\ndb_connection.close()\n```\n\nThis code demonstrates creating a database connection with essential parameters like host, username, password, and database name.",
                    "evaluation": {
                        "score": 5.0,
                        "justification": "The solution achieves a comprehensive 5-point evaluation by:\\n- Implementing core functionality correctly (1)\\n- Showing advanced, correct implementation with proper syntax (2)\\n- Being production-ready with professional code structure (3)\\n- Demonstrating high efficiency with Python best practices (4)\\n- Providing robust error handling, type hints, clear documentation, and modular design (5)\\n\\nThe code exhibits exceptional developer qualities with well-structured, maintainable, and secure database connection implementation."
                    }
                },
                {
                    "question": "How do you delete records from a database using SQLAlchemy?",
                    "solution": "Here's an example of deleting records using SQLAlchemy:\n\n```python\nfrom sqlalchemy import create_engine, delete\nfrom sqlalchemy.orm import Session\n\n# Create engine\nengine = create_engine('postgresql://user:password@localhost/mydatabase')\n\n# Create session\nwith Session(engine) as session:\n    # Delete single record\n    delete_query = delete(User).where(User.id == 5)\n    session.execute(delete_query)\n\n    # Delete multiple records\n    delete_multiple = delete(User).where(User.age < 18)\n    session.execute(delete_multiple)\n\n    # Commit changes\n    session.commit()\n```\n\nThis example demonstrates deleting single and multiple records using SQLAlchemy's delete method with conditional filtering.",
                    "evaluation": {
                        "score": 4,
                        "justification": "The solution demonstrates strong SQLAlchemy record deletion techniques with multiple key aspects:\n\n1. Correct Implementation:\n- Shows both single and multiple record deletion methods\n- Uses SQLAlchemy's delete() method with proper filtering\n- Includes session management and commit process\n- Demonstrates conditional deletion strategies\n\n2. Code Quality:\n- Proper import statements\n- Clear, concise syntax\n- Uses context manager for session handling\n- Shows professional database interaction patterns\n\n3. Practical Approach:\n- Covers common deletion scenarios\n- Uses where() clause for precise record targeting\n- Includes transaction commit for data persistence\n\n4. Best Practices:\n- Separates database connection and session creation\n- Uses SQLAlchemy ORM delete method\n- Provides clear, readable code structure\n\npotential improvements could include error handling and type hinting, but overall an excellent demonstration of SQLAlchemy record deletion techniques."
                    }
                }
            ]
        },
        "Algorithms": {
            "average_score": 3.2,
            "min_score": 3.0,
            "max_score": 4,
            "evaluated_pairs": [
                {
                    "question": "How can you implement a breadth-first search (BFS) algorithm for a graph?",
                    "solution": "Breadth-first search explores all neighbors before moving to the next level. Here's an implementation using a queue:\n\n```python\nfrom collections import deque\n\ndef bfs(graph, start):\n    visited = set()\n    queue = deque([start])\n    visited.add(start)\n\n    while queue:\n        vertex = queue.popleft()\n        print(vertex, end=' ')  # Process current node\n\n        for neighbor in graph[vertex]:\n            if neighbor not in visited:\n                queue.append(neighbor)\n                visited.add(neighbor)\n\n# Example graph represented as an adjacency list\ngraph = {\n    'A': ['B', 'C'],\n    'B': ['A', 'D', 'E'],\n    'C': ['A', 'F'],\n    'D': ['B'],\n    'E': ['B', 'F'],\n    'F': ['C', 'E']\n}\n\nbfs(graph, 'A')  # Output: A B C D E F\n```\n\nBFS uses a queue to explore nodes level by level, ensuring the shortest path in unweighted graphs.",
                    "evaluation": {
                        "score": 4,
                        "justification": "The BFS implementation demonstrates high-quality code with several key strengths:         - Correct algorithm implementation using a queue-based approach (1 point)         - Clean, Pythonic code with proper use of collections.deque (2 points)         - Professional-grade implementation with clear logic and readability (3 points)         - Advanced Python practices including:             * Using set() for efficient visited tracking             * Utilizing collections.deque for optimal queue operations             * Clear, concise function design             * Demonstrating graph traversal with an adjacency list                  The solution provides a robust, efficient BFS implementation that:         - Handles graph traversal correctly         - Shows O(V+E) time complexity         - Uses memory-efficient data structures         - Includes a practical example with sample graph                  Minor improvements could include:         - Adding type hints         - Implementing optional path tracking         - Adding error handling for invalid graph structures"
                    }
                },
                {
                    "question": "How can you implement a depth-first search (DFS) algorithm for a graph?",
                    "solution": "Depth-first search explores as far as possible along each branch before backtracking. Here's a recursive implementation:\n\n```python\ndef dfs(graph, start, visited=None):\n    if visited is None:\n        visited = set()\n    \n    visited.add(start)\n    print(start, end=' ')  # Process current node\n\n    for neighbor in graph[start]:\n        if neighbor not in visited:\n            dfs(graph, neighbor, visited)\n\n# Example graph represented as an adjacency list\ngraph = {\n    'A': ['B', 'C'],\n    'B': ['A', 'D', 'E'],\n    'C': ['A', 'F'],\n    'D': ['B'],\n    'E': ['B', 'F'],\n    'F': ['C', 'E']\n}\n\ndfs(graph, 'A')  # Output: A B D E F C\n```\n\nThis implementation explores graph nodes recursively, marking visited nodes to prevent cycles.",
                    "evaluation": {
                        "score": 3.0,
                        "justification": "The code achieves 3 points by:\\n- Correctly implementing the core DFS algorithm recursively (1 point)\\n- Demonstrating proper Python syntax and graph traversal logic (1 point)\\n- Showing a clean, readable implementation with basic functionality (1 point)\\n\\nStrengths:\\n- Uses a set for tracking visited nodes\\n- Handles graph traversal without infinite loops\\n- Simple and intuitive recursive approach\\n\\nLimitations preventing a higher score:\\n- Lacks type hints\\n- No error handling for invalid graph structures\\n- Minimal documentation\\n- Prints nodes instead of returning a traversal result"
                    }
                },
                {
                    "question": "How do you implement a binary search algorithm in Python?",
                    "solution": "Binary search is an efficient algorithm for finding an element in a sorted array. Here's an implementation:\n\n```python\ndef binary_search(arr, target):\n    left = 0\n    right = len(arr) - 1\n\n    while left <= right:\n        mid = (left + right) // 2\n        \n        if arr[mid] == target:\n            return mid  # Target found, return its index\n        \n        if arr[mid] < target:\n            left = mid + 1  # Search right half\n        else:\n            right = mid - 1  # Search left half\n    \n    return -1  # Target not found\n\n# Example usage\nsorted_array = [1, 3, 5, 7, 9, 11, 13]\nresult = binary_search(sorted_array, 7)\nprint(result)  # Output: 3\n```\n\nThis implementation has O(log n) time complexity, making it very efficient for large sorted arrays.",
                    "evaluation": {
                        "score": 3.0,
                        "justification": "The code achieves 3 points by:\n        - Correctly implementing the core binary search algorithm\n        - Using proper Python syntax and logic\n        - Demonstrating a clear, straightforward implementation\n        \n        Strengths:\n        - Efficient O(log n) time complexity\n        - Handles sorted array search effectively\n        - Simple and readable implementation\n        \n        Areas for Improvement:\n        - Lacks type hints for better type safety\n        - No error handling for unsorted or empty arrays\n        - Could benefit from more comprehensive documentation\n        - No recursive implementation option\n        \n        The solution provides a solid basic implementation of binary search that would be suitable for many basic use cases, but lacks some advanced features and robustness needed for a higher score."
                    }
                },
                {
                    "question": "How do you implement a merge sort algorithm in Python?",
                    "solution": "Merge sort is a divide-and-conquer sorting algorithm with O(n log n) complexity:\n\n```python\ndef merge_sort(arr):\n    if len(arr) <= 1:\n        return arr\n    \n    # Divide the array\n    mid = len(arr) // 2\n    left = arr[:mid]\n    right = arr[mid:]\n\n    # Recursively sort both halves\n    left = merge_sort(left)\n    right = merge_sort(right)\n\n    # Merge the sorted halves\n    return merge(left, right)\n\ndef merge(left, right):\n    result = []\n    i, j = 0, 0\n\n    while i < len(left) and j < len(right):\n        if left[i] <= right[j]:\n            result.append(left[i])\n            i += 1\n        else:\n            result.append(right[j])\n            j += 1\n\n    result.extend(left[i:])\n    result.extend(right[j:])\n    return result\n\n# Example usage\nunsorted_array = [64, 34, 25, 12, 22, 11, 90]\nsorted_array = merge_sort(unsorted_array)\nprint(sorted_array)\n```\n\nMerge sort breaks down the array, sorts subarrays, and then merges them back together.",
                    "evaluation": {
                        "score": 3.0,
                        "justification": "The code achieves 3 points by:\n        - Correctly implementing the core merge sort algorithm\n        - Demonstrating a clear divide-and-conquer approach\n        - Using proper Python syntax and recursive implementation\n        - Providing a working example with clear logic\n\n        Strengths:\n        - Recursive implementation follows divide-and-conquer principle\n        - Separates merge logic into distinct functions\n        - Handles array splitting and merging efficiently\n\n        Areas for Improvement:\n        - Lacks type hints for better type safety\n        - No error handling for edge cases\n        - Could benefit from more comprehensive documentation\n        - No performance optimizations for large datasets"
                    }
                },
                {
                    "question": "How do you implement a quick sort algorithm in Python?",
                    "solution": "Quick sort is another efficient divide-and-conquer sorting algorithm with average O(n log n) complexity:\n\n```python\ndef quick_sort(arr):\n    if len(arr) <= 1:\n        return arr\n    \n    # Choose the pivot (last element)\n    pivot = arr[-1]\n    smaller = [x for x in arr[:-1] if x <= pivot]\n    larger = [x for x in arr[:-1] if x > pivot]\n\n    # Recursively sort subarrays\n    return quick_sort(smaller) + [pivot] + quick_sort(larger)\n\n# Alternative in-place implementation\ndef quick_sort_inplace(arr, low=0, high=None):\n    if high is None:\n        high = len(arr) - 1\n    \n    def partition(low, high):\n        pivot = arr[high]\n        i = low - 1\n\n        for j in range(low, high):\n            if arr[j] <= pivot:\n                i += 1\n                arr[i], arr[j] = arr[j], arr[i]\n\n        arr[i + 1], arr[high] = arr[high], arr[i + 1]\n        return i + 1\n\n    def _quick_sort(low, high):\n        if low < high:\n            pivot_index = partition(low, high)\n            _quick_sort(low, pivot_index - 1)\n            _quick_sort(pivot_index + 1, high)\n\n    _quick_sort(low, high)\n    return arr\n\n# Example usage\nunsorted_array = [10, 7, 8, 9, 1, 5]\nsorted_array = quick_sort(unsorted_array)\nprint(sorted_array)\n```\n\nQuick sort efficiently sorts by partitioning the array around a pivot element.",
                    "evaluation": {
                        "score": 3,
                        "justification": "The solution demonstrates a solid implementation of quick sort with two approaches:  1. Functionality (1 point): - Correctly implements the quick sort algorithm - Provides two implementation styles (list comprehension and in-place) - Handles basic sorting scenarios  2. Implementation Quality (1 point): - Uses list comprehensions for readability - Implements recursive and in-place versions - Shows understanding of divide-and-conquer strategy  3. Professional Usability (1 point): - Clean, pythonic code structure - Includes example usage - Demonstrates different sorting techniques  Limitations preventing a higher score: - Lacks type hints - No comprehensive error handling - Missing docstrings explaining algorithm details - No performance optimization for edge cases - No explicit handling of large or complex input scenarios  The solution provides a good foundational implementation of quick sort with clear logic and multiple approaches."
                    }
                }
            ]
        },
        "Python Basics": {
            "average_score": 3.0,
            "min_score": 0,
            "max_score": 4.0,
            "evaluated_pairs": [
                {
                    "question": "How do you use lambda functions in Python?",
                    "solution": "Lambda functions are small, anonymous functions:\n\n```python\n# Simple lambda function\nsquare = lambda x: x**2\nprint(square(5))  # Output: 25\n\n# Using lambda with built-in functions\nnumbers = [1, 2, 3, 4, 5]\nsorted_numbers = sorted(numbers, key=lambda x: x * -1)\n# Result: [5, 4, 3, 2, 1]\n\n# Lambda in list comprehension\nmultiplied = list(map(lambda x: x * 2, numbers))\n# Result: [2, 4, 6, 8, 10]\n```",
                    "evaluation": {
                        "score": 4.0,
                        "justification": "The solution demonstrates excellent coverage of lambda functions with multiple practical examples:\n\n1. Correctness (1 point):\n- Accurately shows lambda function syntax\n- Demonstrates different use cases (simple function, sorting, mapping)\n- Provides clear, working code examples\n\n2. Implementation Quality (1 point):\n- Uses idiomatic Python lambda patterns\n- Shows integration with built-in functions like sorted() and map()\n- Demonstrates concise and readable lambda implementations\n\n3. Comprehensiveness (1 point):\n- Covers multiple scenarios: basic transformation, sorting with custom key, list manipulation\n- Illustrates lambda's versatility in different contexts\n- Provides clear, executable code snippets\n\n4. Best Practices (1 point):\n- Uses meaningful variable names\n- Shows lambda as a compact alternative to full function definitions\n- Demonstrates common use cases in data manipulation\n- Provides clear output comments\n\nAdditional Strengths:\n- Concise explanations accompanying each code example\n- Shows lambda's flexibility in Python\n- Follows consistent code formatting\n\nPotential Improvements:\n- Could include error handling examples\n- Might benefit from type hinting\n- Could demonstrate more complex lambda scenarios"
                    }
                },
                {
                    "question": "How do you create a list in Python and perform basic list operations?",
                    "solution": "Here's how to create and manipulate lists in Python:\n\n```python\n# Creating a list\nfruits = ['apple', 'banana', 'cherry']\n\n# Adding an element to the end of the list\nfruits.append('orange')\n\n# Inserting an element at a specific index\nfruits.insert(1, 'grape')\n\n# Removing an element by value\nfruits.remove('banana')\n\n# Accessing list elements\nfirst_fruit = fruits[0]  # 'apple'\nlast_fruit = fruits[-1]  # 'orange'\n\n# Slicing a list\nselected_fruits = fruits[1:3]  # ['grape', 'cherry']\n```",
                    "evaluation": {
                        "score": 3,
                        "justification": "The solution demonstrates core list operations in Python with clear, concise examples. It covers fundamental list manipulation techniques including:\n\n- List creation\n- Adding elements (append, insert)\n- Removing elements\n- Accessing list elements\n- Basic list slicing\n\nStrengths:\n- Provides practical, easy-to-understand code snippets\n- Shows multiple ways to interact with lists\n- Uses Pythonic syntax and conventions\n\nlimitations:\n- Lacks error handling\n- No type hints or type annotations\n- Minimal explanation of each operation\n- No advanced list operations or comprehensive examples\n\nThe code is suitable for beginners learning Python list basics but lacks depth for more advanced use cases."
                    }
                },
                {
                    "question": "How do you handle exceptions in Python?",
                    "solution": "Exception handling helps manage runtime errors gracefully:\n\n```python\ndef divide_numbers(a, b):\n    try:\n        # Attempt to perform division\n        result = a / b\n        return result\n    except ZeroDivisionError:\n        # Handle specific division by zero error\n        print('Error: Cannot divide by zero')\n        return None\n    except TypeError:\n        # Handle type-related errors\n        print('Error: Invalid input types')\n        return None\n    finally:\n        # Optional block that always executes\n        print('Division operation completed')\n\n# Example usage\nprint(divide_numbers(10, 2))   # Output: 5.0\nprint(divide_numbers(10, 0))   # Handles division by zero\n```",
                    "evaluation": {
                        "score": 4.0,
                        "justification": "The code demonstrates excellent exception handling in Python with several key strengths:\n        - Implements multiple exception types (ZeroDivisionError, TypeError)\n        - Uses try-except-finally block correctly\n        - Provides clear error messaging\n        - Handles different input scenarios gracefully\n        - Shows professional-level error management technique\n        - Includes practical example of exception handling\n        \n        The solution covers core exception handling principles with clean, readable code. It illustrates how to:\n        1. Attempt risky operations within try block\n        2. Catch specific exception types\n        3. Provide fallback error handling\n        4. Use optional finally block for cleanup/logging\n        \n        Minor improvements could include type hints and more comprehensive error logging, but overall it's a robust implementation of Python exception handling."
                    }
                },
                {
                    "question": "How do you use dictionary comprehensions in Python?",
                    "solution": "Dictionary comprehensions provide a concise way to create dictionaries:\n\n```python\n# Create a dictionary of squares\nsquares = {x: x**2 for x in range(1, 6)}\n# Result: {1: 1, 2: 4, 3: 9, 4: 16, 5: 25}\n\n# Filtering dictionary comprehension\neven_squares = {x: x**2 for x in range(1, 11) if x % 2 == 0}\n# Result: {2: 4, 4: 16, 6: 36, 8: 64, 10: 100}\n\n# Converting two lists to a dictionary\nnames = ['Alice', 'Bob', 'Charlie']\nages = [25, 30, 35]\nname_age_dict = {name: age for name, age in zip(names, ages)}\n# Result: {'Alice': 25, 'Bob': 30, 'Charlie': 35}\n```",
                    "evaluation": {
                        "score": 4.0,
                        "justification": "The solution demonstrates excellent coverage of dictionary comprehensions with multiple high-quality examples:\n\n1. Basic Functionality (1 point):\n   - Correctly shows the fundamental syntax of dictionary comprehensions\n\n   - Provides clear, concise examples of creating dictionaries\n\n2. Comprehensive Coverage (1 point):\n   - Includes three distinct use cases:\n     a) Simple square generation\n     b) Filtered comprehension\n     c) Combining lists into a dictionary using zip()\n\n. Quality ((1 points    - Clean, readable code\n   -' Proper Python syntax\n   - Demonstrates idiomatic Python practices\n4. Concise and expressive comprehensions\n\n():\n   Shows advanced techniques (e.g):.filtering with conditions)\n. Quality:\n   - comments explaining results\npurpose\n   - Demonstrates different dictionary comprehension patterns\n\nStrengths:\n- Covers multiple dictionary comprehension scenarios\n- Provides clear, executable examples\n- Shows both simple and more complex use cases\n\nFor Improvementn::\n- Could potentially add error handling\n- Might benefit from type hints\n- Could more real-world examples"
                    }
                },
                {
                    "question": "How do you work with file I/O in Python?",
                    "solution": "Reading and writing files in Python is straightforward:\n\n```python\n# Writing to a file\nwith open('example.txt', 'w') as file:\n    file.write('Hello, World!\\n')\n    file.write('This is a text file.')\n\n# Reading from a file\nwith open('example.txt', 'r') as file:\n    content = file.read()  # Read entire file\n    print(content)\n\n# Reading line by line\nwith open('example.txt', 'r') as file:\n    for line in file:\n        print(line.strip())  # Remove trailing newline\n```",
                    "evaluation": {
                        "score": 0,
                        "justification": "Error in evaluation: 'score'"
                    }
                }
            ]
        },
        "Data Structures": {
            "average_score": 3.0,
            "min_score": 3.0,
            "max_score": 3.0,
            "evaluated_pairs": [
                {
                    "question": "How do you implement a linked list in Python?",
                    "solution": "Here's an implementation of a singly linked list:\n\n```python\nclass Node:\n    def __init__(self, data):\n        self.data = data\n        self.next = None\n\nclass LinkedList:\n    def __init__(self):\n        self.head = None\n    \n    def append(self, data):\n        # Add a new node at the end of the list\n        new_node = Node(data)\n        if not self.head:\n            self.head = new_node\n            return\n        current = self.head\n        while current.next:\n            current = current.next\n        current.next = new_node\n    \n    def display(self):\n        # Print all elements in the list\n        current = self.head\n        while current:\n            print(current.data, end=' -> ')\n            current = current.next\n        print('None')\n\n# Example usage\nlinked_list = LinkedList()\nlinked_list.append(1)\nlinked_list.append(2)\nlinked_list.append(3)\nlinked_list.display()  # Output: 1 -> 2 -> 3 -> None\n```",
                    "evaluation": {
                        "score": 3.0,
                        "justification": "The code achieves 3 points by:\n        - Correctly implementing core linked list functionality with Node and LinkedList classes\n        - Providing basic methods like append and display\n        - Using proper Python syntax and object-oriented design\n        - Demonstrating a clear and readable implementation\n\n        Areas for improvement:\n        - Lacks additional methods like insert, delete, search\n        - No error handling for edge cases\n        - Missing type hints and docstrings\n        - Could benefit from more comprehensive implementation"
                    }
                },
                {
                    "question": "How do you implement a queue data structure in Python?",
                    "solution": "Here's an implementation of a queue using a list:\n\n```python\nclass Queue:\n    def __init__(self):\n        self.items = []\n    \n    def enqueue(self, item):\n        # Add item to the end of the queue\n        self.items.append(item)\n    \n    def dequeue(self):\n        # Remove and return the first item\n        if not self.is_empty():\n            return self.items.pop(0)\n        else:\n            raise IndexError('Queue is empty')\n    \n    def is_empty(self):\n        # Check if the queue is empty\n        return len(self.items) == 0\n    \n    def front(self):\n        # Return the first item without removing it\n        if not self.is_empty():\n            return self.items[0]\n        else:\n            raise IndexError('Queue is empty')\n\n# Example usage\nqueue = Queue()\nqueue.enqueue(1)\nqueue.enqueue(2)\nqueue.enqueue(3)\nprint(queue.dequeue())  # Output: 1\nprint(queue.front())  # Output: 2\n```",
                    "evaluation": {
                        "score": 3.0,
                        "justification": "The implementation achieves core queue functionality with a straightforward list-based approach. Strengths include:\n        - Correct basic queue operations (enqueue, dequeue, is_empty, front)\n        - Simple and readable implementation\n        - Demonstrates fundamental queue data structure principles\n\n        Limitations preventing a higher score:\n        - Uses list.pop(0), which is O(n) time complexity for dequeuing\n        - Lacks type hints for better type safety\n        - No size limit or maximum capacity handling\n        - Minimal error handling\n        - No docstrings or comprehensive method documentation"
                    }
                },
                {
                    "question": "How do you implement a stack data structure in Python?",
                    "solution": "Here's an implementation of a stack using a list:\n\n```python\nclass Stack:\n    def __init__(self):\n        self.items = []\n    \n    def push(self, item):\n        # Add item to the top of the stack\n        self.items.append(item)\n    \n    def pop(self):\n        # Remove and return the top item\n        if not self.is_empty():\n            return self.items.pop()\n        else:\n            raise IndexError('Stack is empty')\n    \n    def is_empty(self):\n        # Check if the stack is empty\n        return len(self.items) == 0\n    \n    def peek(self):\n        # Return the top item without removing it\n        if not self.is_empty():\n            return self.items[-1]\n        else:\n            raise IndexError('Stack is empty')\n\n# Example usage\nstack = Stack()\nstack.push(1)\nstack.push(2)\nstack.push(3)\nprint(stack.pop())  # Output: 3\nprint(stack.peek())  # Output: 2\n```",
                    "evaluation": {
                        "score": 3.0,
                        "justification": "The code achieves a solid 3-point implementation by:\n        - Correctly implementing core stack functionality (push, pop, peek, is_empty methods)\n        - Using a list as an efficient underlying data structure\n        - Providing basic error handling with IndexError for empty stack operations\n        - Following Pythonic coding conventions with clear method names\n        \n        Areas for improvement to reach a higher score include:\n        - Adding type hints for better type safety\n        - Implementing more robust error handling\n        - Adding docstrings for better documentation\n        - Potentially supporting a maximum stack size\n        - Adding more comprehensive method validation"
                    }
                },
                {
                    "question": "How do you implement a binary search tree in Python?",
                    "solution": "Here's an implementation of a binary search tree:\n\n```python\nclass TreeNode:\n    def __init__(self, value):\n        self.value = value\n        self.left = None\n        self.right = None\n\nclass BinarySearchTree:\n    def __init__(self):\n        self.root = None\n    \n    def insert(self, value):\n        # Insert a new value into the BST\n        if not self.root:\n            self.root = TreeNode(value)\n        else:\n            self._insert_recursive(self.root, value)\n    \n    def _insert_recursive(self, node, value):\n        if value < node.value:\n            if node.left is None:\n                node.left = TreeNode(value)\n            else:\n                self._insert_recursive(node.left, value)\n        else:\n            if node.right is None:\n                node.right = TreeNode(value)\n            else:\n                self._insert_recursive(node.right, value)\n    \n    def inorder_traversal(self):\n        # Traverse the tree in-order\n        result = []\n        self._inorder_recursive(self.root, result)\n        return result\n    \n    def _inorder_recursive(self, node, result):\n        if node:\n            self._inorder_recursive(node.left, result)\n            result.append(node.value)\n            self._inorder_recursive(node.right, result)\n\n# Example usage\nbst = BinarySearchTree()\nbst.insert(5)\nbst.insert(3)\nbst.insert(7)\nbst.insert(1)\nprint(bst.inorder_traversal())  # Output: [1, 3, 5, 7]\n```",
                    "evaluation": {
                        "score": 3.0,
                        "justification": "The code achieves 3 points by implementing core binary search tree functionality correctly. It provides:\n        - A basic TreeNode class with value and child node references\n        - Recursive insertion method that maintains BST properties\n        - Inorder traversal to display tree contents\n        - Simple and clear implementation of fundamental BST operations\n\n        Strengths:\n        - Correct recursive insertion logic\n        - Proper tree structure representation\n        - Basic traversal method\n\n        Areas for Improvement:\n        - Lacks error handling (e.g., duplicate value handling)\n        - No type hints for better type safety\n        - Missing additional methods like search, delete, and balancing\n        - No comprehensive documentation or docstrings\n        - Limited edge case management"
                    }
                },
                {
                    "question": "How do you implement a hash table (dictionary) in Python?",
                    "solution": "Here's a simple implementation of a hash table:\n\n```python\nclass HashTable:\n    def __init__(self, size=100):\n        self.size = size\n        self.table = [[] for _ in range(self.size)]\n    \n    def _hash_function(self, key):\n        # Simple hash function\n        return hash(key) % self.size\n    \n    def insert(self, key, value):\n        # Insert a key-value pair\n        index = self._hash_function(key)\n        for item in self.table[index]:\n            if item[0] == key:\n                item[1] = value\n                return\n        self.table[index].append([key, value])\n    \n    def get(self, key):\n        # Retrieve a value by key\n        index = self._hash_function(key)\n        for item in self.table[index]:\n            if item[0] == key:\n                return item[1]\n        raise KeyError(key)\n    \n    def remove(self, key):\n        # Remove a key-value pair\n        index = self._hash_function(key)\n        for i, item in enumerate(self.table[index]):\n            if item[0] == key:\n                del self.table[index][i]\n                return\n        raise KeyError(key)\n\n# Example usage\nht = HashTable()\nht.insert('name', 'Alice')\nht.insert('age', 30)\nprint(ht.get('name'))  # Output: Alice\nht.remove('age')\n```",
                    "evaluation": {
                        "score": 3,
                        "justification": "The implementation achieves 3 points by:         - Correctly implementing core hash table functionality (insertion, retrieval, removal)         - Using a simple but effective hash function with modulo operation         - Handling collision resolution through chaining (using lists)         - Providing a clean, readable implementation with basic error handling          Areas for improvement:         - Lacks type hints for better type safety         - No comprehensive error handling or input validation         - Missing advanced features like resizing or load factor management         - No docstrings or detailed documentation         - Performance could be optimized for large datasets"
                    }
                }
            ]
        },
        "Overall_Average": 3.25
    },
    "output_path": "qa_pairs_claude_20241215_225902_evaluated.json"
};



export const getTopicMap = (evaluateResult: EvaluateResult) => {
    console.log('---evaluateResult', evaluateResult);
    const result = get(evaluateResult, 'result');
    let topicMap = {};
    const topics = [];

    if (!isEmpty(result)) {
        const keys = Object.keys(result);
        forEach(keys, (topicName: string) => {
            const value = get(result, topicName);
            if (topicName !== 'Overall_Average') {
                topics.push(topicName);
            }
            if (isObject(value)) {
                topicMap = set(topicMap, topicName, value);
            }
        });
    }

    return {
        topics,
        topicMap
    }
};

export enum MODE {
    CREATE = 'CREATE',
    EDIT = 'EDIT'
}

export const FORM_FIELD_META_DATA = {
    caii_endpoint: {
        label: 'Cloudera AI Inference Endpoint',
        tooltip: 'The inference enpoint of your model deployed in Cloudera AI Inference Service',
        doc_link: 'https://docs.cloudera.com/machine-learning/cloud/ai-inference/topics/ml-caii-use-caii.html'
    }
}

export const MAX_PROMPT__EXAMPLES = 5;

export const EVALUATOR_JOB_SUCCESS = 'Your evaluator job has successfully started. Once complete, your evaluation file will be available in your Cloudera AI Workbench Files. Click "View Job" to monitor the progress.'

export const getColorCode = (value: number) => {
    if (value < 3) {
        return '#FF0000';
    } else if (value < 5) {
        return '#faad14';
    }
    return '#52c41a';
}

export const getFilesURL = (fileName: string) => {
    const {
        VITE_WORKBENCH_URL,
        VITE_PROJECT_OWNER,
        VITE_CDSW_PROJECT,
        VITE_IS_COMPOSABLE
    } = import.meta.env

    let previewFileUrl = `${VITE_WORKBENCH_URL}/${VITE_PROJECT_OWNER}/${VITE_CDSW_PROJECT}/preview/${fileName}`;

    // Needed because in prod environment we deploy this app within an iframe and the folder structure is different from CML point of view
    // IS_COMPOSABLE tells us if the app is deployed in prod environment
    if (VITE_IS_COMPOSABLE) {
        previewFileUrl = `${VITE_WORKBENCH_URL}/${VITE_PROJECT_OWNER}/${VITE_CDSW_PROJECT}/preview/synthetic-data-studio/${fileName}`
    }

    return previewFileUrl;
}


