%define name			ecl
%define version			10.4.1
%define release			%mkrel 1
%define ecllibdir		%{_libdir}/%{name}-%{version}

%define before_configure	true
%define _disable_libtoolize	%{nil}

Name:           %{name}
Version:        %{version}
Release:        %{release}
Summary:        Embeddable Common-Lisp
Group:          Development/Other
License:        LGPLv2+
URL:            http://ecls.sourceforge.net
Source:         http://switch.dl.sourceforge.net/sourceforge/ecls/%{name}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}

BuildRequires:  m4
BuildRequires:	texinfo
BuildRequires:  texi2html
BuildRequires:  gmp-devel
BuildRequires:  libgc-devel
BuildRequires:  libx11-devel

# ECL permits to mix C code and Lisp, so users probably want gcc and 
# devel packages of libraries used by ecl
Suggests:       gcc
Suggests:       libgc-devel
Suggests:       gmp-devel

%description
ECL (Embeddable Common-Lisp) is an interpreter of the Common-Lisp
language as described in the X3J13 Ansi specification, featuring CLOS
(Common-Lisp Object System), conditions, loops, etc, plus a translator
to C, which can produce standalone executables.

# no -devel package for header files is split off
# since they are required by the main package

%package doc
Summary:      Documentation for Embeddable Common-Lisp
Group:        Development/Other
Requires:     %{name} = %{version}-%{release}

%description doc
ECL (Embeddable Common-Lisp) is an interpreter of the Common-Lisp
language as described in the X3J13 Ansi specification, featuring CLOS
(Common-Lisp Object System), conditions, loops, etc, plus a translator
to C, which can produce standalone executables.

This package contains the documentation for ECL.

%prep
%setup -q -n %{name}-%{version}
# set rpath to the final path
perl -pi -e 's|-Wl,--rpath,~A|-Wl,--rpath,%{_libdir}/ecl|' src/configure
find -name CVS | xargs rm -rf

%build
CONFIGURE_TOP=. \
%configure --enable-boehm=system --enable-threads=yes --with-clx --with-x
# Parallel make does not work
make

# documentation build broken
#(cd build/doc; make)

%install
%makeinstall_std

# documentation build broken
#(cd build/doc; %makeinstall_std)

# install man pages without invoking broken make rules and remove wrongly
# installed files
mkdir -p %{buildroot}/%{_mandir}/man1
cp -f build/doc/ecl{,-config}.man %{buildroot}/%{_mandir}/man1
lzma %{buildroot}/%{_mandir}/man1/*
rm -f %{buildroot}%{_libdir}/{Copyright,LGPL}

rm -fr %{buildroot}%{_infodir}/dir
rm -fr %{buildroot}%{_docdir}
rm -f %{buildroot}/%{ecllibdir}/BUILD-STAMP
find %{buildroot}%{ecllibdir} -name '*.lsp' | xargs chmod 0644 ||:

%files
%defattr(-,root,root,-)
%{_bindir}/ecl
%{_bindir}/ecl-config
%{ecllibdir}
%{_libdir}/libecl.so*
%{_includedir}/ecl
%{_mandir}/man*/*
%doc ANNOUNCEMENT Copyright

%files doc
%defattr(-,root,root,-)
%doc examples
