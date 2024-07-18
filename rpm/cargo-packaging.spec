#
# spec file for package cargo-packaging
#
# Copyright (c) 2023 SUSE LLC
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via https://bugs.opensuse.org/
#


Name:           cargo-packaging
Version:        1.1.0+0
Release:        0
Summary:        Macros and tools to assist with cargo and rust packaging
License:        MPL-2.0
Group:          Development/Languages/Rust
URL:            https://github.com/Firstyear/cargo-packaging
Source0:        %{name}-%{version}.tar.gz
Source1:        vendor.tar.xz
Source2:        cargo_config
Requires:       cargo
#Requires:       cargo-auditable
Requires:       zstd
BuildRequires:  cargo
BuildRequires:  zstd

Conflicts:      rust-packaging

%description
A set of macros and tools to assist with cargo and rust packaging, written in a manner
that follows upstream rust's best practices.

%define BUILD_DIR "$PWD"/target

%prep
%setup -a1 -n %{name}-%{version}/upstream
mkdir -p .cargo
cp %{SOURCE2} .cargo/config
tar -xJf %{SOURCE1}

%ifarch %arm32
%define SB2_TARGET armv7-unknown-linux-gnueabihf
%endif
%ifarch %arm64
%define SB2_TARGET aarch64-unknown-linux-gnu
%endif
%ifarch %ix86
%define SB2_TARGET i686-unknown-linux-gnu
%endif

%build
# Adopted from https://github.com/sailfishos/gecko-dev/blob/master/rpm/xulrunner-qt5.spec

export CARGO_HOME="%{BUILD_DIR}/cargo"
export CARGO_BUILD_TARGET=%SB2_TARGET

# When cross-compiling under SB2 rust needs to know what arch to emit
# when nothing is specified on the command line. That usually defaults
# to "whatever rust was built as" but in SB2 rust is accelerated and
# would produce x86 so this is how it knows differently. Not needed
# for native x86 builds
export SB2_RUST_TARGET_TRIPLE=%SB2_TARGET
export RUST_HOST_TARGET=%SB2_TARGET

export RUST_TARGET=%SB2_TARGET
export TARGET=%SB2_TARGET
export HOST=%SB2_TARGET
export SB2_TARGET=%SB2_TARGET

%ifarch %arm32 %arm64
export CROSS_COMPILE=%SB2_TARGET

# This avoids a malloc hang in sb2 gated calls to execvp/dup2/chdir
# during fork/exec. It has no effect outside sb2 so doesn't hurt
# native builds.
export SB2_RUST_EXECVP_SHIM="/usr/bin/env LD_PRELOAD=/usr/lib/libsb2/libsb2.so.1 /usr/bin/env"
export SB2_RUST_USE_REAL_EXECVP=Yes
export SB2_RUST_USE_REAL_FN=Yes
export SB2_RUST_NO_SPAWNVP=Yes
%endif

export CC=gcc
export CXX=g++
export AR="ar"
export NM="gcc-nm"
export RANLIB="gcc-ranlib"
export PKG_CONFIG="pkg-config"


cargo build --offline --release


%install
install -D -p -m 0644 -t %{buildroot}%{_fileattrsdir} %{_builddir}/%{name}-%{version}/upstream/rust.attr
install -D -p -m 0644 -t %{buildroot}%{_rpmconfigdir}/macros.d %{_builddir}/%{name}-%{version}/upstream/macros.cargo

install -D -p -m 0755 -t %{buildroot}%{_rpmconfigdir} %{BUILD_DIR}/%{SB2_TARGET}/release/rust-rpm-prov

install -D -p -m 0755 -t %{buildroot}%{_sysconfdir}/zsh_completion.d %{BUILD_DIR}/%{SB2_TARGET}/release/build/completions/_rust-rpm-prov
install -D -p -m 0755 -t %{buildroot}%{_sysconfdir}/bash_completion.d %{BUILD_DIR}/%{SB2_TARGET}/release/build/completions/rust-rpm-prov.bash

%files

%{_fileattrsdir}/rust.attr
%{_rpmconfigdir}/macros.d/macros.cargo
%{_rpmconfigdir}/rust-rpm-prov

%dir %{_sysconfdir}/zsh_completion.d
%dir %{_sysconfdir}/bash_completion.d
%{_sysconfdir}/zsh_completion.d/*
%{_sysconfdir}/bash_completion.d/*

%changelog
