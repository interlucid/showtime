import grp
import os
import pwd

def drop_privileges(uid_name = "interlucid", gid_name = "interlucid"):
    print(f"our uid is {os.getuid()}")
    print(f"our gid is {os.getgid()}")
    print(os.getenv("USER"))
    print(os.getenv("SUDO_USER"))
    if os.getuid() != 0:
        # We're not root so, like, whatever dude
        return

    # Get the uid/gid from the name
    running_uid = pwd.getpwnam(uid_name).pw_uid
    running_gid = grp.getgrnam(gid_name).gr_gid

    # Remove group privileges
    os.setgroups([])

    # Try setting the new uid/gid
    os.setgid(running_gid)
    os.setuid(running_uid)
    os.environ["USER"] = uid_name
    # Ensure a very conservative umask
    old_umask = os.umask(0)
    print(f"our new uid is {os.getuid()}")
    print(f"our new gid is {os.getgid()}")
    print(os.getenv("USER"))
    print(os.getenv("SUDO_USER"))

def up_privileges(uid_name = "root", gid_name = "root"):
    print(f"our uid is {os.getuid()}")
    print(f"our gid is {os.getgid()}")
    print(os.getenv("USER"))
    print(os.getenv("SUDO_USER"))
    if os.getuid() == 0:
        # We're already root so, like, whatever dude
        return

    # Get the uid/gid from the name
    running_uid = pwd.getpwnam(uid_name).pw_uid
    running_gid = grp.getgrnam(gid_name).gr_gid

    # Remove group privileges
    os.setgroups([])

    # Try setting the new uid/gid
    os.setgid(running_gid)
    os.setuid(running_uid)
    os.environ["USER"] = uid_name
    # Ensure a very conservative umask
    old_umask = os.umask(0)
    print(f"our new uid is {os.getuid()}")
    print(f"our new gid is {os.getgid()}")
    print(os.getenv("USER"))
    print(os.getenv("SUDO_USER"))