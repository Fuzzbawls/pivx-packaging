%if 0%{?_no_wallet}
%define walletargs --disable-wallet
%define _buildqt 0
%define guiargs --with-gui=no
%else
%if 0%{?_no_gui}
%define _buildqt 0
%define guiargs --with-gui=no
%else
%define _buildqt 1
%define guiargs --with-qrencode --with-gui=qt5
%endif
%endif

Name:    pivx
Version: 3.2.1
Release: 1%{?dist}
Summary: Peer to Peer Cryptographic Currency
Group:   Applications/System
License: MIT
URL:     https://pivx.org/
Source0: https://github.com/PIVX-Project/PIVX/releases/download/v%{version}/%{name}-%{version}.tar.gz

Source10: pivx.conf
Source11: pivxd.service
Source12: pivx-qt.desktop
Source13: pivx-qt-testnet.desktop

BuildRequires: gcc-c++
BuildRequires: libtool
BuildRequires: make
BuildRequires: autoconf
BuildRequires: automake
BuildRequires: openssl-devel
BuildRequires: libevent-devel
BuildRequires: boost-devel
BuildRequires: miniupnpc-devel

%description
PIVX is a digital cryptographic currency that uses peer-to-peer technology to
operate with no central authority or banks; managing transactions and the
issuing of PIVs is carried out collectively by the network.

%if %{_buildqt}
%package qt
Summary:        Peer to Peer Cryptographic Currency
Group:          Applications/System
Obsoletes:      %{name} < %{version}-%{release}
Provides:       %{name} = %{version}-%{release}
BuildRequires: libdb4-devel
BuildRequires: libdb4-cxx-devel
BuildRequires: qt5-qttools-devel
BuildRequires: qt5-qtbase-devel
BuildRequires: protobuf-devel
BuildRequires: qrencode-devel
BuildRequires: desktop-file-utils

%description qt
PIVX is a digital cryptographic currency that uses peer-to-peer technology to
operate with no central authority or banks; managing transactions and the
issuing of PIVs is carried out collectively by the network.

This package contains the Qt based graphical client and node. If you are looking
to run a PIVX wallet, this is probably the package you want.

%package qt-testnet
Summary:        Peer to Peer Cryptographic Currency
Group:          Applications/System
Requires:       %{name}-qt = %{version}-%{release}

%description qt-testnet
This package provides a .desktop file that launches the PIVX Qt client in
testnet mode.

%endif

%package -n pivx-cli
Summary:        CLI utils for PIVX
Group:          Applications/System

%description -n pivx-cli
This package installs command line programs like pivx-cli and pivx-tx that
can be used to interact with the pivxd daemon.

%package -n pivxd
Summary:        The pivx daemon
Group:          System Environment/Daemons
BuildRequires:  systemd
Requires:       pivx-cli = %{version}-%{release}

%description -n pivxd
This package provides a stand-alone pivx daemon. For most users, this package
is only needed if they need a full-node without the graphical client.

Some third party wallet software will want this package to provide the actual
PIVX node they use to connect to the network.

If you use the graphical PIVX client then you almost certainly do not
need this package.

%prep
%autosetup -n %{name}-%{version}

%build
%configure --disable-bench %{?walletargs} %{?guiargs}
%make_build

%check
make check

%install
make install DESTDIR=%{buildroot}

# no need to generate debuginfo data for the test executables
rm -f %{buildroot}%{_bindir}/test_pivx*

%if %{_buildqt}
# qt icons
install -D -p share/pixmaps/pivx.ico %{buildroot}%{_datadir}/pixmaps/pivx.ico

mkdir -p %{buildroot}%{_datadir}/pivx
install -p share/rpcauth/rpcauth.py %{buildroot}/%{_datadir}/pivx/rpcauth.py

mkdir -p %{buildroot}%{_sharedstatedir}/pivx

mkdir -p %{buildroot}%{_sysconfdir}
install -p %{SOURCE10} %{buildroot}%{_sysconfdir}/pivx.conf

mkdir -p %{buildroot}%{_unitdir}
install -p %{SOURCE11} %{buildroot}%{_unitdir}/pivxd.service

mkdir -p %{buildroot}%{_datadir}/applications
desktop-file-install %{SOURCE12} %{buildroot}%{_datadir}/applications/pivx-qt.desktop
desktop-file-install %{SOURCE13} %{buildroot}%{_datadir}/applications/pivx-qt-testnet.desktop
%endif

%post libs -p /sbin/ldconfig

%postun libs -p /sbin/ldconfig

%pre -n pivxd
getent group pivx >/dev/null || groupadd -r pivx
getent passwd pivx >/dev/null ||\
  useradd -r -g pivx -d %{_sharedstatedir}/pivx -s /sbin/nologin \
  -c "PIVX wallet server" pivx

%post -n pivxd
%systemd_post pivxd.service

%posttrans -n pivxd
%{_bindir}/systemd-tmpfiles --create

%preun -n pivxd
%systemd_preun pivxd.service

%postun -n pivxd
%systemd_postun_with_restart pivxd.service

%clean
rm -rf %{buildroot}

