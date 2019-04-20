[![Copr build status](https://copr.fedorainfracloud.org/coprs/fuzzbawls/PIVX/package/pivx/status_image/last_build.png)](https://copr.fedorainfracloud.org/coprs/fuzzbawls/PIVX/package/pivx/)

A spec file for PIVX Core. The work here is based on the spec file(s) written by
[eklitzke](https://github.com/eklitzke/bitcoin-rpm).

I have created a COPR called
[fuzzbawls/PIVX](https://copr.fedorainfracloud.org/coprs/fuzzbawls/pivx/),
with pre-built RPM packages built from this spec file. I would recommend using
the packages built there, unless you would like to actually modify the spec
file. To enable the COPR:

```bash
$ sudo dnf copr enable fuzzbawls/PIVX
```

Afterwards you should install the `pivx-qt` for the graphical program, or
`pivxd` for the daemon/command line interface.

If you choose to use `pivxd`, note that by default it sets up a system-wide
installation with the following characteristics:

 * A `pivx` user/group is created
 * A systemd service called `pivxd.service` becomes available
 * The service is configured to read its config from `/etc/pivx/pivx.conf`
 * The service is configured to use `/var/lib/pivx` as its datadir

If you would like to use `pivx-cli` as another user (say, your own user) you
need to create RPC credentials using a provided script. To run the script for an
RPC user named `alice` you run:

```bash
# Create RPC credentials for alice
$ python /usr/share/pivx/rpcuser.py alice
```

This will print out an `rpcauth=...` line, which you should add to
`/etc/pivx/pivx.conf`. It will also print out a password. Use this
password to create a file named `~/.pivx/pivx.conf` with your credentials:

```bash
$ mkdir -m 700 ~/.pivx
$ cat <<EOF > ~/.pivx/pivx.conf
rpcuser=alice
rpcpassword=the-password-from-rpcuser.py
EOF
```

If everything worked correctly, once you start the service (`systemctl start
pivxd`) you should be able to run commands like `pivx-cli uptime` without
error. If you're bootstrapping the node, you may find the following command
helpful to check its progress (as a value from 0 to 1):

```bash
# Check progress of initial blockchain sync.
$ pivx-cli getblockchaininfo | jq .verificationprogress -
```
