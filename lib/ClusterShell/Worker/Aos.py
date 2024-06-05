#
# Copyright (C) 2008-2015 CEA/DAM
#
# This file is part of ClusterShell.
#
# ClusterShell is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# ClusterShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with ClusterShell; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

"""
ClusterShell kubectl/kubectl cp support

This module implements kubctl engine client and task's worker.
"""

import os
# Older versions of shlex can not handle unicode correctly.
# Consider using ushlex instead.
import shlex

from ClusterShell.Worker.Exec import ExecClient, CopyClient, ExecWorker


class aosClient(ExecClient):
    """
    Ssh EngineClient.
    """

    def _build_cmd(self):
        """
        Build the shell command line to start the ssh command.
        Return an array of command and arguments.
        """
        # return (["kubectl", "exec", "-it", "-n", "ncs-system", self.key, "--", self.command], None)
        # kubectl exec -i -n ncs-system aos-sc-r0fi8jts -- /bin/sh -c "cat  ok.txt"
        tmp = self.command
        # tmp="'" + tmp + "'"
        print("ssh.py: tmp:", tmp)
        print("ssh.py: self.command:", self.command)
        # cmd_l = ["kubectl", "exec", "-it", "-n", "ncs-system", self.key, "--", "/bin/sh"]
        cmd_l = ["kubectl", "exec", "-i", "-n", "ncs-system", self.key, "--", "/bin/sh", "-c", tmp]
        # if command is cat ok.txt then I should append 'cat ok.txt' to cmd_l
        
        return (cmd_l, None)
        task = self.worker.task
        path = task.info("aos_path") or "kubectl"
        user = task.info("aos_user")
        options = task.info("aos_options")

        # Build ssh command
        cmd_l = [os.path.expanduser(pathc) for pathc in shlex.split(path)]

        # Add custom ssh options first as the first obtained value is
        # used. Thus all options are overridable by custom options.
        if options:
            # use expanduser() for options like '-i ~/.ssh/my_id_rsa'
            cmd_l += [os.path.expanduser(opt) for opt in shlex.split(options)]

        # Hardwired options (overridable by ssh_options)
        # note: you should use only long-format options here

        if user:
            cmd_l.append("-l")
            cmd_l.append(user)

        connect_timeout = task.info("connect_timeout", 0)
        if connect_timeout > 0:
            cmd_l.append("-oConnectTimeout=%d" % connect_timeout)

        # Disable passphrase/password querying
        # When used together with sshpass this must be overwritten
        # by a custom option to "-oBatchMode=no".
        cmd_l.append("-oBatchMode=yes")

        cmd_l.append("%s" % self.key)
        cmd_l.append("%s" % self.command)
        
        print("ssh.py: cmd_l:", cmd_l)

        return (cmd_l, None)

class aoscpClient(CopyClient):
    """
    Scp EngineClient.
    """

    def _build_cmd(self):
        """
        Build the shell command line to start the scp command.
        Return an array of command and arguments.
        """

        # task = self.worker.task
        # path = task.info("scp_path") or "scp"
        # user = task.info("scp_user") or task.info("ssh_user")

        # # If defined exclusively use scp_options. If no scp_options
        # # given use ssh_options instead.
        # options = task.info("scp_options") or task.info("ssh_options")

        # # Build scp command
        # cmd_l = [os.path.expanduser(pathc) for pathc in shlex.split(path)]

        # # Add custom ssh options first as the first obtained value is
        # # used. Thus all options are overridable by custom options.
        # if options:
        #     # use expanduser() for options like '-i ~/.ssh/my_id_rsa'
        #     cmd_l += [os.path.expanduser(opt) for opt in shlex.split(options)]



        # # Hardwired options
        # if self.isdir:
        #     cmd_l.append("-r")




        # if self.preserve:
        #     cmd_l.append("-p")

        # connect_timeout = task.info("connect_timeout", 0)
        # if connect_timeout > 0:
        #     cmd_l.append("-oConnectTimeout=%d" % connect_timeout)

        # Disable passphrase/password querying
        # When used together with sshpass this must be overwritten
        # by a custom option to "-oBatchMode=no".
        #cmd_l.append("-oBatchMode=yes")


        if self.reverse:

            # return "kubectl cp -n ncs-system aos-sc-r0fi8jts:ok.txt  /etc/clustershell/ok.txt"
            # return (["kubectl", "cp", "-n", "ncs-system", "%s:%s" % (self.key, self.source), self.dest], None)
            tmp = self.dest
            if tmp[-1] == '/':
                tmp = tmp[:-1]
            # find the source file name out of /home/../randomfile.txt and append it to the dest
            print(" os.path.basename(self.source):", os.path.basename(self.source))
            tmp = tmp + "/" + os.path.basename(self.source)
            cmd_l = ["kubectl", "cp", "-n", "ncs-system", "%s:%s" % (self.key, self.source), tmp]

            # if user:
            #     cmd_l.append("%s@[%s]:%s" % (user, self.key, self.source))
            # else:
            #     cmd_l.append("[%s]:%s" % (self.key, self.source))

            # cmd_l.append(os.path.join(self.dest, "%s.%s" % \
            #              (os.path.basename(self.source), self.key)))
        else:

            # return "kubectl cp randomfile.txt -n ncs-system aos-sc-r0fi8jts:/home/random.txt"
            # return (["kubectl", "cp", self.source, "-n", "ncs-system", "%s:%s" % (self.key, self.dest)], None)
            
            cmd_l = ["kubectl", "cp", self.source, "-n", "ncs-system", "%s:%s" % (self.key, self.dest)]

            
            # cmd_l.append(self.source)
            # if user:
            #     cmd_l.append("%s@[%s]:%s" % (user, self.key, self.dest))
            # else:
            #     cmd_l.append("[%s]:%s" % (self.key, self.dest))
        print("aos.py: aoscpclient: cmd_l:", cmd_l)
        return (cmd_l, None)

class WorkerSsh(ExecWorker):
    """
    ClusterShell ssh-based worker Class.

    Remote Shell (ssh) usage example:
       >>> worker = WorkerSsh(nodeset, handler=MyEventHandler(),
       ...                    timeout=30, command="/bin/hostname")
       >>> task.schedule(worker)      # schedule worker for execution
       >>> task.resume()              # run

    Remote Copy (scp) usage example:
       >>> worker = WorkerSsh(nodeset, handler=MyEventHandler(),
       ...                    timeout=30, source="/etc/my.conf",
       ...                    dest="/etc/my.conf")
       >>> task.schedule(worker)      # schedule worker for execution
       >>> task.resume()              # run
    """

    SHELL_CLASS = aosClient
    COPY_CLASS = aoscpClient

WORKER_CLASS=WorkerSsh
