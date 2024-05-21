

file_base_installs = open('nt.txt', 'r')
base_installs = file_base_installs.readlines()
file_base_installs.close()


file_requirements = open('requirements.txt')
requirements = file_requirements.readlines()

required_packages = {  line:True for line in requirements}

for line in base_installs:
    if line in requirements:
        required_packages.pop(line)


new_requirements = open('requirements.txt.new', 'w')
for line in required_packages:
    new_requirements.write(line)
new_requirements.close()
