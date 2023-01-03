# def svgReplace(filename, links):
#     with open(filename, 'r') as file:
#         filedata = file.read()
#
#     for user in links:
#         filedata = filedata.replace(f'>{user}<', f'>{links[user]}<')
#
#     # Write the file out again
#     with open(filename, 'w') as file:
#         file.write(filedata)
#
# def getPercent(value):
#     return f'{value * 100}%'
#
#