import logging
from nornir_netmiko.tasks import netmiko_send_config
from nornir_utils.plugins.functions import print_result
from nornir_utils.plugins.tasks.data import load_yaml
from nornir_jinja2.plugins.tasks import template_file
from nornir import InitNornir
from nornir.core.filter import F


nr = InitNornir()


def load_vars(task):
    data = task.run(task=load_yaml, file=f"./host_vars/{task.host}.yaml")
    task.host["facts"] = data.result


def push_isis(task):
    result = task.run(
        task=template_file,
        template="isis.j2",
        path="./templates",
        severity_level=logging.DEBUG,
    )
    task.host["isis_config"] = result.result
    isis_output = task.host["isis_config"]
    isis_send = isis_output.splitlines()
    task.run(
        task=netmiko_send_config,
        name="Pushing ISIS Commands",
        config_commands=isis_send,
    )


def push_vxlan(task):
    result = task.run(
        task=template_file,
        template="vxlan.j2",
        path="./templates",
        severity_level=logging.DEBUG,
    )
    task.host["vxlan_config"] = result.result
    vxlan_output = task.host["vxlan_config"]
    vxlan_send = vxlan_output.splitlines()
    task.run(
        task=netmiko_send_config,
        name="Pushing VXLAN Commands",
        config_commands=vxlan_send,
    )


pull_vars = nr.run(task=load_vars)
routing = nr.run(task=push_isis)
vxlan_targets = nr.filter(F(groups__contains="leafs"))
vxlan = vxlan_targets.run(task=push_vxlan)
print_result(routing)
print_result(vxlan)
