# ============================================================
# Python Objects & Data Structures
# A comprehensive guide with examples
# ============================================================


# ------------------------------------------------------------
# 1. NUMBERS
# ------------------------------------------------------------

# Integer
i = 10
f = 3.14       # Float
c = 2 + 3j     # Complex

print("=== NUMBERS ===")
print(10 // 3)          # 3   - floor division
print(10 % 3)           # 1   - modulus
print(2 ** 8)           # 256 - power
print(abs(-7))          # 7   - absolute value
print(round(3.14159, 2)) # 3.14


# ------------------------------------------------------------
# 2. STRINGS
# ------------------------------------------------------------

print("\n=== STRINGS ===")
s = "Hello, World!"

print(s[0])                      # H
print(s[-1])                     # !
print(s[0:5])                    # Hello
print(s.upper())                 # HELLO, WORLD!
print(s.lower())                 # hello, world!
print(s.split(", "))             # ['Hello', 'World!']
print(s.replace("World", "Python"))  # Hello, Python!
print(s.strip())                 # Hello, World!
print(f"Length: {len(s)}")       # Length: 13
print(f"Formatted: {42}")        # f-string example


# ------------------------------------------------------------
# 3. LISTS
# ------------------------------------------------------------

print("\n=== LISTS ===")
lst = [1, 2, 3, 4, 5]

lst.append(6)
print("After append:", lst)        # [1, 2, 3, 4, 5, 6]

lst.insert(0, 0)
print("After insert:", lst)        # [0, 1, 2, 3, 4, 5, 6]

lst.pop()
print("After pop:", lst)           # [0, 1, 2, 3, 4, 5]

lst.remove(0)
print("After remove:", lst)        # [1, 2, 3, 4, 5]

print("Reversed:", lst[::-1])      # [5, 4, 3, 2, 1]
print("Sorted:", sorted(lst))      # [1, 2, 3, 4, 5]

# List comprehension
squares = [x**2 for x in lst]
print("Squares:", squares)         # [1, 4, 9, 16, 25]

evens = [x for x in lst if x % 2 == 0]
print("Evens:", evens)             # [2, 4]


# ------------------------------------------------------------
# 4. TUPLES
# ------------------------------------------------------------

print("\n=== TUPLES ===")
t = (1, 2, 3)

print(t[0])              # 1
print(t[-1])             # 3
print(t[1:])             # (2, 3)

# Unpacking
a, b, c = t
print(f"a={a}, b={b}, c={c}")

# Extended unpacking
first, *rest = (1, 2, 3, 4, 5)
print(f"first={first}, rest={rest}")

print("Count of 1:", t.count(1))   # 1
print("Index of 2:", t.index(2))   # 1


# ------------------------------------------------------------
# 5. DICTIONARIES
# ------------------------------------------------------------

print("\n=== DICTIONARIES ===")
d = {"name": "Alice", "age": 25, "city": "Nairobi"}

print(d["name"])                   # Alice
print(d.get("age"))                # 25
print(d.get("email", "N/A"))       # N/A (default)
print(list(d.keys()))              # ['name', 'age', 'city']
print(list(d.values()))            # ['Alice', 25, 'Nairobi']

d.update({"email": "alice@gmail.com"})
print("After update:", d)

del d["city"]
print("After delete:", d)

# Dict comprehension
squares_dict = {x: x**2 for x in range(1, 6)}
print("Squares dict:", squares_dict)

# Looping
for key, value in d.items():
    print(f"  {key}: {value}")


# ------------------------------------------------------------
# 6. SETS
# ------------------------------------------------------------

print("\n=== SETS ===")
s = {1, 2, 3, 4}

s.add(5)
print("After add:", s)

s.discard(99)     # no error if not found
s.remove(3)
print("After remove:", s)

# Set operations
a = {1, 2, 3}
b = {2, 3, 4}
print("Union:", a | b)              # {1, 2, 3, 4}
print("Intersection:", a & b)       # {2, 3}
print("Difference:", a - b)         # {1}
print("Symmetric diff:", a ^ b)     # {1, 4}

# Remove duplicates from a list
dupes = [1, 2, 2, 3, 3, 3, 4]
unique = list(set(dupes))
print("Unique:", unique)


# ------------------------------------------------------------
# 7. BOOLEANS & NONE
# ------------------------------------------------------------

print("\n=== BOOLEANS & NONE ===")
print(bool(0))        # False
print(bool(""))       # False
print(bool([]))       # False
print(bool(None))     # False
print(bool(1))        # True
print(bool("hello"))  # True
print(True + True)    # 2 (bool is subclass of int)

x = None
print(x is None)      # True  ✅ use 'is', not '=='


# ------------------------------------------------------------
# 8. TYPE CHECKING & CONVERSION
# ------------------------------------------------------------

print("\n=== TYPE CHECKING & CONVERSION ===")
print(type(42))               # <class 'int'>
print(type("hello"))          # <class 'str'>
print(isinstance(3.14, float)) # True
print(isinstance([], list))    # True

# Type conversion
print(int("10"))              # 10
print(float(5))               # 5.0
print(str(100))               # "100"
print(list((1, 2, 3)))        # [1, 2, 3]
print(tuple([1, 2, 3]))       # (1, 2, 3)
print(set([1, 1, 2, 3]))      # {1, 2, 3}


# ------------------------------------------------------------
# 9. MUTABILITY SUMMARY
# ------------------------------------------------------------

# | Type    | Mutable | Ordered | Duplicates |
# |---------|---------|---------|------------|
# | list    |   Yes   |   Yes   |    Yes     |
# | tuple   |   No    |   Yes   |    Yes     |
# | dict    |   Yes   |   Yes   |  No (keys) |
# | set     |   Yes   |   No    |    No      |
# | str     |   No    |   Yes   |    Yes     |