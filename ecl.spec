%define _disable_lto 1

# (fedora)
# The package notes feature leads to failed builds for everything that depends
# on ECL.  Turn it off until somebody figures out how to make it work without
# polluting linker flags.
%undefine _package_note_file

Summary:	Embeddable Common-Lisp
Name:		ecl
Version:	21.2.1
Release:	2
Group:		Development/Other
License:	LGPLv2+ and BSD and MIT and Public Domain
URL:		https://common-lisp.net/project/ecl/
Source0:	https://common-lisp.net/project/%{name}/static/files/release/%{name}-%{version}.tgz
Source1:	%{name}.desktop
# A modified version of src/util/ecl.svg with extra whitespace removed. The
# extra whitespace made the icon appear very small and shoved into a corner.
Source2:	%{name}.svg
# Metainfo for ECL
Source3:	net.common-lisp.ecl.metainfo.xml
Source4:	%{name}.rpmlintrc
# This patch was sent upstream on 4 Feb 2012. It fixes a few warnings
# from the C compiler that indicate situations that might be dangerous at
# runtime.
Patch0:		%{name}-21.2.1-warnings.patch
# Do not use a separate thread to handle signals by default if built with
# boehm-gc support.
# This prevents a deadlock when building maxima with ecl support in
# fedora, and should handle by default these problems:
# http://trac.sagemath.org/sage_trac/ticket/11752
# http://www.mail-archive.com/ecls-list@lists.sourceforge.net/msg00644.html
Patch1:		%{name}-20.4.24-signal_handling_thread.patch
# Work around xsltproc requiring namespace declarations for entities. This
# patch was sent upstream 3 Jun 2013.
# GCC does not implement support for #pragma STDC FENV_ACCESS
Patch2:		%{name}-20.4.24-fenv-access.patch
# Avoid an infinite loop if there is a write error on stderr.  See
# build/pkgs/ecl/patches/write_error.patch in the sagemath distribution.
Patch3:		%{name}-20.4.24-write-error.patch
# Fix bogus test compromised by LTO.
Patch4:		%{name}-20.4.24-configure.patch

#BuildRequires:	docbook-schemas
BuildRequires:	docbook-style-xsl
BuildRequires: 	emacs-common
BuildRequires:	gmp-devel
BuildRequires:	pkgconfig(atomic_ops)
BuildRequires:	pkgconfig(bdw-gc)
BuildRequires:	pkgconfig(libffi)
BuildRequires:	pkgconfig(x11)
#BuildRequires:	texi2html
BuildRequires:	texinfo
#BuildRequires:	texlive
#BuildRequires:	info
BuildRequires:	xmlto

# ECL permits to mix C code and Lisp, so users probably want clang and
# devel packages of libraries used by ecl
Requires:	clang
Requires:	glibc-devel
Requires:	gmp-devel
Requires:	pkgconfig(atomic_ops)
Requires:	pkgconfig(bdw-gc)
Requires:	pkgconfig(libffi)
Requires:	pkgconfig(x11)

%description
ECL (Embeddable Common-Lisp) is an interpreter of the Common-Lisp
language as described in the X3J13 Ansi specification, featuring CLOS
(Common-Lisp Object System), conditions, loops, etc, plus a translator
to C, which can produce standalone executables.

%files
%license COPYING LICENSE
%doc examples CHANGELOG README.md build/doc/manual/html
%doc src/doc/amop.txt src/doc/types-and-classes
%{_bindir}/ecl
%{_bindir}/ecl-config
%{_includedir}/ecl
%{_libdir}/ecl*
%{_libdir}/libecl.so.*
%{_libdir}/libecl.so
%{_datadir}/applications/ecl.desktop
%{_datadir}/icons/hicolor/scalable/apps/ecl.svg
%{_metainfodir}/net.common-lisp.ecl.metainfo.xml
%{_mandir}/man1/*
#{_infodir}/*.info*

# no -devel package for header files is split off
# since they are required by the main package

#--------------------------------------------------------------------

%prep
%autosetup -p0

# Temporary fix for missing braces in initializers, causes build failure
#sed -i 's/{.*,.*,.*,.*,.*}/{&}/g' src/c/symbols_list.h
#sed -i 's/{.*,.*,.*,.*}/{&}/g' src/c/unicode/ucd_names_pair.c

# Don't give the library a useless rpath
sed -i "/ECL_LDRPATH='-Wl,--rpath,~A'/d" src/configure

# Adapt to texinfo changes
sed -i 's/mv ecl/&_html/' src/doc/manual/Makefile
 
%build
%configure \
	--disable-rpath \
	--enable-c99complex \
	--enable-manual=html \
	--enable-threads=yes \
	--enable-unicode=yes \
	--with-clx \
	--with-sse=auto \
	--with-__thread \
	CFLAGS="%{optflags} -Wno-unused -Wno-return-type -Wno-unknown-pragmas"
%make_build -j1

%check
%make_build -j1 check

%install
%make_install

# Remove installed files that are in the wrong place
rm -fr %{buildroot}%{_docdir}
rm -f %{buildroot}%{_libdir}/Copyright
rm -f %{buildroot}%{_libdir}/LGPL

# man pages
mkdir -p %{buildroot}%{_mandir}/man1
sed -e "s|@bindir@|%{_bindir}|" src/doc/ecl.man.in > \
	%{buildroot}%{_mandir}/man1/ecl.1
cp -p src/doc/ecl-config.man.in %{buildroot}%{_mandir}/man1/ecl-config.1

# Add missing executable bits
chmod a+x %{buildroot}%{_libdir}/ecl-%{version}/dpp
chmod a+x %{buildroot}%{_libdir}/ecl-%{version}/ecl_min

# .desktop
desktop-file-install --dir=%{buildroot}%{_datadir}/applications %{SOURCE1}

# icon
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/scalable/apps
cp -p %{SOURCE2} %{buildroot}%{_datadir}/icons/hicolor/scalable/apps

# appdata
mkdir -p %{buildroot}%{_metainfodir}
install -pm 644 %{SOURCE3} %{buildroot}%{_metainfodir}
appstreamcli validate --no-net \
	%{buildroot}%{_metainfodir}/net.common-lisp.ecl.metainfo.xml

