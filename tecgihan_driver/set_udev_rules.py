import subprocess


def run_udev_rule_commands():
    prefix = subprocess.check_output(
        ['ros2', 'pkg', 'prefix', 'tecgihan_driver'], text=True).strip()
    print(prefix)
    print('Copying udev rules')
    cp_command = [
        'sudo', 'cp',
        f'{prefix}/share/tecgihan_driver/debian/udev',
        '/etc/udev/rules.d/90-tecgihan.rules']
    subprocess.run(cp_command, check=True)

    print('Restarting udev')
    reload_command = ['sudo', 'udevadm', 'control', '--reload-rules']
    trigger_command = ['sudo', 'udevadm', 'trigger']

    subprocess.run(reload_command, check=True)
    subprocess.run(trigger_command, check=True)


def main(args=None):
    run_udev_rule_commands()


if __name__ == '__main__':
    main()
