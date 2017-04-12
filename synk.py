#!/usr/bin/python3

import os, time, argparse, getpass, hashlib


CONFFILE = os.popen("echo $HOME").read().strip('\n') + "/.config/synk.conf"
LOGFILE = "/tmp/synk.log"


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--setup", action="store_true", help="Run the script in setup mode")

    return parser.parse_args()


def setup():
    projectdir = input("Enter directory for project: ").strip()
    usernm = input("Enter username for project directory: ")          # synker
    proto, git_serv = input("Enter url to git project: ").split(':')  # https://github.com/synker/synk.git
    git_serv = git_serv[2:]
    passwd = getpass.getpass()                                        # tosynkornottosynk

    try:
        os.system("git --git-dir=%s --work-tree=%s remote remove origin" % (projectdir + ".git", projectdir))
        os.system("git remote add origin " + proto + "://%s:%s@%s" % (usernm, passwd, git_serv))

        with open(CONFFILE, "w") as cf:
            cf.write(projectdir + "\n" + usernm + "\n" + proto + "\n" + git_serv + "\n" + hashlib.sha512(passwd.encode("utf-8")).hexdigest())
    except Exception as e:
        print("An error occured. Please reenter your information.")
        print(str(e))
        quit()


def detect_changes():
    old_hash = ""
    new_hash = ""
    projectdir = ""
    try:
        with open(CONFFILE, 'r') as cf:
            projectdir = cf.read().split('\n')[0]
        with open(LOGFILE, 'r') as lf:
            for line in lf:
                old_hash += line.strip()
        for rootdir, dirs, files in os.walk(projectdir, topdown=True):
            files = [f for f in files if not f[0] == '.']
            dirs[:] = [d for d in dirs if not d[0] == '.']
            for file in files:
                lines = ""
                with open(file) as f:
                    lines = ''.join([line for line in f])
                new_hash += hashlib.md5(lines.encode("utf-8")).hexdigest()
        with open(LOGFILE, 'w') as lf:
            lf.write(new_hash)
    except FileNotFoundError:
        os.system("touch %s" % LOGFILE)
        return True

    return old_hash != new_hash


def upload_changes():
    os.system("git stash apply && git stash drop && git commit -am 'autocommit' && git push origin master")


def get_changes():
    os.system("git pull origin master --no-edit")


def main():
    args = get_args()
    if args.setup:
        setup()
        quit()
    if not os.path.isfile(CONFFILE):
        print("Please run `./synk_cli.py -s` first.")
        quit()
    while True:
        time.sleep(0.1)
        try:
            if detect_changes():
                os.system("git add -f . && git stash save")
                get_changes()
                upload_changes()
                continue
            get_changes()
        except KeyboardInterrupt:
            break
        except Exception as e:
            print("An error occurred: %s" % str(e))
            break


if __name__ == "__main__":
    main()
