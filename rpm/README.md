A spec file for Bitcoin Core. The work here is based on the spec file in the
Bitcoin contrib directory. The main difference between this spec and the one in
contrib is that this version is less heavily modified, e.g. it doesn't install
SELinux rules or try to create system directories.

I have created a COPR called
[eklitzke/bitcoin](https://copr.fedorainfracloud.org/coprs/eklitzke/bitcoin/),
with pre-built RPM packages built from this spec file. I would recommend using
the packages built there, unless you would like to actually modify the spec
file. To enable the COPR:

```bash
$ sudo dnf copr enable eklitzke/bitcoin
```

Afterwards you should install the `bitcoin-qt` for the graphical program, or
`bitcoind` for the daemon/command line interface.

If you choose to use `bitcoind`, note that by default it sets up a system-wide
installation with the following characteristics:

 * A `bitcoin` user/group is created
 * A systemd service called `bitcoind.service` becomes available
 * The service is configured to read its config from `/etc/bitcoin/bitcoin.conf`
 * The service is configured to use `/var/lib/bitcoin` as its datadir

If you would like to use `bitcoin-cli` as another user (say, your own user) you
need to create RPC credentials using a provided script. To run the script for an
RPC user named `alice` you run:

```bash
# Create RPC credentials for alice
$ python /usr/share/bitcoin/rpcuser.py alice
```

This will print out an `rpcauth=...` line, which you should add to
`/etc/bitcoin/bitcoin.conf`. It will also print out a password. Use this
password to create a file named `~/.bitcoin/bitcoin.conf` with your credentials:

```bash
$ mkdir -m 700 ~/.bitcoin
$ cat <<EOF > ~/.bitcoin/bitcoin.conf
rpcuser=alice
rpcpassword=the-password-from-rpcuser.py
EOF
```

If everything worked correctly, once you start the service (`systemctl start
bitcoind`) you should be able to run commands like `bitcoin-cli uptime` without
error. If you're bootstrapping the node, you may find the following command
helpful to check its progress (as a value from 0 to 1):

```bash
# Check progress of initial blockchain sync.
$ bitcoin-cli getblockchaininfo | jq .verificationprogress -
```
