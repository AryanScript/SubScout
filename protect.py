ignore_list = """credentials.json
token.pickle
__pycache__/
*.pyc
.env
"""
with open('.gitignore', 'w') as f:
    f.write(ignore_list)
print("SUCCESS! .gitignore created. Your secrets are safe.")