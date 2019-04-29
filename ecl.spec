#% define Werror_cflags	%{nil}

%global vermajor 16
%global verminor 1
%global verpatch 3

Name:		ecl
Version:	%{vermajor}.%{verminor}.%{verpatch}
Release:	1
Summary:	Embeddable Common-Lisp
Group:		Development/Other
License:	LGPLv2+ and BSD and MIT and Public Domain
URL:		https://common-lisp.net/project/ecl/
Source0:	https://common-lisp.net/project/%{name}/static/files/release/%{name}-%{version}.tgz
# The manual has not yet been released. Use the following commands to generate
# the manual tarball:
#	git clone https://gitlab.com/embeddable-common-lisp/ecl-doc.git
#	cd ecl-doc
#	git checkout a0bab55012b31416dfc8b36da75745a2a7a71621
#	rm -fr .git
#	cd ..
#	tar cJf ecl-doc.tar.xz ecl-doc
Source1:	%{name}-doc.tar.xz
Source2:	%{name}.desktop
# A modified version of src/util/ecl.svg with extra whitespace removed. The
# extra whitespace made the icon appear very small and shoved into a corner.
Source3:	%{name}.svg
Source4:	%{name}.rpmlintrc
# This patch was sent upstream on 4 Feb 2012. It fixes a few warnings
# from the C compiler that indicate situations that might be dangerous at
# runtime.
Patch0:		%{name}-16.1.3-warnings.patch
# Do not use a separate thread to handle signals by default if built with
# boehm-gc support.
# This prevents a deadlock when building maxima with ecl support in
# fedora, and should handle by default these problems:
# http://trac.sagemath.org/sage_trac/ticket/11752
# http://www.mail-archive.com/ecls-list@lists.sourceforge.net/msg00644.html
Patch1:		%{name}-16.1.3-signal_handling_thread.patch
# Work around xsltproc requiring namespace declarations for entities. This
# patch was sent upstream 3 Jun 2013.
# GCC does not implement support for #pragma STDC FENV_ACCESS
Patch2:		%{name}-16.1.3-fenv-access.patch
# fix when building with -Werror=format-security, upstreamable
Patch3:		%{name}-16.1.3-end_of_line.patch
# Upstream patch to fix the SSE printer
Patch4:		%{name}-16.1.3-sse-printer.patch
# Upstream patch to fix maxima test failure with atan with signed zero
Patch5:		%{name}-16.1.3-atan.patch
# Upstream patch to work around https://trac.sagemath.org/ticket/23011
Patch6:		%{name}-16.1.3-format-directive-limit.patch

BuildRequires:	m4
BuildRequires:	texi2html
BuildRequires:	texinfo
#BuildRequires:	texlive
BuildRequires:	gmp-devel
BuildRequires:	pkgconfig(bdw-gc)
BuildRequires:	pkgconfig(x11)
BuildRequires:	xmlto

# ECL permits to mix C code and Lisp, so users probably want clang and
# devel packages of libraries used by ecl
Suggests:	clang
Suggests:	pkgconfig(bdw-gc)
Suggests:	gmp-devel

%description
ECL (Embeddable Common-Lisp) is an interpreter of the Common-Lisp
language as described in the X3J13 Ansi specification, featuring CLOS
(Common-Lisp Object System), conditions, loops, etc, plus a translator
to C, which can produce standalone executables.

%files
%{_bindir}/ecl
%{_bindir}/ecl-config
%{_datadir}/applications/ecl.desktop
%{_datadir}/icons/hicolor/scalable/apps/ecl.svg
%{_libdir}/ecl*
%{_libdir}/libecl.so.%{vermajor}.%{verminor}*
%{_libdir}/libecl.so.%{vermajor}
%{_libdir}/libecl.so
%{_includedir}/ecl
%{_mandir}/man1/*
%doc COPYING LICENSE examples CHANGELOG
%doc ecl-doc/html src/doc/amop.txt src/doc/types-and-classes

# no -devel package for header files is split off
# since they are required by the main package

#--------------------------------------------------------------------

%prep
%setup -q
%setup -q -T -D -a 1
%patch0
%patch1
#% patch2
%patch3
%patch4
%patch5
%patch6

# Remove spurious executable bits
find src/c -type f -perm /0111 | xargs chmod a-x
find src/h -type f -perm /0111 | xargs chmod a-x

# Temporary fix for missing braces in initializers, causes build failure
sed -i 's/{.*,.*,.*,.*,.*}/{&}/g' src/c/symbols_list.h
sed -i 's/{.*,.*,.*,.*}/{&}/g' src/c/unicode/ucd_names_pair.c

%build
%configure \
	--enable-unicode=yes \
	--enable-c99complex \
 	--enable-threads=yes \
	--with-__thread \
	--with-clx \
	--disable-rpath \
	--with-sse=auto \
	CPPFLAGS=`pkg-config --cflags libffi` \
	CFLAGS="%{optflags} -fuse-ld=bfd -std=gnu99 -Wno-unused -Wno-return-type" \
	LD=%{_bindir}/ld.bfd
%make_build

# docs
mkdir -p ecl-doc/tmp
%make_build -C ecl-doc
rm ecl-doc/html/ecl2.proc

%install
%make_install DESTDIR=%{buildroot}

# Remove installed files that are in the wrong place
rm -fr %{buildroot}%{_docdir}
rm -f %{buildroot}%{_libdir}/Copyright
rm -f %{buildroot}%{_libdir}/LGPL

# Install the man pages
mkdir -p %{buildroot}%{_mandir}/man1
sed -e "s|@bindir@|%{_bindir}|" src/doc/ecl.man.in > \
	%{buildroot}%{_mandir}/man1/ecl.1
cp -p src/doc/ecl-config.man.in %{buildroot}%{_mandir}/man1/ecl-config.1

# Add missing executable bits
chmod a+x %{buildroot}%{_libdir}/ecl-%{version}/dpp
chmod a+x %{buildroot}%{_libdir}/ecl-%{version}/ecl_min

# Install the desktop file
desktop-file-install --dir=%{buildroot}%{_datadir}/applications %{SOURCE2}

# Install the desktop icon
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/scalable/apps
cp -p %{SOURCE3} %{buildroot}%{_datadir}/icons/hicolor/scalable/apps

