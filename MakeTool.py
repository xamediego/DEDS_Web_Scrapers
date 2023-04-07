import subprocess


def make_woord():
    cmd1 = ['make', 'woord']
    subprocess.run(cmd1)


def make_wordcount():
    cmd1 = ['make', 'wordcount']
    subprocess.run(cmd1)


def make_clear():
    cmd1 = ['make', 'clear']
    subprocess.run(cmd1)


def upload(path_source, path_destination):
    cmd1 = ['docker', 'exec', 'namenode', 'hdfs', 'dfs', '-mkdir', '-p', path_destination]
    subprocess.run(cmd1)

    cmd2 = ['docker', 'cp', path_source, 'namenode:/user-input/']
    subprocess.run(cmd2)

    cmd3 = ['docker', 'exec', 'namenode', 'hdfs', 'dfs', '-copyFromLocal', '-f', '/user-input/', path_destination]
    subprocess.run(cmd3)

    cmd4 = ['docker', 'exec', 'namenode', 'rm', '-rf', '/user-input/*']
    subprocess.run(cmd4)



def remove(path):
    cmd1 = ['docker', 'exec', 'namenode', 'hdfs', 'dfs', '-rm', '-r', path]
    subprocess.run(cmd1)
