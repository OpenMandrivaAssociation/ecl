%define Werror_cflags	%{nil}

Name:           ecl
Version:        13.5.1
Release:        1
Summary:        Embeddable Common-Lisp
Group:          Development/Other
License:        LGPLv2+ and BSD and MIT and Public Domain
URL:            http://ecls.sourceforge.net/
Source0:        http://downloads.sourceforge.net/ecls/%{name}-%{version}.tgz
# The manual has not yet been released.  Use the following commands to generate
# the manual tarball:
#   git clone git://ecls.git.sourceforge.net/gitroot/ecls/ecl-doc
#   cd ecl-doc
#   git checkout 5d2657b5b32a2b5df701ba1ffa768e3e05816b70
#   rm -fr .git
#   cd ..
#   tar cJf ecl-doc.tar.xz ecl-doc
Source1:        %{name}-doc.tar.xz
Source2:        %{name}.desktop
# A modified version of src/util/ecl.svg with extra whitespace removed.  The
# extra whitespace made the icon appear very small and shoved into a corner.
Source3:        %{name}.svg
Source4:        %{name}.rpmlintrc
# This patch was sent upstream on 4 Feb 2012.  It fixes a few warnings
# from the C compiler that indicate situations that might be dangerous at
# runtime.
Patch0:         %{name}-13.5.1-warnings.patch
# Do not use a separate thread to handle signals by default if built with
# boehm-gc support.
# This prevents a deadlock when building maxima with ecl support in
# fedora, and should handle by default these problems:
# http://trac.sagemath.org/sage_trac/ticket/11752
# http://www.mail-archive.com/ecls-list@lists.sourceforge.net/msg00644.html
Patch1:         %{name}-13.5.1-signal_handling_thread.patch
# Work around xsltproc requiring namespace declarations for entities.  This
# patch was sent upstream 3 Jun 2013.
Patch2:         %{name}-12.12.1-xsltproc.patch
# GCC does not implement support for #pragma STDC FENV_ACCESS
Patch3:         %{name}-13.5.1-fenv-access.patch

BuildRequires:  m4
BuildRequires:  texi2html
BuildRequires:	texinfo
#BuildRequires:	texlive
BuildRequires:  gmp-devel
BuildRequires:  pkgconfig(bdw-gc)
BuildRequires:  pkgconfig(x11)
BuildRequires:  xmlto

# ECL permits to mix C code and Lisp, so users probably want gcc and 
# devel packages of libraries used by ecl
Suggests:       gcc
Suggests:       pkgconfig(bdw-gc)
Suggests:       gmp-devel

%description
ECL (Embeddable Common-Lisp) is an interpreter of the Common-Lisp
language as described in the X3J13 Ansi specification, featuring CLOS
(Common-Lisp Object System), conditions, loops, etc, plus a translator
to C, which can produce standalone executables.

# no -devel package for header files is split off
# since they are required by the main package

%prep
%setup -q
%setup -q -T -D -a 1
%patch0
%patch1
%patch2
%patch3

# Remove spurious executable bits
chmod a-x src/CHANGELOG
find src/c -type f -perm /0111 | xargs chmod a-x
find src/h -type f -perm /0111 | xargs chmod a-x

%build
export PATH=$PWD/bin:$PATH
CONFIGURE_TOP=$PWD \
%configure2_5x --enable-unicode=yes --enable-c99complex \
%ifarch x86_64
  --enable-threads=yes \
  --with-__thread \
%endif
  --with-clx --disable-rpath \
%ifarch x86_64
  --with-sse \
%endif
  CPPFLAGS=`pkg-config --cflags libffi` \
  CFLAGS="%{optflags}  -fuse-ld=bfd -std=gnu99 -Wno-unused -Wno-return-type" \
  LD=%{_bindir}/ld.bfd
make
mkdir -p ecl-doc/tmp
make -C ecl-doc
rm ecl-doc/html/ecl2.proc

%install
make DESTDIR=$RPM_BUILD_ROOT install

# Remove installed files that are in the wrong place
rm -fr $RPM_BUILD_ROOT%{_docdir}
rm -f $RPM_BUILD_ROOT%{_libdir}/Copyright
rm -f $RPM_BUILD_ROOT%{_libdir}/LGPL

# Install the man pages
mkdir -p $RPM_BUILD_ROOT%{_mandir}/man1
sed -e "s|@bindir@|%{_bindir}|" src/doc/ecl.man.in > \
  $RPM_BUILD_ROOT%{_mandir}/man1/ecl.1
cp -p src/doc/ecl-config.man.in $RPM_BUILD_ROOT%{_mandir}/man1/ecl-config.1

# Add missing executable bits
chmod a+x $RPM_BUILD_ROOT%{_libdir}/ecl-%{version}/dpp
chmod a+x $RPM_BUILD_ROOT%{_libdir}/ecl-%{version}/ecl_min

# Install the desktop file
desktop-file-install --dir=$RPM_BUILD_ROOT%{_datadir}/applications %{SOURCE2}

# Install the desktop icon
mkdir -p $RPM_BUILD_ROOT%{_datadir}/icons/hicolor/scalable/apps
cp -p %{SOURCE3} $RPM_BUILD_ROOT%{_datadir}/icons/hicolor/scalable/apps

%files
%{_bindir}/ecl
%{_bindir}/ecl-config
%{_datadir}/applications/ecl.desktop
%{_datadir}/icons/hicolor/scalable/apps/ecl.svg
%{_libdir}/ecl*
%{_libdir}/libecl.so.13.5*
%{_libdir}/libecl.so.13
%{_libdir}/libecl.so
%{_includedir}/ecl
%{_mandir}/man1/*
%doc ANNOUNCEMENT Copyright LGPL examples src/CHANGELOG
%doc ecl-doc/html src/doc/amop.txt src/doc/types-and-classes
