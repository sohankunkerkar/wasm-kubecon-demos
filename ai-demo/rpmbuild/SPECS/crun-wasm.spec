Name: crun-wasm
Version: 1.15
Release: %autorelease
License: GPL-2.0-only
Summary: Provides crun built with wasm support
URL: https://github.com/containers/crun
Source0: %{url}/releases/download/%{version}/crun-%{version}.tar.gz
Patch0: 0001-debug-wasi-nn-information.patch
# wasmedge is packaged only for aarch64 and x86_64
# Ref: https://src.fedoraproject.org/rpms/wasmedge/raw/rawhide/f/wasmedge.spec
ExclusiveArch: aarch64 x86_64
BuildRequires: autoconf
BuildRequires: automake
BuildRequires: git-core
BuildRequires: libcap-devel
BuildRequires: libseccomp-devel
BuildRequires: libtool
BuildRequires: systemd-devel
BuildRequires: wasmedge-devel
BuildRequires: yajl-devel
Requires: wasm-library
Recommends: wasmedge

%description
%{name} provides crun built with wasm support

%prep
%autosetup -Sgit -n crun-%{version}

%build
./autogen.sh
%configure --disable-silent-rules --with-wasmedge
%make_build

%install
%make_install
rm -rf %{buildroot}%{_prefix}/lib*
mv %{buildroot}%{_bindir}/crun %{buildroot}%{_bindir}/%{name}
mv %{buildroot}%{_mandir}/man1/crun.1 %{buildroot}%{_mandir}/man1/%{name}.1

%files
%license COPYING
%{_bindir}/%{name}
%{_mandir}/man1/%{name}.1.gz

%changelog
%autochangelog