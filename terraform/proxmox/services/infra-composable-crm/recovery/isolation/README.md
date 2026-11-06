# Isolation used for the approved restore rehearsal

Recovery CT 9618 only: onboot=0, net0 ip=manual, ip6=manual, link_down=1.
No default route or external egress. To preserve the original container port bindings
without publishing the production IP, Docker's clone-only ExecStartPre assigns
192.168.1.118/32 to the clone loopback interface. This never goes on the bridge.
The corresponding EVA test uses CT 9622 and 192.168.1.122/32.
Do not install this configuration on production CTs.
