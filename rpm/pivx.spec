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
Version: 3.3.0
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
BuildRequires: libevent-devel
BuildRequires: boost-devel
BuildRequires: miniupnpc-devel
BuildRequires: gmp-devel

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
%doc COPYING doc/README.md doc/files.md doc/release-notes.md doc/tor.md
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
%doc COPYING doc/README.md doc/REST-interface.md doc/dnsseed-policy.md doc/files.md doc/release-notes.md doc/tor.md
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
* Tue Jun 18 2019 Fuzzbawls <fuzzbawls@gmail.com> - 3.3.0-1
- Update for PIVX Core 3.3.0

* Fri Apr 19 2019 Fuzzbawls <fuzzbawls@gmail.com> - 3.2.1-1
- Update for PIVX 3.2.1
