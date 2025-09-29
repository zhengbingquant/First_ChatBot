# TODO:
# Create a function called check_string that takes one string argument
# If the string starts with the letters "The", return "Found it!"
# Otherwise, return "Nope."

# Insert your code here
# def ...

def check_string(s):
    if s.startswith("The"):
        return "Found it!"
    else:
        return "Nope."


# Test cases
str1 = 'The'
str2 = 'Thumbs up'
str3 = 'Theatre can be boring'

print(check_string(str1))    # ➜ Found it!
print(check_string(str2))    # ➜ Nope.
print(check_string(str3))    # ➜ Found it!


