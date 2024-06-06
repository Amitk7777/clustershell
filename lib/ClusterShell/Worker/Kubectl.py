"""
ClusterShell kubectl/kubectlcp support

This module implements kubctl engine client and task's worker.
"""

import os
# Older versions of shlex can not handle unicode correctly.
# Consider using ushlex instead.
import shlex

from ClusterShell.Worker.Exec import ExecClient, CopyClient, ExecWorker


class kubectlClient(ExecClient):
    """
    Kubectl EngineClient.
    """

    def _build_cmd(self):
        """
        Build the kubernetes command line to start the command.
        Return an array of command and arguments.
        """
        # cmd_l = ["kubectl", "exec", "-i", "-n", "ncs-system", self.key, "--", "/bin/sh", "-c", self.command]  
        # return (cmd_l, None)

        task = self.worker.task
        path = task.info("kubectl_path") or "kubectl"
        # user = task.info("kubectl_user")
        options = task.info("kubectl_options")

        cmd_l = [os.path.expanduser(pathc) for pathc in shlex.split(path)]

        # Add custom  options first as the first obtained value is
        # used. Thus all options are overridable by custom options.
        if options:
            cmd_l += [os.path.expanduser(opt) for opt in shlex.split(options)]

        cmd_l.append("%s" % self.key)
        cmd_l.append("--")
        cmd_l.append("/bin/sh")
        cmd_l.append("-c")
        cmd_l.append("%s" % self.command)
        
        print("kubectl.py: cmd_l:", cmd_l)

        return (cmd_l, None)

class kubectlcpClient(CopyClient):
    """
    kubectlcp EngineClient.
    """

    def _build_cmd(self):
        """
        Build the shell command line to start the kubectlcp command.
        Return an array of command and arguments.
        """

        task = self.worker.task
        path = task.info("kubectlcp_path") or "kubectl"
        # user = task.info("kubectlcp_user") or task.info("kubectl_user")

        # If defined exclusively use kubectlcp_options. If no kubectlcp_options
        # given use kubectl_options instead.
        options = task.info("kubectlcp_options") or task.info("kubectl_options")

        # Build kubectlcp command
        cmd_l = [os.path.expanduser(pathc) for pathc in shlex.split(path)]

        # Add custom kubectl options first as the first obtained value is
        # used. Thus all options are overridable by custom options.
        if options:
            cmd_l += [os.path.expanduser(opt) for opt in shlex.split(options)]


        if self.reverse:
            cmd_l.append("%s:%s" % (self.key, self.source))
            # pod name gets appended in the end of the file name
            cmd_l.append(os.path.join(self.dest, "%s.%s" % \
                         (os.path.basename(self.source), self.key)))
        else:
            cmd_l.append(self.source)
            cmd_l.append("%s:%s" % (self.key, self.dest))
                    
        print("kubectl.py: kubectlcpclient: cmd_l:", cmd_l)
        return (cmd_l, None)

class WorkerKubectl(ExecWorker):
    """
    ClusterShell kubectl-based worker Class.

    Remote Shell (kubectl) usage example:
       >>> worker = WorkerKubectl(nodeset, handler=MyEventHandler(),
       ...                    timeout=30, command="/bin/hostname")
       >>> task.schedule(worker)      # schedule worker for execution
       >>> task.resume()              # run

    Remote Copy (kubectlcp) usage example:
       >>> worker = WorkerKubectl(nodeset, handler=MyEventHandler(),
       ...                    timeout=30, source="/etc/my.conf",
       ...                    dest="/etc/my.conf")
       >>> task.schedule(worker)      # schedule worker for execution
       >>> task.resume()              # run
    """

    SHELL_CLASS = kubectlClient
    COPY_CLASS = kubectlcpClient

WORKER_CLASS=WorkerKubectl
