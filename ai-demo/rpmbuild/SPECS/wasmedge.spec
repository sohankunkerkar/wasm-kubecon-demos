%global version 0.14.0
%global reponame WasmEdge
%global capi_soname 0
%global capi_version 0.1.0

Name:    wasmedge
Version: %{version}
Release: %autorelease
Summary: High performance WebAssembly Virtual Machine
# The entire source code is ASL 2.0 except LICENSE.spdx which is CC0
License: ASL 2.0 and CC0
URL:     https://github.com/%{reponame}/%{reponame}
Source0: %{url}/releases/download/%{version}/%{reponame}-%{version}-src.tar.gz
BuildRequires: cmake
BuildRequires: gcc-c++
BuildRequires: git
BuildRequires: lld-devel
BuildRequires: llvm-devel
BuildRequires: ninja-build
BuildRequires: spdlog-devel
BuildRequires: openssl-devel
Requires:      lld
Requires:      llvm
Requires:      spdlog
# Currently wasmedge could only be built on specific arches
ExclusiveArch: x86_64 aarch64
Provides: %{reponame} = %{version}-%{release}
Provides: bundled(blake3) = 1.2.0
Provides: bundled(wasi-cpp-header) = 0.0.1
Provides: wasm-library
Conflicts: %{name}-rt

%description
High performance WebAssembly Virtual Machine

%package rt
Summary: %{reponame} Runtime
Requires: spdlog
Provides: %{reponame}-rt = %{version}-%{release}
Provides: bundled(blake3) = 1.3.3
Provides: bundled(wasi-cpp-header) = 0.0.1
Provides: wasm-library
Conflicts: %{name}
RemovePathPostfixes: .rt

%description rt
This package contains only %{reponame} runtime without LLVM dependency.

%package devel
Summary: %{reponame} development files
Requires: %{name}%{?_isa} = %{version}-%{release}
Provides: %{reponame}-devel = %{version}-%{release}

%description devel
This package contains necessary header files for %{reponame} development.

%prep
%autosetup -n %{name}
[ -f VERSION ] || echo -n %{version} > VERSION

%build
%cmake -GNinja -DCMAKE_BUILD_TYPE=RelWithDebInfo \
    -DBUILD_SHARED_LIBS=OFF \
    -DWASMEDGE_BUILD_TESTS=OFF \
    -DWASMEDGE_PLUGIN_WASI_NN=ON \
    -DWASMEDGE_PLUGIN_WASI_NN_BACKEND="GGML" \
    -DWASMEDGE_PLUGIN_WASI_NN_GGML_LLAMA=ON \
    -DWASMEDGE_PLUGIN_WASI_NN_GGML_LLAMA_NATIVE=ON \
    -DWASMEDGE_PLUGIN_WASI_NN_RUST_MODEL="squeezenet;whisper" \
    .
%cmake_build
mkdir rt
cd rt
%cmake -S .. -GNinja -DCMAKE_BUILD_TYPE=RelWithDebInfo \
    -DBUILD_SHARED_LIBS=OFF \
    -DWASMEDGE_BUILD_TESTS=OFF \
    -DWASMEDGE_BUILD_AOT_RUNTIME=OFF \
    -DWASMEDGE_PLUGIN_WASI_NN=ON \
    -DWASMEDGE_PLUGIN_WASI_NN_BACKEND="GGML" \
    -DWASMEDGE_PLUGIN_WASI_NN_GGML_LLAMA=ON \
    -DWASMEDGE_PLUGIN_WASI_NN_GGML_LLAMA_NATIVE=ON \
    -DWASMEDGE_PLUGIN_WASI_NN_RUST_MODEL="squeezenet;whisper" \
    .
%cmake_build

%install
cd rt
%cmake_install
mv %{buildroot}%{_bindir}/wasmedge{,.rt}
mv %{buildroot}%{_libdir}/lib%{name}.so.%{capi_version}{,.rt}
mv %{buildroot}%{_libdir}/lib%{name}.so.%{capi_soname}{,.rt}
mv %{buildroot}%{_libdir}/lib%{name}.so{,.rt}
rm -rf %{buildroot}%{_includedir}
cd ..
%cmake_install

# Remove unpackaged files
rm -f %{buildroot}%{_bindir}/convert.py
rm -f %{buildroot}%{_includedir}/ggml-alloc.h
rm -f %{buildroot}%{_includedir}/ggml-backend.h
rm -f %{buildroot}%{_includedir}/ggml.h
rm -f %{buildroot}%{_includedir}/llama.h
rm -f %{buildroot}%{_libdir}/libllama.a
rm -rf %{buildroot}%{_libdir}/cmake/Llama

%files
%license LICENSE LICENSE.spdx
%doc Changelog.md README.md SECURITY.md
%{_bindir}/wasmedge
%{_bindir}/wasmedgec
%{_libdir}/lib%{name}.so.%{capi_version}
%{_libdir}/lib%{name}.so.%{capi_soname}
%{_libdir}/wasmedge/libwasmedgePluginWasiNN.so

%files rt
%license LICENSE LICENSE.spdx
%doc Changelog.md README.md SECURITY.md
%{_bindir}/wasmedge.rt
%{_libdir}/lib%{name}.so.%{capi_version}.rt
%{_libdir}/lib%{name}.so.%{capi_soname}.rt
%{_libdir}/lib%{name}.so.rt

%files devel
%dir %{_includedir}/%{name}
%{_includedir}/%{name}/enum.inc
%{_includedir}/%{name}/enum_configure.h
%{_includedir}/%{name}/enum_errcode.h
%{_includedir}/%{name}/enum_types.h
%{_includedir}/%{name}/int128.h
%{_includedir}/%{name}/version.h
%{_includedir}/%{name}/wasmedge.h
%{_libdir}/lib%{name}.so
%{_libdir}/wasmedge/libwasmedgePluginWasiNN.so

# Exclude files that should not be packaged
%exclude %{_includedir}/simdjson.h
%exclude %{_libdir}/libsimdjson.a
%exclude %{_libdir}/pkgconfig/simdjson.pc
%exclude %{_libdir}/cmake/simdjson/

%changelog
%autochangelog