%if %{_buildqt}
%files qt
%defattr(-,root,root,-)
%license COPYING
%doc COPYING doc/README.md doc/bips.md doc/files.md doc/reduce-traffic.md doc/release-notes.md doc/tor.md
%attr(0755,root,root) %{_bindir}/pivx-qt
%attr(0644,root,root) %{_datadir}/applications/pivx-qt.desktop
%attr(0644,root,root) %{_datadir}/pixmaps/*.ico
%attr(0644,root,root) %{_mandir}/man1/pivx-qt.1*

%files qt-testnet
%attr(0644,root,root) %{_datadir}/applications/pivx-qt-testnet.desktop
%endif

%files -n pivx-cli
%defattr(-,root,root,-)
%license COPYING
%attr(0644,root,root) %{_mandir}/man1/pivx-cli.1*
%attr(0644,root,root) %{_mandir}/man1/pivx-tx.1*
%attr(0755,root,root) %{_bindir}/pivx-cli
%attr(0755,root,root) %{_bindir}/pivx-tx

%files -n pivxd
%defattr(-,root,root,-)
%license COPYING
%doc COPYING doc/README.md doc/REST-interface.md doc/bips.md doc/dnsseed-policy.md doc/files.md doc/reduce-traffic.md doc/release-notes.md doc/tor.md
%attr(0644,root,root) %{_mandir}/man1/pivxd.1*
%attr(0644,root,root) %{_unitdir}/pivxd.service
%attr(0644,root,root) %{_sysconfdir}/pivx.conf
%attr(0700,pivx,pivx) %{_sharedstatedir}/pivx
%attr(0755,root,root) %{_bindir}/pivxd
%attr(0644,root,root) %{_datadir}/pivx/rpcauth.py
%config(noreplace) %{_sysconfdir}/pivx.conf
%exclude %{_datadir}/pivx/*.pyc
%exclude %{_datadir}/pivx/*.pyo

%changelog
* Sat Mar 16 2019 Evan Klitzke <evan@eklitzke.org> - 0.17.1-1
- Update for Bitcoin 0.17.1

* Tue Oct 23 2018 Evan Klitzke <evan@eklitzke.org> - 0.17.0-1
- Update for Bitcoin 0.17.0

* Mon Feb 26 2018 Evan Klitzke <evan@eklitzke.org> - 0.16.0-3
- split out bitcoin-cli package

* Fri Feb 23 2018 Evan Klitzke <evan@eklitzke.org> - 0.16.0-2
- Add BuildRequires: systemd for F28/Rawhide

* Fri Feb 23 2018 Evan Klitzke <evan@eklitzke.org> - 0.16.0-1
- Bump for official 0.16.0 release

* Fri Feb 16 2018 Evan Klitzke <evan@eklitzke.org> - 0.16.0rc4-1
- rebuild for rc4

* Sat Feb 10 2018 Evan Klitzke <evan@eklitzke.org> - 0.16.0rc3-2
- Fix for GitHub tarballs (not created with "make dist")

* Sat Feb 10 2018 Evan Klitzke <evan@eklitzke.org> - 0.16.0rc3-1
- rebuilt for rc3

* Mon Feb 05 2018 Evan Klitzke <evan@eklitzke.org> - 0.16.0rc2-2
- rebuilt

* Wed Jan 31 2018 Evan Klitzke <evan@eklitzke.org> - 0.16.0rc1-1
- rebuilt for 0.16

* Wed Dec 13 2017 Evan Klitzke <evan@eklitzke.org> - 0.15.1-13
- Configure systemd to use bitcoin-cli stop to shutdown bitcoind

* Wed Nov 29 2017 Evan Klitzke <evan@eklitzke.org>
- Add .desktop file for bitcoin-qt testnet

* Mon Nov 20 2017 Evan Klitzke <evan@eklitzke.org> - 0.15.1-11
- Mark /etc/bitcoin.conf as a (noreplace) config file

* Sun Nov 19 2017 Evan Klitzke <evan@eklitzke.org> - 0.15.1-10
- Just use /etc/bitcoin.conf, a whole new dir seems unnecessary

* Sun Nov 19 2017 Evan Klitzke <evan@eklitzke.org> - 0.15.1-9
- Remove bitcoin-cli package (move those to bitcoind)
- Set up a real system service for bitcoind

* Wed Nov 15 2017 Evan Klitzke <evan@eklitzke.org> - 0.15.1-8
- Remove bench_bitcoin from the bitcoin-cli package.

* Wed Nov 15 2017 Evan Klitzke <evan@eklitzke.org> - 0.15.1-7
- bitcoin-daemon -> bitcoind, bitcoin-utils -> bitcoin-cli

* Wed Nov 15 2017 Evan Klitzke <evan@eklitzke.org> - 0.15.1-6
- Fix the desktop file.

* Wed Nov 15 2017 Evan Klitzke <evan@eklitzke.org> - 0.15.1-5
- Don't depend on SELinux stuff, rename the .desktop file

* Wed Nov 15 2017 Evan Klitzke <evan@eklitzke.org> - 0.15.1-4
- Split into subpackages.

* Wed Nov 15 2017 Evan Klitzke <evan@eklitzke.org> - 0.15.1-3
- Fix test_bitcoin logic, allow building without wallet.

* Wed Nov 15 2017 Evan Klitzke <evan@eklitzke.org> - 0.15.1-2
- Remove test_bitcoin executable from bindir.

* Tue Nov 14 2017 Evan Klitzke <evan@eklitzke.org> - 0.15.1-1
- Initial build.
